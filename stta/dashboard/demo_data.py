"""Demo data generator for Streamlit Cloud deployment."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict


def generate_demo_data(num_calls: int = 500) -> Dict[str, pd.DataFrame]:
    """Generate synthetic demo data for dashboard."""
    
    np.random.seed(42)
    call_ids = [f'call_{i:05d}' for i in range(num_calls)]
    
    # CALLS
    start_date = datetime.now() - timedelta(days=90)
    calls_df = pd.DataFrame({
        'call_id': call_ids,
        'call_start_meta': [start_date + timedelta(hours=i*2) for i in range(num_calls)],
        'source_file': [f'demo_file_{i//100}.csv' for i in range(num_calls)]
    })
    
    # CALL METRICS
    call_metrics_df = pd.DataFrame({
        'call_id': call_ids,
        'total_duration': np.random.uniform(60, 1200, num_calls),
        'total_utterances': np.random.randint(10, 100, num_calls),
        'total_words': np.random.randint(100, 2000, num_calls),
        'speech_time': np.random.uniform(40, 800, num_calls),
        'silence_time': np.random.uniform(10, 200, num_calls),
        'overlap_time': np.random.uniform(0, 50, num_calls),
        'unique_speakers': np.random.randint(2, 4, num_calls),
        'speaker_switches': np.random.randint(5, 50, num_calls),
        'avg_gap_between_utterances': np.random.uniform(0.5, 3.0, num_calls),
        'max_gap_between_utterances': np.random.uniform(3.0, 15.0, num_calls),
        'avg_utterance_duration': np.random.uniform(2.0, 8.0, num_calls),
        'speech_rate': np.random.uniform(0.6, 0.9, num_calls)
    })
    
    # SPEAKER METRICS
    speaker_rows = []
    for call_id in call_ids:
        call_dur = call_metrics_df[call_metrics_df['call_id'] == call_id]['total_duration'].values[0]
        
        for speaker in ['AGENT', 'CUSTOMER']:
            speaking_time = np.random.uniform(0.2, 0.5) * call_dur
            speaker_rows.append({
                'call_id': call_id,
                'speaker': speaker,
                'utterance_count': np.random.randint(5, 40),
                'total_speaking_time': speaking_time,
                'apportioned_speaking_time': speaking_time * 0.95,
                'total_words': np.random.randint(50, 800),
                'words_per_minute': np.random.uniform(120, 180) if speaker == 'AGENT' else np.random.uniform(100, 160),
                'avg_utterance_duration': np.random.uniform(2, 6),
                'max_utterance_duration': np.random.uniform(10, 30)
            })
    
    speaker_metrics_df = pd.DataFrame(speaker_rows)
    
    # QUALITY METRICS
    quality_metrics_df = pd.DataFrame({
        'call_id': call_ids,
        'total_utterances': call_metrics_df['total_utterances'],
        'valid_utterances': (call_metrics_df['total_utterances'] * np.random.uniform(0.85, 1.0, num_calls)).astype(int),
        'invalid_time_count': np.random.randint(0, 10, num_calls),
        'empty_text_count': np.random.randint(0, 5, num_calls),
        'unknown_speaker_count': np.random.randint(0, 3, num_calls),
        'valid_time_ratio': np.random.uniform(0.85, 1.0, num_calls),
        'empty_text_ratio': np.random.uniform(0.0, 0.1, num_calls),
        'unknown_speaker_ratio': np.random.uniform(0.0, 0.05, num_calls),
        'quality_score': np.random.uniform(0.7, 1.0, num_calls)
    })
    
    # TEXT STATISTICS
    text_stats_df = pd.DataFrame({
        'call_id': call_ids,
        'total_words': call_metrics_df['total_words'],
        'unique_words_count': (call_metrics_df['total_words'] * np.random.uniform(0.6, 0.9, num_calls)).astype(int),
        'vocabulary_richness': np.random.uniform(0.6, 0.95, num_calls),
        'sentence_count': np.random.randint(10, 100, num_calls),
        'avg_sentence_length': np.random.uniform(8, 20, num_calls),
        'question_count': np.random.randint(1, 15, num_calls),
        'exclamation_count': np.random.randint(0, 5, num_calls),
        'agent_questions': np.random.randint(0, 8, num_calls),
        'customer_questions': np.random.randint(1, 10, num_calls),
        'agent_exclamations': np.random.randint(0, 3, num_calls),
        'customer_exclamations': np.random.randint(0, 3, num_calls)
    })
    
    # FILLER WORDS
    filler_words_df = pd.DataFrame({
        'call_id': call_ids,
        'filler_words_total': np.random.randint(5, 50, num_calls),
        'filler_words_rate': np.random.uniform(0.01, 0.08, num_calls),
        'agent_filler_rate': np.random.uniform(0.015, 0.06, num_calls),
        'customer_filler_rate': np.random.uniform(0.01, 0.07, num_calls)
    })
    
    # INTERACTION METRICS
    interaction_metrics_df = pd.DataFrame({
        'call_id': call_ids,
        'long_pauses_count': np.random.randint(0, 8, num_calls),
        'long_pauses_rate': np.random.uniform(0.0, 0.15, num_calls),
        'interruption_rate': np.random.uniform(0.1, 0.9, num_calls),
        'agent_turns': np.random.randint(5, 40, num_calls),
        'customer_turns': np.random.randint(5, 40, num_calls),
        'agent_avg_response_delay': np.random.uniform(0.2, 3.0, num_calls),
        'customer_avg_response_delay': np.random.uniform(0.3, 4.0, num_calls),
        'monologue_segments': np.random.randint(0, 5, num_calls),
        'turn_taking_balance': np.random.uniform(0.3, 0.95, num_calls),
        'avg_gap_duration': np.random.uniform(0.5, 2.5, num_calls),
        'max_gap_duration': np.random.uniform(3.0, 15.0, num_calls),
        'interruption_count': np.random.randint(1, 20, num_calls),
        'total_gaps': np.random.randint(10, 80, num_calls),
        'silence_ratio': np.random.uniform(0.1, 0.4, num_calls)
    })
    
    # UTTERANCES (minimal for individual view)
    utterance_rows = []
    sample_texts = [
        "Dobrý den, děkuji za zavolání.",
        "Zdravím, mám dotaz ohledně faktury.",
        "Ano, rozumím. Podívám se na to.",
        "Můžete mi prosím poskytnout číslo objednávky?",
        "Samozřejmě, moment prosím."
    ]
    
    for call_id in call_ids[:10]:  # Only first 10 calls for demo
        num_utts = np.random.randint(8, 20)
        start_time = 0
        
        for i in range(num_utts):
            duration = np.random.uniform(1.5, 8.0)
            utterance_rows.append({
                'call_id': call_id,
                'idx': i,
                'speaker': 'AGENT' if i % 2 == 0 else 'CUSTOMER',
                'start_sec': start_time,
                'end_sec': start_time + duration,
                'text': np.random.choice(sample_texts),
                'valid_time': True
            })
            start_time += duration + np.random.uniform(0.3, 2.0)
    
    utterances_df = pd.DataFrame(utterance_rows)
    
    return {
        'calls': calls_df,
        'utterances': utterances_df,
        'call_metrics': call_metrics_df,
        'speaker_metrics': speaker_metrics_df,
        'quality_metrics': quality_metrics_df,
        'text_stats': text_stats_df,
        'filler_words': filler_words_df,
        'interaction_metrics': interaction_metrics_df
    }
