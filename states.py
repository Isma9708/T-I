"""
States Processing Module - Handles state abbreviation and region processing

This module provides functions to standardize state information, add custom abbreviations,
and apply regional classifications for analysis and reporting purposes.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# State abbreviation mapping dictionary
STATE_ABBREVIATIONS = {
    "Delaware": "DE",
    "Florida": "FL",
    "Kentucky": "KY",
    "Maryland": "MD/DC",
    "District of Columbia": "MD/DC",
    "Montgomery Co. MD": "MD/DC",
    "New York - Metro": "NY METRO",
    "New York - Upstate": "NY UPSTATE",
    "Ohio (Wine)": "OH (Wine)",
    "South Carolina": "SC",
    "Arkansas": "AR",
    "Colorado": "CO",
    "Iowa (Wine)": "IA (Wine)",
    "Illinois": "IL",
    "Indiana": "IN",
    "Louisiana": "LA",
    "Minnesota": "MN",
    "Oklahoma": "OK",
    "South Dakota": "SD",
    "Texas": "TX",
    "Nebraska": "NE",
    "Tennessee": "TN",
    "North Dakota": "ND",
    "Kansas": "KS",
    "California - North": "NCA",
    "Nevada": "NV",
    "California - South": "SCA",
    "Washington": "WA",
    "Hawaii": "HI",
    "California": "CA",
    "Arizona": "AZ",
    "New Mexico": "NM",
    "Oregon": "OR",
    "Idaho": "ID",
    "Ohio": "OH"
}

def add_custom_abbreviation(states: pd.DataFrame) -> pd.DataFrame:
    """
    Add custom state abbreviations to the states dataframe and apply filtering
    
    Args:
        states: DataFrame containing state information with at least 'State' and 'Region' columns
    
    Returns:
        DataFrame with added 'Custom Abbreviation' column and filtered to exclude Canadian regions
    """
    logger.info("Adding custom state abbreviations")
    
    try:
        # Make a copy to avoid modifying the original
        result_df = states.copy()
        
        # Add custom abbreviations
        result_df["Custom Abbreviation"] = result_df["State"].apply(get_state_abbreviation)
        
        # Filter out Canadian regions
        result_df = result_df[result_df["Region"] != "Canada Region"].copy()
        
        # Clean up the abbreviations
        result_df = clean_abbreviations(result_df)
        
        logger.info(f"Custom abbreviations added successfully for {len(result_df)} states")
        return result_df
        
    except Exception as e:
        logger.error(f"Error adding custom abbreviations: {str(e)}")
        # Return original dataframe if operation fails
        return states

def get_state_abbreviation(state_name: str) -> Optional[str]:
    """
    Get the custom abbreviation for a given state name
    
    Args:
        state_name: Name of the state to abbreviate
    
    Returns:
        Abbreviated state code or np.nan if no match is found
    """
    try:
        state = str(state_name).strip()
        
        # Direct lookup in mapping dictionary
        if state in STATE_ABBREVIATIONS:
            return STATE_ABBREVIATIONS[state]
        
        # Partial match for special cases
        if "Oregon" in state:
            return "OR"
        elif "Idaho" in state:
            return "ID"
        elif "Ohio" in state:
            return "OH"
            
        # No match found
        return np.nan
        
    except Exception as e:
        logger.debug(f"Error getting abbreviation for '{state_name}': {str(e)}")
        return np.nan

def clean_abbreviations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize state abbreviations in the dataframe
    
    Args:
        df: DataFrame with 'Custom Abbreviation' column
    
    Returns:
        DataFrame with cleaned abbreviations
    """
    try:
        df["Custom Abbreviation"] = (
            df["Custom Abbreviation"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
        )
        return df
    except Exception as e:
        logger.warning(f"Error cleaning abbreviations: {str(e)}")
        return df

def get_regional_states(states_df: pd.DataFrame, region: str) -> pd.DataFrame:
    """
    Filter states dataframe to a specific region
    
    Args:
        states_df: DataFrame containing state information
        region: Region name to filter by
    
    Returns:
        DataFrame filtered to only include states in the specified region
    """
    logger.debug(f"Filtering states for region: {region}")
    
    try:
        return states_df[states_df["Region"] == region].copy()
    except Exception as e:
        logger.error(f"Error filtering states by region '{region}': {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_regions_list(states_df: pd.DataFrame) -> list:
    """
    Get a list of all unique regions in the states dataframe
    
    Args:
        states_df: DataFrame containing state information with a 'Region' column
    
    Returns:
        List of unique region names
    """
    try:
        regions = states_df["Region"].unique().tolist()
        return sorted([r for r in regions if pd.notna(r)])
    except Exception as e:
        logger.error(f"Error getting regions list: {str(e)}")
        return []

def get_states_in_regions(states_df: pd.DataFrame) -> Dict[str, list]:
    """
    Get a dictionary mapping each region to its list of states
    
    Args:
        states_df: DataFrame containing state information
    
    Returns:
        Dictionary with regions as keys and lists of state names as values
    """
    logger.debug("Building region to states mapping")
    
    try:
        result = {}
        for region in get_regions_list(states_df):
            region_states = states_df[states_df["Region"] == region]["State"].tolist()
            result[region] = sorted(region_states)
        return result
    except Exception as e:
        logger.error(f"Error mapping regions to states: {str(e)}")
        return {}