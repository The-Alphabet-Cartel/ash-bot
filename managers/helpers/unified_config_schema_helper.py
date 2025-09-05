# ash-thrash/managers/helpers/unified_config_schema_helper.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Schema Management Helper for UnifiedConfigManager
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-29
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VariableSchema:
    """Schema definition for environment variable validation"""
    var_type: str  # 'str', 'int', 'float', 'bool', 'list'
    default: Any
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    required: bool = False
    description: str = ""

class UnifiedConfigSchemaHelper:
    """
    Helper class for managing UnifiedConfigManager schema initialization and validation
    
    This helper extracts the complex schema management logic from the main UnifiedConfigManager
    to reduce file size while maintaining all functionality.
    """
    
    def __init__(self, config_dir: Path, config_files: Dict[str, str]):
        """
        Initialize schema helper
        
        Args:
            config_dir: Path to configuration directory
            config_files: Dictionary mapping config names to filenames
        """
        self.config_dir = config_dir
        self.config_files = config_files
    
    def initialize_schemas(self) -> Dict[str, VariableSchema]:
        """
        Initialize schemas using JSON-driven validation + essential core schemas
        
        This method:
        1. Loads essential core schemas from Python (for system startup)
        2. Dynamically loads remaining schemas from JSON validation blocks
        3. Significantly reduces code duplication and maintenance burden
        
        Returns:
            Dictionary of all VariableSchema objects
        """
        schemas = {}
        
        # ESSENTIAL CORE SCHEMAS (Python-defined for system startup)
        logger.debug("Loading essential core schemas from Python...")
        schemas.update(self.get_essential_core_schemas())
        
        # DYNAMIC JSON SCHEMAS (Loaded from validation blocks in JSON files)
        logger.debug("Loading dynamic schemas from JSON validation blocks...")
        schemas.update(self.load_json_validation_schemas())
        
        core_count = self.count_core_schemas()
        json_count = len(schemas) - core_count
        
        logger.info(f"Initialized {len(schemas)} schemas ({core_count} core + {json_count} JSON-driven)")
        return schemas
    
    def get_essential_core_schemas(self) -> Dict[str, VariableSchema]:
        """
        Essential core schemas needed for system startup (Python-defined)
        
        These are the absolute minimum schemas needed for the system to boot and connect.
        Everything else is loaded dynamically from JSON validation blocks.
        
        Returns:
            Dictionary of essential core schemas
        """
        return {
            # GLOBAL_* Ecosystem Variables (Must remain for ecosystem compatibility)
            'GLOBAL_LOG_LEVEL': VariableSchema('str', 'INFO',
                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                description='Global logging level for Ash ecosystem'),
            'GLOBAL_ENABLE_LOGGING': VariableSchema('bool', True,
                description='Global logging enablement for Ash ecosystem')
        }
    
    def count_core_schemas(self) -> int:
        """Helper method to count core schemas for logging"""
        return len(self.get_essential_core_schemas())
    
    def load_json_validation_schemas(self) -> Dict[str, VariableSchema]:
        """
        Load validation schemas dynamically from JSON configuration files
        
        This method examines all JSON configuration files for 'validation' blocks
        and converts them into VariableSchema objects, eliminating code duplication.
        
        Returns:
            Dictionary of VariableSchema objects loaded from JSON files
        """
        json_schemas = {}
        
        # Iterate through all configuration files to find validation blocks
        for config_name, config_file in self.config_files.items():
            try:
                # Load raw JSON without processing (to avoid circular dependency)
                config_path = self.config_dir / config_file
                if not config_path.exists():
                    continue
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    raw_config = json.load(f)
                
                # Extract validation schemas from this config file
                file_schemas = self.extract_validation_schemas(raw_config, config_name)
                
                if file_schemas:
                    json_schemas.update(file_schemas)
                    logger.debug(f"Loaded {len(file_schemas)} schemas from {config_name}")
                    
            except Exception as e:
                logger.warning(f"Error loading schemas from {config_name}: {e}")
                continue
        
        logger.info(f"Loaded {len(json_schemas)} schemas from JSON validation blocks")
        return json_schemas
    
    def extract_validation_schemas(self, config: Dict[str, Any], config_name: str) -> Dict[str, VariableSchema]:
        """
        Extract VariableSchema objects from a configuration's validation block
        
        Args:
            config: Raw configuration dictionary
            config_name: Name of the configuration file (for logging)
            
        Returns:
            Dictionary of VariableSchema objects from this config's validation block
        """
        schemas = {}
        
        # Look for validation blocks in the configuration
        validation_blocks = self.find_validation_blocks(config)
        
        for validation_path, validation_block in validation_blocks:
            for var_name, validation_rules in validation_block.items():
                if not isinstance(validation_rules, dict):
                    continue
                
                try:
                    # Convert JSON validation rules to VariableSchema
                    schema = self.json_to_schema(validation_rules, var_name)
                    schemas[var_name] = schema
                    
                except Exception as e:
                    logger.warning(f"Error converting {var_name} in {config_name}: {e}")
                    continue
        
        return schemas
    
    def find_validation_blocks(self, config: Dict[str, Any], path: str = "") -> List[tuple]:
        """
        Recursively find all validation blocks in a configuration
        
        Args:
            config: Configuration dictionary to search
            path: Current path in the configuration (for logging)
            
        Returns:
            List of (path, validation_block) tuples
        """
        validation_blocks = []
        
        if not isinstance(config, dict):
            return validation_blocks
        
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            
            # Skip metadata blocks
            if key.startswith('_'):
                continue
            
            if key == 'validation' and isinstance(value, dict):
                # Found a validation block
                validation_blocks.append((current_path, value))
            elif isinstance(value, dict):
                # Recursively search nested dictionaries
                validation_blocks.extend(self.find_validation_blocks(value, current_path))
        
        return validation_blocks
    
    def json_to_schema(self, json_rules: Dict[str, Any], var_name: str) -> VariableSchema:
        """
        Convert JSON validation rules to VariableSchema object
        
        Args:
            json_rules: JSON validation rules dictionary
            var_name: Variable name (for context in error messages)
            
        Returns:
            VariableSchema object
        """
        # Extract validation parameters from JSON
        var_type = json_rules.get('type', 'str')
        default = json_rules.get('default')
        choices = json_rules.get('enum') or json_rules.get('choices')
        description = json_rules.get('description', '')
        
        # JSON validation blocks are for configuration validation, not environment variable requirements
        # Only essential core schemas (defined in Python) should be truly required
        required = False  # JSON-based schemas are never required (they have defaults)
        
        # Handle range validation
        min_value = None
        max_value = None
        if 'range' in json_rules:
            range_val = json_rules['range']
            if isinstance(range_val, list) and len(range_val) >= 2:
                min_value = range_val[0] if range_val[0] is not None else None
                max_value = range_val[1] if range_val[1] is not None else None
        
        # Handle individual min/max values
        if 'min_value' in json_rules:
            min_value = json_rules['min_value']
        if 'max_value' in json_rules:
            max_value = json_rules['max_value']
        
        # Provide sensible defaults if not specified in JSON
        if default is None:
            if var_type == 'bool':
                default = False
            elif var_type == 'int':
                default = 0
            elif var_type == 'float':
                default = 0.0
            elif var_type == 'list':
                default = []
            else:  # str
                default = ''
        
        return VariableSchema(
            var_type=var_type,
            default=default,
            choices=choices,
            min_value=min_value,
            max_value=max_value,
            required=required,  # Always False for JSON-based schemas
            description=description
        )


def create_schema_helper(config_dir: Path, config_files: Dict[str, str]) -> UnifiedConfigSchemaHelper:
    """
    Factory function to create UnifiedConfigSchemaHelper instance
    
    Args:
        config_dir: Path to configuration directory
        config_files: Dictionary mapping config names to filenames
        
    Returns:
        UnifiedConfigSchemaHelper instance
    """
    return UnifiedConfigSchemaHelper(config_dir, config_files)

# Export the VariableSchema dataclass and helper class
__all__ = ['VariableSchema', 'UnifiedConfigSchemaHelper', 'create_schema_helper']