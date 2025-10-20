"""Validation utilities."""

from typing import Any, Optional
from pathlib import Path


def validate_file_exists(path: Path, description: str = "File") -> None:
    """
    Validate that file exists.
    
    Args:
        path: File path
        description: Description for error message
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"{description} is not a file: {path}")


def validate_dir_exists(path: Path, description: str = "Directory") -> None:
    """
    Validate that directory exists.
    
    Args:
        path: Directory path
        description: Description for error message
        
    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")
    
    if not path.is_dir():
        raise ValueError(f"{description} is not a directory: {path}")


def validate_required_field(
    value: Any,
    field_name: str,
    allow_empty: bool = False
) -> None:
    """
    Validate that required field has value.
    
    Args:
        value: Field value
        field_name: Field name for error message
        allow_empty: Allow empty strings
        
    Raises:
        ValueError: If field is missing or invalid
    """
    if value is None:
        raise ValueError(f"Required field missing: {field_name}")
    
    if not allow_empty and isinstance(value, str) and not value.strip():
        raise ValueError(f"Required field empty: {field_name}")


def validate_positive_number(
    value: float,
    field_name: str,
    allow_zero: bool = True
) -> None:
    """
    Validate that number is positive.
    
    Args:
        value: Number value
        field_name: Field name for error message
        allow_zero: Allow zero value
        
    Raises:
        ValueError: If number is negative or (if not allow_zero) zero
    """
    if allow_zero:
        if value < 0:
            raise ValueError(f"{field_name} must be >= 0, got {value}")
    else:
        if value <= 0:
            raise ValueError(f"{field_name} must be > 0, got {value}")
