"""
States Processing Module - Handles state-level data operations

This module provides functionality for working with state information,
including adding custom state abbreviations, mapping state codes, and
filtering data by state.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

def add_custom_abbreviation(states_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a custom abbreviation column to the states dataframe
    
    Args:
        states_df: DataFrame containing state information
        
    Returns:
        DataFrame with added Custom Abbreviation column
    """
    if states_df is None or states_df.empty:
        logger.warning("Empty states dataframe provided")
        return pd.DataFrame()
    
    logger.info("Adding custom abbreviations to states dataframe")
    
    try:
        # Create a copy to avoid modifying the original
        result_df = states_df.copy()
        
        # Check if the required columns exist
        required_columns = ['State', 'State Code', 'Region']
        missing_columns = [col for col in required_columns if col not in result_df.columns]
        
        if missing_columns:
            logger.warning(f"Missing required columns in states_df: {missing_columns}")
            # Add placeholder columns if missing
            for col in missing_columns:
                result_df[col] = ""
        
        # Create custom abbreviation based on State Code if available, otherwise use first 2 chars of State
        if 'State Code' in result_df.columns and not result_df['State Code'].isna().all():
            # Use state code where available
            result_df['Custom Abbreviation'] = result_df['State Code'].fillna("")
        else:
            # Fallback to first 2 characters of state name
            result_df['Custom Abbreviation'] = result_df['State'].str[:2].str.upper()
        
        # Handle special cases and ensure uniqueness
        abbrev_map = {
            'CALIFORNIA': 'CA',
            'NEW YORK': 'NY',
            'FLORIDA': 'FL',
            'TEXAS': 'TX',
            'ILLINOIS': 'IL',
            'PENNSYLVANIA': 'PA',
            'OHIO': 'OH',
            'MICHIGAN': 'MI',
            'GEORGIA': 'GA',
            'NORTH CAROLINA': 'NC',
            'NEW JERSEY': 'NJ',
            'VIRGINIA': 'VA',
            'WASHINGTON': 'WA',
            'MASSACHUSETTS': 'MA',
            'ARIZONA': 'AZ',
            'INDIANA': 'IN',
            'TENNESSEE': 'TN',
            'MISSOURI': 'MO',
            'MARYLAND': 'MD',
            'WISCONSIN': 'WI',
            'MINNESOTA': 'MN',
            'COLORADO': 'CO',
            'ALABAMA': 'AL',
            'SOUTH CAROLINA': 'SC',
            'LOUISIANA': 'LA',
            'KENTUCKY': 'KY',
            'OREGON': 'OR',
            'OKLAHOMA': 'OK',
            'CONNECTICUT': 'CT',
            'IOWA': 'IA',
            'MISSISSIPPI': 'MS',
            'ARKANSAS': 'AR',
            'KANSAS': 'KS',
            'UTAH': 'UT',
            'NEVADA': 'NV',
            'NEW MEXICO': 'NM',
            'NEBRASKA': 'NE',
            'WEST VIRGINIA': 'WV',
            'IDAHO': 'ID',
            'HAWAII': 'HI',
            'MAINE': 'ME',
            'NEW HAMPSHIRE': 'NH',
            'RHODE ISLAND': 'RI',
            'MONTANA': 'MT',
            'DELAWARE': 'DE',
            'SOUTH DAKOTA': 'SD',
            'NORTH DAKOTA': 'ND',
            'ALASKA': 'AK',
            'VERMONT': 'VT',
            'WYOMING': 'WY'
        }
        
        # Apply the mapping where state names match (case insensitive)
        for idx, row in result_df.iterrows():
            state_name = row['State'].upper() if not pd.isna(row['State']) else ""
            if state_name in abbrev_map:
                result_df.at[idx, 'Custom Abbreviation'] = abbrev_map[state_name]
        
        logger.info(f"Successfully added custom abbreviations to {len(result_df)} state records")
        return result_df
        
    except Exception as e:
        logger.error(f"Error adding custom abbreviations: {str(e)}")
        return states_df  # Return original dataframe on error

def get_state_region_mapping(states_df: pd.DataFrame) -> Dict[str, str]:
    """
    Creates a mapping of state abbreviations to their regions
    
    Args:
        states_df: DataFrame containing state information with Custom Abbreviation and Region columns
        
    Returns:
        Dictionary mapping state abbreviations to regions
    """
    if states_df is None or states_df.empty:
        logger.warning("Empty states dataframe provided for region mapping")
        return {}
    
    try:
        # Check if required columns exist
        if 'Custom Abbreviation' not in states_df.columns or 'Region' not in states_df.columns:
            logger.warning("Missing required columns for region mapping")
            return {}
        
        # Create mapping dictionary
        mapping = dict(zip(
            states_df['Custom Abbreviation'].fillna("").astype(str),
            states_df['Region'].fillna("Unknown").astype(str)
        ))
        
        logger.info(f"Created state-region mapping with {len(mapping)} entries")
        return mapping
        
    except Exception as e:
        logger.error(f"Error creating state-region mapping: {str(e)}")
        return {}

def filter_by_state(df: pd.DataFrame, 
                   state_abbr: str, 
                   state_column: str = 'Custom Abbreviation') -> pd.DataFrame:
    """
    Filters a dataframe to include only rows for a specific state
    
    Args:
        df: DataFrame to filter
        state_abbr: State abbreviation to filter by
        state_column: Column name containing state abbreviations
        
    Returns:
        Filtered DataFrame containing only rows for the specified state
    """
    if df is None or df.empty:
        logger.warning("Empty dataframe provided for state filtering")
        return pd.DataFrame()
    
    if state_column not in df.columns:
        logger.warning(f"State column '{state_column}' not found in dataframe")
        return pd.DataFrame()
    
    try:
        filtered = df[df[state_column].astype(str).str.strip() == state_abbr.strip()]
        logger.info(f"Filtered to {len(filtered)} rows for state {state_abbr}")
        return filtered
        
    except Exception as e:
        logger.error(f"Error filtering by state: {str(e)}")
        return pd.DataFrame()

def group_by_region(df: pd.DataFrame, 
                   states_df: pd.DataFrame,
                   state_column: str = 'Custom Abbreviation') -> Dict[str, pd.DataFrame]:
    """
    Groups a dataframe by regions based on state information
    
    Args:
        df: DataFrame to group
        states_df: DataFrame containing state and region information
        state_column: Column name containing state abbreviations
        
    Returns:
        Dictionary mapping regions to filtered DataFrames
    """
    if df is None or df.empty or states_df is None or states_df.empty:
        logger.warning("Empty dataframe(s) provided for region grouping")
        return {}
    
    try:
        # Get state-region mapping
        state_regions = get_state_region_mapping(states_df)
        
        # Add region column to the dataframe
        df_with_regions = df.copy()
        df_with_regions['Region'] = df[state_column].map(state_regions)
        
        # Group by region
        result = {}
        for region in df_with_regions['Region'].dropna().unique():
            region_df = df_with_regions[df_with_regions['Region'] == region].copy()
            result[region] = region_df
            logger.info(f"Region {region}: {len(region_df)} records")
        
        return result
        
    except Exception as e:
        logger.error(f"Error grouping by region: {str(e)}")
        return {}
