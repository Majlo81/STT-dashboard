"""Logging configuration using loguru."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def setup_logging(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "30 days",
    compression: str = "zip"
) -> None:
    """
    Configure loguru logger.
    
    Args:
        log_file: Path to log file (if None, only stderr)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        rotation: Log rotation size
        retention: How long to keep old logs
        compression: Compression format for rotated logs
    """
    # Remove default handler
    logger.remove()
    
    # Console handler (stderr) with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression
        )
    
    logger.info(f"Logging initialized at level {level}")
    if log_file:
        logger.info(f"Log file: {log_file}")


def get_logger(name: str):
    """
    Get logger instance with context.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
