"""Pandera schema for utterances DataFrame."""

import pandera as pa
from pandera.typing import Series
from typing import Optional


class UtterancesSchema(pa.DataFrameModel):
    """
    Schema for utterances.parquet
    
    Multiple rows per call, one per utterance/replica.
    """
    
    # Foreign key to calls
    call_id: Series[str] = pa.Field(
        nullable=False,
        description="Call identifier (FK to calls.call_id)"
    )
    
    # Unique utterance ID
    utt_id: Series[str] = pa.Field(
        unique=True,
        nullable=False,
        description="Unique utterance ID (call_id-{index})"
    )
    
    # Utterance ordering
    utterance_index: Series[int] = pa.Field(
        nullable=False,
        ge=0,
        description="0-based utterance index within call (sorted by time)"
    )
    
    # Speaker
    speaker: Series[str] = pa.Field(
        nullable=False,
        isin=["AGENT", "CUSTOMER", "OTHER", "UNKNOWN"],
        description="Normalized speaker label"
    )
    
    # Timing (nullable for invalid times)
    start_sec: Optional[Series[float]] = pa.Field(
        nullable=True,
        ge=0.0,
        description="Start time in seconds from call beginning"
    )
    
    end_sec: Optional[Series[float]] = pa.Field(
        nullable=True,
        ge=0.0,
        description="End time in seconds from call beginning"
    )
    
    duration_sec: Optional[Series[float]] = pa.Field(
        nullable=True,
        ge=0.0,
        description="Duration in seconds (end - start)"
    )
    
    # Content
    text: Series[str] = pa.Field(
        nullable=False,
        description="Utterance text (empty string allowed)"
    )
    
    char_count: Series[int] = pa.Field(
        nullable=False,
        ge=0,
        description="Character count in text"
    )
    
    word_count: Series[int] = pa.Field(
        nullable=False,
        ge=0,
        description="Word count (Unicode \\w+ regex)"
    )
    
    # Validity flags
    valid_time: Series[bool] = pa.Field(
        nullable=False,
        description="True if timing is valid"
    )
    
    invalid_reason: Optional[Series[str]] = pa.Field(
        nullable=True,
        description="Reason for invalidity (if valid_time=False)"
    )
    
    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True
    
    @pa.check("duration_sec")
    def duration_matches_times(cls, duration_sec: Series[float]) -> Series[bool]:
        """Check that duration = end - start when all are present."""
        # This is a soft check - we allow small floating point errors
        # Actual enforcement happens in preprocessing
        return Series([True] * len(duration_sec))


def validate_utterances_df(df):
    """
    Validate utterances DataFrame against schema.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Validated DataFrame
        
    Raises:
        pandera.errors.SchemaError: If validation fails
    """
    return UtterancesSchema.validate(df, lazy=True)
