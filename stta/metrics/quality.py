"""Quality and data health metrics."""

import pandas as pd
from typing import Dict, Optional
from loguru import logger


def compute_quality_metrics(
    call_id: str,
    utterances_df: pd.DataFrame,
    call_duration_meta: Optional[float],
    timeline_stats: Dict
) -> Dict:
    """
    Compute quality/health metrics for data validation.
    
    Args:
        call_id: Call identifier
        utterances_df: Utterances for this call
        call_duration_meta: Call duration from metadata (if available)
        timeline_stats: Computed timeline statistics
        
    Returns:
        Dictionary of quality metrics
    """
    total_utts = len(utterances_df)
    
    if total_utts == 0:
        logger.warning(f"No utterances for quality metrics: {call_id}")
        return _empty_quality_metrics(call_id)
    
    # Invalid timestamps
    invalid_time_count = (~utterances_df['valid_time']).sum()
    invalid_time_ratio = invalid_time_count / total_utts
    
    # Unknown speakers
    unknown_speaker_count = (utterances_df['speaker'] == 'UNKNOWN').sum()
    unknown_speaker_ratio = unknown_speaker_count / total_utts
    
    # Empty text segments
    empty_text_count = (utterances_df['text'].str.strip() == '').sum()
    empty_text_ratio = empty_text_count / total_utts
    
    # Zero-duration segments (among valid)
    valid_df = utterances_df[utterances_df['valid_time']]
    if len(valid_df) > 0:
        zero_duration_count = (valid_df['duration_sec'] == 0).sum()
        zero_duration_ratio = zero_duration_count / len(valid_df)
    else:
        zero_duration_count = 0
        zero_duration_ratio = 0.0
    
    # Metadata vs computed timeline delta
    T = timeline_stats['T']
    if call_duration_meta is not None and call_duration_meta > 0:
        metadata_timeline_delta = abs(call_duration_meta - T)
        metadata_timeline_delta_ratio = metadata_timeline_delta / call_duration_meta
    else:
        metadata_timeline_delta = None
        metadata_timeline_delta_ratio = None
    
    # Invalid reason breakdown
    invalid_reasons = utterances_df[~utterances_df['valid_time']]['invalid_reason'].value_counts().to_dict()
    
    metrics = {
        'call_id': call_id,
        
        # Counts
        'total_utterances': total_utts,
        'invalid_time_count': invalid_time_count,
        'unknown_speaker_count': unknown_speaker_count,
        'empty_text_count': empty_text_count,
        'zero_duration_count': zero_duration_count,
        
        # Ratios
        'invalid_time_ratio': invalid_time_ratio,
        'unknown_speaker_ratio': unknown_speaker_ratio,
        'empty_text_ratio': empty_text_ratio,
        'zero_duration_ratio': zero_duration_ratio,
        
        # Metadata comparison
        'call_duration_meta': call_duration_meta,
        'call_duration_computed': T,
        'metadata_timeline_delta': metadata_timeline_delta,
        'metadata_timeline_delta_ratio': metadata_timeline_delta_ratio,
        
        # Invalid reason counts
        'invalid_reason_missing_time': invalid_reasons.get('missing_time', 0),
        'invalid_reason_nonpositive_duration': invalid_reasons.get('nonpositive_duration', 0),
        'invalid_reason_negative_time': invalid_reasons.get('negative_time', 0),
        'invalid_reason_parse_error': invalid_reasons.get('parse_error', 0),
        
        # Overall quality score (0-1, higher is better)
        'quality_score': _compute_quality_score(
            invalid_time_ratio,
            unknown_speaker_ratio,
            empty_text_ratio
        )
    }
    
    logger.debug(f"Computed quality metrics for {call_id}")
    
    return metrics


def _empty_quality_metrics(call_id: str) -> Dict:
    """Return empty quality metrics structure."""
    return {
        'call_id': call_id,
        'total_utterances': 0,
        'invalid_time_count': 0,
        'unknown_speaker_count': 0,
        'empty_text_count': 0,
        'zero_duration_count': 0,
        'invalid_time_ratio': 0.0,
        'unknown_speaker_ratio': 0.0,
        'empty_text_ratio': 0.0,
        'zero_duration_ratio': 0.0,
        'call_duration_meta': None,
        'call_duration_computed': 0.0,
        'metadata_timeline_delta': None,
        'metadata_timeline_delta_ratio': None,
        'invalid_reason_missing_time': 0,
        'invalid_reason_nonpositive_duration': 0,
        'invalid_reason_negative_time': 0,
        'invalid_reason_parse_error': 0,
        'quality_score': 0.0
    }


def _compute_quality_score(
    invalid_time_ratio: float,
    unknown_speaker_ratio: float,
    empty_text_ratio: float
) -> float:
    """
    Compute overall quality score (0-1).
    
    Simple weighted average of validity ratios.
    
    Args:
        invalid_time_ratio: Ratio of invalid timestamps
        unknown_speaker_ratio: Ratio of unknown speakers
        empty_text_ratio: Ratio of empty text
        
    Returns:
        Quality score (0 = worst, 1 = best)
    """
    # Weights (can be tuned)
    w_time = 0.5
    w_speaker = 0.3
    w_text = 0.2
    
    # Invert ratios (lower is better -> higher score)
    time_score = 1.0 - invalid_time_ratio
    speaker_score = 1.0 - unknown_speaker_ratio
    text_score = 1.0 - empty_text_ratio
    
    quality = (
        w_time * time_score +
        w_speaker * speaker_score +
        w_text * text_score
    )
    
    return quality
