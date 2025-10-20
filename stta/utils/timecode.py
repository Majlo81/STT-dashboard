"""
Timecode parsing utilities.

Supports formats:
- SS
- SS.mmm
- MM:SS
- MM:SS.mmm
- HH:MM:SS
- HH:MM:SS.mmm

Handles decimal comma → dot conversion.
Returns float seconds or raises ValueError for invalid input.
"""

import re
from typing import Union


def parse_timecode(value: Union[str, int, float]) -> float:
    """
    Parse timecode string to seconds (float).
    
    Args:
        value: Timecode in supported format, or numeric seconds
        
    Returns:
        Float seconds (>= 0.0)
        
    Raises:
        ValueError: If format is invalid or time is negative
        
    Examples:
        >>> parse_timecode("45.5")
        45.5
        >>> parse_timecode("1:30")
        90.0
        >>> parse_timecode("1:02:30.500")
        3750.5
    """
    # Handle None
    if value is None:
        raise ValueError("Timecode cannot be None")
    
    # Handle numeric types
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds < 0:
            raise ValueError(f"Negative time not allowed: {seconds}")
        return seconds
    
    # Handle string
    if not isinstance(value, str):
        raise ValueError(f"Invalid timecode type: {type(value)}")
    
    # Clean string
    value = value.strip()
    if not value:
        raise ValueError("Empty timecode string")
    
    # Replace decimal comma with dot
    value = value.replace(",", ".")
    
    # Pattern: HH:MM:SS.mmm or MM:SS.mmm or SS.mmm or SS
    # Optional negative sign (will be rejected later)
    pattern = r'^(-?)(?:(\d+):)?(?:(\d+):)?(\d+)(?:\.(\d+))?$'
    
    match = re.match(pattern, value)
    if not match:
        raise ValueError(f"Invalid timecode format: {value}")
    
    sign, h, m, s, ms = match.groups()
    
    # Check for negative
    if sign == '-':
        raise ValueError(f"Negative time not allowed: {value}")
    
    # Parse components
    hours = int(h) if h else 0
    minutes = int(m) if m else 0
    seconds_int = int(s)
    
    # Handle fractional seconds (milliseconds or more precision)
    if ms:
        # Pad or truncate to 3 digits for milliseconds
        ms_padded = (ms + "000")[:3]
        milliseconds = int(ms_padded)
    else:
        milliseconds = 0
    
    # Calculate total seconds
    total_seconds = (
        hours * 3600 +
        minutes * 60 +
        seconds_int +
        milliseconds / 1000.0
    )
    
    # Validate ranges
    if minutes >= 60:
        raise ValueError(f"Minutes must be < 60: {value}")
    if seconds_int >= 60:
        raise ValueError(f"Seconds must be < 60: {value}")
    
    return total_seconds


def format_timecode(seconds: float, include_hours: bool = True) -> str:
    """
    Format seconds as timecode string.
    
    Args:
        seconds: Time in seconds
        include_hours: Include hours component even if zero
        
    Returns:
        Formatted timecode string (HH:MM:SS.mmm or MM:SS.mmm)
        
    Examples:
        >>> format_timecode(90.5)
        '00:01:30.500'
        >>> format_timecode(90.5, include_hours=False)
        '01:30.500'
    """
    if seconds < 0:
        raise ValueError("Cannot format negative time")
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if include_hours or hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def validate_time_range(start: float, end: float) -> tuple[bool, str]:
    """
    Validate time range is valid.
    
    Args:
        start: Start time in seconds
        end: End time in seconds
        
    Returns:
        (is_valid, reason) tuple
        
    Examples:
        >>> validate_time_range(10.0, 15.0)
        (True, '')
        >>> validate_time_range(15.0, 10.0)
        (False, 'nonpositive_duration')
    """
    if start < 0 or end < 0:
        return False, "negative_time"
    
    if end <= start:
        return False, "nonpositive_duration"
    
    return True, ""
