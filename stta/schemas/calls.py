"""Pandera schema for calls DataFrame."""

import pandera as pa
from pandera.typing import Series
from datetime import datetime
from typing import Optional


class CallsSchema(pa.DataFrameModel):
    """
    Schema for calls.parquet
    
    One row per call with metadata.
    """
    
    # Primary key
    call_id: Series[str] = pa.Field(
        unique=True,
        nullable=False,
        description="Unique call identifier"
    )
    
    # Source tracking
    source_file: Series[str] = pa.Field(
        nullable=False,
        description="Relative path to source CSV file"
    )
    
    # Metadata from CSV (optional)
    call_start_meta: Optional[Series[datetime]] = pa.Field(
        nullable=True,
        description="Call start timestamp from metadata"
    )
    
    call_duration_meta: Optional[Series[float]] = pa.Field(
        nullable=True,
        ge=0.0,
        description="Call duration from metadata (seconds)"
    )
    
    direction: Series[str] = pa.Field(
        nullable=True,
        isin=["INBOUND", "OUTBOUND", "UNKNOWN"],
        description="Call direction"
    )
    
    agent_id: Optional[Series[str]] = pa.Field(
        nullable=True,
        description="Agent identifier"
    )
    
    agent_name: Optional[Series[str]] = pa.Field(
        nullable=True,
        description="Agent name"
    )
    
    customer_id: Optional[Series[str]] = pa.Field(
        nullable=True,
        description="Customer identifier"
    )
    
    language: Optional[Series[str]] = pa.Field(
        nullable=True,
        description="Language code (e.g., cs-CZ)"
    )
    
    # Ingestion tracking
    ingested_at: Series[datetime] = pa.Field(
        nullable=False,
        description="Timestamp of ingestion"
    )
    
    class Config:
        """Pandera configuration."""
        strict = True
        coerce = True


def validate_calls_df(df):
    """
    Validate calls DataFrame against schema.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Validated DataFrame
        
    Raises:
        pandera.errors.SchemaError: If validation fails
    """
    return CallsSchema.validate(df, lazy=True)
