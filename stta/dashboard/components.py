"""Reusable dashboard components."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List


def create_speaker_colors(speakers: List[str]) -> Dict[str, str]:
    """Create color mapping for speakers (Coworkers.ai branding)."""
    colors = {
        'AGENT': '#7DD3D3',      # Coworkers cyan
        'CUSTOMER': '#E6458B',   # Coworkers magenta
        'OTHER': '#FFA726',      # Orange
        'UNKNOWN': '#9E9E9E'     # Gray
    }
    return {s: colors.get(s, '#888888') for s in speakers}


def render_kpi_cards(call_metrics: pd.Series, speaker_metrics: pd.DataFrame):
    """Render KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Duration",
            f"{call_metrics['total_duration']:.1f}s",
            help="Total timeline from first to last utterance"
        )
    
    with col2:
        st.metric(
            "Speech Time",
            f"{call_metrics['speech_time']:.1f}s",
            delta=f"{call_metrics['speech_ratio']:.1%}",
            help="Total time with active speech (union of intervals)"
        )
    
    with col3:
        st.metric(
            "Silence Time",
            f"{call_metrics['silence_time']:.1f}s",
            delta=f"{call_metrics['silence_ratio']:.1%}",
            help="Time without any active speech"
        )
    
    with col4:
        st.metric(
            "Overlap Time",
            f"{call_metrics['overlap_time']:.1f}s",
            delta=f"{call_metrics['overlap_ratio']:.1%}",
            help="Time with multiple speakers talking simultaneously"
        )
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Utterances",
            int(call_metrics['total_utterances']),
            help="Number of utterance segments"
        )
    
    with col2:
        st.metric(
            "Speaker Switches",
            int(call_metrics['speaker_switches']),
            delta=f"{call_metrics['switches_per_min']:.1f}/min",
            help="Number of turn changes between speakers"
        )
    
    with col3:
        st.metric(
            "Total Words",
            int(call_metrics['total_words']),
            help="Total word count across all utterances"
        )
    
    with col4:
        st.metric(
            "Interruptions",
            int(call_metrics['interruptions_total']),
            help="Number of times a speaker started before another finished"
        )


def render_timeline_gantt(utterances_df: pd.DataFrame, speaker_metrics: pd.DataFrame):
    """Render timeline Gantt chart."""
    
    valid_utts = utterances_df[utterances_df['valid_time']].copy()
    
    if valid_utts.empty:
        st.warning("No valid utterances to display")
        return
    
    # CRITICAL FIX: Convert seconds to datetime for Plotly timeline
    # Plotly timeline requires datetime objects, not float seconds
    from datetime import datetime, timedelta
    
    # Use a reference datetime (arbitrary, just for visualization)
    base_time = datetime(2025, 1, 1, 0, 0, 0)
    
    # Normalize to start at 0 and convert to datetime
    min_start = valid_utts['start_sec'].min()
    valid_utts['start_dt'] = valid_utts['start_sec'].apply(
        lambda x: base_time + timedelta(seconds=float(x - min_start))
    )
    valid_utts['end_dt'] = valid_utts['end_sec'].apply(
        lambda x: base_time + timedelta(seconds=float(x - min_start))
    )
    
    # Create color mapping
    colors = create_speaker_colors(valid_utts['speaker'].unique())
    
    # Prepare data for Gantt
    gantt_data = []
    for _, row in valid_utts.iterrows():
        # Calculate duration if not present (backward compatibility)
        duration = row.get('duration_sec', row['end_sec'] - row['start_sec'])
        
        gantt_data.append({
            'Task': f"{row['speaker']}",
            'Start': row['start_dt'],
            'Finish': row['end_dt'],
            'Resource': row['speaker'],
            'Duration': f"{duration:.1f}s",
            'Text': row['text'][:50] + '...' if len(row['text']) > 50 else row['text']
        })
    
    gantt_df = pd.DataFrame(gantt_data)
    
    # Create figure
    fig = px.timeline(
        gantt_df,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='Resource',
        color_discrete_map=colors,
        hover_data=['Duration', 'Text'],
        title="Speaker Timeline (Gantt Chart)"
    )
    
    fig.update_yaxes(categoryorder='total ascending')
    
    # Format x-axis to show seconds instead of full datetime
    fig.update_xaxes(
        tickformat='%M:%S',  # MM:SS format
        title_text="Time from call start (MM:SS)"
    )
    
    fig.update_layout(
        height=400,
        yaxis_title="Speaker",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_speaking_time_chart(speaker_metrics: pd.DataFrame, time_type: str = "apportioned"):
    """Render speaking time comparison chart."""
    
    if time_type == "apportioned":
        y_col = 'apportioned_speaking_time'
        title = "Apportioned Speaking Time"
    else:
        y_col = 'raw_speaking_time'
        title = "Raw Speaking Time"
    
    colors = create_speaker_colors(speaker_metrics['speaker'].tolist())
    
    fig = px.bar(
        speaker_metrics,
        x='speaker',
        y=y_col,
        color='speaker',
        color_discrete_map=colors,
        text=y_col
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}s',
        textposition='outside'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="Time (seconds)"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_gaps_histogram(utterances_df: pd.DataFrame):
    """Render histogram of gaps between utterances."""
    
    valid_utts = utterances_df[utterances_df['valid_time']].copy()
    valid_utts = valid_utts.sort_values('start_sec')
    
    if len(valid_utts) < 2:
        st.info("Not enough utterances to compute gaps")
        return
    
    # Compute gaps
    gaps = []
    for i in range(len(valid_utts) - 1):
        curr = valid_utts.iloc[i]
        next_utt = valid_utts.iloc[i + 1]
        gap = next_utt['start_sec'] - curr['end_sec']
        gaps.append(gap)
    
    # Create histogram
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=gaps,
        nbinsx=50,
        name='Gaps',
        marker_color='#2E86AB'
    ))
    
    fig.update_layout(
        title="Distribution of Gaps Between Utterances",
        xaxis_title="Gap Duration (seconds)",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    
    # Add vertical line at 0 (negative gaps = overlaps)
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Overlap threshold")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Median Gap", f"{pd.Series(gaps).median():.2f}s")
    
    with col2:
        st.metric("Avg Gap", f"{pd.Series(gaps).mean():.2f}s")
    
    with col3:
        st.metric("P95 Gap", f"{pd.Series(gaps).quantile(0.95):.2f}s")
    
    with col4:
        negative_count = sum(1 for g in gaps if g < 0)
        st.metric("Negative Gaps", negative_count)


def render_quality_flags(quality_metrics: pd.Series):
    """Render quality flag indicators."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'invalid_time_ratio' in quality_metrics:
            st.metric(
                "Invalid Timestamps",
                f"{quality_metrics['invalid_time_ratio']:.1%}",
                help="Ratio of utterances with invalid time data"
            )
        else:
            st.metric("Invalid Timestamps", "N/A")
    
    with col2:
        if 'unknown_speaker_ratio' in quality_metrics:
            st.metric(
                "Unknown Speakers",
                f"{quality_metrics['unknown_speaker_ratio']:.1%}",
                help="Ratio of utterances with unmapped speaker labels"
            )
        else:
            st.metric("Unknown Speakers", "N/A")
    
    with col3:
        if 'empty_text_ratio' in quality_metrics:
            st.metric(
                "Empty Text Segments",
                f"{quality_metrics['empty_text_ratio']:.1%}",
                help="Ratio of utterances with no text content"
            )
        else:
            st.metric("Empty Text Segments", "N/A")
    
    # Metadata comparison
    if 'metadata_timeline_delta' in quality_metrics and quality_metrics['metadata_timeline_delta'] is not None:
        st.markdown("---")
        st.subheader("Metadata vs Computed")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Metadata Duration",
                f"{quality_metrics['call_duration_meta']:.1f}s" if quality_metrics['call_duration_meta'] else "N/A"
            )
        
        with col2:
            st.metric(
                "Computed Duration",
                f"{quality_metrics['call_duration_computed']:.1f}s"
            )
        
        with col3:
            delta = quality_metrics['metadata_timeline_delta']
            st.metric(
                "Delta",
                f"{delta:.1f}s",
                help="Absolute difference between metadata and computed duration"
            )


def render_storytelling(call_metrics: pd.Series, speaker_metrics: pd.DataFrame):
    """Render narrative summary."""
    
    # Build narrative
    T = call_metrics['total_duration']
    L = call_metrics['speech_time']
    S = call_metrics['silence_time']
    O = call_metrics['overlap_time']
    
    narrative = f"""
**Call Duration:** {T:.1f} seconds ({T/60:.1f} minutes)

**Speech & Silence:**
- Active speech: {L:.1f}s ({call_metrics['speech_ratio']:.1%} of timeline)
- Silence: {S:.1f}s ({call_metrics['silence_ratio']:.1%} of timeline)
- Speech-to-silence ratio: {call_metrics['speech_to_silence_ratio']:.2f}

**Overlap:**
- Simultaneous speech: {O:.1f}s ({call_metrics['overlap_ratio']:.1%} of timeline)
- This indicates {'minimal' if call_metrics['overlap_ratio'] < 0.05 else 'moderate' if call_metrics['overlap_ratio'] < 0.15 else 'significant'} overlap

**Speaker Distribution:**
"""
    
    # Add speaker details
    for _, spk in speaker_metrics.iterrows():
        proportion = spk['apportioned_proportion'] * 100
        narrative += f"\n- **{spk['speaker']}:** {spk['apportioned_speaking_time']:.1f}s ({proportion:.1f}%), {spk['turn_count']} turns, {spk['words_per_minute']:.1f} WPM"
    
    narrative += f"""

**Turn-Taking:**
- Speaker switches: {call_metrics['speaker_switches']} ({call_metrics['switches_per_min']:.1f} per minute)
- Total interruptions: {call_metrics['interruptions_total']}
  - By Agent: {call_metrics['interruptions_by_agent']}
  - By Customer: {call_metrics['interruptions_by_customer']}

**Dialog Balance:**
- Gini coefficient: {speaker_metrics.iloc[0]['dialog_balance_gini']:.3f} ({'balanced' if speaker_metrics.iloc[0]['dialog_balance_gini'] < 0.3 else 'moderately unbalanced' if speaker_metrics.iloc[0]['dialog_balance_gini'] < 0.5 else 'highly unbalanced'})
"""
    
    st.markdown(narrative)
