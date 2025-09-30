"""
Reporting Module - Generates detailed reports from analysis results

This module provides functions to create summary reports, detailed reports,
and export results in various formats.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
import os
import json
import datetime

# Configure logging
logger = logging.getLogger(__name__)

def generate_summary_report(analysis_results: pd.DataFrame, 
                          stats: Dict[str, Any],
                          output_format: str = 'html') -> str:
    """
    Generate a summary report from analysis results
    
    Args:
        analysis_results: DataFrame with analysis results
        stats: Dictionary with summary statistics
        output_format: Format for output report ('html', 'markdown', 'text')
        
    Returns:
        Report content as string in the specified format
    """
    logger.info(f"Generating summary report in {output_format} format")
    
    if analysis_results.empty:
        return "No data available for reporting"
    
    try:
        # Create report content based on format
        if output_format == 'html':
            return _generate_html_summary(analysis_results, stats)
        elif output_format == 'markdown':
            return _generate_markdown_summary(analysis_results, stats)
        else:  # Default to text
            return _generate_text_summary(analysis_results, stats)
            
    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        return f"Error generating report: {str(e)}"

def _generate_html_summary(analysis_results: pd.DataFrame, stats: Dict[str, Any]) -> str:
    """Generate HTML format summary report"""
    
    # Create summary table
    summary_table = f"""
    <table class="summary-table">
        <tr>
            <th colspan="2">Analysis Summary</th>
        </tr>
        <tr>
            <td>Total Records</td>
            <td>{stats.get('total_records', 0)}</td>
        </tr>
        <tr>
            <td>Perfect Matches</td>
            <td>{stats.get('perfect_matches', 0)} ({stats.get('percent_matched', 0):.1f}%)</td>
        </tr>
        <tr>
            <td>Mismatches</td>
            <td>{stats.get('mismatches', 0)}</td>
        </tr>
        <tr>
            <td>Missing Deals</td>
            <td>{stats.get('missing_deals', 0)}</td>
        </tr>
        <tr>
            <td>PPM Only</td>
            <td>{stats.get('ppm_only', 0)}</td>
        </tr>
        <tr>
            <td>Total Variance</td>
            <td>${stats.get('total_variance', 0):.2f}</td>
        </tr>
        <tr>
            <td>Absolute Variance</td>
            <td>${stats.get('absolute_variance', 0):.2f}</td>
        </tr>
    </table>
    """
    
    # Create category breakdown
    categories = analysis_results['Comment'].fillna('Perfect Match')
    category_counts = categories.value_counts()
    category_html = "<h3>Category Breakdown</h3><ul>"
    for cat, count in category_counts.items():
        category_html += f"<li>{cat}: {count}</li>"
    category_html += "</ul>"
    
    # Create top mismatches
    if 'Category' not in analysis_results.columns:
        analysis_results['Category'] = 'Perfect Match'
        analysis_results.loc[analysis_results['Comment'].str.contains('mismatch', na=False), 'Category'] = 'Mismatch'
        analysis_results.loc[analysis_results['Comment'] == 'Missing Deal', 'Category'] = 'Missing Deal'
        analysis_results.loc[analysis_results['Comment'] == 'PPM Only', 'Category'] = 'PPM Only'
    
    mismatches = analysis_results[analysis_results['Category'] == 'Mismatch']
    top_mismatches_html = ""
    if not mismatches.empty:
        top_mismatches = mismatches.sort_values('VAR', key=abs, ascending=False).head(10)
        top_mismatches_html = "<h3>Top 10 Mismatches by Variance</h3>"
        top_mismatches_html += top_mismatches[['Material', 'VAR', 'Comment']].to_html(index=False)
    
    # Combine all sections
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Material Analysis Summary Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333366; }}
            .summary-table {{ border-collapse: collapse; width: 50%; margin-bottom: 20px; }}
            .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 8px; }}
            .summary-table th {{ background-color: #f2f2f2; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            table th, table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            table th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Material Analysis Summary Report</h1>
        <p>Generated on: {timestamp}</p>
        
        <h2>Summary</h2>
        {summary_table}
        
        {category_html}
        
        {top_mismatches_html}
        
        <h3>About This Report</h3>
        <p>This report summarizes the analysis of material variances between Bill back and PPM data.</p>
    </body>
    </html>
    """
    
    return html

def _generate_markdown_summary(analysis_results: pd.DataFrame, stats: Dict[str, Any]) -> str:
    """Generate Markdown format summary report"""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""
# Material Analysis Summary Report

Generated on: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Total Records | {stats.get('total_records', 0)} |
| Perfect Matches | {stats.get('perfect_matches', 0)} ({stats.get('percent_matched', 0):.1f}%) |
| Mismatches | {stats.get('mismatches', 0)} |
| Missing Deals | {stats.get('missing_deals', 0)} |
| PPM Only | {stats.get('ppm_only', 0)} |
| Total Variance | ${stats.get('total_variance', 0):.2f} |
| Absolute Variance | ${stats.get('absolute_variance', 0):.2f} |

## Category Breakdown

"""
    
    categories = analysis_results['Comment'].fillna('Perfect Match')
    category_counts = categories.value_counts()
    for cat, count in category_counts.items():
        markdown += f"- {cat}: {count}\n"
    
    # Create top mismatches
    if 'Category' not in analysis_results.columns:
        analysis_results['Category'] = 'Perfect Match'
        analysis_results.loc[analysis_results['Comment'].str.contains('mismatch', na=False), 'Category'] = 'Mismatch'
        analysis_results.loc[analysis_results['Comment'] == 'Missing Deal', 'Category'] = 'Missing Deal'
        analysis_results.loc[analysis_results['Comment'] == 'PPM Only', 'Category'] = 'PPM Only'
    
    mismatches = analysis_results[analysis_results['Category'] == 'Mismatch']
    if not mismatches.empty:
        markdown += "\n## Top 10 Mismatches by Variance\n\n"
        top_mismatches = mismatches.sort_values('VAR', key=abs, ascending=False).head(10)
        
        # Create markdown table header
        markdown += "| Material | VAR | Comment |\n"
        markdown += "|----------|-----|--------|\n"
        
        # Add rows
        for _, row in top_mismatches.iterrows():
            markdown += f"| {row['Material']} | ${row['VAR']:.2f} | {row['Comment']} |\n"
    
    markdown += """
## About This Report

This report summarizes the analysis of material variances between Bill back and PPM data.
"""
    
    return markdown

def _generate_text_summary(analysis_results: pd.DataFrame, stats: Dict[str, Any]) -> str:
    """Generate plain text format summary report"""
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    text = f"""
MATERIAL ANALYSIS SUMMARY REPORT
===============================
Generated on: {timestamp}

SUMMARY
-------
Total Records: {stats.get('total_records', 0)}
Perfect Matches: {stats.get('perfect_matches', 0)} ({stats.get('percent_matched', 0):.1f}%)
Mismatches: {stats.get('mismatches', 0)}
Missing Deals: {stats.get('missing_deals', 0)}
PPM Only: {stats.get('ppm_only', 0)}
Total Variance: ${stats.get('total_variance', 0):.2f}
Absolute Variance: ${stats.get('absolute_variance', 0):.2f}

CATEGORY BREAKDOWN
-----------------
"""
    
    categories = analysis_results['Comment'].fillna('Perfect Match')
    category_counts = categories.value_counts()
    for cat, count in category_counts.items():
        text += f"{cat}: {count}\n"
    
    # Create top mismatches
    if 'Category' not in analysis_results.columns:
        analysis_results['Category'] = 'Perfect Match'
        analysis_results.loc[analysis_results['Comment'].str.contains('mismatch', na=False), 'Category'] = 'Mismatch'
        analysis_results.loc[analysis_results['Comment'] == 'Missing Deal', 'Category'] = 'Missing Deal'
        analysis_results.loc[analysis_results['Comment'] == 'PPM Only', 'Category'] = 'PPM Only'
    
    mismatches = analysis_results[analysis_results['Category'] == 'Mismatch']
    if not mismatches.empty:
        text += "\nTOP 10 MISMATCHES BY VARIANCE\n"
        text += "----------------------------\n"
        top_mismatches = mismatches.sort_values('VAR', key=abs, ascending=False).head(10)
        
        # Format as fixed-width columns
        text += f"{'Material':<15} {'VAR':>10} {'Comment':<50}\n"
        text += f"{'-'*15} {'-'*10} {'-'*50}\n"
        
        # Add rows
        for _, row in top_mismatches.iterrows():
            text += f"{str(row['Material']):<15} {row['VAR']:>10.2f} {str(row['Comment']):<50}\n"
    
    text += """
ABOUT THIS REPORT
---------------
This report summarizes the analysis of material variances between Bill back and PPM data.
"""
    
    return text

def export_results(analysis_results: pd.DataFrame, 
                 export_format: str = 'excel',
                 file_path: Optional[str] = None) -> str:
    """
    Export analysis results to a file
    
    Args:
        analysis_results: DataFrame with analysis results
        export_format: Format for export ('excel', 'csv', 'json')
        file_path: Path to save the file (optional)
        
    Returns:
        Path to the exported file
    """
    if analysis_results.empty:
        logger.warning("No data available for export")
        return ""
        
    try:
        # Generate default file name if none provided
        if not file_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"./reports/analysis_results_{timestamp}"
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
        # Export based on format
        if export_format == 'excel':
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            analysis_results.to_excel(file_path, index=False)
            
        elif export_format == 'csv':
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            analysis_results.to_csv(file_path, index=False)
            
        elif export_format == 'json':
            if not file_path.endswith('.json'):
                file_path += '.json'
            # Convert to dict, handle NaN values
            result_dict = analysis_results.fillna("null").to_dict(orient='records')
            with open(file_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
        
        logger.info(f"Successfully exported results to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")
        return ""