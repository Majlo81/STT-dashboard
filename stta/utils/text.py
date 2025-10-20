"""Text processing utilities."""

import re
from typing import Optional


def count_words(text: Optional[str], pattern: str = r"\w+") -> int:
    """
    Count words in text using Unicode-aware regex.
    
    Args:
        text: Input text (None or empty treated as 0 words)
        pattern: Regex pattern for word matching (default: \\w+)
        
    Returns:
        Word count (>= 0)
        
    Examples:
        >>> count_words("Hello world")
        2
        >>> count_words("Dobrý den, jak se máte?")
        5
        >>> count_words(None)
        0
    """
    if not text:
        return 0
    
    matches = re.findall(pattern, text, re.UNICODE)
    return len(matches)


def count_chars(text: Optional[str], exclude_whitespace: bool = False) -> int:
    """
    Count characters in text.
    
    Args:
        text: Input text (None or empty treated as 0)
        exclude_whitespace: If True, exclude whitespace characters
        
    Returns:
        Character count (>= 0)
    """
    if not text:
        return 0
    
    if exclude_whitespace:
        return len(re.sub(r'\s+', '', text))
    
    return len(text)


def normalize_text(text: Optional[str]) -> str:
    """
    Normalize text for consistent processing.
    
    - None → empty string
    - Strip leading/trailing whitespace
    - Collapse multiple spaces
    
    Args:
        text: Input text
        
    Returns:
        Normalized text string
    """
    if text is None:
        return ""
    
    # Strip and collapse whitespace
    normalized = re.sub(r'\s+', ' ', text.strip())
    return normalized


def is_empty_text(text: Optional[str]) -> bool:
    """
    Check if text is effectively empty.
    
    Args:
        text: Input text
        
    Returns:
        True if None, empty, or only whitespace
    """
    return not text or not text.strip()
