"""
Data Loading Module - Provides efficient, error-handled data loading capabilities
"""

import pandas as pd
import logging
from typing import Tuple, Optional, List, Dict
import os

# Import the file path manager
from data.files import get_file_paths, data_manager

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

def load_single_dataframe(name: str) -> Optional[pd.DataFrame]:
    """
    Load a single dataframe by name
    
    Args:
        name: Name of the dataframe to load (e.g., "Bill back", "PPM")
        
    Returns:
        DataFrame if successful, None if failed
    """
    return data_manager.load_dataframe(name)

def get_data_sources_status() -> List[Dict[str, str]]:
    """
    Get the status of all data sources
    
    Returns:
        List of dictionaries with data source status information
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