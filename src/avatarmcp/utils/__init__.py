"""
Utility functions for AvatarMCP server.

This module provides common utility functions used throughout the AvatarMCP
server, including error handling and input validation.
"""
from __future__ import annotations
from typing import Dict, Any, Optional, TypeVar, Type, TypeVar

T = TypeVar('T', int, float)

def create_error_response(
    error: str, 
    details: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized error response.
    
    Args:
        error: Human-readable error message
        details: Optional dictionary with additional error details
        error_code: Optional error code for programmatic error handling
        
    Returns:
        Dictionary with error information in the format:
        {
            'status': 'error',
            'error': str,
            'error_code': Optional[str],
            'details': Optional[Dict[str, Any]]
        }
    """
    response: Dict[str, Any] = {
        'status': 'error',
        'error': error
    }
    
    if error_code:
        response['error_code'] = error_code
        
    if details:
        response['details'] = details
        
    return response

def validate_range(
    value: T, 
    min_val: T, 
    max_val: T, 
    value_name: str = 'value'
) -> T:
    """Validate and clamp a numeric value within a specified range.
    
    Args:
        value: The value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        value_name: Name of the value for error messages
        
    Returns:
        The clamped value within the specified range
        
    Raises:
        ValueError: If min_val > max_val
    """
    if min_val > max_val:
        raise ValueError(f"min_val ({min_val}) cannot be greater than max_val ({max_val})")
    
    return max(min_val, min(max_val, value))

def validate_model_scale(scale: float) -> float:
    """Validate and clamp model scale value.
    
    Args:
        scale: Input scale value
        
    Returns:
        Clamped scale value between 0.1 and 10.0
    """
    return validate_range(scale, 0.1, 10.0, 'scale')

def validate_weight(weight: float) -> float:
    """Validate and clamp weight value.
    
    Args:
        weight: Input weight value (0.0 to 1.0)
        
    Returns:
        Clamped weight value between 0.0 and 1.0
    """
    return validate_range(weight, 0.0, 1.0, 'weight')

def validate_speed(speed: float) -> float:
    """Validate and clamp animation speed multiplier.
    
    Args:
        speed: Input speed multiplier value
        
    Returns:
        Clamped speed value between 0.1 and 10.0
    """
    return validate_range(speed, 0.1, 10.0, 'speed')

def validate_positive(value: float, value_name: str = 'value') -> float:
    """Validate that a value is positive.
    
    Args:
        value: The value to validate
        value_name: Name of the value for error messages
        
    Returns:
        The input value if valid
        
    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{value_name} must be positive, got {value}")
    return value

# Re-export common utilities for easier imports
__all__ = [
    'create_error_response',
    'validate_range',
    'validate_model_scale',
    'validate_weight',
    'validate_speed',
    'validate_positive'
]
