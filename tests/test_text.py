"""Tests for text processing utilities."""

import pytest
from stta.utils.text import count_words, count_chars, normalize_text, is_empty_text


class TestCountWords:
    """Test word counting."""
    
    def test_simple_text(self):
        """Test simple word counting."""
        assert count_words("Hello world") == 2
        assert count_words("one two three") == 3
    
    def test_czech_text(self):
        """Test Czech text."""
        assert count_words("Dobrý den, jak se máte?") == 5
    
    def test_empty_text(self):
        """Test empty text."""
        assert count_words("") == 0
        assert count_words(None) == 0
        assert count_words("   ") == 0
    
    def test_punctuation(self):
        """Test text with punctuation."""
        assert count_words("Hello, world!") == 2


class TestCountChars:
    """Test character counting."""
    
    def test_simple_text(self):
        """Test simple character counting."""
        assert count_chars("Hello") == 5
        assert count_chars("Hello world") == 11  # includes space
    
    def test_exclude_whitespace(self):
        """Test excluding whitespace."""
        assert count_chars("Hello world", exclude_whitespace=True) == 10
    
    def test_empty_text(self):
        """Test empty text."""
        assert count_chars("") == 0
        assert count_chars(None) == 0


class TestNormalizeText:
    """Test text normalization."""
    
    def test_strip_whitespace(self):
        """Test stripping whitespace."""
        assert normalize_text("  hello  ") == "hello"
    
    def test_collapse_spaces(self):
        """Test collapsing multiple spaces."""
        assert normalize_text("hello    world") == "hello world"
    
    def test_none_input(self):
        """Test None input."""
        assert normalize_text(None) == ""


class TestIsEmptyText:
    """Test empty text detection."""
    
    def test_empty_strings(self):
        """Test empty strings."""
        assert is_empty_text("") is True
        assert is_empty_text("   ") is True
        assert is_empty_text(None) is True
    
    def test_non_empty(self):
        """Test non-empty text."""
        assert is_empty_text("hello") is False
        assert is_empty_text("  hello  ") is False
