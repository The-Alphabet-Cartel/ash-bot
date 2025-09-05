# ash-thrash/managers/helpers/unified_config_value_helper.py
"""
Ash-Thrash: Crisis Detection Testing for The Alphabet Cartel Discord Community
********************************************************************************
Value Conversion Helper for UnifiedConfigManager
---
FILE VERSION: v3.1-1a-1
LAST MODIFIED: 2025-08-29
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import os
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class UnifiedConfigValueHelper:
    """
    Helper class for managing value conversion and placeholder resolution in UnifiedConfigManager
    
    This helper extracts the complex value conversion logic from the main UnifiedConfigManager
    to reduce file size while maintaining all functionality.
    """
    
    def __init__(self, variable_schemas: Dict[str, Any]):
        """
        Initialize value helper
        
        Args:
            variable_schemas: Dictionary of VariableSchema objects for validation
        """
        self.variable_schemas = variable_schemas
        self.env_override_pattern = re.compile(r'\$\{([^}]+)\}')
    
    def convert_value_type(self, env_var: str, value: str) -> str:
        """
        Convert string value to appropriate type for substitution
        
        Args:
            env_var: Environment variable name (for logging)
            value: String value to convert
            
        Returns:
            String representation of converted value
        """
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            result = str(value.lower() == 'true')
            logger.debug(f"   {env_var} -> Boolean conversion: {value} -> {result}")
            return result
        
        # Numeric conversion
        if value.replace('.', '').replace('-', '').isdigit():
            try:
                if '.' in value:
                    result = str(float(value))
                    logger.debug(f"   {env_var} -> Float conversion: {value} -> {result}")
                    return result
                else:
                    result = str(int(value))
                    logger.debug(f"   {env_var} -> Int conversion: {value} -> {result}")
                    return result
            except ValueError:
                logger.debug(f"   {env_var} -> String (conversion failed): {value}")
                return value
        
        # String (no conversion)
        logger.debug(f"   {env_var} -> String (no conversion): {value}")
        return value
    
    def apply_type_conversion(self, value: Any) -> Any:
        """
        Apply type conversion to default values
        
        Args:
            value: Value to convert
            
        Returns:
            Type-converted value
        """
        if isinstance(value, str):
            # Try to convert string defaults to appropriate types
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            elif value.replace('.', '').replace('-', '').isdigit():
                try:
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
                except ValueError:
                    return value
            else:
                return value
        else:
            # Return non-string values as-is
            return value
    
    def find_default_value(self, env_var: str, defaults_context: Dict[str, Any]) -> Any:
        """
        Find default value for environment variable in JSON defaults context
        
        This method searches through the defaults context to find a matching default value
        for the given environment variable.
        
        Args:
            env_var: Environment variable name
            defaults_context: Current defaults context dictionary
            
        Returns:
            Default value if found, None otherwise
        """
        if not isinstance(defaults_context, dict):
            return None
        
        # Direct key lookup (most common case)
        if env_var in defaults_context:
            logger.debug(f"   Direct match for {env_var} in defaults")
            return defaults_context[env_var]
        
        # Search through nested structures
        for key, value in defaults_context.items():
            # Skip metadata and other non-data keys
            if key.startswith('_') or key == 'defaults':
                continue
                
            if isinstance(value, dict):
                # Recursive search in nested dictionaries
                found = self.find_default_value(env_var, value)
                if found is not None:
                    logger.debug(f"   Nested match for {env_var} in defaults.{key}")
                    return found
            
            # Pattern matching for common variable patterns
            # Convert env var name to potential JSON key patterns
            simplified_key = self.env_var_to_json_key(env_var)
            if key == simplified_key:
                logger.debug(f"   Pattern match for {env_var} -> {key}")
                return value
        
        return None
    
    def env_var_to_json_key(self, env_var: str) -> str:
        """
        Convert environment variable name to potential JSON key
        
        Args:
            env_var: Environment variable name
            
        Returns:
            Potential JSON key name
        """
        # Remove common prefixes
        key = env_var.replace('THRASH_', '').replace('CONFIG_', '').replace('GLOBAL_', '')
        
        # Convert to lowercase with underscores
        key = key.lower()
        
        # Common pattern mappings
        pattern_mappings = {}
        
        return pattern_mappings.get(key, key)
    
    def substitute_environment_variables(self, value: Any, defaults_context: Dict[str, Any] = None) -> Any:
        """
        Substitute environment variables with immediate defaults fallback
        
        ENHANCED RESOLUTION ORDER:
        1. Environment variables (os.getenv())
        2. JSON defaults block (when available)
        3. Schema defaults (when available)
        4. Original placeholder (only if no resolution possible)
        
        Args:
            value: Value to process (can be string, dict, list, or primitive)
            defaults_context: Current defaults context for this configuration section
            
        Returns:
            Processed value with placeholders resolved
        """
        if isinstance(value, str):
            def replace_env_var(match):
                env_var = match.group(1)
                
                # Step 1: Try environment variable first
                env_value = os.getenv(env_var)
                if env_value is not None:
                    return self.convert_value_type(env_var, env_value)
                
                # Step 2: Try JSON defaults context
                if defaults_context:
                    defaults_value = self.find_default_value(env_var, defaults_context)
                    if defaults_value is not None:
                        return str(defaults_value)  # Convert to string for substitution
                
                # Step 3: Try schema defaults
                if env_var in self.variable_schemas:
                    schema_default = self.variable_schemas[env_var].default
                    return str(schema_default)
                
                # Step 4: No resolution possible - warn and keep placeholder
                logger.warning(f"Unresolved placeholder: ${{{env_var}}}")
                return match.group(0)  # Return original placeholder
            
            # Apply substitution with enhanced resolution
            result = self.env_override_pattern.sub(replace_env_var, value)
            return result
            
        elif isinstance(value, dict):
            # Process dictionaries recursively, passing defaults context
            # Skip _metadata blocks to avoid processing documentation examples
            result = {}
            current_defaults = defaults_context or value.get('defaults', {})
            
            for k, v in value.items():
                if k.startswith('_'):
                    # Skip metadata blocks (they contain documentation and examples, not real config)
                    result[k] = v  # Keep metadata as-is without processing
                elif k == 'defaults':
                    # Keep defaults block as-is for reference
                    result[k] = v
                else:
                    # Get defaults for this key if available
                    key_defaults = current_defaults.get(k, {}) if isinstance(current_defaults, dict) else {}
                    result[k] = self.substitute_environment_variables(v, key_defaults)
            return result
            
        elif isinstance(value, list):
            # Process lists recursively
            return [self.substitute_environment_variables(item, defaults_context) for item in value]
            
        else:
            # Return primitive values as-is
            return value
    
    def apply_defaults_fallback(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy defaults fallback - now mostly redundant
        
        This method is kept for backward compatibility but most placeholder resolution
        now happens in substitute_environment_variables() with immediate defaults lookup.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with any remaining placeholders resolved
        """
        defaults = config.get('defaults', {})
        if not defaults:
            return config
        
        def apply_legacy_defaults_recursive(main_value: Any, defaults_value: Any) -> Any:
            if isinstance(main_value, str) and main_value.startswith('${') and main_value.endswith('}'):
                # This is still an unresolved placeholder - use the default
                return self.apply_type_conversion(defaults_value)
            elif isinstance(main_value, dict) and isinstance(defaults_value, dict):
                # Recursively apply defaults to nested dictionaries
                result = {}
                for key in main_value:
                    if key in defaults_value:
                        result[key] = apply_legacy_defaults_recursive(main_value[key], defaults_value[key])
                    else:
                        result[key] = main_value[key]
                # Add any defaults that aren't in main config
                for key in defaults_value:
                    if key not in result:
                        result[key] = self.apply_type_conversion(defaults_value[key])
                return result
            elif isinstance(main_value, list) and isinstance(defaults_value, list):
                # For lists, prefer main_value if it exists, otherwise use defaults
                return main_value if main_value else defaults_value
            else:
                # Use main value if it's not a placeholder
                return main_value
        
        # Apply legacy defaults to the main configuration sections
        result = {}
        for key, value in config.items():
            if key == 'defaults':
                # Keep the defaults block for reference
                result[key] = value
            elif key in defaults:
                # Apply defaults to this section
                result[key] = apply_legacy_defaults_recursive(value, defaults[key])
            else:
                # No defaults for this section, keep as-is
                result[key] = value
        
        return result


def create_value_helper(variable_schemas: Dict[str, Any]) -> UnifiedConfigValueHelper:
    """
    Factory function to create UnifiedConfigValueHelper instance
    
    Args:
        variable_schemas: Dictionary of VariableSchema objects for validation
        
    Returns:
        UnifiedConfigValueHelper instance
    """
    return UnifiedConfigValueHelper(variable_schemas)

# Export the helper class
__all__ = ['UnifiedConfigValueHelper', 'create_value_helper']