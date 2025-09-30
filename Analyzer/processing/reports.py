"""
Reports Generation Module - Creates formatted reports from analysis results

This module provides functions for generating structured reports in various formats,
including HTML, Markdown, and plain text, to present analysis findings in a readable format.
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, List, Union, Optional, Any
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def generate_summary_report(result_df: pd.DataFrame, 
                           stats: Dict[str, Any], 
                           format_type: str = 'html') -> str:
    """
    Generates a summary report of analysis results
    
    Args:
        result_df: DataFrame with analysis results
        stats: Dictionary of statistics about the results
        format_type: Output format ('html', 'markdown', or 'text')
        
    Returns:
        Formatted report as a string
    """
    if result_df.empty:
        logger.warning("Empty dataframe provided for report generation")
        return f"No data available for report generation"
    
    try:
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate additional stats if not provided
        if not stats:
            stats = {
                'total_records': len(result_df),
                'perfect_matches': len(result_df[result_df['Comment'].isna()]),
                'mismatches': len(result_df[result_df['Comment'].str.contains('mismatch', na=False)]),
                'missing_deals': len(result_df[result_df['Comment'] == 'Missing Deal']),
                'ppm_only': len(result_df[result_df['Comment'] == 'PPM Only']),
                'total_variance': result_df['VAR'].fillna(0).sum(),
                'absolute_variance': result_df['VAR'].abs().fillna(0).sum(),
                'percent_matched': (len(result_df[result_df['Comment'].isna()]) / len(result_df) * 100) if len(result_df) > 0 else 0
            }
        
        # Generate appropriate format
        if format_type.lower() == 'html':
            return _generate_html_report(result_df, stats, timestamp)
        elif format_type.lower() == 'markdown':
            return _generate_markdown_report(result_df, stats, timestamp)
        else:  # Default to text
            return _generate_text_report(result_df, stats, timestamp)
            
    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        return f"Error generating report: {str(e)}"

def _generate_html_report(result_df: pd.DataFrame, 
                         stats: Dict[str, Any], 
                         timestamp: str) -> str:
    """
    Generates an HTML formatted report
    
    Args:
        result_df: DataFrame with analysis results
        stats: Dictionary of statistics about the results
        timestamp: Timestamp for the report
        
    Returns:
        HTML formatted report as a string
    """
    # CSS styles for the report
    css = """
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #284b63;
        }
        .header {
            border-bottom: 2px solid #3c6e71;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .timestamp {
            color: #6c757d;
            font-style: italic;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #3c6e71;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .summary {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
        }
        .stat-positive {
            color: #28a745;
            font-weight: bold;
        }
        .stat-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .stat-neutral {
            color: #6c757d;
            font-weight: bold;
        }
        .chart {
            margin: 20px 0;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """
    
    # Create HTML report structure
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dispute Analysis Report</title>
        {css}
    </head>
    <body>
        <div class="header">
            <h1>Dispute Analysis Report</h1>
            <p class="timestamp">Generated on: {timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report analyzes the comparison between Bill Back and PPM data to identify discrepancies and variances.</p>
            
            <h3>Key Statistics</h3>
            <ul>
                <li>Total Records Analyzed: <span class="stat-neutral">{stats['total_records']:,}</span></li>
                <li>Perfect Matches: <span class="stat-positive">{stats['perfect_matches']:,} ({stats['percent_matched']:.1f}%)</span></li>
                <li>Records with Mismatches: <span class="stat-neutral">{stats['mismatches']:,}</span></li>
                <li>Missing Deals: <span class="stat-negative">{stats['missing_deals']:,}</span></li>
                <li>PPM Only Records: <span class="stat-neutral">{stats['ppm_only']:,}</span></li>
                <li>Total Variance: <span class="{_get_variance_class(stats['total_variance'])}">${stats['total_variance']:,.2f}</span></li>
                <li>Absolute Variance (Sum of Absolute Values): <span class="stat-neutral">${stats['absolute_variance']:,.2f}</span></li>
            </ul>
        </div>
        
        <h2>Distribution of Match Types</h2>
        <table>
            <tr>
                <th>Match Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
    """
    
    # Add match type distribution
    match_counts = result_df['Comment'].fillna('Perfect Match').value_counts()
    for match_type, count in match_counts.items():
        percentage = count / stats['total_records'] * 100
        html += f"""
            <tr>
                <td>{match_type}</td>
                <td>{count:,}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Variance by Match Type</h2>
        <table>
            <tr>
                <th>Match Type</th>
                <th>Variance Amount</th>
                <th>Percentage of Total</th>
            </tr>
    """
    
    # Add variance by match type
    var_by_type = result_df.groupby(result_df['Comment'].fillna('Perfect Match'))['VAR'].sum()
    for match_type, variance in var_by_type.items():
        percentage = variance / stats['total_variance'] * 100 if stats['total_variance'] != 0 else 0
        variance_class = _get_variance_class(variance)
        html += f"""
            <tr>
                <td>{match_type}</td>
                <td class="{variance_class}">${variance:,.2f}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h2>Top 10 Materials by Variance</h2>
        <table>
            <tr>
                <th>Material</th>
                <th>Variance Amount</th>
                <th>Match Type</th>
            </tr>
    """
    
    # Add top 10 materials by absolute variance
    top_materials = (result_df.sort_values(by='VAR', key=abs, ascending=False)
                   .head(10))
    for _, row in top_materials.iterrows():
        variance_class = _get_variance_class(row['VAR'])
        comment = row['Comment'] if pd.notna(row['Comment']) else 'Perfect Match'
        html += f"""
            <tr>
                <td>{row['Material']}</td>
                <td class="{variance_class}">${row['VAR']:,.2f}</td>
                <td>{comment}</td>
            </tr>
        """
    
    # Close the HTML structure
    html += """
        </table>
        
        <div class="chart">
            <h2>Analysis Recommendations</h2>
            <p>Based on the analysis results, the following actions are recommended:</p>
            <ol>
    """
    
    # Add recommendations based on the results
    if stats['missing_deals'] > 0:
        html += f"<li>Investigate the {stats['missing_deals']} missing deals to determine why they appear in Bill Back but not in PPM.</li>"
    
    if stats['ppm_only'] > 0:
        html += f"<li>Review the {stats['ppm_only']} PPM-only records to understand why they don't have corresponding Bill Back entries.</li>"
    
    if stats['mismatches'] > 0:
        html += f"<li>Examine the {stats['mismatches']} records with mismatches to identify patterns and potential data entry or process issues.</li>"
    
    if stats['total_variance'] != 0:
        if stats['total_variance'] > 0:
            html += f"<li>Address the ${stats['total_variance']:,.2f} positive variance (Bill Back > PPM) to ensure proper accounting.</li>"
        else:
            html += f"<li>Investigate the ${abs(stats['total_variance']):,.2f} negative variance (PPM > Bill Back) to identify potential missing rebates.</li>"
    
    html += """
            </ol>
        </div>
        
        <div class="footer">
            <p>End of Report</p>
        </div>
    </body>
    </html>
    """
    
    return html

def _generate_markdown_report(result_df: pd.DataFrame, 
                            stats: Dict[str, Any], 
                            timestamp: str) -> str:
    """
    Generates a Markdown formatted report
    
    Args:
        result_df: DataFrame with analysis results
        stats: Dictionary of statistics about the results
        timestamp: Timestamp for the report
        
    Returns:
        Markdown formatted report as a string
    """
    # Create Markdown report structure
    markdown = f"""
# Dispute Analysis Report

*Generated on: {timestamp}*

## Executive Summary

This report analyzes the comparison between Bill Back and PPM data to identify discrepancies and variances.

### Key Statistics

- Total Records Analyzed: **{stats['total_records']:,}**
- Perfect Matches: **{stats['perfect_matches']:,} ({stats['percent_matched']:.1f}%)**
- Records with Mismatches: **{stats['mismatches']:,}**
- Missing Deals: **{stats['missing_deals']:,}**
- PPM Only Records: **{stats['ppm_only']:,}**
- Total Variance: **${stats['total_variance']:,.2f}**
- Absolute Variance (Sum of Absolute Values): **${stats['absolute_variance']:,.2f}**

## Distribution of Match Types

| Match Type | Count | Percentage |
|------------|-------|------------|
"""
    
    # Add match type distribution
    match_counts = result_df['Comment'].fillna('Perfect Match').value_counts()
    for match_type, count in match_counts.items():
        percentage = count / stats['total_records'] * 100
        markdown += f"| {match_type} | {count:,} | {percentage:.1f}% |\n"
    
    markdown += """
## Variance by Match Type

| Match Type | Variance Amount | Percentage of Total |
|------------|----------------|---------------------|
"""
    
    # Add variance by match type
    var_by_type = result_df.groupby(result_df['Comment'].fillna('Perfect Match'))['VAR'].sum()
    for match_type, variance in var_by_type.items():
        percentage = variance / stats['total_variance'] * 100 if stats['total_variance'] != 0 else 0
        markdown += f"| {match_type} | ${variance:,.2f} | {percentage:.1f}% |\n"
    
    markdown += """
## Top 10 Materials by Variance

| Material | Variance Amount | Match Type |
|----------|----------------|------------|
"""
    
    # Add top 10 materials by absolute variance
    top_materials = (result_df.sort_values(by='VAR', key=abs, ascending=False)
                   .head(10))
    for _, row in top_materials.iterrows():
        comment = row['Comment'] if pd.notna(row['Comment']) else 'Perfect Match'
        markdown += f"| {row['Material']} | ${row['VAR']:,.2f} | {comment} |\n"
    
    markdown += """
## Analysis Recommendations

Based on the analysis results, the following actions are recommended:

"""
    
    # Add recommendations based on the results
    if stats['missing_deals'] > 0:
        markdown += f"1. Investigate the {stats['missing_deals']} missing deals to determine why they appear in Bill Back but not in PPM.\n"
    
    if stats['ppm_only'] > 0:
        markdown += f"2. Review the {stats['ppm_only']} PPM-only records to understand why they don't have corresponding Bill Back entries.\n"
    
    if stats['mismatches'] > 0:
        markdown += f"3. Examine the {stats['mismatches']} records with mismatches to identify patterns and potential data entry or process issues.\n"
    
    if stats['total_variance'] != 0:
        if stats['total_variance'] > 0:
            markdown += f"4. Address the ${stats['total_variance']:,.2f} positive variance (Bill Back > PPM) to ensure proper accounting.\n"
        else:
            markdown += f"4. Investigate the ${abs(stats['total_variance']):,.2f} negative variance (PPM > Bill Back) to identify potential missing rebates.\n"
    
    markdown += """
---

*End of Report*
"""
    
    return markdown

def _generate_text_report(result_df: pd.DataFrame, 
                        stats: Dict[str, Any], 
                        timestamp: str) -> str:
    """
    Generates a plain text formatted report
    
    Args:
        result_df: DataFrame with analysis results
        stats: Dictionary of statistics about the results
        timestamp: Timestamp for the report
        
    Returns:
        Plain text formatted report as a string
    """
    # Create text report structure
    text = f"""
===========================================================
                  DISPUTE ANALYSIS REPORT                  
===========================================================

Generated on: {timestamp}

-----------------------------------------------------------
                    EXECUTIVE SUMMARY                      
-----------------------------------------------------------

This report analyzes the comparison between Bill Back and 
PPM data to identify discrepancies and variances.

KEY STATISTICS:
- Total Records Analyzed: {stats['total_records']:,}
- Perfect Matches: {stats['perfect_matches']:,} ({stats['percent_matched']:.1f}%)
- Records with Mismatches: {stats['mismatches']:,}
- Missing Deals: {stats['missing_deals']:,}
- PPM Only Records: {stats['ppm_only']:,}
- Total Variance: ${stats['total_variance']:,.2f}
- Absolute Variance: ${stats['absolute_variance']:,.2f}

-----------------------------------------------------------
                DISTRIBUTION OF MATCH TYPES               
-----------------------------------------------------------
"""
    
    # Add match type distribution
    match_counts = result_df['Comment'].fillna('Perfect Match').value_counts()
    for match_type, count in match_counts.items():
        percentage = count / stats['total_records'] * 100
        text += f"{match_type}: {count:,} ({percentage:.1f}%)\n"
    
    text += """
-----------------------------------------------------------
                 VARIANCE BY MATCH TYPE                   
-----------------------------------------------------------
"""
    
    # Add variance by match type
    var_by_type = result_df.groupby(result_df['Comment'].fillna('Perfect Match'))['VAR'].sum()
    for match_type, variance in var_by_type.items():
        percentage = variance / stats['total_variance'] * 100 if stats['total_variance'] != 0 else 0
        text += f"{match_type}: ${variance:,.2f} ({percentage:.1f}%)\n"
    
    text += """
-----------------------------------------------------------
               TOP 10 MATERIALS BY VARIANCE               
-----------------------------------------------------------
"""
    
    # Add top 10 materials by absolute variance
    top_materials = (result_df.sort_values(by='VAR', key=abs, ascending=False)
                   .head(10))
    
    material_col_width = max(len(str(m)) for m in top_materials['Material']) + 2
    text += f"{'Material'.ljust(material_col_width)} | {'Variance'.rjust(15)} | Match Type\n"
    text += "-" * material_col_width + "-+-" + "-" * 15 + "-+-" + "-" * 20 + "\n"
    
    for _, row in top_materials.iterrows():
        comment = row['Comment'] if pd.notna(row['Comment']) else 'Perfect Match'
        text += f"{str(row['Material']).ljust(material_col_width)} | ${row['VAR']:>13,.2f} | {comment}\n"
    
    text += """
-----------------------------------------------------------
                 ANALYSIS RECOMMENDATIONS                 
-----------------------------------------------------------
"""
    
    # Add recommendations based on the results
    if stats['missing_deals'] > 0:
        text += f"1. Investigate the {stats['missing_deals']} missing deals to determine\n   why they appear in Bill Back but not in PPM.\n\n"
    
    if stats['ppm_only'] > 0:
        text += f"2. Review the {stats['ppm_only']} PPM-only records to understand\n   why they don't have corresponding Bill Back entries.\n\n"
    
    if stats['mismatches'] > 0:
        text += f"3. Examine the {stats['mismatches']} records with mismatches to identify\n   patterns and potential data entry or process issues.\n\n"
    
    if stats['total_variance'] != 0:
        if stats['total_variance'] > 0:
            text += f"4. Address the ${stats['total_variance']:,.2f} positive variance\n   (Bill Back > PPM) to ensure proper accounting.\n\n"
        else:
            text += f"4. Investigate the ${abs(stats['total_variance']):,.2f} negative variance\n   (PPM > Bill Back) to identify potential missing rebates.\n\n"
    
    text += """
===========================================================
                      END OF REPORT                       
===========================================================
"""
    
    return text

def _get_variance_class(variance: float) -> str:
    """
    Determines the CSS class to use for variance values
    
    Args:
        variance: The variance value
        
    Returns:
        CSS class name for styling
    """
    if variance > 0:
        return "stat-positive"
    elif variance < 0:
        return "stat-negative"
    else:
        return "stat-neutral"

def export_results(result_df: pd.DataFrame, 
                  export_format: str = 'excel', 
                  file_path: Optional[str] = None) -> str:
    """
    Exports analysis results to a file
    
    Args:
        result_df: DataFrame with analysis results
        export_format: Format to export ('excel', 'csv', 'json')
        file_path: Path to export file (or None to generate a default path)
        
    Returns:
        Path to the exported file
    """
    if result_df.empty:
        logger.warning("Empty dataframe provided for export")
        return ""
    
    try:
        # Generate default file path if not provided
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format.lower() == 'excel':
                file_path = f"dispute_analysis_results_{timestamp}.xlsx"
            elif export_format.lower() == 'csv':
                file_path = f"dispute_analysis_results_{timestamp}.csv"
            elif export_format.lower() == 'json':
                file_path = f"dispute_analysis_results_{timestamp}.json"
            else:
                file_path = f"dispute_analysis_results_{timestamp}.txt"
        
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Export based on format
        if export_format.lower() == 'excel':
            result_df.to_excel(file_path, index=False)
        elif export_format.lower() == 'csv':
            result_df.to_csv(file_path, index=False)
        elif export_format.lower() == 'json':
            result_df.to_json(file_path, orient='records')
        else:
            # Default to plain text
            with open(file_path, 'w') as f:
                f.write(result_df.to_string())
        
        logger.info(f"Exported results to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")
        return ""
