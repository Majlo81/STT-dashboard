"""Speaker-level metrics computation."""

import pandas as pd
import numpy as np
from typing import Dict, List
from loguru import logger

from .timeline import TimelineCalculator


def compute_speaker_metrics(
    call_id: str,
    utterances_df: pd.DataFrame,
    timeline_stats: Dict
) -> List[Dict]:
    """
    Compute speaker-level metrics.
    
    Args:
        call_id: Call identifier
        utterances_df: Utterances for this call
        timeline_stats: Pre-computed timeline statistics
        
    Returns:
        List of speaker metric dictionaries
    """
    valid_df = utterances_df[utterances_df['valid_time']]
    
    if valid_df.empty:
        logger.warning(f"No valid utterances for speaker metrics: {call_id}")
        return []
    
    speakers = valid_df['speaker'].unique()
    metrics_list = []
    
    # Get apportioned and raw speaking times
    apportioned = timeline_stats['apportioned']
    raw_speaking = timeline_stats['raw_speaking']
    
    # Compute turns per speaker
    calc = TimelineCalculator()
    turns = calc.compute_turns(utterances_df)
    turns_df = pd.DataFrame(turns)
    
    L = timeline_stats['L']
    
    for speaker in speakers:
        speaker_utts = valid_df[valid_df['speaker'] == speaker]
        speaker_turns = turns_df[turns_df['speaker'] == speaker] if not turns_df.empty else pd.DataFrame()
        
        # Speaking times
        raw_time = raw_speaking.get(speaker, 0.0)
        apportioned_time = apportioned.get(speaker, 0.0)
        
        # Proportions
        raw_proportion = (raw_time / L) if L > 0 else 0.0
        apportioned_proportion = (apportioned_time / L) if L > 0 else 0.0
        
        # Turn statistics
        turn_count = len(speaker_turns)
        
        if turn_count > 0:
            avg_turn_duration = speaker_turns['duration_sec'].mean()
            max_turn_duration = speaker_turns['duration_sec'].max()
            avg_utts_per_turn = speaker_turns['utterance_count'].mean()
        else:
            avg_turn_duration = 0.0
            max_turn_duration = 0.0
            avg_utts_per_turn = 0.0
        
        # Utterance statistics
        utt_count = len(speaker_utts)
        total_words = speaker_utts['word_count'].sum()
        avg_words_per_utt = speaker_utts['word_count'].mean()
        
        # Words per minute (using apportioned time)
        wpm = (total_words / (apportioned_time / 60)) if apportioned_time > 0 else 0.0
        
        # Longest monologue (max turn duration)
        longest_monologue = max_turn_duration
        
        metrics = {
            'call_id': call_id,
            'speaker': speaker,
            
            # Speaking time
            'raw_speaking_time': raw_time,
            'apportioned_speaking_time': apportioned_time,
            'raw_proportion': raw_proportion,
            'apportioned_proportion': apportioned_proportion,
            
            # Turns
            'turn_count': turn_count,
            'avg_turn_duration': avg_turn_duration,
            'max_turn_duration': max_turn_duration,
            'longest_monologue': longest_monologue,
            'avg_utts_per_turn': avg_utts_per_turn,
            
            # Utterances
            'utterance_count': utt_count,
            'total_words': total_words,
            'avg_words_per_utt': avg_words_per_utt,
            
            # Speech rate
            'words_per_minute': wpm
        }
        
        metrics_list.append(metrics)
    
    # Compute dialog balance (Gini coefficient on apportioned times)
    gini = _compute_gini(list(apportioned.values()))
    
    # Add Gini to all speaker records (call-level stat)
    for m in metrics_list:
        m['dialog_balance_gini'] = gini
    
    logger.debug(f"Computed metrics for {len(metrics_list)} speakers in {call_id}")
    
    return metrics_list


def _compute_gini(values: List[float]) -> float:
    """
    Compute Gini coefficient for dialog balance.
    
    Gini ∈ [0, 1]:
    - 0 = perfect equality (all speakers equal time)
    - 1 = perfect inequality (one speaker dominates)
    
    Args:
        values: List of speaking times
        
    Returns:
        Gini coefficient
    """
    if not values or len(values) < 2:
        return 0.0
    
    # Remove zeros and sort
    values = [v for v in values if v > 0]
    if len(values) < 2:
        return 0.0
    
    values = sorted(values)
    n = len(values)
    
    # Gini formula: G = (2 * Σ(i * x_i)) / (n * Σ(x_i)) - (n + 1) / n
    cumsum = 0
    for i, val in enumerate(values, start=1):
        cumsum += i * val
    
    total = sum(values)
    
    gini = (2 * cumsum) / (n * total) - (n + 1) / n
    
    return gini
