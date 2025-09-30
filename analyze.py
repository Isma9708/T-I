"""
Material Analysis Module - Provides advanced comparison algorithms for rebate analysis

This module handles the core business logic for comparing materials and rebates
between different data sources, identifying discrepancies, and calculating variances.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Union, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

def analyze_materials(tabla1: pd.DataFrame, 
                     tabla2: pd.DataFrame, 
                     brandpk: str, 
                     close_threshold: float = 10) -> pd.DataFrame:
    """
    Analyzes materials between two tables and identifies matches, mismatches, and variances
    
    Args:
        tabla1: First dataframe (Bill back table)
        tabla2: Second dataframe (PPM table)
        brandpk: Brand + Pack size identifier to filter records
        close_threshold: Threshold for considering values as "close" matches (default: 10)
        
    Returns:
        DataFrame containing analysis results with matches, variances, and comments
    """
    logger.info(f"Analyzing materials for brand+pk: {brandpk}")
    
    # Filter tables by brand+pk
    try:
        t1 = tabla1[tabla1['Brand + Pk size'] == brandpk].copy()
        t2 = tabla2[tabla2['ppm_Brand+pk size'] == brandpk].copy()
        
        logger.info(f"Found {len(t1)} records in Bill back and {len(t2)} records in PPM")
    except KeyError as e:
        logger.error(f"Column not found in dataframes: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error
    
    all_results = []
    material_ids = t1['Material'].unique()
    
    # Process each material ID
    for material_id in material_ids:
        logger.debug(f"Processing material ID: {material_id}")
        material_results = _process_single_material(t1, t2, material_id, close_threshold)
        all_results.extend(material_results)
    
    result = pd.DataFrame(all_results)
    logger.info(f"Analysis complete. Found {len(result)} total matches/mismatches")
    return result

def _process_single_material(t1: pd.DataFrame, 
                           t2: pd.DataFrame, 
                           material_id: str, 
                           close_threshold: float) -> List[Dict[str, Any]]:
    """
    Process a single material ID, finding matches between tables
    
    Args:
        t1: Filtered bill back dataframe
        t2: Filtered PPM dataframe
        material_id: Material ID to process
        close_threshold: Threshold for considering values as "close"
        
    Returns:
        List of dictionaries containing match results
    """
    # Filter for this material only
    t1_mat = t1[t1['Material'] == material_id].reset_index(drop=True)
    t2_mat = t2[t2['Dist Item#'] == material_id].reset_index(drop=True)
    
    t1_mat['id_t1'] = t1_mat.index
    t2_mat['id_t2'] = t2_mat.index
    
    matches = []
    used_t2_indices = set()
    
    # Find matches between t1 and t2
    for idx1, row1 in t1_mat.iterrows():
        match_row = _find_best_match(row1, t2_mat, close_threshold)
        if match_row.get('matched'):
            used_t2_indices.add(match_row.pop('matched_idx'))
        matches.append(match_row)
    
    # Find records only in PPM (t2) that weren't matched
    ppm_only_matches = _find_ppm_only_records(t2_mat, used_t2_indices)
    matches.extend(ppm_only_matches)
    
    return matches

def _find_best_match(row1: pd.Series, 
                    t2_mat: pd.DataFrame, 
                    close_threshold: float) -> Dict[str, Any]:
    """
    Find the best matching record in t2 for a given t1 record
    
    Args:
        row1: Single row from t1 to match
        t2_mat: Filtered t2 dataframe for this material
        close_threshold: Threshold for considering values as "close"
        
    Returns:
        Dictionary containing match result information
    """
    candidates = []
    
    # Check each potential match in t2
    for idx2, row2 in t2_mat.iterrows():
        # Check match criteria
        price_match = row1['At price'] == row2['Net$']
        qty_match = row1['Case in Part'] == row2['Quantity']
        partamt_match = row1['Part Amount'] == row2['Unit Rebate$']
        total_matches = sum([price_match, qty_match, partamt_match])
        
        # If at least 2 of 3 fields match, consider it a potential match
        if total_matches >= 2:
            # Determine which field doesn't match (if any)
            field, val1, val2, diff = _identify_mismatch(row1, row2, price_match, qty_match, partamt_match)
            
            # Add to candidates list
            candidates.append({
                'idx2': idx2,
                'diff': diff,
                'field': field,
                'val1': val1,
                'val2': val2,
                'row2': row2
            })
    
    # If we have candidates, pick the best one
    if candidates:
        # Filter for close matches first, then pick the smallest difference
        close_candidates = [c for c in candidates if c['diff'] < close_threshold]
        best = min(close_candidates, key=lambda x: x['diff']) if close_candidates else min(candidates, key=lambda x: x['diff'])
        
        field = best['field']
        comment = f"{field} mismatch ({best['val1']} vs {best['val2']})" if field else ""
        row2 = best['row2']
        
        # Calculate variance if both values are available
        var_value = row1['Extended Part'] - row2['Rebate'] if pd.notnull(row1['Extended Part']) and pd.notnull(row2['Rebate']) else np.nan
        
        return {
            'Material': row1['Material'],
            'At price': row1['At price'],
            'Case in Part': row1['Case in Part'],
            'Part Amount': row1['Part Amount'],
            'Extended Part': row1['Extended Part'],
            'Net$': row2['Net$'],
            'Quantity': row2['Quantity'],
            'Unit Rebate$': row2['Unit Rebate$'],
            'Rebate': row2['Rebate'],
            'VAR': var_value,
            'Comment': comment,
            'matched': True,
            'matched_idx': best['idx2']
        }
    else:
        # No match found - this is a missing deal
        return {
            'Material': row1['Material'],
            'At price': row1['At price'],
            'Case in Part': row1['Case in Part'],
            'Part Amount': row1['Part Amount'],
            'Extended Part': row1['Extended Part'],
            'Net$': np.nan,
            'Quantity': np.nan,
            'Unit Rebate$': np.nan,
            'Rebate': np.nan,
            'VAR': row1['Extended Part'],
            'Comment': 'Missing Deal',
            'matched': False
        }

def _identify_mismatch(row1: pd.Series, 
                      row2: pd.Series, 
                      price_match: bool, 
                      qty_match: bool, 
                      partamt_match: bool) -> tuple:
    """
    Identify which field has a mismatch between two rows
    
    Args:
        row1: Row from first table
        row2: Row from second table
        price_match: Whether price fields match
        qty_match: Whether quantity fields match
        partamt_match: Whether part amount fields match
        
    Returns:
        Tuple of (field_name, value1, value2, difference)
    """
    if not price_match:
        diff = abs(row1['At price'] - row2['Net$'])
        field = 'At price'
        val1 = row1['At price']
        val2 = row2['Net$']
    elif not qty_match:
        diff = abs(row1['Case in Part'] - row2['Quantity'])
        field = 'Case in Part'
        val1 = row1['Case in Part']
        val2 = row2['Quantity']
    elif not partamt_match:
        diff = abs(row1['Part Amount'] - row2['Unit Rebate$'])
        field = 'Part Amount'
        val1 = row1['Part Amount']
        val2 = row2['Unit Rebate$']
    else:
        # All match (unlikely to happen given the logic that calls this)
        diff = 0
        field = ''
        val1 = val2 = ""
    
    return field, val1, val2, diff

def _find_ppm_only_records(t2_mat: pd.DataFrame, 
                          used_t2_indices: set) -> List[Dict[str, Any]]:
    """
    Find records that only exist in the PPM table
    
    Args:
        t2_mat: PPM table filtered for current material
        used_t2_indices: Set of indices already matched to bill back records
        
    Returns:
        List of dictionaries for PPM-only records
    """
    ppm_only_matches = []
    
    ppm_only = t2_mat.loc[~t2_mat['id_t2'].isin(used_t2_indices)].copy()
    for _, row2 in ppm_only.iterrows():
        match_row = {
            'Material': row2['Dist Item#'],
            'At price': np.nan,
            'Case in Part': np.nan,
            'Part Amount': np.nan,
            'Extended Part': np.nan,
            'Net$': row2['Net$'],
            'Quantity': row2['Quantity'],
            'Unit Rebate$': row2['Unit Rebate$'],
            'Rebate': row2['Rebate'],
            'VAR': -row2['Rebate'],
            'Comment': 'PPM Only'
        }
        ppm_only_matches.append(match_row)
    
    return ppm_only_matches

def analyze_by_state(analysis_result: pd.DataFrame, 
                    states_df: pd.DataFrame, 
                    item_ref_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Further analyze results by state to provide state-specific breakdowns
    
    Args:
        analysis_result: Output from analyze_materials
        states_df: DataFrame with state information
        item_ref_df: DataFrame with item reference information
        
    Returns:
        Dictionary of DataFrames with state-specific analysis
    """
    logger.info("Starting state-level analysis")
    
    # Implementation would go here - this is a placeholder for extending functionality
    # This would join the analysis results with state information to provide
    # state-specific breakdowns
    
    return {"state_analysis": analysis_result}  # Placeholder return

def generate_summary_statistics(analysis_result: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics from analysis results
    
    Args:
        analysis_result: Output from analyze_materials
        
    Returns:
        Dictionary with summary statistics
    """
    if analysis_result.empty:
        logger.warning("Cannot generate statistics from empty analysis result")
        return {}
    
    try:
        total_records = len(analysis_result)
        missing_deals = len(analysis_result[analysis_result['Comment'] == 'Missing Deal'])
        ppm_only = len(analysis_result[analysis_result['Comment'] == 'PPM Only'])
        mismatches = len(analysis_result[analysis_result['Comment'].str.contains('mismatch', na=False)])
        perfect_matches = total_records - missing_deals - ppm_only - mismatches
        
        total_variance = analysis_result['VAR'].sum()
        abs_variance = analysis_result['VAR'].abs().sum()
        
        logger.info(f"Analysis summary: {perfect_matches} perfect matches, {mismatches} mismatches, " 
                   f"{missing_deals} missing deals, {ppm_only} PPM only. Total variance: ${total_variance:.2f}")
        
        return {
            "total_records": total_records,
            "perfect_matches": perfect_matches,
            "mismatches": mismatches,
            "missing_deals": missing_deals,
            "ppm_only": ppm_only,
            "total_variance": total_variance,
            "absolute_variance": abs_variance,
            "percent_matched": (perfect_matches / total_records * 100) if total_records else 0
        }
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        return {}