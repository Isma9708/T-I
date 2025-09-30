"""
Data Enrichment Module - Enhances raw data with additional attributes

This module provides functions for enriching raw data tables with calculated fields,
joined data, and normalized attributes to prepare for analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Union, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def enrich_billback_table(billback_df: pd.DataFrame, 
                         states_df: pd.DataFrame,
                         item_ref_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the bill back table with additional information and calculated fields
    
    Args:
        billback_df: Bill back dataframe
        states_df: States dataframe with Custom Abbreviation
        item_ref_df: Item reference dataframe
        
    Returns:
        Enriched bill back dataframe with additional columns
    """
    if billback_df is None or billback_df.empty:
        logger.warning("Empty bill back dataframe provided")
        return pd.DataFrame()
    
    logger.info("Enriching bill back dataframe")
    
    try:
        # Create a copy to avoid modifying the original
        result_df = billback_df.copy()
        
        # Add state abbreviation mapping
        if 'State' in result_df.columns and not states_df.empty:
            # Create state name to abbreviation mapping
            state_mapping = dict(zip(
                states_df['State'].str.upper().fillna(""),
                states_df['Custom Abbreviation'].fillna("")
            ))
            
            # Map state names to abbreviations
            result_df['Custom Abbreviation'] = result_df['State'].str.upper().map(state_mapping)
            logger.info("Added state abbreviations to bill back data")
        
        # Add brand and package information
        if not item_ref_df.empty:
            # First prepare the item reference dataframe
            if 'Material' in item_ref_df.columns and 'Supp. Brand Desc.' in item_ref_df.columns:
                # Create material to brand mapping
                material_to_brand = dict(zip(
                    item_ref_df['Material'].astype(str),
                    item_ref_df['Supp. Brand Desc.'].astype(str)
                ))
                
                # Create material to package size mapping
                if 'Package Size' in item_ref_df.columns:
                    material_to_package = dict(zip(
                        item_ref_df['Material'].astype(str),
                        item_ref_df['Package Size'].astype(str)
                    ))
                else:
                    material_to_package = {}
                    
                # Add brand information
                result_df['Brand'] = result_df['Material'].astype(str).map(material_to_brand)
                
                # Add package size
                if material_to_package:
                    result_df['Package Size'] = result_df['Material'].astype(str).map(material_to_package)
                
                # Create combined Brand + Package Size field
                if 'Brand' in result_df.columns:
                    if 'Package Size' in result_df.columns:
                        result_df['Brand + Pk size'] = result_df[['Brand', 'Package Size']].fillna("").agg(' '.join, axis=1).str.strip()
                    else:
                        result_df['Brand + Pk size'] = result_df['Brand']
                        
                logger.info("Added brand and package information to bill back data")
        
        # Convert date fields
        date_fields = ['Posting Date', 'Posting Period ']
        for field in date_fields:
            if field in result_df.columns:
                try:
                    result_df[field] = pd.to_datetime(result_df[field], errors='coerce')
                except:
                    logger.warning(f"Could not convert {field} to datetime")
                    
        # Add complete date with year and month
        if 'Posting Period ' in result_df.columns:
            try:
                result_df['Complete Date'] = pd.to_datetime(result_df['Posting Period '], errors='coerce')
                logger.info("Added complete date field to bill back data")
            except:
                logger.warning("Could not create complete date field")
        
        # Calculate extended part amount if not present
        if 'Part Amount' in result_df.columns and 'Case in Part' in result_df.columns:
            if 'Extended Part' not in result_df.columns:
                result_df['Extended Part'] = result_df['Part Amount'] * result_df['Case in Part']
                logger.info("Calculated extended part amount")
        
        # Add sequential ID for easier tracking
        result_df['bill_back_id'] = range(1, len(result_df) + 1)
        
        logger.info(f"Successfully enriched bill back dataframe with {len(result_df)} rows")
        return result_df
        
    except Exception as e:
        logger.error(f"Error enriching bill back data: {str(e)}")
        return billback_df  # Return original on error

def enrich_ppm_table(ppm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches the PPM table with additional information and calculated fields
    
    Args:
        ppm_df: PPM dataframe
        
    Returns:
        Enriched PPM dataframe with additional columns
    """
    if ppm_df is None or ppm_df.empty:
        logger.warning("Empty PPM dataframe provided")
        return pd.DataFrame()
    
    logger.info("Enriching PPM dataframe")
    
    try:
        # Create a copy to avoid modifying the original
        result_df = ppm_df.copy()
        
        # Convert date fields
        date_fields = ['Start', 'End']
        for field in date_fields:
            if field in result_df.columns:
                try:
                    result_df[field] = pd.to_datetime(result_df[field], errors='coerce')
                except:
                    logger.warning(f"Could not convert {field} to datetime")
        
        # Calculate rebate amount if not present
        if 'Unit Rebate$' in result_df.columns and 'Quantity' in result_df.columns:
            if 'Rebate' not in result_df.columns:
                result_df['Rebate'] = result_df['Unit Rebate$'] * result_df['Quantity']
                logger.info("Calculated rebate amount")
        
        # Create combined Brand + Package Size field
        brand_cols = ['Brand', 'Supp. Brand Desc.', 'Brand Name']
        brand_col = next((col for col in brand_cols if col in result_df.columns), None)
        
        package_cols = ['Package Size', 'Pkg Size', 'Size']
        package_col = next((col for col in package_cols if col in result_df.columns), None)
        
        if brand_col is not None:
            if package_col is not None:
                result_df['ppm_Brand+pk size'] = result_df[[brand_col, package_col]].fillna("").agg(' '.join, axis=1).str.strip()
            else:
                result_df['ppm_Brand+pk size'] = result_df[brand_col]
            logger.info("Created combined brand+package field")
        
        # Add sequential ID for easier tracking
        result_df['ppm_id'] = range(1, len(result_df) + 1)
        
        logger.info(f"Successfully enriched PPM dataframe with {len(result_df)} rows")
        return result_df
        
    except Exception as e:
        logger.error(f"Error enriching PPM data: {str(e)}")
        return ppm_df  # Return original on error

def standardize_units(df: pd.DataFrame, 
                     column: str, 
                     from_unit: str, 
                     to_unit: str, 
                     conversion_factor: float) -> pd.DataFrame:
    """
    Standardizes units in a specific column
    
    Args:
        df: DataFrame containing the column to standardize
        column: Column name to standardize
        from_unit: Original unit
        to_unit: Target unit
        conversion_factor: Factor to multiply for conversion
        
    Returns:
        DataFrame with standardized column
    """
    if df is None or df.empty or column not in df.columns:
        logger.warning(f"Cannot standardize units: column {column} not found or empty dataframe")
        return df
    
    try:
        result = df.copy()
        
        # Perform conversion
        result[f"{column}_{to_unit}"] = result[column] * conversion_factor
        
        # Add units metadata
        result[f"{column}_unit"] = to_unit
        
        logger.info(f"Standardized {column} from {from_unit} to {to_unit}")
        return result
        
    except Exception as e:
        logger.error(f"Error standardizing units: {str(e)}")
        return df

def normalize_column_names(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Normalizes column names according to a mapping
    
    Args:
        df: DataFrame to normalize
        mapping: Dictionary mapping original names to normalized names
        
    Returns:
        DataFrame with normalized column names
    """
    if df is None or df.empty:
        return df
    
    try:
        result = df.copy()
        result.columns = [mapping.get(col, col) for col in result.columns]
        
        logger.info("Normalized column names")
        return result
        
    except Exception as e:
        logger.error(f"Error normalizing column names: {str(e)}")
        return df
