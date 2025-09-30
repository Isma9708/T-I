"""
Data File Management Module - Handles access to data sources
Provides centralized path management with error handling and configuration options
"""

import os
import logging
from typing import List, Dict, Union, Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSourceConfig:
    """Centralized configuration for data sources"""
    
    def __init__(self):
        """Initialize with default configuration"""
        self.user = os.environ.get("USERNAME", "")
        # Primary path - OneDrive location
        self.primary_path = fr"C:\Users\{self.user}\OneDrive - Constellation Brands\T&I Dev - PPM"
        # Backup path - local folder in case OneDrive is not available
        self.backup_path = fr"C:\Users\{self.user}\Documents\T&I Dev - PPM"
        # Flag to use backup path if primary not available
        self.use_backup_if_needed = True
        # Current active path
        self.active_path = self._determine_active_path()
    
    def _determine_active_path(self) -> str:
        """Determine which path to use based on availability"""
        if os.path.exists(self.primary_path):
            logger.info(f"Using primary data path: {self.primary_path}")
            return self.primary_path
            
        if self.use_backup_if_needed and os.path.exists(self.backup_path):
            logger.warning(f"Primary path not found. Using backup path: {self.backup_path}")
            return self.backup_path
            
        logger.warning("No valid data path found. Using primary path as fallback.")
        return self.primary_path
    
    def get_base_path(self) -> str:
        """Get the currently active base path"""
        return self.active_path
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if a file exists and is accessible"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
            
        if not os.access(file_path, os.R_OK):
            logger.error(f"File not readable: {file_path}")
            return False
            
        return True


class DataFileManager:
    """Manager for data file access with error handling and validation"""
    
    def __init__(self):
        """Initialize with configuration"""
        self.config = DataSourceConfig()
        self.file_info = self._define_file_info()
        
    def _define_file_info(self) -> List[Dict[str, str]]:
        """Define information about data files"""
        base_path = self.config.get_base_path()
        return [
            {
                "name": "Bill back",
                "description": "CBI Regions Price Support",
                "path": os.path.join(base_path, "Bill back", "CBI Regions Price Support (DP DA CQD NC) - (SM DN NC) - BM Reporting Apr-May-Jun 2025 - 072025 (1).xlsx"),
                "sheet": "Data DE DP DQ NC"
            },
            {
                "name": "Item x Ref",
                "description": "item x ref",
                "path": os.path.join(base_path, "Item x Ref", "item x ref.xlsx"),
                "sheet": 0
            },
            {
                "name": "PPM",
                "description": "PPM",
                "path": os.path.join(base_path, "PPM", "PPM.xlsx"),
                "sheet": "Sheet1"
            },
            {
                "name": "States",
                "description": "States",
                "path": os.path.join(base_path, "States", "States.xlsx"),
                "sheet": "States"
            }
        ]
    
    def get_file_paths(self) -> List[Dict[str, str]]:
        """Get information about all data files"""
        return self.file_info
    
    def get_file_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get file information by name"""
        for file in self.file_info:
            if file["name"].lower() == name.lower():
                return file
        return None
    
    def load_dataframe(self, name: str) -> Optional[pd.DataFrame]:
        """Load a dataframe by file name with error handling"""
        file_info = self.get_file_by_name(name)
        if not file_info:
            logger.error(f"Unknown data source: {name}")
            return None
            
        file_path = file_info["path"]
        if not self.config.validate_file(file_path):
            return None
            
        try:
            logger.info(f"Loading dataframe from {name}")
            return pd.read_excel(file_path, sheet_name=file_info["sheet"])
        except Exception as e:
            logger.error(f"Error loading {name}: {str(e)}")
            return None


# Create global instances for easy access
data_config = DataSourceConfig()
data_manager = DataFileManager()

def get_base_path() -> str:
    """Get the base directory path based on current user"""
    return data_config.get_base_path()

def get_file_paths() -> List[Dict[str, str]]:
    """Get all file information"""
    return data_manager.get_file_paths()

def load_dataframe(name: str) -> Optional[pd.DataFrame]:
    """Convenience function to load a dataframe by name"""
    return data_manager.load_dataframe(name)