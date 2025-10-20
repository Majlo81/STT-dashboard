"""Interaction pattern metrics for call analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from loguru import logger


def compute_interaction_metrics(utterances_df: pd.DataFrame, call_id: str) -> Dict[str, Any]:
    """
    Compute interaction pattern metrics.
    
    Args:
        utterances_df: DataFrame with utterances for a single call
        call_id: Unique call identifier
        
    Returns:
        Dictionary with interaction metrics
    """
    
    valid_utts = utterances_df[utterances_df['valid_time']].copy()
    
    if len(valid_utts) < 2:
        return _empty_interaction_metrics(call_id)
    
    # Sort by start time
    valid_utts = valid_utts.sort_values('start_sec').reset_index(drop=True)
    
    # 1. Calculate gaps between utterances
    gaps = []
    for i in range(len(valid_utts) - 1):
        gap = valid_utts.iloc[i + 1]['start_sec'] - valid_utts.iloc[i]['end_sec']
        gaps.append(gap)
    
    # 2. Long pauses (> 3 seconds)
    long_pauses = [g for g in gaps if g > 3.0]
    long_pauses_count = len(long_pauses)
    
    # 3. Interruptions (negative or very small gaps)
    interruptions = [g for g in gaps if g < 0.5]
    interruption_rate = len(interruptions) / len(gaps) if len(gaps) > 0 else 0.0
    
    # 4. Response delays per speaker
    agent_response_delays = []
    customer_response_delays = []
    
    for i in range(len(valid_utts) - 1):
        current_speaker = valid_utts.iloc[i]['speaker']
        next_speaker = valid_utts.iloc[i + 1]['speaker']
        
        if current_speaker != next_speaker:  # Speaker switch
            gap = valid_utts.iloc[i + 1]['start_sec'] - valid_utts.iloc[i]['end_sec']
            
            if next_speaker == 'AGENT':
                agent_response_delays.append(gap)
            elif next_speaker == 'CUSTOMER':
                customer_response_delays.append(gap)
    
    # 5. Monologue detection (consecutive utterances by same speaker)
    monologue_segments = 0
    current_speaker = None
    consecutive_count = 0
    
    for _, row in valid_utts.iterrows():
        if row['speaker'] == current_speaker:
            consecutive_count += 1
        else:
            if consecutive_count >= 3:  # 3+ consecutive = monologue
                monologue_segments += 1
            current_speaker = row['speaker']
            consecutive_count = 1
    
    # Check last segment
    if consecutive_count >= 3:
        monologue_segments += 1
    
    # 6. Turn-taking balance
    speaker_turns = valid_utts.groupby('speaker').size().to_dict()
    agent_turns = speaker_turns.get('AGENT', 0)
    customer_turns = speaker_turns.get('CUSTOMER', 0)
    
    total_turns = agent_turns + customer_turns
    turn_balance = min(agent_turns, customer_turns) / max(agent_turns, customer_turns) if max(agent_turns, customer_turns) > 0 else 0.0
    
    return {
        'call_id': call_id,
        
        # Gap statistics
        'avg_gap': np.mean(gaps) if len(gaps) > 0 else 0.0,
        'median_gap': np.median(gaps) if len(gaps) > 0 else 0.0,
        'std_gap': np.std(gaps) if len(gaps) > 0 else 0.0,
        'long_pauses_count': long_pauses_count,
        'long_pauses_rate': long_pauses_count / len(gaps) if len(gaps) > 0 else 0.0,
        
        # Interruptions
        'interruptions_count': len(interruptions),
        'interruption_rate': interruption_rate,
        
        # Response times
        'agent_avg_response_delay': np.mean(agent_response_delays) if len(agent_response_delays) > 0 else 0.0,
        'customer_avg_response_delay': np.mean(customer_response_delays) if len(customer_response_delays) > 0 else 0.0,
        'agent_median_response_delay': np.median(agent_response_delays) if len(agent_response_delays) > 0 else 0.0,
        'customer_median_response_delay': np.median(customer_response_delays) if len(customer_response_delays) > 0 else 0.0,
        
        # Monologues and turn-taking
        'monologue_segments': monologue_segments,
        'turn_taking_balance': turn_balance,
        'agent_turns': agent_turns,
        'customer_turns': customer_turns
    }


def compute_dead_air_time(utterances_df: pd.DataFrame, call_metrics: pd.Series) -> float:
    """
    Compute total "dead air" time (silence with no speech).
    
    Args:
        utterances_df: DataFrame with utterances for a single call
        call_metrics: Series with call-level metrics (contains silence_time)
        
    Returns:
        Dead air time in seconds (long silences > 5 seconds)
    """
    
    valid_utts = utterances_df[utterances_df['valid_time']].copy()
    
    if len(valid_utts) < 2:
        return 0.0
    
    valid_utts = valid_utts.sort_values('start_sec')
    
    # Find gaps longer than 5 seconds (awkward silence)
    dead_air = 0.0
    for i in range(len(valid_utts) - 1):
        gap = valid_utts.iloc[i + 1]['start_sec'] - valid_utts.iloc[i]['end_sec']
        if gap > 5.0:
            dead_air += gap
    
    return dead_air


def _empty_interaction_metrics(call_id: str) -> Dict[str, Any]:
    """Return empty interaction metrics."""
    return {
        'call_id': call_id,
        'avg_gap': 0.0,
        'median_gap': 0.0,
        'std_gap': 0.0,
        'long_pauses_count': 0,
        'long_pauses_rate': 0.0,
        'interruptions_count': 0,
        'interruption_rate': 0.0,
        'agent_avg_response_delay': 0.0,
        'customer_avg_response_delay': 0.0,
        'agent_median_response_delay': 0.0,
        'customer_median_response_delay': 0.0,
        'monologue_segments': 0,
        'turn_taking_balance': 0.0,
        'agent_turns': 0,
        'customer_turns': 0
    }
