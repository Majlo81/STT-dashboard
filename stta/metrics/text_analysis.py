"""Text analysis metrics for call transcripts."""

import pandas as pd
import re
from typing import Dict, Any
from loguru import logger


def compute_text_statistics(utterances_df: pd.DataFrame, call_id: str) -> Dict[str, Any]:
    """
    Compute text-based statistics for a call.
    
    Args:
        utterances_df: DataFrame with utterances for a single call
        call_id: Unique call identifier
        
    Returns:
        Dictionary with text statistics metrics
    """
    
    # Filter valid utterances with text
    valid_utts = utterances_df[
        (utterances_df['valid_time']) & 
        (utterances_df['text'].notna()) &
        (utterances_df['text'].str.strip() != '')
    ].copy()
    
    if len(valid_utts) == 0:
        logger.warning(f"No valid utterances with text for call {call_id}")
        return _empty_text_stats(call_id)
    
    # Combine all text
    all_text = ' '.join(valid_utts['text'].astype(str))
    
    # 1. Word statistics
    words = all_text.split()
    unique_words = set(w.lower() for w in words if len(w) > 0)
    
    # 2. Sentence statistics
    sentences = re.split(r'[.!?]+', all_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) > 0:
        words_per_sentence = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(words_per_sentence) / len(words_per_sentence)
    else:
        avg_sentence_length = 0.0
    
    # 3. Punctuation counts
    question_count = all_text.count('?')
    exclamation_count = all_text.count('!')
    
    # 4. Vocabulary richness (Type-Token Ratio)
    vocabulary_richness = len(unique_words) / len(words) if len(words) > 0 else 0.0
    
    # 5. Per-speaker statistics
    speaker_stats = {}
    for speaker in valid_utts['speaker'].unique():
        speaker_utts = valid_utts[valid_utts['speaker'] == speaker]
        speaker_text = ' '.join(speaker_utts['text'].astype(str))
        speaker_words = speaker_text.split()
        
        speaker_stats[speaker] = {
            'unique_words': len(set(w.lower() for w in speaker_words)),
            'question_count': speaker_text.count('?'),
            'exclamation_count': speaker_text.count('!')
        }
    
    return {
        'call_id': call_id,
        'total_words': len(words),
        'unique_words_count': len(unique_words),
        'vocabulary_richness': vocabulary_richness,
        'sentence_count': len(sentences),
        'avg_sentence_length': avg_sentence_length,
        'question_count': question_count,
        'exclamation_count': exclamation_count,
        'questions_per_utterance': question_count / len(valid_utts) if len(valid_utts) > 0 else 0.0,
        'agent_questions': speaker_stats.get('AGENT', {}).get('question_count', 0),
        'customer_questions': speaker_stats.get('CUSTOMER', {}).get('question_count', 0),
        'agent_exclamations': speaker_stats.get('AGENT', {}).get('exclamation_count', 0),
        'customer_exclamations': speaker_stats.get('CUSTOMER', {}).get('exclamation_count', 0)
    }


def compute_filler_words(utterances_df: pd.DataFrame, call_id: str) -> Dict[str, Any]:
    """
    Compute filler word statistics.
    
    Args:
        utterances_df: DataFrame with utterances for a single call
        call_id: Unique call identifier
        
    Returns:
        Dictionary with filler word metrics
    """
    
    # Czech filler words
    fillers = [
        'ehm', 'em', 'hm', 'hmm', 'aha', 'ano', 'eh', 'uh', 'um',
        'jako', 'jakoby', 'vlastně', 'víš', 'víte', 'teda', 'prostě',
        'tak', 'takže', 'no', 'jo', 'ježiš', 'kruci'
    ]
    
    valid_utts = utterances_df[
        (utterances_df['valid_time']) & 
        (utterances_df['text'].notna()) &
        (utterances_df['text'].str.strip() != '')
    ].copy()
    
    if len(valid_utts) == 0:
        return {
            'call_id': call_id,
            'filler_words_total': 0,
            'filler_words_rate': 0.0,
            'agent_filler_rate': 0.0,
            'customer_filler_rate': 0.0
        }
    
    all_text = ' '.join(valid_utts['text'].astype(str).str.lower())
    words = all_text.split()
    
    # Count filler words
    filler_count = sum(1 for word in words if word in fillers)
    filler_rate = filler_count / len(words) if len(words) > 0 else 0.0
    
    # Per-speaker filler rates
    agent_utts = valid_utts[valid_utts['speaker'] == 'AGENT']
    customer_utts = valid_utts[valid_utts['speaker'] == 'CUSTOMER']
    
    agent_text = ' '.join(agent_utts['text'].astype(str).str.lower()) if len(agent_utts) > 0 else ''
    customer_text = ' '.join(customer_utts['text'].astype(str).str.lower()) if len(customer_utts) > 0 else ''
    
    agent_words = agent_text.split()
    customer_words = customer_text.split()
    
    agent_fillers = sum(1 for w in agent_words if w in fillers)
    customer_fillers = sum(1 for w in customer_words if w in fillers)
    
    agent_filler_rate = agent_fillers / len(agent_words) if len(agent_words) > 0 else 0.0
    customer_filler_rate = customer_fillers / len(customer_words) if len(customer_words) > 0 else 0.0
    
    return {
        'call_id': call_id,
        'filler_words_total': filler_count,
        'filler_words_rate': filler_rate,
        'agent_filler_rate': agent_filler_rate,
        'customer_filler_rate': customer_filler_rate
    }


def _empty_text_stats(call_id: str) -> Dict[str, Any]:
    """Return empty text statistics."""
    return {
        'call_id': call_id,
        'total_words': 0,
        'unique_words_count': 0,
        'vocabulary_richness': 0.0,
        'sentence_count': 0,
        'avg_sentence_length': 0.0,
        'question_count': 0,
        'exclamation_count': 0,
        'questions_per_utterance': 0.0,
        'agent_questions': 0,
        'customer_questions': 0,
        'agent_exclamations': 0,
        'customer_exclamations': 0
    }
