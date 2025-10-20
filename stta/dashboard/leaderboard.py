"""Agent leaderboard and performance ranking."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def calculate_agent_scores(
    speaker_metrics_df: pd.DataFrame,
    call_metrics_df: pd.DataFrame,
    quality_metrics_df: pd.DataFrame,
    text_stats_df: pd.DataFrame,
    filler_words_df: pd.DataFrame,
    interaction_metrics_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate comprehensive agent performance scores.
    
    Returns:
        DataFrame with agent rankings and scores
    """
    
    # Filter for AGENT speaker only
    agent_metrics = speaker_metrics_df[speaker_metrics_df['speaker'] == 'AGENT'].copy()
    
    # Merge with other metrics
    agent_data = agent_metrics.merge(
        call_metrics_df[['call_id', 'total_duration', 'total_utterances']],
        on='call_id'
    )
    agent_data = agent_data.merge(
        quality_metrics_df[['call_id', 'quality_score']],
        on='call_id'
    )
    agent_data = agent_data.merge(
        text_stats_df[['call_id', 'vocabulary_richness', 'agent_questions']],
        on='call_id'
    )
    agent_data = agent_data.merge(
        filler_words_df[['call_id', 'agent_filler_rate']],
        on='call_id'
    )
    agent_data = agent_data.merge(
        interaction_metrics_df[['call_id', 'agent_avg_response_delay', 'turn_taking_balance']],
        on='call_id'
    )
    
    # If we don't have agent identifiers, create aggregate statistics
    # For now, we'll use call_id as "agent" (in real scenario, you'd have agent_id)
    
    # Aggregate by call_id (treating each call as separate "agent" for demo)
    # In production, you'd aggregate by actual agent_id
    agent_summary = pd.DataFrame({
        'agent_id': agent_data['call_id'],
        'total_calls': 1,  # Each row is one call
        'total_duration': agent_data['total_duration'],
        'avg_speaking_time': agent_data['apportioned_speaking_time'],
        'avg_words_per_minute': agent_data['words_per_minute'],
        'avg_quality_score': agent_data['quality_score'],
        'avg_vocabulary_richness': agent_data['vocabulary_richness'],
        'avg_questions_asked': agent_data['agent_questions'],
        'avg_filler_rate': agent_data['agent_filler_rate'],
        'avg_response_delay': agent_data['agent_avg_response_delay'],
        'avg_turn_balance': agent_data['turn_taking_balance']
    })
    
    # Calculate composite performance score (0-100)
    # Weights for different components
    weights = {
        'quality': 0.25,
        'vocabulary': 0.15,
        'filler': 0.15,
        'response': 0.20,
        'balance': 0.15,
        'engagement': 0.10
    }
    
    # Normalize metrics (0-1 scale)
    agent_summary['quality_norm'] = agent_summary['avg_quality_score']
    agent_summary['vocabulary_norm'] = agent_summary['avg_vocabulary_richness']
    agent_summary['filler_norm'] = 1 - np.clip(agent_summary['avg_filler_rate'] / 0.1, 0, 1)  # Lower is better
    agent_summary['response_norm'] = 1 - np.clip(agent_summary['avg_response_delay'] / 5, 0, 1)  # Lower is better
    agent_summary['balance_norm'] = agent_summary['avg_turn_balance']
    agent_summary['engagement_norm'] = np.clip(agent_summary['avg_questions_asked'] / 10, 0, 1)
    
    # Calculate composite score
    agent_summary['performance_score'] = (
        weights['quality'] * agent_summary['quality_norm'] +
        weights['vocabulary'] * agent_summary['vocabulary_norm'] +
        weights['filler'] * agent_summary['filler_norm'] +
        weights['response'] * agent_summary['response_norm'] +
        weights['balance'] * agent_summary['balance_norm'] +
        weights['engagement'] * agent_summary['engagement_norm']
    ) * 100
    
    # Add performance tier
    agent_summary['tier'] = pd.cut(
        agent_summary['performance_score'],
        bins=[0, 60, 75, 85, 100],
        labels=['🔴 Needs Improvement', '🟡 Good', '🟢 Excellent', '⭐ Outstanding']
    )
    
    # Sort by performance score
    agent_summary = agent_summary.sort_values('performance_score', ascending=False)
    agent_summary['rank'] = range(1, len(agent_summary) + 1)
    
    return agent_summary


def identify_top_performers(agent_summary: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Get top performing agents."""
    return agent_summary.head(top_n)


def identify_improvement_needed(agent_summary: pd.DataFrame, bottom_n: int = 10) -> pd.DataFrame:
    """Get agents needing improvement."""
    return agent_summary.tail(bottom_n)


def get_performance_breakdown(agent_summary: pd.DataFrame) -> Dict[str, int]:
    """Get performance tier breakdown."""
    return agent_summary['tier'].value_counts().to_dict()


def calculate_team_kpis(agent_summary: pd.DataFrame) -> Dict[str, float]:
    """Calculate team-wide KPIs."""
    return {
        'avg_performance_score': agent_summary['performance_score'].mean(),
        'avg_quality': agent_summary['avg_quality_score'].mean() * 100,
        'avg_vocabulary': agent_summary['avg_vocabulary_richness'].mean() * 100,
        'avg_filler_rate': agent_summary['avg_filler_rate'].mean() * 100,
        'avg_response_time': agent_summary['avg_response_delay'].mean(),
        'outstanding_agents': (agent_summary['performance_score'] >= 85).sum(),
        'needs_improvement': (agent_summary['performance_score'] < 60).sum()
    }
