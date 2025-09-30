"""
Visualization Module - Creates visual representations of analysis results

This module provides functions to visualize analysis results using matplotlib and seaborn.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logger = logging.getLogger(__name__)

def create_variance_summary(analysis_results: pd.DataFrame, title: str = "Variance Summary") -> plt.Figure:
    """
    Create a summary visualization of variances
    
    Args:
        analysis_results: DataFrame with analysis results
        title: Title for the plot
        
    Returns:
        Matplotlib figure with variance summary
    """
    logger.info("Creating variance summary visualization")
    
    if analysis_results.empty:
        logger.warning("Cannot create visualization from empty dataframe")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
        return fig
    
    try:
        # Create a copy to avoid modifying the original
        df = analysis_results.copy()
        
        # Add a category column based on the Comment
        df['Category'] = 'Perfect Match'
        df.loc[df['Comment'].str.contains('mismatch', na=False), 'Category'] = 'Mismatch'
        df.loc[df['Comment'] == 'Missing Deal', 'Category'] = 'Missing Deal'
        df.loc[df['Comment'] == 'PPM Only', 'Category'] = 'PPM Only'
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Plot 1: Category counts
        category_counts = df['Category'].value_counts()
        category_colors = {
            'Perfect Match': 'green',
            'Mismatch': 'orange',
            'Missing Deal': 'red',
            'PPM Only': 'purple'
        }
        colors = [category_colors.get(cat, 'gray') for cat in category_counts.index]
        
        category_counts.plot(kind='bar', ax=ax1, color=colors)
        ax1.set_title('Distribution of Match Categories')
        ax1.set_ylabel('Count')
        ax1.set_xlabel('Category')
        
        # Plot 2: Variance by category
        var_by_cat = df.groupby('Category')['VAR'].sum()
        var_by_cat.plot(kind='bar', ax=ax2, color=colors)
        ax2.set_title('Total Variance by Category')
        ax2.set_ylabel('Total Variance ($)')
        ax2.set_xlabel('Category')
        
        # Annotate bars with values
        for i, v in enumerate(var_by_cat):
            ax2.text(i, v + (0.1 if v >= 0 else -0.1), f'${v:.2f}', 
                    ha='center', va='bottom' if v >= 0 else 'top')
        
        # Add overall title and adjust layout
        plt.suptitle(title, fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        logger.info("Visualization created successfully")
        return fig
    
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error creating visualization: {str(e)}", ha='center', va='center')
        return fig

def create_detail_plots(analysis_results: pd.DataFrame, 
                       material_id: Optional[str] = None) -> Dict[str, plt.Figure]:
    """
    Create detailed plots for specific analysis results
    
    Args:
        analysis_results: DataFrame with analysis results
        material_id: Optional material ID to filter results
        
    Returns:
        Dictionary of matplotlib figures with various visualizations
    """
    logger.info(f"Creating detail plots{' for material '+material_id if material_id else ''}")
    
    figures = {}
    
    try:
        # Filter by material if specified
        df = analysis_results.copy()
        if material_id:
            df = df[df['Material'] == material_id]
        
        if df.empty:
            logger.warning("No data available for detail plots")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14)
            figures['no_data'] = fig
            return figures
        
        # Plot 1: Variance distribution
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        sns.histplot(df['VAR'].dropna(), kde=True, ax=ax1)
        ax1.set_title('Variance Distribution')
        ax1.set_xlabel('Variance Value ($)')
        ax1.set_ylabel('Frequency')
        figures['variance_dist'] = fig1
        
        # Plot 2: Top 10 materials by absolute variance
        top_materials = df.groupby('Material')['VAR'].sum().abs().sort_values(ascending=False).head(10)
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        top_materials.plot(kind='bar', ax=ax2)
        ax2.set_title('Top 10 Materials by Absolute Variance')
        ax2.set_xlabel('Material')
        ax2.set_ylabel('Total Absolute Variance ($)')
        plt.xticks(rotation=45, ha='right')
        figures['top_materials'] = fig2
        
        # Plot 3: Correlation between fields (if available)
        numeric_cols = ['At price', 'Case in Part', 'Part Amount', 'Extended Part', 
                      'Net$', 'Quantity', 'Unit Rebate$', 'Rebate', 'VAR']
        numeric_df = df[numeric_cols].dropna(thresh=4)  # Require at least 4 non-NA values
        
        if len(numeric_df) > 5:  # Only create correlation if we have enough data
            fig3, ax3 = plt.subplots(figsize=(12, 10))
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax3, fmt='.2f')
            ax3.set_title('Correlation Between Numeric Fields')
            figures['correlations'] = fig3
        
        logger.info("Detail plots created successfully")
        return figures
    
    except Exception as e:
        logger.error(f"Error creating detail plots: {str(e)}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error creating detail plots: {str(e)}", ha='center', va='center')
        figures['error'] = fig
        return figures

def save_visualizations(figures: Dict[str, plt.Figure], 
                       base_path: str = "./reports") -> Dict[str, str]:
    """
    Save visualization figures to files
    
    Args:
        figures: Dictionary of matplotlib figures
        base_path: Base path to save figures
        
    Returns:
        Dictionary mapping figure keys to file paths
    """
    import os
    
    # Create directory if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    
    saved_paths = {}
    
    for key, fig in figures.items():
        try:
            file_path = os.path.join(base_path, f"{key}.png")
            fig.savefig(file_path, bbox_inches='tight', dpi=150)
            saved_paths[key] = file_path
            logger.info(f"Saved visualization to {file_path}")
        except Exception as e:
            logger.error(f"Error saving {key} visualization: {str(e)}")
    
    return saved_paths