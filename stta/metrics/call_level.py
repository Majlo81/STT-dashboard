"""Call-level metrics computation."""

import pandas as pd
import numpy as np
from typing import Dict
from loguru import logger

from .timeline import TimelineCalculator


def compute_call_metrics(
    call_id: str,
    utterances_df: pd.DataFrame,
    timeline_stats: Dict
) -> Dict:
    """
    Compute all call-level metrics.
    
    Args:
        call_id: Call identifier
        utterances_df: Utterances for this call
        timeline_stats: Pre-computed timeline statistics
        
    Returns:
        Dictionary of call-level metrics
    """
    valid_df = utterances_df[utterances_df['valid_time']]
    
    # Basic counts
    total_utterances = len(utterances_df)
    valid_utterances = len(valid_df)
    invalid_utterances = total_utterances - valid_utterances
    
    # Timeline metrics (from timeline_stats)
    T = timeline_stats['T']
    L = timeline_stats['L']
    O = timeline_stats['O']
    S = timeline_stats['S']
    
    # Derived ratios
    silence_ratio = S / T if T > 0 else 0.0
    speech_ratio = L / T if T > 0 else 0.0
    overlap_ratio = O / T if T > 0 else 0.0
    speech_to_silence_ratio = L / S if S > 0 else float('inf')
    
    # Utterance statistics
    if valid_utterances > 0:
        avg_utt_duration = valid_df['duration_sec'].mean()
        median_utt_duration = valid_df['duration_sec'].median()
        p95_utt_duration = valid_df['duration_sec'].quantile(0.95)
        
        avg_utt_words = valid_df['word_count'].mean()
        median_utt_words = valid_df['word_count'].median()
        total_words = valid_df['word_count'].sum()
    else:
        avg_utt_duration = 0.0
        median_utt_duration = 0.0
        p95_utt_duration = 0.0
        avg_utt_words = 0.0
        median_utt_words = 0.0
        total_words = 0
    
    # Compute gaps
    calc = TimelineCalculator()
    gaps = calc.compute_gaps(utterances_df)
    
    if gaps:
        gap_values = [g['gap_sec'] for g in gaps]
        avg_gap = np.mean(gap_values)
        median_gap = np.median(gap_values)
        p95_gap = np.percentile(gap_values, 95)
        negative_gaps = sum(1 for g in gap_values if g < 0)
    else:
        avg_gap = 0.0
        median_gap = 0.0
        p95_gap = 0.0
        negative_gaps = 0
    
    # Compute turns and switches
    turns = calc.compute_turns(utterances_df)
    total_turns = len(turns)
    
    # Count speaker switches (turn boundaries)
    speaker_switches = max(0, total_turns - 1)
    switches_per_min = (speaker_switches / (T / 60)) if T > 0 else 0.0
    
    # Count interruptions (speaker change with overlap)
    interruptions = _count_interruptions(utterances_df)
    
    metrics = {
        'call_id': call_id,
        
        # Timeline
        'total_duration': T,
        'speech_time': L,
        'silence_time': S,
        'overlap_time': O,
        
        # Ratios
        'silence_ratio': silence_ratio,
        'speech_ratio': speech_ratio,
        'overlap_ratio': overlap_ratio,
        'speech_to_silence_ratio': speech_to_silence_ratio,
        
        # Utterances
        'total_utterances': total_utterances,
        'valid_utterances': valid_utterances,
        'invalid_utterances': invalid_utterances,
        'avg_utt_duration': avg_utt_duration,
        'median_utt_duration': median_utt_duration,
        'p95_utt_duration': p95_utt_duration,
        
        # Words
        'total_words': total_words,
        'avg_utt_words': avg_utt_words,
        'median_utt_words': median_utt_words,
        
        # Gaps
        'avg_gap': avg_gap,
        'median_gap': median_gap,
        'p95_gap': p95_gap,
        'negative_gaps_count': negative_gaps,
        
        # Turns
        'total_turns': total_turns,
        'speaker_switches': speaker_switches,
        'switches_per_min': switches_per_min,
        
        # Interruptions
        'interruptions_total': interruptions['total'],
        'interruptions_by_agent': interruptions['AGENT'],
        'interruptions_by_customer': interruptions['CUSTOMER'],
        'interruptions_by_other': interruptions['OTHER']
    }
    
    logger.debug(f"Computed call metrics for {call_id}")
    
    return metrics


def _count_interruptions(utterances_df: pd.DataFrame) -> Dict[str, int]:
    """
    Count interruptions by speaker.
    
    An interruption occurs when speaker Y starts before speaker X finishes.
    
    Args:
        utterances_df: Sorted utterances
        
    Returns:
        Dictionary with counts by speaker
    """
    valid_df = utterances_df[utterances_df['valid_time']].copy()
    valid_df = valid_df.sort_values('start_sec').reset_index(drop=True)
    
    interruptions = {
        'total': 0,
        'AGENT': 0,
        'CUSTOMER': 0,
        'OTHER': 0,
        'UNKNOWN': 0
    }
    
    for i in range(len(valid_df) - 1):
        curr = valid_df.iloc[i]
        next_utt = valid_df.iloc[i + 1]
        
        # Interruption: next starts before curr ends AND different speaker
        if (next_utt['start_sec'] < curr['end_sec'] and 
            next_utt['speaker'] != curr['speaker']):
            
            interrupting_speaker = next_utt['speaker']
            interruptions['total'] += 1
            
            if interrupting_speaker in interruptions:
                interruptions[interrupting_speaker] += 1
    
    return interruptions
