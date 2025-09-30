"""
Data Enrichment Module - Enhances datasets with additional information

This module provides functions to enrich data tables with calculated fields,
reference data, and standardized formatting to prepare them for analysis.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Union, Optional, Any, Tuple

# Configure logging
logger = logging.getLogger(__name__)

def enrich_billback_table(tabla1: pd.DataFrame, 
                         states: pd.DataFrame, 
                         item_ref: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the Bill Back table with additional information from States and Item Reference tables
    
    Args:
        tabla1: Bill Back DataFrame to enrich
        states: States reference DataFrame
        item_ref: Item reference DataFrame
    
    Returns:
        Enriched Bill Back DataFrame with additional columns and transformations
    """
    logger.info("Starting Bill Back table enrichment")
    try:
        # Make a copy to avoid modifying the original
        result_df = tabla1.copy()
        
        # Add month names
        result_df = _add_month_names(result_df)
        
        # Join with States table
        result_df = _merge_with_states(result_df, states)
        
        # Prepare and join with Item Reference table
        result_df = _merge_with_item_ref(result_df, item_ref)
        
        # Add state abbreviations
        result_df = _add_state_abbreviations(result_df)
        
        # Add complete dates
        result_df = _add_complete_dates(result_df)
        
        # Final cleaning
        result_df = result_df[result_df["CoCd"].notnull()]
        
        logger.info(f"Bill Back enrichment complete. Result has {len(result_df)} rows and {len(result_df.columns)} columns")
        return result_df
        
    except Exception as e:
        logger.error(f"Error enriching Bill Back table: {str(e)}")
        # Return original table if enrichment fails
        return tabla1

def _add_month_names(df: pd.DataFrame) -> pd.DataFrame:
    """Add month names based on posting period"""
    logger.debug("Adding month names")
    
    def get_month_name(posting_period):
        try:
            posting_str = str(posting_period).zfill(6)
            month_number = int(posting_str[-2:])
            months = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
            return months[month_number - 1] if 1 <= month_number <= 12 else np.nan
        except Exception as e:
            logger.warning(f"Error getting month name for {posting_period}: {str(e)}")
            return np.nan
            
    df["Month Name"] = df["Posting Period "].apply(get_month_name)
    return df

def _merge_with_states(df: pd.DataFrame, states: pd.DataFrame) -> pd.DataFrame:
    """Join bill back table with states reference"""
    logger.debug("Merging with States reference table")
    
    try:
        # Perform LEFT JOIN with States table
        result = pd.merge(
            df,
            states[["Company Code (SAP)", "State", "Region", "State Abbreviation", "Custom Abbreviation"]],
            left_on="CoCd",
            right_on="Company Code (SAP)",
            how="left"
        )
        
        # Rename columns to avoid ambiguity
        result.rename(columns={
            "State": "States.State",
            "Region": "States.Region",
            "State Abbreviation": "States.State Abbreviation",
            "Custom Abbreviation": "Custom Abbreviation"
        }, inplace=True)
        
        # Drop redundant column
        if "Company Code (SAP)" in result.columns:
            result.drop("Company Code (SAP)", axis=1, inplace=True)
            
        return result
        
    except Exception as e:
        logger.error(f"Error merging with states table: {str(e)}")
        return df  # Return original on error

def _merge_with_item_ref(df: pd.DataFrame, item_ref: pd.DataFrame) -> pd.DataFrame:
    """Join bill back table with item reference data"""
    logger.debug("Merging with Item Reference table")
    
    try:
        # Force string type conversion for safe merging
        df["Material"] = df["Material"].astype(str)
        item_ref_copy = item_ref.copy()
        item_ref_copy["Dist. Item Code"] = item_ref_copy["Dist. Item Code"].astype(str)
        
        # Prepare brand and package data
        item_ref_copy["Supp. Brand Desc."] = item_ref_copy["Supp. Brand Desc."].fillna("").astype(str)
        item_ref_copy["Package Size"] = item_ref_copy["Package Size"].fillna("").astype(str)
        item_ref_copy["Brand + Pk size"] = item_ref_copy[["Supp. Brand Desc.", "Package Size"]].agg(' '.join, axis=1).str.strip()
        
        # Remove existing column if present
        if "Brand + Pk size" in df.columns:
            df = df.drop(columns=["Brand + Pk size"])
        
        # Perform LEFT JOIN with Item Reference
        result = pd.merge(
            df,
            item_ref_copy[["Dist. Item Code", "Supp. Brand Desc.", "Package Size", "Brand + Pk size"]],
            left_on="Material",
            right_on="Dist. Item Code",
            how="left"
        )
        
        # Rename columns for clarity
        result.rename(columns={
            "Supp. Brand Desc.": "Brand",
            "Package Size": "Pck Size"
        }, inplace=True)
        
        # Drop redundant column
        if "Dist. Item Code" in result.columns:
            result.drop("Dist. Item Code", axis=1, inplace=True)
        
        # Create robust Brand + Pk size column
        result["Brand"] = result["Brand"].fillna("").astype(str)
        result["Pck Size"] = result["Pck Size"].fillna("").astype(str)
        result["Brand + Pk size"] = result[["Brand", "Pck Size"]].agg(' '.join, axis=1).str.strip()
        
        return result
        
    except Exception as e:
        logger.error(f"Error merging with item reference: {str(e)}")
        return df  # Return original on error

def _add_state_abbreviations(df: pd.DataFrame) -> pd.DataFrame:
    """Add standard state abbreviations based on state names"""
    logger.debug("Adding state abbreviations")
    
    def get_abbreviation(state):
        if pd.isnull(state):
            return np.nan
            
        mapping = {
            "Delaware": "DE", 
            "Florida": "FL", 
            "Kentucky": "KY", 
            "Maryland": "MD/DC",
            "District of Columbia": "MD/DC", 
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
            "Oregon": "OR"
        }
        return mapping.get(state, np.nan)
        
    df["Abbreviation"] = df["States.State"].apply(get_abbreviation)
    df["Abbreviation"] = df["Abbreviation"].astype(str).str.strip()
    return df

def _add_complete_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert posting period to complete date"""
    logger.debug("Adding complete dates")
    
    def get_complete_date(posting_period):
        try:
            posting_str = str(posting_period).zfill(6)
            year = int(posting_str[:4])
            month = int(posting_str[-2:])
            return pd.Timestamp(year=year, month=month, day=1)
        except Exception as e:
            logger.debug(f"Error converting posting period {posting_period} to date: {str(e)}")
            return pd.NaT
            
    df["Complete Date"] = df["Posting Period "].apply(get_complete_date)
    return df

def enrich_ppm_table(ppm: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the PPM table with data cleaning, transformations, and derived columns
    
    Args:
        ppm: PPM DataFrame to enrich
        
    Returns:
        Enriched PPM DataFrame with clean data types and additional columns
    """
    logger.info("Starting PPM table enrichment")
    
    try:
        # Make a copy to avoid modifying the original
        result_df = ppm.copy()
        
        # Convert numeric columns
        result_df = _convert_ppm_numeric_columns(result_df)
        
        # Clean and standardize text columns
        result_df = _clean_ppm_text_columns(result_df)
        
        # Convert date columns
        result_df = _convert_ppm_date_columns(result_df)
        
        # Split distributor name
        result_df = _split_distributor_name(result_df)
        
        # Create combined brand+size column
        result_df = _create_ppm_brand_size(result_df)
        
        logger.info(f"PPM enrichment complete. Result has {len(result_df)} rows and {len(result_df.columns)} columns")
        return result_df
        
    except Exception as e:
        logger.error(f"Error enriching PPM table: {str(e)}")
        # Return original table if enrichment fails
        return ppm

def _convert_ppm_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert PPM numeric columns to proper types"""
    logger.debug("Converting PPM numeric columns")
    
    num_cols = ["Dist Code", "Dist Item#", "Package#", "Net$", "Quantity", "Unit Rebate$", "Rebate"]
    for col in num_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception as e:
                logger.warning(f"Error converting {col} to numeric: {str(e)}")
    
    # Ensure rebate is never null
    if "Rebate" in df.columns:
        df["Rebate"] = pd.to_numeric(df["Rebate"], errors="coerce").fillna(0)
        
    return df

def _clean_ppm_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize text columns in PPM table"""
    logger.debug("Cleaning PPM text columns")
    
    str_cols = ["Dist Name", "Brand", "Pkg Size", "Promotion", "Acct Group", "Type", "Status"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
            
    return df

def _convert_ppm_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date columns in PPM table to datetime"""
    logger.debug("Converting PPM date columns")
    
    try:
        df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    except Exception as e:
        logger.warning(f"Error converting Start column to datetime: {str(e)}")
        
    return df

def _split_distributor_name(df: pd.DataFrame) -> pd.DataFrame:
    """Split distributor name into components"""
    logger.debug("Splitting distributor name")
    
    try:
        # Split on hyphen with a maximum of 1 split
        split_cols = df["Dist Name"].str.split("-", n=1, expand=True)
        
        # First part (always present)
        df["Dist Name.1"] = split_cols[0].str.strip().str.upper()
        
        # Second part (may not be present if no hyphen)
        if split_cols.shape[1] > 1:
            df["Dist Name.2"] = split_cols[1].str.strip().str.upper()
        else:
            df["Dist Name.2"] = ""
            
        # Extra cleanup for second part
        df["Dist Name.2"] = (
            df["Dist Name.2"]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
        )
        
    except Exception as e:
        logger.warning(f"Error splitting distributor name: {str(e)}")
        # Create empty columns if splitting fails
        df["Dist Name.1"] = df["Dist Name"]
        df["Dist Name.2"] = ""
        
    return df

def _create_ppm_brand_size(df: pd.DataFrame) -> pd.DataFrame:
    """Create combined brand and package size column"""
    logger.debug("Creating PPM brand+size column")
    
    try:
        df["Brand"] = df["Brand"].fillna("").astype(str)
        df["Pkg Size"] = df["Pkg Size"].fillna("").astype(str)
        df["ppm_Brand+pk size"] = df[["Brand", "Pkg Size"]].agg(' '.join, axis=1).str.strip()
    except Exception as e:
        logger.warning(f"Error creating ppm_Brand+pk size: {str(e)}")
        # Create empty column if operation fails
        df["ppm_Brand+pk size"] = ""
        
    return df

def get_data_quality_report(billback_df: pd.DataFrame, 
                           ppm_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Generate a data quality report for enriched dataframes
    
    Args:
        billback_df: Enriched Bill Back DataFrame
        ppm_df: Enriched PPM DataFrame
        
    Returns:
        Dictionary with data quality metrics for both datasets
    """
    logger.info("Generating data quality report")
    
    report = {
        "billback": {},
        "ppm": {}
    }
    
    try:
        # Bill Back quality metrics
        report["billback"] = {
            "total_rows": len(billback_df),
            "total_columns": len(billback_df.columns),
            "missing_values": billback_df.isna().sum().sum(),
            "missing_percent": round((billback_df.isna().sum().sum() / (len(billback_df) * len(billback_df.columns))) * 100, 2),
            "brand_pk_size_count": len(billback_df["Brand + Pk size"].unique()),
            "states_count": len(billback_df["States.State"].dropna().unique()),
            "material_count": len(billback_df["Material"].unique()),
            "date_range": _get_date_range(billback_df, "Complete Date"),
        }
        
        # PPM quality metrics
        report["ppm"] = {
            "total_rows": len(ppm_df),
            "total_columns": len(ppm_df.columns),
            "missing_values": ppm_df.isna().sum().sum(),
            "missing_percent": round((ppm_df.isna().sum().sum() / (len(ppm_df) * len(ppm_df.columns))) * 100, 2),
            "brand_pk_size_count": len(ppm_df["ppm_Brand+pk size"].unique()),
            "distributor_count": len(ppm_df["Dist Name"].unique()),
            "item_count": len(ppm_df["Dist Item#"].dropna().unique()),
            "date_range": _get_date_range(ppm_df, "Start"),
        }
        
        logger.info("Data quality report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"Error generating data quality report: {str(e)}")
        return {
            "billback": {"error": str(e)},
            "ppm": {"error": str(e)}
        }

def _get_date_range(df: pd.DataFrame, date_col: str) -> Dict[str, str]:
    """Get min and max dates from a date column"""
    if date_col not in df.columns:
        return {"min": "N/A", "max": "N/A"}
        
    dates = df[date_col].dropna()
    if len(dates) == 0:
        return {"min": "N/A", "max": "N/A"}
        
    return {
        "min": str(dates.min().date()) if pd.notna(dates.min()) else "N/A",
        "max": str(dates.max().date()) if pd.notna(dates.max()) else "N/A"
    }