"""Tests for timecode parsing utilities."""

import pytest
from stta.utils.timecode import parse_timecode, format_timecode, validate_time_range


class TestParseTimecode:
    """Test timecode parsing."""
    
    def test_seconds_only(self):
        """Test parsing seconds."""
        assert parse_timecode("45") == 45.0
        assert parse_timecode("45.5") == 45.5
        assert parse_timecode("45,5") == 45.5  # Decimal comma
    
    def test_mm_ss(self):
        """Test MM:SS format."""
        assert parse_timecode("1:30") == 90.0
        assert parse_timecode("2:05") == 125.0
        assert parse_timecode("0:45") == 45.0
    
    def test_mm_ss_mmm(self):
        """Test MM:SS.mmm format."""
        assert parse_timecode("1:30.500") == 90.5
        assert parse_timecode("2:05.250") == 125.25
    
    def test_hh_mm_ss(self):
        """Test HH:MM:SS format."""
        assert parse_timecode("1:02:30") == 3750.0
        assert parse_timecode("0:01:30") == 90.0
    
    def test_hh_mm_ss_mmm(self):
        """Test HH:MM:SS.mmm format."""
        assert parse_timecode("1:02:30.500") == 3750.5
    
    def test_numeric_input(self):
        """Test numeric input."""
        assert parse_timecode(45) == 45.0
        assert parse_timecode(45.5) == 45.5
    
    def test_invalid_formats(self):
        """Test invalid formats."""
        with pytest.raises(ValueError):
            parse_timecode("-10")  # Negative
        
        with pytest.raises(ValueError):
            parse_timecode("abc")  # Non-numeric
        
        with pytest.raises(ValueError):
            parse_timecode("")  # Empty
        
        with pytest.raises(ValueError):
            parse_timecode(None)  # None
    
    def test_invalid_ranges(self):
        """Test invalid time ranges."""
        with pytest.raises(ValueError):
            parse_timecode("5:70")  # Minutes >= 60
        
        with pytest.raises(ValueError):
            parse_timecode("1:05:70")  # Seconds >= 60


class TestFormatTimecode:
    """Test timecode formatting."""
    
    def test_format_with_hours(self):
        """Test formatting with hours."""
        assert format_timecode(90.5, include_hours=True) == "00:01:30.500"
        assert format_timecode(3750.5, include_hours=True) == "01:02:30.500"
    
    def test_format_without_hours(self):
        """Test formatting without hours."""
        assert format_timecode(90.5, include_hours=False) == "01:30.500"
    
    def test_negative_time(self):
        """Test negative time raises error."""
        with pytest.raises(ValueError):
            format_timecode(-10.0)


class TestValidateTimeRange:
    """Test time range validation."""
    
    def test_valid_range(self):
        """Test valid time range."""
        valid, reason = validate_time_range(10.0, 15.0)
        assert valid is True
        assert reason == ""
    
    def test_nonpositive_duration(self):
        """Test nonpositive duration."""
        valid, reason = validate_time_range(15.0, 10.0)
        assert valid is False
        assert reason == "nonpositive_duration"
        
        valid, reason = validate_time_range(10.0, 10.0)
        assert valid is False
        assert reason == "nonpositive_duration"
    
    def test_negative_time(self):
        """Test negative time."""
        valid, reason = validate_time_range(-5.0, 10.0)
        assert valid is False
        assert reason == "negative_time"
        
        valid, reason = validate_time_range(5.0, -10.0)
        assert valid is False
        assert reason == "negative_time"
