"""
Utility module for validating environment variables.
"""
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def validate_env_vars(required_vars: List[str]) -> Dict[str, Optional[str]]:
    """
    Validates that all required environment variables are present.
    
    Args:
        required_vars: A list of required environment variable names
        
    Returns:
        A dictionary mapping environment variable names to their values,
        or None if the variable is missing
        
    Raises:
        ValueError: If any required environment variables are missing
    """
    env_vars = {}
    missing_vars = []
    
    for var_name in required_vars:
        value = os.getenv(var_name)
        env_vars[var_name] = value
        
        if value is None:
            missing_vars.append(var_name)
            
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    return env_vars

def validate_chai_api_key() -> str:
    """
    Validates that the CHAI API key is present in the environment.
    
    Returns:
        The CHAI API key
        
    Raises:
        ValueError: If the CHAI API key is missing
    """
    env_vars = validate_env_vars(["CHAI_API_BEARER_TOKEN"])
    return env_vars["CHAI_API_BEARER_TOKEN"]
