"""Tests for timeline calculations (sweep-line algorithm)."""

import pytest
import pandas as pd
from stta.metrics.timeline import TimelineCalculator


class TestTimelineCalculator:
    """Test timeline calculations."""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return TimelineCalculator()
    
    @pytest.fixture
    def simple_utterances(self):
        """Create simple test data."""
        data = {
            'start_sec': [0.0, 5.0, 10.0],
            'end_sec': [5.0, 10.0, 15.0],
            'duration_sec': [5.0, 5.0, 5.0],
            'speaker': ['AGENT', 'CUSTOMER', 'AGENT'],
            'valid_time': [True, True, True]
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def overlapping_utterances(self):
        """Create overlapping test data."""
        data = {
            'start_sec': [0.0, 3.0, 8.0],
            'end_sec': [5.0, 7.0, 12.0],
            'duration_sec': [5.0, 4.0, 4.0],
            'speaker': ['AGENT', 'CUSTOMER', 'AGENT'],
            'valid_time': [True, True, True]
        }
        return pd.DataFrame(data)
    
    def test_simple_timeline(self, calculator, simple_utterances):
        """Test timeline with no overlaps."""
        stats = calculator.compute_timeline_stats(simple_utterances)
        
        assert stats['T'] == 15.0  # 0 to 15
        assert stats['L'] == 15.0  # All speech
        assert stats['S'] == 0.0   # No silence
        assert stats['O'] == 0.0   # No overlap
    
    def test_overlapping_timeline(self, calculator, overlapping_utterances):
        """Test timeline with overlaps."""
        stats = calculator.compute_timeline_stats(overlapping_utterances)
        
        assert stats['T'] == 12.0  # 0 to 12
        assert stats['O'] == 2.0   # [3, 5) overlaps
        
        # L + S = T
        assert abs((stats['L'] + stats['S']) - stats['T']) < 0.001
        
        # O <= L
        assert stats['O'] <= stats['L']
    
    def test_apportioned_speaking_time(self, calculator, overlapping_utterances):
        """Test apportioned speaking time calculation."""
        stats = calculator.compute_timeline_stats(overlapping_utterances)
        
        apportioned = stats['apportioned']
        
        # Sum of apportioned = L
        total_apportioned = sum(apportioned.values())
        assert abs(total_apportioned - stats['L']) < 0.001
        
        # Both speakers should have time
        assert 'AGENT' in apportioned
        assert 'CUSTOMER' in apportioned
        assert apportioned['AGENT'] > 0
        assert apportioned['CUSTOMER'] > 0
    
    def test_empty_utterances(self, calculator):
        """Test with no utterances."""
        df = pd.DataFrame({
            'start_sec': [],
            'end_sec': [],
            'duration_sec': [],
            'speaker': [],
            'valid_time': []
        })
        
        stats = calculator.compute_timeline_stats(df)
        
        assert stats['T'] == 0.0
        assert stats['L'] == 0.0
        assert stats['S'] == 0.0
        assert stats['O'] == 0.0
        assert len(stats['apportioned']) == 0
    
    def test_gaps_computation(self, calculator, simple_utterances):
        """Test gap computation."""
        gaps = calculator.compute_gaps(simple_utterances)
        
        assert len(gaps) == 2  # 3 utterances = 2 gaps
        assert all(g['gap_sec'] == 0.0 for g in gaps)  # No gaps
    
    def test_turns_computation(self, calculator, simple_utterances):
        """Test turn computation."""
        # Add utterance_index
        simple_utterances['utterance_index'] = range(len(simple_utterances))
        
        turns = calculator.compute_turns(simple_utterances)
        
        # Should be 3 turns (AGENT, CUSTOMER, AGENT)
        assert len(turns) == 3
        assert turns[0]['speaker'] == 'AGENT'
        assert turns[1]['speaker'] == 'CUSTOMER'
        assert turns[2]['speaker'] == 'AGENT'
    
    def test_invariants(self, calculator, overlapping_utterances):
        """Test mathematical invariants."""
        stats = calculator.compute_timeline_stats(overlapping_utterances)
        
        T = stats['T']
        L = stats['L']
        O = stats['O']
        S = stats['S']
        
        # Invariant 1: L + S = T
        assert abs((L + S) - T) < 0.001
        
        # Invariant 2: O <= L
        assert O <= L + 0.001
        
        # Invariant 3: Σ apportioned = L
        total_app = sum(stats['apportioned'].values())
        assert abs(total_app - L) < 0.001
        
        # Invariant 4: All values non-negative
        assert T >= 0
        assert L >= 0
        assert O >= 0
        assert S >= 0
