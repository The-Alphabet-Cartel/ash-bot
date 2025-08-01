"""
Data Management Package for Ash Bot v3.0
Handles persistent storage for custom keywords and statistics
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Data directory path
DATA_DIR = Path(__file__).parent

def ensure_data_directory():
    """Ensure data directory exists with proper permissions"""
    DATA_DIR.mkdir(exist_ok=True)
    logger.debug(f"Data directory ensured: {DATA_DIR}")

def load_json_file(filename: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Load JSON file from data directory with error handling
    
    Args:
        filename: Name of JSON file (without .json extension)
        default: Default data if file doesn't exist
        
    Returns:
        Dictionary containing loaded data
    """
    if default is None:
        default = {}
    
    file_path = DATA_DIR / f"{filename}.json"
    
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Loaded {filename}.json successfully")
                return data
        else:
            logger.info(f"File {filename}.json doesn't exist, using defaults")
            return default
            
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {filename}.json: {e}")
        return default

def save_json_file(filename: str, data: Dict[str, Any]) -> bool:
    """
    Save data to JSON file in data directory
    
    Args:
        filename: Name of JSON file (without .json extension)  
        data: Data to save
        
    Returns:
        True if successful, False otherwise
    """
    ensure_data_directory()
    file_path = DATA_DIR / f"{filename}.json"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved {filename}.json successfully")
        return True
        
    except (IOError, TypeError) as e:
        logger.error(f"Error saving {filename}.json: {e}")
        return False

def get_data_file_path(filename: str) -> Path:
    """Get full path for a data file"""
    return DATA_DIR / filename

# Initialize data directory on import
ensure_data_directory()

__all__ = [
    "DATA_DIR",
    "ensure_data_directory", 
    "load_json_file",
    "save_json_file", 
    "get_data_file_path",
]