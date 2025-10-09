# ash-thrash/managers/unified_config.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Unified Configuration Manager for Ash NLP Service
---
FILE VERSION: v3.1-1a-3
LAST MODIFIED: 2025-10-09
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional

# Import helper classes for reduced complexity
from managers.helpers.unified_config_schema_helper import (
    VariableSchema, 
    UnifiedConfigSchemaHelper, 
    create_schema_helper
)
from managers.helpers.unified_config_value_helper import (
    UnifiedConfigValueHelper,
    create_value_helper
)
from managers.helpers.unified_config_caching_helper import (
    UnifiedConfigCachingHelper,
    create_caching_helper
)

logger = logging.getLogger(__name__)

class UnifiedConfigManager:
    """
    Unified Configuration Manager for Ash-Thrash v3.1 with Helper File Optimization
    
    This manager consolidates:
    - JSON loading with ${VAR} substitution and enhanced defaults resolution
    - Schema validation and type conversion
    - Centralized environment variable access
    
    Clean Architecture:
    - Factory function pattern  
    - Dependency injection support
    - Fail-fast validation
    - Helper file optimization for maintainability
    
    FOUNDATION LAYER: This manager provides configuration services to ALL other managers.
    No methods should be extracted to other managers to avoid circular dependencies.
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize Unified Configuration Manager
        
        Args:
            config_dir: Directory containing JSON configuration files
        """
        self.config_dir = Path(config_dir)
        
        # Configuration file mappings
        self.config_files = {
            'logging_settings': 'logging_settings.json',
        }
        
        # Initialize helper classes for reduced complexity
        self.schema_helper = create_schema_helper(self.config_dir, self.config_files)
        self.variable_schemas = self.schema_helper.initialize_schemas()
        self.value_helper = create_value_helper(self.variable_schemas)
        
        # PHASE 3E STEP 7: Initialize caching helper for performance optimization
        caching_enabled = os.getenv('THRASH_ENABLE_CONFIG_CACHING', 'true').lower() == 'true'
        if caching_enabled:
            self.caching_helper = create_caching_helper(self.config_dir, self.config_files)
            self._caching_enabled = True
            logger.info("🚀 UnifiedConfigManager intelligent caching enabled - system-wide performance enhancement")
        else:
            self.caching_helper = None
            self._caching_enabled = False
            logger.info("UnifiedConfigManager caching disabled by configuration")
        
        # Load and validate all environment variables
        self.env_config = self._load_all_environment_variables()
        
        logger.info("UnifiedConfigManager v3.1e optimized initialized - Helper file architecture with enhanced performance")
    # ========================================================================
    
    # ========================================================================
    # ENVIRONMENT VARIABLE VALIDATION AND LOADING
    # ========================================================================
    def _load_all_environment_variables(self) -> Dict[str, Any]:
        """Load and validate all environment variables using schemas"""
        env_config = {}
        validation_errors = []
        
        logger.info("Loading and validating all environment variables...")
        
        for var_name, schema in self.variable_schemas.items():
            try:
                # Get environment value or use default
                env_value = os.getenv(var_name)
                
                if env_value is None:
                    if schema.required:
                        validation_errors.append(f"Required variable {var_name} not found")
                        continue
                    else:
                        env_config[var_name] = schema.default
                        logger.debug(f"{var_name}: Using default '{schema.default}'")
                        continue
                
                # Validate and convert the environment value
                validated_value = self._validate_and_convert(var_name, env_value)
                env_config[var_name] = validated_value
                
                logger.debug(f"{var_name}: '{env_value}' -> {validated_value}")
                
            except Exception as e:
                validation_errors.append(f"Validation error for {var_name}: {e}")
                logger.error(f"{var_name}: {e}")
        
        # Fail-fast on validation errors
        if validation_errors:
            error_msg = f"Environment variable validation failed:\n" + "\n".join(validation_errors)
            logger.error(f"{error_msg}")
            raise ValueError(error_msg)
        
        logger.info(f"Successfully loaded and validated {len(env_config)} environment variables")
        return env_config
    
    def _validate_and_convert(self, var_name: str, value: str) -> Any:
        """Validate and convert environment variable using schema"""
        schema = self.variable_schemas[var_name]
        
        try:
            # Type conversion
            if schema.var_type == 'bool':
                converted = value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            elif schema.var_type == 'int':
                converted = int(value)
            elif schema.var_type == 'float':
                converted = float(value)
            elif schema.var_type == 'list':
                converted = [item.strip() for item in value.split(',')]
            else:  # str
                converted = value
            
            # Validation
            if schema.choices and converted not in schema.choices:
                logger.error(f"Invalid choice for {var_name}: {converted} not in {schema.choices}")
                return schema.default
                
            if schema.min_value is not None and isinstance(converted, (int, float)):
                if converted < schema.min_value:
                    logger.error(f"Value too low for {var_name}: {converted} < {schema.min_value}")
                    return schema.default
                    
            if schema.max_value is not None and isinstance(converted, (int, float)):
                if converted > schema.max_value:
                    logger.error(f"Value too high for {var_name}: {converted} > {schema.max_value}")
                    return schema.default
            
            logger.debug(f"Validated {var_name}: {converted}")
            return converted
            
        except (ValueError, TypeError) as e:
            logger.error(f"Conversion error for {var_name}: {e}")
            return schema.default
    # ========================================================================
    
    # ========================================================================
    # UNIFIED ENVIRONMENT VARIABLE ACCESS (CRITICAL METHODS)
    # ========================================================================
    def get_env(self, var_name: str, default: Any = None) -> Any:
        """
        Get environment variable with schema validation, type conversion, and Docker secrets support
        CRITICAL METHOD - Used by all managers
        
        Supports Docker secrets by detecting file paths and reading file contents:
        - If env value starts with / or ./ and file exists, reads file contents
        - Common Docker secrets paths: /run/secrets/*, ./secrets/*
        """
        # Get raw environment value
        env_value = os.getenv(var_name)
        
        # If no environment value, use schema default or provided default
        if env_value is None:
            if var_name in self.variable_schemas:
                result = self.variable_schemas[var_name].default
                logger.debug(f"Using schema default for {var_name}: {result}")
                return result
            else:
                logger.debug(f"Using provided default for {var_name}: {default}")
                return default
        
        # DOCKER SECRETS SUPPORT: Check if env_value is a file path
        if isinstance(env_value, str) and (env_value.startswith('/') or env_value.startswith('./')):
            file_content = self._read_secret_file(env_value, var_name)
            if file_content is not None:
                env_value = file_content  # Replace path with file contents
                logger.info(f"🔐 Read {var_name} from Docker secret file: {os.getenv(var_name)}")
        
        # Validate and convert using schema
        if var_name in self.variable_schemas:
            return self._validate_and_convert(var_name, env_value)
        else:
            logger.warning(f"No schema found for {var_name}, returning raw value")
            return env_value
    
    def _read_secret_file(self, file_path: str, var_name: str) -> Optional[str]:
        """
        Read Docker secrets file if it exists
        
        Args:
            file_path: Path to secret file
            var_name: Variable name (for logging)
            
        Returns:
            File contents stripped of whitespace, or None if file doesn't exist
        """
        try:
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    secret = f.read().strip()
                    
                if secret:
                    logger.debug(f"✅ Successfully read {var_name} from {file_path} ({len(secret)} chars)")
                    return secret
                else:
                    logger.warning(f"⚠️ Secret file {file_path} for {var_name} is empty")
                    return None
            else:
                logger.debug(f"🔍 Secret file not found: {file_path} for {var_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to read secret file {file_path} for {var_name}: {e}")
            return None
    
    def get_env_str(self, var_name: str, default: str = '') -> str:
        """Get environment variable as string"""
        result = self.get_env(var_name, default)
        return str(result) if result is not None else default
    
    def get_env_int(self, var_name: str, default: int = 0) -> int:
        """Get environment variable as integer"""
        result = self.get_env(var_name, default)
        try:
            return int(result) if result is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert {var_name}={result} to int, using default: {default}")
            return default
    
    def get_env_float(self, var_name: str, default: float = 0.0) -> float:
        """Get environment variable as float"""
        result = self.get_env(var_name, default)
        try:
            return float(result) if result is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Cannot convert {var_name}={result} to float, using default: {default}")
            return default
    
    def get_env_bool(self, var_name: str, default: bool = False) -> bool:
        """Get environment variable as boolean"""
        result = self.get_env(var_name, default)
        if isinstance(result, bool):
            return result
        if isinstance(result, str):
            return result.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(result) if result is not None else default
    
    def get_env_list(self, var_name: str, default: List[str] = None) -> List[str]:
        """Get environment variable as list (comma-separated)"""
        if default is None:
            default = []
        result = self.get_env(var_name, ','.join(default) if default else '')
        if isinstance(result, str) and result:
            return [item.strip() for item in result.split(',')]
        return default
    # ========================================================================
    
    # ========================================================================
    # JSON CONFIGURATION METHODS WITH HELPER DELEGATION
    # ========================================================================
    def load_config_file(self, config_name: str) -> Dict[str, Any]:
        """
        Load and parse configuration file with enhanced placeholder resolution and intelligent caching
        
        Args:
            config_name: Name of configuration to load
            
        Returns:
            Processed configuration dictionary
        """
        # Use caching if enabled
        if self._caching_enabled and self.caching_helper:
            def load_function() -> Dict[str, Any]:
                return self._load_config_file_original(config_name)
            
            return self.caching_helper.get_cached_config_file(config_name, load_function)
        else:
            # Caching disabled - use original method
            return self._load_config_file_original(config_name)

    def _load_config_file_original(self, config_name: str) -> Dict[str, Any]:
        """
        Original load_config_file implementation with enhanced config file handling
        
        FIXED: Support for dynamic config names and better error handling
        """
        # Check if config_name is in the predefined mapping
        config_file = self.config_files.get(config_name)
        
        if not config_file:
            # ENHANCEMENT: Try to construct filename for dynamic configs (like test configs)
            # This allows tests and dynamic configs to work without modifying the main mapping
            if config_name.endswith('.json'):
                config_file = config_name
            else:
                config_file = f"{config_name}.json"
            
            logger.debug(f"Config '{config_name}' not in predefined mapping, trying filename: {config_file}")
        
        config_path = self.config_dir / config_file
        
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            
            # Use helper for enhanced placeholder resolution
            processed_config = self.value_helper.substitute_environment_variables(raw_config)
            
            # Apply legacy fallback for any remaining placeholders
            processed_config = self.value_helper.apply_defaults_fallback(processed_config)
            
            logger.debug(f"Successfully loaded configuration: {config_name}")
            return processed_config
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {config_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {config_file}: {e}")
            return {}
    # ========================================================================
    
    # ========================================================================
    # ENHANCED CONFIGURATION SECTION ACCESS - CLEAN API
    # ========================================================================
    def get_config_section(self, config_file: str, section_path: str = None, default: Any = None) -> Any:
        """
        Get a specific section from a configuration file with support for nested paths and intelligent caching
        
        Args:
            config_file: Name of the configuration file (e.g., 'analysis_config')
            section_path: Dot-separated path to the section (e.g., 'learning_system.thresholds')
            default: Default value to return if section not found
            
        Returns:
            The requested configuration section or default value
        """
        # Use caching if enabled
        if self._caching_enabled and self.caching_helper:
            def load_function() -> Any:
                return self._get_config_section_original(config_file, section_path, default)
            
            return self.caching_helper.get_cached_config_section(config_file, section_path, default, load_function)
        else:
            # Caching disabled - use original method
            return self._get_config_section_original(config_file, section_path, default)

    def _get_config_section_original(self, config_file: str, section_path: str = None, default: Any = None) -> Any:
        """
        Original get_config_section implementation WITH PROPER VALIDATION FOR LEAF VALUES
        """
        try:
            # Load the configuration file
            config_data = self.load_config_file(config_file)
            
            if not config_data:
                logger.warning(f"Configuration file '{config_file}' not found or empty")
                return default if default is not None else {}
            
            # If no section path specified, return entire config (but validate it)
            if section_path is None:
                return self._apply_json_validation(config_data, config_file, "root")
            
            # Navigate through the nested path
            result = config_data
            path_parts = section_path.split('.')
            
            for part in path_parts:
                if isinstance(result, dict) and part in result:
                    result = result[part]
                else:
                    logger.debug(f"Section path '{section_path}' not found in '{config_file}', using default")
                    return default if default is not None else {}
            
            # ENHANCED: Handle both dictionary sections and leaf values
            if isinstance(result, dict):
                # Dictionary section - apply validation normally
                validated_result = self._apply_json_validation(result, config_file, section_path)
                logger.debug(f"Retrieved and validated section '{section_path}' from '{config_file}'")
                return validated_result
            else:
                # Leaf value - find parent section and apply specific validation
                validated_result = self._validate_leaf_value(result, config_file, section_path)
                logger.debug(f"Retrieved and validated leaf value '{section_path}' from '{config_file}'")
                return validated_result
            
        except Exception as e:
            logger.error(f"Error getting config section '{section_path}' from '{config_file}': {e}")
            return default if default is not None else {}

    def _validate_leaf_value(self, value: Any, config_file: str, section_path: str) -> Any:
        """
        Validate a single leaf value by finding its parent section's validation rules
        
        Args:
            value: The leaf value to validate
            config_file: Source configuration file name  
            section_path: Full path to the leaf value
            
        Returns:
            Validated and type-converted leaf value
        """
        # Extract parent section path and leaf key
        path_parts = section_path.split('.')
        if len(path_parts) < 2:
            # Can't validate root level items without context
            return value
            
        parent_path = '.'.join(path_parts[:-1])
        leaf_key = path_parts[-1]
        
        logger.debug(f"Validating leaf: {leaf_key} in parent: {parent_path}")
        
        # Get validation rules from parent section
        validation_rules = self._get_validation_rules(config_file, parent_path)
        
        if not validation_rules or leaf_key not in validation_rules:
            logger.debug(f"No validation rule found for {leaf_key} in {parent_path}")
            return value
        
        # Apply validation to the leaf value
        try:
            validated_value = self._validate_json_setting(leaf_key, value, validation_rules[leaf_key])
            logger.debug(f"Leaf validation: {config_file}:{section_path} = {value} -> {validated_value} ({type(validated_value).__name__})")
            return validated_value
        except Exception as e:
            logger.warning(f"Leaf validation failed for {config_file}:{section_path}: {e}, returning original value")
            return value

    def _apply_json_validation(self, data: Any, config_file: str, section_path: str) -> Any:
        """
        Apply JSON validation rules to configuration data
        """
        logger.debug(f"_apply_json_validation called: {config_file}, {section_path}, data type: {type(data).__name__}")
        
        if not isinstance(data, dict):
            logger.debug(f"Data is not dict, returning as-is: {type(data).__name__}")
            return data
            
        # Load validation rules for this config file
        validation_rules = self._get_validation_rules(config_file, section_path)
        logger.debug(f"Validation rules retrieved: {validation_rules}")
        
        if not validation_rules:
            logger.debug(f"No validation rules found for {config_file}:{section_path}")
            return data
            
        # Apply validation to each setting in the data
        validated_data = {}
        
        for key, value in data.items():
            logger.debug(f"Processing key '{key}' with value '{value}' (type: {type(value).__name__})")
            
            # Skip metadata and validation blocks
            if key.startswith('_') or key in ('defaults', 'validation'):
                logger.debug(f"  Skipping metadata/validation key: {key}")
                validated_data[key] = value
                continue
                
            # Apply validation if rules exist for this key
            if key in validation_rules:
                logger.debug(f"  Found validation rules for key '{key}': {validation_rules[key]}")
                try:
                    validated_value = self._validate_json_setting(key, value, validation_rules[key])
                    validated_data[key] = validated_value
                    logger.info(f"Validated {config_file}:{section_path}.{key}: {value} -> {validated_value} ({type(validated_value).__name__})")
                except Exception as e:
                    logger.warning(f"Validation failed for {config_file}:{section_path}.{key}: {e}, keeping original value")
                    validated_data[key] = value
            else:
                # No validation rules - keep original value
                logger.debug(f"  No validation rules for key '{key}', keeping original")
                validated_data[key] = value
        
        logger.debug(f"Validation complete. Returning: {type(validated_data).__name__}")
        return validated_data

    def _get_validation_rules(self, config_file: str, section_path: str) -> Dict[str, Any]:
        """
        Get validation rules for a specific config section
        
        Args:
            config_file: Configuration file name
            section_path: Path to the section within the config
            
        Returns:
            Dictionary of validation rules for settings in this section
        """
        try:
            # Load the raw config file to get validation block
            config_path = self.config_dir / self.config_files.get(config_file, f"{config_file}.json")
            if not config_path.exists():
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            
            # Navigate to the section containing validation rules
            validation_section = raw_config
            if section_path != "root":
                path_parts = section_path.split('.')
                for part in path_parts:
                    if isinstance(validation_section, dict) and part in validation_section:
                        validation_section = validation_section[part]
                    else:
                        return {}
            
            # Get the validation block from this section
            if isinstance(validation_section, dict) and 'validation' in validation_section:
                return validation_section['validation']
            else:
                return {}
                
        except Exception as e:
            logger.debug(f"Error getting validation rules for {config_file}:{section_path}: {e}")
            return {}
    
    def _validate_json_setting(self, setting_name: str, value: Any, validation_rules: Dict[str, Any]) -> Any:
        """
        Validate and convert a single setting based on JSON validation rules
        
        Args:
            setting_name: Name of the setting (for error messages)
            value: Current value to validate
            validation_rules: Validation rules dictionary
            
        Returns:
            Validated and type-converted value
        """
        # Get validation parameters
        expected_type = validation_rules.get('type', 'str')
        choices = validation_rules.get('enum') or validation_rules.get('choices')
        min_value = validation_rules.get('min_value')
        max_value = validation_rules.get('max_value')
        
        # Handle range validation (can be list [min, max])
        if 'range' in validation_rules:
            range_val = validation_rules['range']
            if isinstance(range_val, list) and len(range_val) >= 2:
                min_value = range_val[0] if range_val[0] is not None else min_value
                max_value = range_val[1] if range_val[1] is not None else max_value
        
        # ENHANCED: Handle multiple types (e.g., ["string", "null"])
        if isinstance(expected_type, list):
            type_list = expected_type
        else:
            type_list = [expected_type]
        
        # Normalize type names (JSON Schema -> internal)
        type_mapping = {
            'integer': 'int',
            'boolean': 'bool', 
            'string': 'str',
            'array': 'list',
            'number': 'float',
            'null': 'null'
        }
        
        normalized_types = [type_mapping.get(t, t) for t in type_list]
        
        # Handle null/None values first
        if value is None or (isinstance(value, str) and value.lower() in ('null', 'none', '')):
            if 'null' in normalized_types:
                logger.debug(f"JSON validation applied to {setting_name}: '{value}' -> None (allowed null)")
                return None
            else:
                raise ValueError(f"Null value not allowed for {setting_name}: expected types {type_list}")
        
        # Try each allowed type until one succeeds
        conversion_errors = []
        
        for normalized_type in normalized_types:
            if normalized_type == 'null':
                continue  # Already handled above
                
            try:
                # Type conversion
                if normalized_type == 'bool':
                    if isinstance(value, str):
                        converted_value = value.lower() in ('true', '1', 'yes', 'on', 'enabled')
                    else:
                        converted_value = bool(value)
                elif normalized_type == 'int':
                    converted_value = int(float(value))  # Handle string floats like "2.0"
                elif normalized_type == 'float':
                    converted_value = float(value)
                elif normalized_type == 'list':
                    if isinstance(value, str):
                        converted_value = [item.strip() for item in value.split(',')]
                    elif isinstance(value, list):
                        converted_value = value
                    else:
                        converted_value = [str(value)]
                else:  # str
                    converted_value = str(value) if value is not None else ''
                
                # If we get here, conversion succeeded
                break
                    
            except (ValueError, TypeError) as e:
                conversion_errors.append(f"{normalized_type}: {e}")
                continue
        else:
            # No type conversion succeeded
            raise ValueError(f"Type conversion failed for {setting_name}: cannot convert '{value}' to any of {type_list}. Errors: {'; '.join(conversion_errors)}")
        
        # Validate choices
        if choices and converted_value not in choices:
            raise ValueError(f"Invalid choice for {setting_name}: '{converted_value}' not in {choices}")
        
        # Validate numeric ranges
        if min_value is not None and isinstance(converted_value, (int, float)):
            if converted_value < min_value:
                raise ValueError(f"Value too low for {setting_name}: {converted_value} < {min_value}")
        
        if max_value is not None and isinstance(converted_value, (int, float)):
            if converted_value > max_value:
                raise ValueError(f"Value too high for {setting_name}: {converted_value} > {max_value}")
        
        logger.debug(f"JSON validation applied to {setting_name}: '{value}' ({type(value).__name__}) -> {converted_value} ({type(converted_value).__name__})")
        return converted_value
    
    def get_config_section_with_env_fallback(self, config_file: str, section_path: str, 
                                           env_prefix: str = None, default: Any = None) -> Any:
        """
        Get configuration section with environment variable fallback support
        
        Args:
            config_file: Name of the configuration file
            section_path: Dot-separated path to the section
            env_prefix: Environment variable prefix (e.g., 'NLP_LEARNING_')
            default: Default value if neither config nor env vars found
            
        Returns:
            Configuration section with environment variable overrides applied
        """
        try:
            # First try to get from JSON config
            result = self.get_config_section(config_file, section_path, {})
            
            # If we got something from JSON and no env prefix specified, return it
            if result and env_prefix is None:
                return result
            
            # Apply environment variable overrides if prefix specified
            if env_prefix:
                result = dict(result) if result else {}  # Ensure we have a mutable dict
                
                # Look for environment variables with the specified prefix
                for env_var, env_value in os.environ.items():
                    if env_var.startswith(env_prefix):
                        # Convert env var name to config key
                        config_key = env_var[len(env_prefix):].lower()
                        
                        # Convert environment value to appropriate type
                        converted_value = self.value_helper.convert_value_type(env_var, env_value)
                        result[config_key] = converted_value
                        
                        logger.debug(f"Environment override: {env_var} -> {config_key} = {converted_value}")
            
            return result if result else (default if default is not None else {})
            
        except Exception as e:
            logger.error(f"Error getting config section with env fallback: {e}")
            return default if default is not None else {}
    
    def get_all_config_sections(self, config_file: str) -> Dict[str, Any]:
        """Get all top-level sections from a configuration file"""
        try:
            config_data = self.load_config_file(config_file)
            
            if not isinstance(config_data, dict):
                logger.warning(f"Config file '{config_file}' is not a dictionary")
                return {}
            
            return {
                section_name: section_data 
                for section_name, section_data in config_data.items()
                if not section_name.startswith('_')  # Skip metadata sections
            }
            
        except Exception as e:
            logger.error(f"Error getting all config sections from '{config_file}': {e}")
            return {}
    
    def has_config_section(self, config_file: str, section_path: str) -> bool:
        """Check if a configuration section exists without loading it"""
        try:
            result = self.get_config_section(config_file, section_path, None)
            return result is not None
        except Exception:
            return False
    
    def list_config_files(self) -> List[str]:
        """Get a list of all available configuration files"""
        return list(self.config_files.keys())
    
    def list_config_sections(self, config_file: str) -> List[str]:
        """Get a list of all top-level sections in a configuration file"""
        try:
            config_data = self.load_config_file(config_file)
            
            if isinstance(config_data, dict):
                return [
                    section_name 
                    for section_name in config_data.keys() 
                    if not section_name.startswith('_')
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error listing sections in '{config_file}': {e}")
            return []
    # ========================================================================

    # ========================================================================
    # BACKWARD COMPATIBILITY METHODS
    # ========================================================================
    def get_status(self) -> Dict[str, Any]:
        """Get status of UnifiedConfigManager with caching and optimization info"""
        status = {
            'status': 'operational',
            'version': 'v3.1-1a-1',
            'enhancement': 'Helper File Architecture with Enhanced Performance and Intelligent Caching',
            'config_files': len(self.config_files),
            'variables_managed': len([k for k in os.environ.keys() if k.startswith('NLP_') or k.startswith('GLOBAL_')]),
            'config_directory': str(self.config_dir),
            'architecture': 'Clean with Helper File Optimization and Intelligent Caching',
            'optimization_status': {
                'helper_files_used': True,
                'schema_helper': 'managers/helpers/unified_config_schema_helper.py',
                'value_helper': 'managers/helpers/unified_config_value_helper.py',
                'caching_helper': 'managers/helpers/unified_config_caching_helper.py' if self._caching_enabled else 'disabled',
                'main_file_reduction': '40% (1089 -> ~650 lines)',
                'extracted_functionality': ['Schema management', 'Value conversion', 'Intelligent caching', 'Documentation']
            },
            'schema_system': {
                'total_schemas': len(self.variable_schemas),
                'core_python_schemas': self.schema_helper.count_core_schemas(),
                'json_driven_schemas': len(self.variable_schemas) - self.schema_helper.count_core_schemas(),
                'helper_managed': True,
                'validation_source': 'JSON configuration files + essential core'
            }
        }
        
        # PHASE 3E STEP 7: Add cache statistics if caching is enabled
        if self._caching_enabled and self.caching_helper:
            try:
                cache_stats = self.caching_helper.get_cache_statistics()
                status['caching'] = {
                    'enabled': True,
                    'hit_rate_percent': cache_stats['hit_rate'],
                    'performance_improvement_factor': cache_stats['performance_improvement'],
                    'total_requests': cache_stats['total_requests'],
                    'cache_entries': cache_stats['current_entries'],
                    'memory_usage_mb': cache_stats['memory_usage_mb'],
                    'memory_utilization_percent': cache_stats['memory_utilization_pct'],
                    'efficiency_rating': cache_stats['cache_efficiency'],
                    'average_load_time_ms': cache_stats['average_load_time_ms'],
                    'average_cached_time_ms': cache_stats['average_cached_time_ms']
                }
                
                # Add performance summary
                if cache_stats['total_requests'] > 0:
                    status['caching']['performance_summary'] = f"Cache improving config access by {cache_stats['performance_improvement']:.1f}x " + \
                                                             f"({cache_stats['average_load_time_ms']:.1f}ms → {cache_stats['average_cached_time_ms']:.2f}ms)"
            except Exception as e:
                status['caching'] = {'enabled': True, 'status': 'error', 'error': str(e)}
        else:
            status['caching'] = {'enabled': False, 'reason': 'disabled by NLP_PERFORMANCE_ENABLE_CONFIG_CACHING=false'}
        
        return status
    # ========================================================================

    # ============================================================================
    # Cache management methods
    # ============================================================================
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get detailed cache performance statistics
        
        Returns:
            Dictionary with cache statistics or empty dict if caching disabled
        """
        if self._caching_enabled and self.caching_helper:
            return self.caching_helper.get_cache_statistics()
        else:
            return {'enabled': False}

    def clear_configuration_cache(self, pattern: str = None) -> int:
        """
        Clear configuration cache entries
        
        Args:
            pattern: Optional pattern to match cache keys (None clears all)
            
        Returns:
            Number of cache entries cleared
        """
        if self._caching_enabled and self.caching_helper:
            return self.caching_helper.clear_cache(pattern)
        else:
            return 0

    def invalidate_configuration_cache(self, config_name: str) -> int:
        """
        Invalidate cache entries for a specific configuration file
        
        Args:
            config_name: Name of configuration file to invalidate
            
        Returns:
            Number of cache entries invalidated
        """
        if self._caching_enabled and self.caching_helper:
            return self.caching_helper.invalidate_config(config_name)
        else:
            return 0
    # ========================================================================

# ============================================================================
# FACTORY FUNCTION - Clean v3.1 Architecture Compliance
# ============================================================================
def create_unified_config_manager(config_dir: str = "/app/config") -> UnifiedConfigManager:
    """
    Factory function to create UnifiedConfigManager instance
    
    Args:
        config_dir: Directory containing JSON configuration files
        
    Returns:
        UnifiedConfigManager instance with helper file optimization
    """
    return UnifiedConfigManager(config_dir)

__all__ = [
    'UnifiedConfigManager',
    'create_unified_config_manager'
]

logger.info("UnifiedConfigManager v3.1 with intelligent caching loaded")