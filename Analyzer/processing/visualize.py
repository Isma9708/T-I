"""
Visualization Module - Creates data visualizations for analysis results

This module provides functions for generating charts, graphs, and visual
representations of analysis results to aid in interpretation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import logging
import os
from typing import Dict, List, Union, Optional, Any
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly

# Configure logging
logger = logging.getLogger(__name__)

# Set seaborn styling for better aesthetics
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']

# Define color palette for consistent visualizations
COLORS = {
    'primary': '#3c6e71',
    'secondary': '#284b63',
    'accent': '#ff7f50',
    'positive': '#28a745',
    'negative': '#dc3545',
    'neutral': '#6c757d',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

def create_variance_summary(result_df: pd.DataFrame) -> plt.Figure:
    """
    Creates a summary visualization of variance analysis
    
    Args:
        result_df: DataFrame with analysis results
        
    Returns:
        Matplotlib figure containing the visualization
    """
    if result_df.empty or 'Comment' not in result_df.columns:
        logger.warning("Empty dataframe or missing Comment column")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
        return fig
    
    try:
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
        fig.suptitle('Variance Analysis Summary', fontsize=16, fontweight='bold')
        
        # First subplot: Distribution of match types
        match_counts = result_df['Comment'].fillna('Perfect Match').value_counts()
        match_counts = match_counts.reindex(['Perfect Match', 'At price mismatch', 'Case in Part mismatch', 
                                           'Part Amount mismatch', 'Missing Deal', 'PPM Only'])
        match_counts = match_counts.dropna()
        
        # Colors for each category
        colors = [
            COLORS['positive'],  # Perfect Match
            COLORS['neutral'],   # At price mismatch
            COLORS['neutral'],   # Case in Part mismatch
            COLORS['neutral'],   # Part Amount mismatch
            COLORS['negative'],  # Missing Deal
            COLORS['accent']     # PPM Only
        ]
        
        # Use only colors for categories that exist in the data
        colors = colors[:len(match_counts)]
        
        ax1.bar(match_counts.index, match_counts.values, color=colors)
        ax1.set_title('Distribution of Match Types', fontsize=14)
        ax1.set_xlabel('Match Type')
        ax1.set_ylabel('Count')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add count labels on top of bars
        for i, v in enumerate(match_counts.values):
            ax1.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
        
        # Second subplot: Variance waterfall chart
        var_by_type = result_df.groupby(result_df['Comment'].fillna('Perfect Match'))['VAR'].sum().reindex(
            ['Perfect Match', 'At price mismatch', 'Case in Part mismatch', 
             'Part Amount mismatch', 'Missing Deal', 'PPM Only']
        ).dropna()
        
        # Create waterfall chart
        bottom = 0
        for i, (category, value) in enumerate(var_by_type.items()):
            color = COLORS['positive'] if value >= 0 else COLORS['negative']
            ax2.bar(i, value, bottom=bottom if value < 0 else bottom, color=color, label=category)
            
            # Add value labels
            text_color = 'black'
            label_pos = bottom + value / 2 if value >= 0 else bottom + value / 2
            ax2.text(i, label_pos, f"${value:,.2f}", ha='center', va='center', 
                    color=text_color, fontweight='bold')
            
            bottom += value
        
        # Add total bar
        total = var_by_type.sum()
        ax2.bar(len(var_by_type), total, color=COLORS['secondary'], label='Total')
        ax2.text(len(var_by_type), total/2, f"${total:,.2f}", ha='center', va='center', 
                color='white', fontweight='bold')
        
        ax2.set_title('Variance by Match Type ($)', fontsize=14)
        ax2.set_ylabel('Variance Amount ($)')
        ax2.set_xticks(range(len(var_by_type) + 1))
        ax2.set_xticklabels(list(var_by_type.index) + ['Total'], rotation=45)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Format y-axis as currency
        ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
        
        fig.tight_layout()
        fig.subplots_adjust(top=0.9)
        
        logger.info("Created variance summary visualization")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating variance summary: {str(e)}")
        # Return a simple error figure
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error creating visualization: {str(e)}", ha='center', va='center')
        return fig

def create_web_visualizations(result_df: pd.DataFrame, viz_type: str = 'all') -> Dict[str, Any]:
    """
    Creates interactive web visualizations using Plotly
    
    Args:
        result_df: DataFrame with analysis results
        viz_type: Type of visualization to create ('all' or specific type)
        
    Returns:
        Dictionary of JSON-serialized Plotly figures
    """
    if result_df.empty:
        logger.warning("Empty dataframe provided for visualizations")
        return {}
    
    visualizations = {}
    
    try:
        # Create different visualizations based on viz_type
        if viz_type in ['all', 'match_distribution']:
            # Match type distribution
            match_counts = result_df['Comment'].fillna('Perfect Match').value_counts().reset_index()
            match_counts.columns = ['Match Type', 'Count']
            
            # Define color mapping
            color_map = {
                'Perfect Match': COLORS['positive'],
                'At price mismatch': COLORS['neutral'],
                'Case in Part mismatch': COLORS['neutral'],
                'Part Amount mismatch': COLORS['neutral'],
                'Missing Deal': COLORS['negative'],
                'PPM Only': COLORS['accent']
            }
            
            # Create colors list in the right order
            colors = [color_map.get(match_type, COLORS['neutral']) 
                     for match_type in match_counts['Match Type']]
            
            # Create bar chart
            fig = go.Figure(go.Bar(
                x=match_counts['Match Type'],
                y=match_counts['Count'],
                text=match_counts['Count'],
                textposition='auto',
                marker_color=colors
            ))
            
            fig.update_layout(
                title='Distribution of Match Types',
                xaxis_title='Match Type',
                yaxis_title='Count',
                template='plotly_white'
            )
            
            visualizations['match_distribution'] = json.loads(plotly.io.to_json(fig))
        
        if viz_type in ['all', 'variance_by_type']:
            # Variance by match type
            var_by_type = result_df.groupby(
                result_df['Comment'].fillna('Perfect Match')
            )['VAR'].sum().reset_index()
            var_by_type.columns = ['Match Type', 'Variance']
            
            # Create colors based on variance values
            colors = ['#28a745' if var >= 0 else '#dc3545' 
                     for var in var_by_type['Variance']]
            
            # Create waterfall-like bar chart
            fig = go.Figure()
            
            # Add individual bars
            for i, row in var_by_type.iterrows():
                fig.add_trace(go.Bar(
                    x=[row['Match Type']],
                    y=[row['Variance']],
                    marker_color=colors[i],
                    name=row['Match Type']
                ))
            
            # Add total bar
            total_variance = var_by_type['Variance'].sum()
            total_color = '#28a745' if total_variance >= 0 else '#dc3545'
            
            fig.add_trace(go.Bar(
                x=['Total'],
                y=[total_variance],
                marker_color=COLORS['secondary'],
                name='Total'
            ))
            
            fig.update_layout(
                title='Variance by Match Type',
                xaxis_title='Match Type',
                yaxis_title='Variance Amount ($)',
                yaxis_tickformat='$,.0f',
                template='plotly_white'
            )
            
            visualizations['variance_by_type'] = json.loads(plotly.io.to_json(fig))
            
        if viz_type in ['all', 'billback_vs_ppm']:
            # Billback vs PPM scatter plot
            if all(col in result_df.columns for col in ['Extended Part', 'Rebate']):
                # Filter out missing values
                plot_df = result_df.dropna(subset=['Extended Part', 'Rebate'])
                
                if not plot_df.empty:
                    # Create color mapping for comments
                    plot_df['Comment_Clean'] = plot_df['Comment'].fillna('Perfect Match')
                    
                    # Simplify comment categories
                    plot_df['Comment_Category'] = plot_df['Comment_Clean'].apply(
                        lambda x: 'Perfect Match' if x == 'Perfect Match' else
                                ('Mismatch' if 'mismatch' in x else
                                 ('Missing Deal' if x == 'Missing Deal' else
                                  ('PPM Only' if x == 'PPM Only' else 'Other')))
                    )
                    
                    # Create color mapping
                    color_discrete_map = {
                        'Perfect Match': COLORS['positive'],
                        'Mismatch': COLORS['neutral'],
                        'Missing Deal': COLORS['negative'],
                        'PPM Only': COLORS['accent'],
                        'Other': COLORS['dark']
                    }
                    
                    # Create scatter plot
                    fig = px.scatter(
                        plot_df,
                        x='Extended Part',
                        y='Rebate',
                        color='Comment_Category',
                        hover_data=['Material', 'VAR', 'Comment_Clean'],
                        labels={
                            'Extended Part': 'Bill Back Extended Part ($)',
                            'Rebate': 'PPM Rebate ($)',
                            'Comment_Category': 'Match Type'
                        },
                        color_discrete_map=color_discrete_map
                    )
                    
                    # Add 45-degree line (perfect match line)
                    min_val = min(plot_df['Extended Part'].min(), plot_df['Rebate'].min())
                    max_val = max(plot_df['Extended Part'].max(), plot_df['Rebate'].max())
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[min_val, max_val],
                            y=[min_val, max_val],
                            mode='lines',
                            line=dict(dash='dash', color='black', width=1),
                            name='Perfect Match Line'
                        )
                    )
                    
                    fig.update_layout(
                        title='Bill Back vs PPM Rebate Comparison',
                        xaxis_title='Bill Back Extended Part ($)',
                        yaxis_title='PPM Rebate ($)',
                        xaxis_tickformat='$,.0f',
                        yaxis_tickformat='$,.0f',
                        template='plotly_white'
                    )
                    
                    visualizations['billback_vs_ppm'] = json.loads(plotly.io.to_json(fig))
                    
        if viz_type in ['all', 'top_materials']:
            # Top materials by absolute variance
            if 'Material' in result_df.columns and 'VAR' in result_df.columns:
                top_materials = (result_df.groupby('Material')['VAR']
                               .sum()
                               .sort_values(key=abs, ascending=False)
                               .head(10)
                               .reset_index())
                
                if not top_materials.empty:
                    # Create colors based on variance values
                    colors = ['#28a745' if var >= 0 else '#dc3545' 
                             for var in top_materials['VAR']]
                    
                    # Create horizontal bar chart
                    fig = go.Figure(go.Bar(
                        y=top_materials['Material'],
                        x=top_materials['VAR'],
                        orientation='h',
                        marker_color=colors,
                        text=[f"${var:,.2f}" for var in top_materials['VAR']],
                        textposition='auto'
                    ))
                    
                    fig.update_layout(
                        title='Top 10 Materials by Variance Impact',
                        xaxis_title='Variance Amount ($)',
                        yaxis_title='Material ID',
                        xaxis_tickformat='$,.0f',
                        template='plotly_white'
                    )
                    
                    visualizations['top_materials'] = json.loads(plotly.io.to_json(fig))
                    
        if viz_type in ['all', 'variance_distribution']:
            # Variance distribution histogram
            if 'VAR' in result_df.columns:
                fig = px.histogram(
                    result_df,
                    x='VAR',
                    nbins=20,
                    labels={'VAR': 'Variance Amount ($)'},
                    color_discrete_sequence=[COLORS['primary']]
                )
                
                # Add KDE-like line
                fig.add_trace(
                    go.Scatter(
                        x=result_df['VAR'].sort_values(),
                        y=np.linspace(0, fig.data[0].y.max(), len(result_df)),
                        mode='lines',
                        line=dict(color=COLORS['accent'], width=2),
                        name='Distribution'
                    )
                )
                
                # Calculate summary statistics
                mean_var = result_df['VAR'].mean()
                median_var = result_df['VAR'].median()
                min_var = result_df['VAR'].min()
                max_var = result_df['VAR'].max()
                
                # Add statistics annotation
                stats_text = (
                    f"Mean: ${mean_var:,.2f}<br>"
                    f"Median: ${median_var:,.2f}<br>"
                    f"Min: ${min_var:,.2f}<br>"
                    f"Max: ${max_var:,.2f}"
                )
                
                fig.add_annotation(
                    x=0.05,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=stats_text,
                    showarrow=False,
                    bgcolor="white",
                    opacity=0.8,
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=5
                )
                
                fig.update_layout(
                    title='Distribution of Variance Values',
                    xaxis_title='Variance Amount ($)',
                    yaxis_title='Frequency',
                    xaxis_tickformat='$,.0f',
                    template='plotly_white',
                    bargap=0.1
                )
                
                visualizations['variance_distribution'] = json.loads(plotly.io.to_json(fig))
        
        return visualizations
        
    except Exception as e:
        logger.error(f"Error creating web visualizations: {str(e)}")
        return {'error': str(e)}

def create_detail_plots(result_df: pd.DataFrame) -> Dict[str, plt.Figure]:
    """
    Creates detailed visualizations for deeper analysis
    
    Args:
        result_df: DataFrame with analysis results
        
    Returns:
        Dictionary of matplotlib figures with detailed visualizations
    """
    if result_df.empty:
        logger.warning("Empty dataframe provided for detail plots")
        return {}
    
    figures = {}
    
    try:
        # Figure 1: Variance distribution histogram
        if 'VAR' in result_df.columns:
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            # Create histogram with KDE
            sns.histplot(result_df['VAR'].dropna(), kde=True, ax=ax1, color=COLORS['primary'])
            
            ax1.set_title('Distribution of Variance Values', fontsize=14)
            ax1.set_xlabel('Variance Amount ($)')
            ax1.set_ylabel('Frequency')
            
            # Format x-axis as currency
            ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
            
            # Add summary statistics
            stats_text = (
                f"Mean: ${result_df['VAR'].mean():,.2f}\n"
                f"Median: ${result_df['VAR'].median():,.2f}\n"
                f"Min: ${result_df['VAR'].min():,.2f}\n"
                f"Max: ${result_df['VAR'].max():,.2f}"
            )
            
            # Add text box with stats
            props = dict(boxstyle='round', facecolor='white', alpha=0.8)
            ax1.text(0.05, 0.95, stats_text, transform=ax1.transAxes, fontsize=12,
                    verticalalignment='top', bbox=props)
            
            figures['variance_distribution'] = fig1
            logger.info("Created variance distribution visualization")
        
        # Figure 2: Billback vs PPM comparison scatter plot
        if all(col in result_df.columns for col in ['Extended Part', 'Rebate']):
            fig2, ax2 = plt.subplots(figsize=(10, 8))
            
            # Remove rows where either value is missing
            plot_df = result_df.dropna(subset=['Extended Part', 'Rebate'])
            
            # Add a 45-degree line (perfect match line)
            min_val = min(plot_df['Extended Part'].min(), plot_df['Rebate'].min())
            max_val = max(plot_df['Extended Part'].max(), plot_df['Rebate'].max())
            ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect Match Line')
            
            # Create color mapping based on Comment
            comment_map = {
                np.nan: COLORS['positive'],  # Perfect match
                'Perfect Match': COLORS['positive'],
                'At price mismatch': COLORS['neutral'],
                'Case in Part mismatch': COLORS['neutral'],
                'Part Amount mismatch': COLORS['neutral'],
                'Missing Deal': COLORS['negative'],
                'PPM Only': COLORS['accent']
            }
            
            # Map comments to colors
            colors = plot_df['Comment'].fillna('Perfect Match').map(comment_map)
            
            # Create scatter plot
            scatter = ax2.scatter(plot_df['Extended Part'], plot_df['Rebate'], 
                                 alpha=0.7, c=colors, s=50, edgecolor='w')
            
            ax2.set_title('Bill Back vs PPM Rebate Comparison', fontsize=14)
            ax2.set_xlabel('Bill Back Extended Part ($)')
            ax2.set_ylabel('PPM Rebate ($)')
            
            # Format axes as currency
            ax2.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
            ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
            
            # Add equal scaling and grid
            ax2.set_aspect('equal')
            ax2.grid(True, alpha=0.3)
            
            # Create legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['positive'], 
                      label='Perfect Match', markersize=10),
                Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['neutral'], 
                      label='Mismatch', markersize=10),
                Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['negative'], 
                      label='Missing Deal', markersize=10),
                Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['accent'], 
                      label='PPM Only', markersize=10)
            ]
            ax2.legend(handles=legend_elements, loc='upper left')
            
            figures['billback_vs_ppm'] = fig2
            logger.info("Created Bill Back vs PPM comparison visualization")
        
        # Figure 3: Top materials with variance issues
        if all(col in result_df.columns for col in ['Material', 'VAR']):
            # Get top 10 materials by absolute variance
            top_materials = (result_df.groupby('Material')['VAR']
                           .sum()
                           .abs()
                           .sort_values(ascending=False)
                           .head(10))
            
            if not top_materials.empty:
                fig3, ax3 = plt.subplots(figsize=(12, 8))
                
                # Create horizontal bar chart
                bars = ax3.barh(top_materials.index, top_materials, 
                              color=[COLORS['positive'] if x >= 0 else COLORS['negative'] 
                                    for x in top_materials])
                
                ax3.set_title('Top 10 Materials by Variance Impact', fontsize=14)
                ax3.set_xlabel('Total Variance Amount ($)')
                ax3.set_ylabel('Material ID')
                
                # Format x-axis as currency
                ax3.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
                
                # Add value labels to bars
                for bar in bars:
                    width = bar.get_width()
                    label_x = width if width >= 0 else width - 1000
                    ax3.text(label_x, bar.get_y() + bar.get_height()/2, 
                           f'${width:,.2f}',
                           va='center', fontsize=10,
                           color='white' if abs(width) > 5000 else 'black')
                
                figures['top_materials'] = fig3
                logger.info("Created top materials visualization")
        
        return figures
        
    except Exception as e:
        logger.error(f"Error creating detailed visualizations: {str(e)}")
        return figures

def create_comparison_chart(billback_df: pd.DataFrame, 
                          ppm_df: pd.DataFrame, 
                          time_period: str = 'M') -> plt.Figure:
    """
    Creates a time-series comparison of bill back and PPM data
    
    Args:
        billback_df: DataFrame with bill back data
        ppm_df: DataFrame with PPM data
        time_period: Time period for grouping ('D'=daily, 'W'=weekly, 'M'=monthly)
        
    Returns:
        Matplotlib figure with time series comparison
    """
    try:
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        date_formats = {'D': '%Y-%m-%d', 'W': '%Y-%W', 'M': '%Y-%m'}
        date_format = date_formats.get(time_period, '%Y-%m')
        
        if 'Complete Date' in billback_df.columns and 'Extended Part' in billback_df.columns:
            # Group bill back data by time period
            billback_grouped = (billback_df.groupby(pd.Grouper(key='Complete Date', freq=time_period))
                              ['Extended Part'].sum().reset_index())
            
            # Plot bill back data
            ax.plot(billback_grouped['Complete Date'], billback_grouped['Extended Part'], 
                   marker='o', linewidth=2, color=COLORS['primary'], label='Bill Back')
        
        if 'Start' in ppm_df.columns and 'Rebate' in ppm_df.columns:
            # Group PPM data by time period
            ppm_grouped = (ppm_df.groupby(pd.Grouper(key='Start', freq=time_period))
                         ['Rebate'].sum().reset_index())
            
            # Plot PPM data
            ax.plot(ppm_grouped['Start'], ppm_grouped['Rebate'], 
                   marker='s', linewidth=2, color=COLORS['accent'], label='PPM')
        
        # Set title and labels
        ax.set_title('Bill Back vs PPM Over Time', fontsize=16)
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Amount ($)')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
        
        # Add legend and grid
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        logger.info("Created time series comparison visualization")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating time series visualization: {str(e)}")
        # Return a simple error figure
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error creating time series visualization: {str(e)}", 
               ha='center', va='center')
        return fig

def save_visualizations(figures: Dict[str, plt.Figure], save_dir: str) -> List[str]:
    """
    Saves generated visualizations to files
    
    Args:
        figures: Dictionary of matplotlib figures
        save_dir: Directory to save files
        
    Returns:
        List of saved file paths
    """
    if not figures:
        logger.warning("No figures provided to save")
        return []
    
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            logger.info(f"Created directory: {save_dir}")
        except Exception as e:
            logger.error(f"Could not create directory {save_dir}: {str(e)}")
            return []
    
    saved_paths = []
    
    for name, fig in figures.items():
        try:
            # Create filename with timestamp
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            
            # Save figure
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
            saved_paths.append(filepath)
            
            logger.info(f"Saved visualization to {filepath}")
        except Exception as e:
            logger.error(f"Error saving visualization {name}: {str(e)}")
    
    return saved_paths
