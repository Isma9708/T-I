"""
Dispute Analysis Tool - Web Application
Main Flask application entry point
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go
from werkzeug.utils import secure_filename
from tempfile import mkdtemp

# Import analyzer modules
from Analyzer.data.loader import load_uploaded_dataframes, check_dataframe_compatibility
from Analyzer.processing.states import add_custom_abbreviation
from Analyzer.processing.enrich import enrich_billback_table, enrich_ppm_table
from Analyzer.processing.analyze import analyze_materials
from Analyzer.processing.visualize import create_web_visualizations
from Analyzer.processing.reports import generate_summary_report, export_results

# Configure Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session encryption
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = mkdtemp()
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Home page / file upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    # Check if all required files are present
    required_files = ['billback', 'item_ref', 'ppm', 'states']
    uploaded_files = {}
    
    try:
        for file_type in required_files:
            if file_type not in request.files:
                flash(f"Missing file: {file_type}", "error")
                return redirect(request.url)
            
            file = request.files[file_type]
            
            if file.filename == '':
                flash(f"No selected file for {file_type}", "error")
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                # Secure the filename but keep standard names for internal processing
                filename = secure_filename(file.filename)
                safe_filename = f"{file_type}.xlsx"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
                
                # Save the file
                file.save(file_path)
                uploaded_files[file_type] = file_path
            else:
                flash(f"Invalid file format for {file_type}. Please use Excel files (.xlsx, .xls)", "error")
                return redirect(request.url)
        
        # Store uploaded file paths in session
        session['uploaded_files'] = uploaded_files
        flash("Files uploaded successfully!", "success")
        
        # Check data compatibility
        try:
            billback_df, item_ref_df, ppm_df, states_df = load_uploaded_dataframes(uploaded_files)
            issues = check_dataframe_compatibility(billback_df, item_ref_df, ppm_df, states_df)
            
            if issues:
                flash("Warning: Some issues were detected with your data files.", "warning")
                for issue in issues:
                    flash(issue, "warning")
            
            # Extract filter options
            filter_options = extract_filter_options(billback_df, ppm_df, states_df)
            session['filter_options'] = filter_options
            
            return redirect(url_for('analyzer'))
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            flash(f"Error loading data: {str(e)}", "error")
            return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

def extract_filter_options(billback_df, item_ref_df, ppm_df, states_df):
    """Extract filter options from dataframes for the UI"""
    options = {}
    
    try:
        # Get state abbreviations
        states_df = add_custom_abbreviation(states_df)
        options['markets'] = sorted(states_df['Custom Abbreviation'].dropna().unique().tolist())
        
        # Get brand + package size options
        if not item_ref_df.empty:
            item_ref_df["Brand + Pk size"] = item_ref_df[["Supp. Brand Desc.", "Package Size"]].fillna("").agg(' '.join, axis=1).str.strip()
            options['brands_pk'] = sorted(item_ref_df["Brand + Pk size"].dropna().unique().tolist())
        else:
            options['brands_pk'] = []
        
        # Get years from both dataframes
        years = set()
        
        # Extract years from billback
        if 'Posting Period ' in billback_df.columns:
            billback_dates = pd.to_datetime(billback_df["Posting Period "], errors="coerce")
            bb_years = billback_dates.dt.year.dropna().unique()
            years.update([int(y) for y in bb_years if not pd.isnull(y)])
        
        # Extract years from PPM
        if 'Start' in ppm_df.columns:
            ppm_dates = pd.to_datetime(ppm_df["Start"], errors="coerce")
            ppm_years = ppm_dates.dt.year.dropna().unique()
            years.update([int(y) for y in ppm_years if not pd.isnull(y)])
        
        options['years'] = sorted(list(years))
        options['months'] = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"]
        
        return options
        
    except Exception as e:
        logger.error(f"Error extracting filter options: {str(e)}")
        return {
            'markets': ['FL'],
            'brands_pk': [],
            'years': [],
            'months': ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        }

@app.route('/analyzer')
def analyzer():
    """Main analyzer page"""
    if 'uploaded_files' not in session:
        flash("Please upload files first", "error")
        return redirect(url_for('index'))
        
    filter_options = session.get('filter_options', {})
    return render_template('analyzer.html', filter_options=filter_options)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Run the analysis based on selected filters"""
    if 'uploaded_files' not in session:
        return jsonify({
            'success': False,
            'error': 'No uploaded files found. Please upload files first.'
        })
    
    try:
        # Get filter values
        data = request.get_json()
        selected_market = data.get('market')
        selected_brandpk = data.get('brand')
        selected_year = int(data.get('year'))
        selected_month = data.get('month')
        
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        month_number = months.index(selected_month) + 1 if selected_month in months else None
        
        if not selected_brandpk or not selected_year or not month_number:
            return jsonify({
                'success': False,
                'error': 'Invalid selection. Please select all filter options.'
            })
        
        # Load and prepare dataframes
        file_paths = session.get('uploaded_files')
        billback_df, item_ref_df, ppm_df, states_df = load_uploaded_dataframes(file_paths)
        
        states_df = add_custom_abbreviation(states_df)
        enriched_billback_df = enrich_billback_table(billback_df, states_df, item_ref_df)
        enriched_ppm_df = enrich_ppm_table(ppm_df)
        
        # Filter data based on selections
        billback = enriched_billback_df
        ppm = enriched_ppm_df

        billback_dates = pd.to_datetime(billback['Complete Date'], errors='coerce')
        ppm_dates = pd.to_datetime(ppm['Start'], errors='coerce')

        billback = billback[
            (billback['Custom Abbreviation'].astype(str).str.strip() == selected_market) &
            (billback['Brand + Pk size'].astype(str).str.strip() == selected_brandpk) &
            (billback_dates.dt.year == selected_year) &
            (billback_dates.dt.month == month_number)
        ].copy()

        ppm = ppm[
            (ppm['Dist Name.2'].astype(str).str.strip() == selected_market) &
            (ppm['ppm_Brand+pk size'].astype(str).str.strip() == selected_brandpk) &
            (ppm_dates.dt.year == selected_year) &
            (ppm_dates.dt.month == month_number)
        ].copy()

        if billback.empty or ppm.empty:
            return jsonify({
                'success': False,
                'error': 'No matching records found for the selected filters.'
            })

        # Run analysis
        ppm.loc[:, 'Dist Item#'] = ppm['Dist Item#'].astype(str).str.strip()
        billback.loc[:, 'Material'] = billback['Material'].astype(str).str.strip()
        
        result_df = analyze_materials(billback, ppm, selected_brandpk)
        
        if result_df.empty:
            return jsonify({
                'success': False,
                'error': 'Analysis produced no results.'
            })
        
        # Store results in session for other endpoints
        session['analysis_results'] = result_df.to_json(orient='records', date_format='iso')
        
        # Calculate summary statistics
        stats = {
            'total_records': len(result_df),
            'perfect_matches': len(result_df[result_df['Comment'].isna()]),
            'mismatches': len(result_df[result_df['Comment'].str.contains('mismatch', na=False)]),
            'missing_deals': len(result_df[result_df['Comment'] == 'Missing Deal']),
            'ppm_only': len(result_df[result_df['Comment'] == 'PPM Only']),
            'total_variance': result_df['VAR'].fillna(0).sum(),
            'absolute_variance': result_df['VAR'].abs().fillna(0).sum(),
            'percent_matched': len(result_df[result_df['Comment'].isna()]) / len(result_df) * 100 if len(result_df) > 0 else 0
        }
        
        # Store results and stats in session
        session['analysis_stats'] = stats
        
        # Create visualizations
        visualizations = create_web_visualizations(result_df)
        
        # Convert results to format for data table
        results_for_table = []
        for _, row in result_df.iterrows():
            formatted_row = {}
            for col, val in row.items():
                # Format numeric columns
                if col in ['At price', 'Part Amount', 'Extended Part', 'Net$', 'Unit Rebate$', 'Rebate', 'VAR']:
                    formatted_row[col] = f"{val:,.2f}" if pd.notnull(val) else ""
                elif col in ['Case in Part', 'Quantity']:
                    formatted_row[col] = f"{val:,.0f}" if pd.notnull(val) else ""
                else:
                    formatted_row[col] = str(val) if pd.notnull(val) else ""
            results_for_table.append(formatted_row)
        
        return jsonify({
            'success': True,
            'data': results_for_table,
            'stats': stats,
            'visualizations': visualizations
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Analysis error: {str(e)}"
        })

@app.route('/get_visualization/<viz_type>')
def get_visualization(viz_type):
    """Get a specific visualization"""
    if 'analysis_results' not in session:
        return jsonify({
            'success': False,
            'error': 'No analysis results found. Please run analysis first.'
        })
    
    try:
        result_df = pd.read_json(session['analysis_results'], orient='records')
        fig = create_web_visualizations(result_df, viz_type)
        
        return jsonify({
            'success': True,
            'plot': fig
        })
        
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error creating visualization: {str(e)}"
        })

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate a summary report of the analysis results"""
    if 'analysis_results' not in session:
        return jsonify({
            'success': False,
            'error': 'No analysis results found. Please run analysis first.'
        })
    
    try:
        # Get requested format
        data = request.get_json()
        report_format = data.get('format', 'html')
        
        # Get analysis results and stats
        result_df = pd.read_json(session['analysis_results'], orient='records')
        stats = session.get('analysis_stats', {})
        
        # Generate report
        report_content = generate_summary_report(result_df, stats, report_format)
        
        return jsonify({
            'success': True,
            'report': report_content,
            'format': report_format
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error generating report: {str(e)}"
        })

@app.route('/export_excel')
def export_excel():
    """Export analysis results to Excel"""
    if 'analysis_results' not in session:
        flash("No analysis results found. Please run analysis first.", "error")
        return redirect(url_for('analyzer'))
    
    try:
        # Get analysis results
        result_df = pd.read_json(session['analysis_results'], orient='records')
        
        # Create export filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dispute_analysis_results_{timestamp}.xlsx"
        export_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Export to Excel
        result_df.to_excel(export_path, index=False)
        
        # Send file as download
        return send_file(export_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        flash(f"Error exporting to Excel: {str(e)}", "error")
        return redirect(url_for('analyzer'))

@app.route('/clear')
def clear_session():
    """Clear session data and uploaded files"""
    # Delete uploaded files
    if 'uploaded_files' in session:
        for file_path in session['uploaded_files'].values():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {str(e)}")
    
    # Clear session
    session.clear()
    flash("Session cleared. You can upload new files.", "success")
    return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    flash("File too large. Maximum allowed size is 50MB.", "error")
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def page_not_found(error):
    """Handle page not found errors"""
    return render_template('error.html', error="Page Not Found"), 404

if __name__ == '__main__':
    app.run(debug=True)
