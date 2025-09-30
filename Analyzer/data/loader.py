"""
Data Loading Module - Provides efficient, error-handled data loading capabilities
"""

import pandas as pd
import logging
from typing import Tuple, Optional, List, Dict
import os

# Configure logging
logger = logging.getLogger(__name__)

def load_dataframes() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all required dataframes with proper error handling and logging
    
    Returns:
        Tuple containing (billback_df, item_ref_df, ppm_df, states_df)
    """
    file_info = get_file_paths()
    dataframes = {}
    
    for file in file_info:
        name = file["name"]
        file_path = file["path"]
        sheet = file["sheet"]
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                raise FileNotFoundError(f"Could not find {name} file at {file_path}")
            
            logger.info(f"Loading {name} from {file_path}")
            dataframes[name] = pd.read_excel(file_path, sheet_name=sheet)
            logger.info(f"Successfully loaded {name} with {len(dataframes[name])} rows")
            
        except Exception as e:
            logger.error(f"Error loading {name}: {str(e)}")
            # Provide empty DataFrame as fallback to prevent application crash
            dataframes[name] = pd.DataFrame()
            
    # Return dataframes in the expected order
    return (
        dataframes.get("Bill back", pd.DataFrame()),
        dataframes.get("Item x Ref", pd.DataFrame()),
        dataframes.get("PPM", pd.DataFrame()),
        dataframes.get("States", pd.DataFrame())
    )

def load_uploaded_dataframes(file_paths: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load dataframes from uploaded files
    
    Args:
        file_paths: Dictionary mapping file types to file paths
        
    Returns:
        Tuple containing (billback_df, item_ref_df, ppm_df, states_df)
    """
    dataframes = {}
    
    # Map file types to expected names
    file_mapping = {
        'billback': "Bill back",
        'item_ref': "Item x Ref",
        'ppm': "PPM",
        'states': "States"
    }
    
    # Define sheet names for each file type
    sheet_mapping = {
        'billback': "Data DE DP DQ NC",
        'item_ref': 0,
        'ppm': "Sheet1",
        'states': "States"
    }
    
    for file_type, file_path in file_paths.items():
        name = file_mapping.get(file_type, file_type)
        sheet = sheet_mapping.get(file_type, 0)
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"Uploaded file not found: {file_path}")
                raise FileNotFoundError(f"Could not find uploaded {name} file")
            
            logger.info(f"Loading uploaded {name} from {file_path}")
            dataframes[name] = pd.read_excel(file_path, sheet_name=sheet)
            logger.info(f"Successfully loaded {name} with {len(dataframes[name])} rows")
            
        except Exception as e:
            logger.error(f"Error loading uploaded {name}: {str(e)}")
            dataframes[name] = pd.DataFrame()
            
    # Return dataframes in the expected order
    return (
        dataframes.get("Bill back", pd.DataFrame()),
        dataframes.get("Item x Ref", pd.DataFrame()),
        dataframes.get("PPM", pd.DataFrame()),
        dataframes.get("States", pd.DataFrame())
    )

def check_dataframe_compatibility(billback_df: pd.DataFrame,
                                item_ref_df: pd.DataFrame,
                                ppm_df: pd.DataFrame,
                                states_df: pd.DataFrame) -> List[str]:
    """
    Check if uploaded dataframes have the required structure and columns
    
    Args:
        billback_df: Bill back dataframe
        item_ref_df: Item reference dataframe
        ppm_df: PPM dataframe
        states_df: States dataframe
        
    Returns:
        List of issues found (empty if no issues)
    """
    issues = []
    
    # Check Bill back dataframe
    required_billback_cols = ['Material', 'At price', 'Case in Part', 'Part Amount', 'Posting Period ']
    missing_bb_cols = [col for col in required_billback_cols if col not in billback_df.columns]
    if missing_bb_cols:
        issues.append(f"Bill back file is missing required columns: {', '.join(missing_bb_cols)}")
    
    # Check Item ref dataframe
    required_item_ref_cols = ['Material', 'Supp. Brand Desc.', 'Package Size']
    missing_ir_cols = [col for col in required_item_ref_cols if col not in item_ref_df.columns]
    if missing_ir_cols:
        issues.append(f"Item reference file is missing required columns: {', '.join(missing_ir_cols)}")
    
    # Check PPM dataframe
    required_ppm_cols = ['Dist Item#', 'Net$', 'Quantity', 'Unit Rebate$', 'Start']
    missing_ppm_cols = [col for col in required_ppm_cols if col not in ppm_df.columns]
    if missing_ppm_cols:
        issues.append(f"PPM file is missing required columns: {', '.join(missing_ppm_cols)}")
    
    # Check States dataframe
    required_states_cols = ['State', 'State Code', 'Region']
    missing_states_cols = [col for col in required_states_cols if col not in states_df.columns]
    if missing_states_cols:
        issues.append(f"States file is missing required columns: {', '.join(missing_states_cols)}")
    
    return issues

def get_file_paths() -> List[Dict[str, str]]:
    """
    Get file paths for the original desktop app
    This is retained for compatibility
    """
    from data.files import get_file_paths as get_original_paths
    return get_original_paths()

def load_single_dataframe(name: str) -> Optional[pd.DataFrame]:
    """
    Load a single dataframe by name
    This is retained for compatibility
    """
    from data.files import data_manager
    return data_manager.load_dataframe(name)

def get_data_sources_status() -> List[Dict[str, str]]:
    """
    Get the status of all data sources
    This is retained for compatibility
    """
    file_info = get_file_paths()
    status_info = []
    
    for file in file_info:
        file_path = file["path"]
        status = {
            "name": file["name"],
            "description": file["description"],
            "path": file_path,
            "status": "Available" if os.path.exists(file_path) else "Missing",
            "last_modified": ""
        }
        
        if os.path.exists(file_path):
            try:
                mod_time = os.path.getmtime(file_path)
                status["last_modified"] = pd.Timestamp(mod_time, unit='s').strftime('%Y-%m-%d %H:%M')
            except:
                status["last_modified"] = "Unknown"
        
        status_info.append(status)
    
    return status_info
