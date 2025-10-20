"""Parquet writer with schema versioning."""

import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Dict, Any


def write_parquet(
    df: pd.DataFrame,
    output_path: Path,
    schema_version: str = "1.0.0",
    metadata: Dict[str, Any] = None
) -> None:
    """
    Write DataFrame to Parquet with metadata.
    
    Args:
        df: DataFrame to write
        output_path: Output file path
        schema_version: Schema version string
        metadata: Additional metadata to embed
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare metadata
    parquet_metadata = {
        'schema_version': schema_version,
        'row_count': str(len(df))
    }
    
    if metadata:
        parquet_metadata.update({
            k: str(v) for k, v in metadata.items()
        })
    
    # Write with pyarrow engine
    df.to_parquet(
        output_path,
        engine='pyarrow',
        compression='snappy',
        index=False,
        # Note: pyarrow doesn't support custom metadata directly via to_parquet
        # For full metadata support, would need to use pyarrow.parquet API
    )
    
    logger.info(f"Wrote {len(df)} rows to {output_path}")
    logger.debug(f"Schema version: {schema_version}")


def read_parquet(input_path: Path) -> pd.DataFrame:
    """
    Read Parquet file.
    
    Args:
        input_path: Input file path
        
    Returns:
        DataFrame
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {input_path}")
    
    df = pd.read_parquet(input_path, engine='pyarrow')
    
    logger.info(f"Read {len(df)} rows from {input_path}")
    
    return df
