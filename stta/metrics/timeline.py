"""
Sweep-line algorithm for precise timeline calculations.

Computes:
- Total speech time (union of intervals)
- Overlap time (multi-talk)
- Silence time
- Apportioned speaking time per speaker (fair overlap distribution)

Mathematical guarantees:
- L + S = T (total timeline)
- O ≤ L (overlap is subset of speech)
- Σ A_k = L (apportioned sum equals total speech)
"""

import pandas as pd
from typing import Dict, List, Tuple
from collections import defaultdict
from loguru import logger


class TimelineCalculator:
    """Sweep-line algorithm for interval algebra."""
    
    def __init__(self, precision: float = 0.001):
        """
        Initialize calculator.
        
        Args:
            precision: Time precision in seconds (for floating point comparisons)
        """
        self.precision = precision
    
    def compute_timeline_stats(
        self,
        utterances_df: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Compute timeline statistics using sweep-line algorithm.
        
        Args:
            utterances_df: DataFrame with columns:
                - start_sec
                - end_sec
                - speaker
                - valid_time
                
        Returns:
            Dictionary with keys:
                - T: total timeline (seconds)
                - L: total speech time (seconds)
                - O: overlap time (seconds)
                - S: silence time (seconds)
                - apportioned: {speaker: apportioned_seconds}
                - raw_speaking: {speaker: raw_seconds}
        """
        # Filter valid utterances
        valid_df = utterances_df[utterances_df['valid_time']].copy()
        
        if valid_df.empty:
            logger.warning("No valid utterances for timeline calculation")
            return {
                'T': 0.0,
                'L': 0.0,
                'O': 0.0,
                'S': 0.0,
                'apportioned': {},
                'raw_speaking': {}
            }
        
        # Calculate timeline bounds
        T = valid_df['end_sec'].max() - valid_df['start_sec'].min()
        
        # Create events list: (time, delta, speaker)
        # delta = +1 for start, -1 for end
        events = []
        for _, row in valid_df.iterrows():
            events.append((row['start_sec'], +1, row['speaker']))
            events.append((row['end_sec'], -1, row['speaker']))
        
        # Sort events
        # For same time: process start (+1) before end (-1) to handle touching intervals
        events.sort(key=lambda x: (x[0], -x[1]))
        
        # Sweep through events
        active_speakers = defaultdict(int)  # speaker -> count of active segments
        last_t = None
        
        L = 0.0  # Total speech
        O = 0.0  # Overlap
        apportioned = defaultdict(float)  # Fair speaking time
        
        for t, delta, speaker in events:
            # Process segment [last_t, t) if exists
            if last_t is not None and t > last_t:
                duration = t - last_t
                
                # Count active speakers (those with count > 0)
                active_count = sum(1 for cnt in active_speakers.values() if cnt > 0)
                
                if active_count >= 1:
                    L += duration
                    
                    # Apportion time fairly among active speakers
                    share = 1.0 / active_count
                    for spk, cnt in active_speakers.items():
                        if cnt > 0:
                            apportioned[spk] += duration * share
                
                if active_count >= 2:
                    O += duration
            
            # Update active speakers
            active_speakers[speaker] += delta
            last_t = t
        
        # Calculate silence
        S = max(0.0, T - L)
        
        # Calculate raw speaking time (with overlaps double-counted)
        raw_speaking = defaultdict(float)
        for _, row in valid_df.iterrows():
            raw_speaking[row['speaker']] += row['duration_sec']
        
        logger.debug(f"Timeline: T={T:.2f}s, L={L:.2f}s, O={O:.2f}s, S={S:.2f}s")
        
        # Validate invariants
        self._validate_invariants(T, L, O, S, apportioned)
        
        return {
            'T': T,
            'L': L,
            'O': O,
            'S': S,
            'apportioned': dict(apportioned),
            'raw_speaking': dict(raw_speaking)
        }
    
    def _validate_invariants(
        self,
        T: float,
        L: float,
        O: float,
        S: float,
        apportioned: Dict[str, float]
    ) -> None:
        """Validate mathematical invariants."""
        
        # L + S = T (within precision)
        if abs((L + S) - T) > self.precision:
            logger.warning(f"Invariant violation: L + S != T ({L} + {S} != {T})")
        
        # O ≤ L
        if O > L + self.precision:
            logger.warning(f"Invariant violation: O > L ({O} > {L})")
        
        # Σ A_k = L
        total_apportioned = sum(apportioned.values())
        if abs(total_apportioned - L) > self.precision:
            logger.warning(
                f"Invariant violation: Σ apportioned != L "
                f"({total_apportioned} != {L})"
            )
    
    def compute_gaps(
        self,
        utterances_df: pd.DataFrame
    ) -> List[Dict[str, any]]:
        """
        Compute gaps between consecutive utterances.
        
        Args:
            utterances_df: DataFrame sorted by start_sec
            
        Returns:
            List of gap dicts with keys:
                - gap_sec: gap duration (can be negative for overlaps)
                - prev_end: previous utterance end time
                - next_start: next utterance start time
                - prev_speaker: previous speaker
                - next_speaker: next speaker
        """
        valid_df = utterances_df[utterances_df['valid_time']].copy()
        valid_df = valid_df.sort_values('start_sec').reset_index(drop=True)
        
        gaps = []
        
        for i in range(len(valid_df) - 1):
            curr = valid_df.iloc[i]
            next_utt = valid_df.iloc[i + 1]
            
            gap_sec = next_utt['start_sec'] - curr['end_sec']
            
            gaps.append({
                'gap_sec': gap_sec,
                'prev_end': curr['end_sec'],
                'next_start': next_utt['start_sec'],
                'prev_speaker': curr['speaker'],
                'next_speaker': next_utt['speaker']
            })
        
        return gaps
    
    def compute_turns(
        self,
        utterances_df: pd.DataFrame
    ) -> List[Dict[str, any]]:
        """
        Compute speaker turns (maximal blocks of same speaker).
        
        A turn is a maximal sequence of consecutive utterances by the same speaker,
        regardless of gaps between them.
        
        Args:
            utterances_df: DataFrame sorted by utterance_index
            
        Returns:
            List of turn dicts with keys:
                - speaker: speaker label
                - start_sec: turn start time
                - end_sec: turn end time
                - duration_sec: turn duration
                - utterance_count: number of utterances in turn
        """
        valid_df = utterances_df[utterances_df['valid_time']].copy()
        valid_df = valid_df.sort_values('utterance_index').reset_index(drop=True)
        
        if valid_df.empty:
            return []
        
        turns = []
        current_speaker = valid_df.iloc[0]['speaker']
        turn_start = valid_df.iloc[0]['start_sec']
        turn_end = valid_df.iloc[0]['end_sec']
        utt_count = 1
        
        for i in range(1, len(valid_df)):
            row = valid_df.iloc[i]
            
            if row['speaker'] == current_speaker:
                # Continue current turn
                turn_end = max(turn_end, row['end_sec'])
                utt_count += 1
            else:
                # End current turn, start new one
                turns.append({
                    'speaker': current_speaker,
                    'start_sec': turn_start,
                    'end_sec': turn_end,
                    'duration_sec': turn_end - turn_start,
                    'utterance_count': utt_count
                })
                
                current_speaker = row['speaker']
                turn_start = row['start_sec']
                turn_end = row['end_sec']
                utt_count = 1
        
        # Add final turn
        turns.append({
            'speaker': current_speaker,
            'start_sec': turn_start,
            'end_sec': turn_end,
            'duration_sec': turn_end - turn_start,
            'utterance_count': utt_count
        })
        
        logger.debug(f"Computed {len(turns)} turns")
        
        return turns
