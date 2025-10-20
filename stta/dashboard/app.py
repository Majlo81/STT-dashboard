"""
Streamlit Dashboard for STT Analytics.

Interactive visualization of call transcript metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from stta.io.writer import read_parquet
from stta.dashboard.components import (
    render_kpi_cards,
    render_timeline_gantt,
    render_speaking_time_chart,
    render_gaps_histogram,
    render_quality_flags,
    render_storytelling,
    create_speaker_colors
)


# Custom CSS - Coworkers.ai Branding
# Note: st.set_page_config is in streamlit_app.py (entry point)
st.markdown("""
<style>
    /* Coworkers.ai Color Palette */
    :root {
        --cw-cyan: #7DD3D3;
        --cw-cyan-light: #C5E8E8;
        --cw-cyan-bg: #E8F7F7;
        --cw-magenta: #E6458B;
        --cw-magenta-dark: #C73570;
        --cw-navy: #1A2B3C;
        --cw-navy-light: #2D4558;
        --cw-gray: #6B7280;
    }
    
    /* Main background */
    .main {
        background: linear-gradient(180deg, var(--cw-cyan-bg) 0%, #ffffff 100%);
    }
    
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, var(--cw-cyan) 0%, var(--cw-magenta) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.1rem;
        color: var(--cw-navy-light);
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--cw-navy);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--cw-gray);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--cw-navy);
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--cw-cyan);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--cw-cyan-light) 0%, #ffffff 100%);
        border-right: 3px solid var(--cw-cyan);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(120deg, var(--cw-magenta) 0%, var(--cw-magenta-dark) 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(230, 69, 139, 0.3);
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(230, 69, 139, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 25px 25px 0 0;
        font-weight: 600;
        color: var(--cw-navy-light);
        background: var(--cw-cyan-light);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        color: var(--cw-magenta);
        border-top: 3px solid var(--cw-magenta);
    }
    
    /* Card-like containers */
    div.element-container {
        border-radius: 12px;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid var(--cw-cyan-light);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid var(--cw-cyan);
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: var(--cw-navy);
        font-weight: 600;
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: var(--cw-navy);
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes only
def load_data(data_dir: Path):
    """Load all Parquet data (real or demo)."""
    # Try to load real data first
    try:
        calls_df = read_parquet(data_dir / "calls.parquet")
        utterances_df = read_parquet(data_dir / "utterances.parquet")
        call_metrics_df = read_parquet(data_dir / "call_metrics.parquet")
        speaker_metrics_df = read_parquet(data_dir / "speaker_metrics.parquet")
        quality_metrics_df = read_parquet(data_dir / "quality_metrics.parquet")
        
        # Load new advanced metrics
        text_stats_df = read_parquet(data_dir / "text_statistics.parquet")
        filler_words_df = read_parquet(data_dir / "filler_words.parquet")
        interaction_metrics_df = read_parquet(data_dir / "interaction_metrics.parquet")
        
        return {
            'calls': calls_df,
            'utterances': utterances_df,
            'call_metrics': call_metrics_df,
            'speaker_metrics': speaker_metrics_df,
            'quality_metrics': quality_metrics_df,
            'text_stats': text_stats_df,
            'filler_words': filler_words_df,
            'interaction_metrics': interaction_metrics_df,
            'is_demo': False
        }
    except Exception as e:
        # If real data not available, generate demo data
        st.info("📊 Real data not found. Loading demo data for demonstration...")
        try:
            from stta.dashboard.demo_data import generate_demo_data
            demo_data = generate_demo_data(num_calls=500)
            demo_data['is_demo'] = True
            return demo_data
        except Exception as demo_error:
            st.error(f"Error loading data: {e}\nDemo data error: {demo_error}")
            return None


def main():
    """Main dashboard application."""
    
    # Title with Coworkers.ai branding
    st.markdown('''
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <h1 class="main-title" style="margin: 0;">🤖 STT Analytics Platform</h1>
    </div>
    <p class="subtitle">by <b>Coworkers.ai</b> | Advanced Speech-to-Text Analytics & Call Intelligence</p>
    ''', unsafe_allow_html=True)
    
    # Sidebar - Data loading
    st.sidebar.header("⚙️ Configuration")
    
    data_dir = st.sidebar.text_input(
        "Data Directory",
        value="data/clean",
        help="Path to directory containing Parquet files"
    )
    
    data_path = Path(data_dir)
    
    # Load data (will use demo if real data not available)
    with st.spinner("Loading data..."):
        data = load_data(data_path)
    
    if data is None:
        st.error("Failed to load data. Please check the data directory or demo data generator.")
        return
    
    # Show demo data warning banner
    if data.get('is_demo', False):
        st.warning("""
        ⚠️ **DEMO MODE** - Using synthetic data for demonstration.  
        This dashboard is showing 500 generated calls with realistic metrics.  
        Deploy with real data by uploading Parquet files to `data/clean/` directory.
        """)
    
    calls_df = data['calls']
    utterances_df = data['utterances']
    call_metrics_df = data['call_metrics']
    speaker_metrics_df = data['speaker_metrics']
    quality_metrics_df = data['quality_metrics']
    text_stats_df = data['text_stats']
    filler_words_df = data['filler_words']
    interaction_metrics_df = data['interaction_metrics']
    
    # Sidebar - View mode
    st.sidebar.header("🎯 View Mode")
    
    view_mode = st.sidebar.radio(
        "Select View",
        options=[
            "📊 Summary (All Calls)", 
            "🔍 Individual Call",
            "🏆 Agent Leaderboard",
            "🚨 Alerts & Issues",
            "📄 Export Report"
        ],
        index=0
    )
    
    # Date range filter
    if 'call_start_meta' in calls_df.columns and calls_df['call_start_meta'].notna().any():
        st.sidebar.markdown("---")
        st.sidebar.subheader("Date Range Filter")
        
        min_date = pd.to_datetime(calls_df['call_start_meta']).min()
        max_date = pd.to_datetime(calls_df['call_start_meta']).max()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        # Filter calls by date
        if len(date_range) == 2:
            calls_df_filtered = calls_df[
                (pd.to_datetime(calls_df['call_start_meta']).dt.date >= date_range[0]) &
                (pd.to_datetime(calls_df['call_start_meta']).dt.date <= date_range[1])
            ]
            filtered_call_ids = calls_df_filtered['call_id'].tolist()
        else:
            filtered_call_ids = calls_df['call_id'].tolist()
    else:
        filtered_call_ids = calls_df['call_id'].tolist()
    
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Call Selection")
    
    call_ids = filtered_call_ids
    selected_call_id = st.sidebar.selectbox(
        "Select Call",
        options=call_ids,
        help="Choose a call to analyze",
        disabled=(view_mode != "🔍 Individual Call")
    )
    
    # Main content
    st.markdown("---")
    
    # ========================================
    # SUMMARY VIEW (All Calls)
    # ========================================
    if view_mode == "📊 Summary (All Calls)":
        # Filter datasets by date range
        filtered_calls = calls_df[calls_df['call_id'].isin(filtered_call_ids)]
        filtered_call_metrics = call_metrics_df[call_metrics_df['call_id'].isin(filtered_call_ids)]
        filtered_quality = quality_metrics_df[quality_metrics_df['call_id'].isin(filtered_call_ids)]
        
        st.markdown(f'<h2 class="section-header">📊 Summary Dashboard</h2>', unsafe_allow_html=True)
        st.markdown(f"<div style='background: linear-gradient(120deg, #f0f7ff 0%, #fff0f7 100%); padding: 1rem; border-radius: 8px; margin-bottom: 2rem;'><b style='font-size: 1.2rem;'>Showing {len(filtered_calls):,} calls</b></div>", unsafe_allow_html=True)
        
        # KPIs
        st.markdown('<h3 class="section-header">📈 Key Performance Indicators</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Calls",
                f"{len(filtered_calls):,}",
                help="Total number of calls in selected date range"
            )
        
        with col2:
            total_duration = filtered_call_metrics['total_duration'].sum()
            avg_duration = filtered_call_metrics['total_duration'].mean()
            st.metric(
                "Total Duration",
                f"{total_duration / 3600:.1f}h",
                delta=f"Avg: {avg_duration / 60:.1f}min"
            )
        
        with col3:
            total_utts = filtered_call_metrics['total_utterances'].sum()
            avg_utts = filtered_call_metrics['total_utterances'].mean()
            st.metric(
                "Total Utterances",
                f"{total_utts:,}",
                delta=f"Avg: {avg_utts:.0f}/call"
            )
        
        with col4:
            total_words = filtered_call_metrics['total_words'].sum()
            avg_words = filtered_call_metrics['total_words'].mean()
            st.metric(
                "Total Words",
                f"{total_words:,}",
                delta=f"Avg: {avg_words:.0f}/call"
            )
        
        with col5:
            avg_quality = filtered_quality['quality_score'].mean() * 100
            st.metric(
                "Avg Quality",
                f"{avg_quality:.1f}%",
                help="Average data quality score across all calls"
            )
        
        # Trends over time
        st.markdown('<h3 class="section-header">📈 Trends Over Time</h3>', unsafe_allow_html=True)
        
        if 'call_start_meta' in filtered_calls.columns:
            # Create time-based aggregations
            calls_with_time = filtered_calls.copy()
            calls_with_time['date'] = pd.to_datetime(calls_with_time['call_start_meta']).dt.date
            calls_with_time['hour'] = pd.to_datetime(calls_with_time['call_start_meta']).dt.hour
            
            # Merge with metrics
            calls_with_metrics = calls_with_time.merge(
                filtered_call_metrics[['call_id', 'total_duration', 'total_utterances']],
                on='call_id'
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Calls per Day")
                daily_counts = calls_with_time.groupby('date').size().reset_index(name='count')
                fig = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    markers=True,
                    title="Number of Calls by Date"
                )
                fig.update_traces(line_color='#7DD3D3', marker=dict(size=8, color='#E6458B'))
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Calls by Hour of Day")
                hourly_counts = calls_with_time.groupby('hour').size().reset_index(name='count')
                fig = px.bar(
                    hourly_counts,
                    x='hour',
                    y='count',
                    title="Call Distribution by Hour"
                )
                fig.update_traces(marker_color='#7DD3D3')
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Metrics distributions
        st.markdown('<h3 class="section-header">📊 Metrics Distributions</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Call Duration Distribution")
            fig = px.histogram(
                filtered_call_metrics,
                x='total_duration',
                nbins=50,
                title="Distribution of Call Durations (seconds)"
            )
            fig.update_traces(marker_color='#7DD3D3', marker_line_color='#5AB8B8', marker_line_width=1)
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Speech Ratio Distribution")
            fig = px.histogram(
                filtered_call_metrics,
                x='speech_ratio',
                nbins=50,
                title="Distribution of Speech Ratio (Speech Time / Total Duration)"
            )
            fig.update_traces(marker_color='#E6458B', marker_line_color='#C73570', marker_line_width=1)
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top/Bottom calls
        st.markdown('<h3 class="section-header">🏆 Top & Bottom Calls</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Longest Calls")
            top_long = filtered_call_metrics.nlargest(10, 'total_duration')[['call_id', 'total_duration']]
            top_long['duration_min'] = top_long['total_duration'] / 60
            st.dataframe(top_long[['call_id', 'duration_min']], use_container_width=True)
        
        with col2:
            st.subheader("Most Utterances")
            top_utts = filtered_call_metrics.nlargest(10, 'total_utterances')[['call_id', 'total_utterances']]
            st.dataframe(top_utts, use_container_width=True)
        
        # Quality overview
        st.markdown('<h3 class="section-header">🔍 Quality Overview</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            invalid_pct = (filtered_quality['invalid_time_count'].sum() / total_utts) * 100 if total_utts > 0 else 0
            st.metric(
                "Invalid Timestamps",
                f"{filtered_quality['invalid_time_count'].sum():,}",
                delta=f"{invalid_pct:.1f}% of total"
            )
        
        with col2:
            empty_pct = (filtered_quality['empty_text_count'].sum() / total_utts) * 100 if total_utts > 0 else 0
            st.metric(
                "Empty Text",
                f"{filtered_quality['empty_text_count'].sum():,}",
                delta=f"{empty_pct:.1f}% of total"
            )
        
        with col3:
            unknown_pct = (filtered_quality['unknown_speaker_count'].sum() / total_utts) * 100 if total_utts > 0 else 0
            st.metric(
                "Unknown Speakers",
                f"{filtered_quality['unknown_speaker_count'].sum():,}",
                delta=f"{unknown_pct:.1f}% of total"
            )
        
        # Advanced Language Analytics
        st.markdown('<h3 class="section-header">💬 Language & Communication Analytics</h3>', unsafe_allow_html=True)
        
        filtered_text_stats = text_stats_df[text_stats_df['call_id'].isin(filtered_call_ids)]
        filtered_filler_words = filler_words_df[filler_words_df['call_id'].isin(filtered_call_ids)]
        filtered_interaction = interaction_metrics_df[interaction_metrics_df['call_id'].isin(filtered_call_ids)]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_vocab = filtered_text_stats['vocabulary_richness'].mean() * 100
            st.metric(
                "Vocabulary Richness",
                f"{avg_vocab:.1f}%",
                help="Type-Token Ratio - unique words / total words"
            )
        
        with col2:
            avg_questions = filtered_text_stats['question_count'].mean()
            st.metric(
                "Avg Questions/Call",
                f"{avg_questions:.1f}",
                help="Average number of questions per call"
            )
        
        with col3:
            avg_filler_rate = filtered_filler_words['filler_words_rate'].mean() * 100
            st.metric(
                "Filler Words Rate",
                f"{avg_filler_rate:.2f}%",
                help="Percentage of filler words (ehm, jako, prostě...)"
            )
        
        with col4:
            avg_response_time = filtered_interaction['agent_avg_response_delay'].mean()
            st.metric(
                "Agent Response Time",
                f"{avg_response_time:.2f}s",
                help="Average time for agent to respond"
            )
        
        # Detailed charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Questions Distribution (Agent vs Customer)")
            question_data = pd.DataFrame({
                'Speaker': ['Agent', 'Customer'],
                'Questions': [
                    filtered_text_stats['agent_questions'].sum(),
                    filtered_text_stats['customer_questions'].sum()
                ]
            })
            fig = px.bar(
                question_data,
                x='Speaker',
                y='Questions',
                color='Speaker',
                color_discrete_map={'Agent': '#7DD3D3', 'Customer': '#E6458B'},
                title="Who asks more questions?"
            )
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Filler Words Rate by Speaker")
            filler_data = pd.DataFrame({
                'Speaker': ['Agent', 'Customer'],
                'Filler Rate (%)': [
                    filtered_filler_words['agent_filler_rate'].mean() * 100,
                    filtered_filler_words['customer_filler_rate'].mean() * 100
                ]
            })
            fig = px.bar(
                filler_data,
                x='Speaker',
                y='Filler Rate (%)',
                color='Speaker',
                color_discrete_map={'Agent': '#7DD3D3', 'Customer': '#E6458B'},
                title="Filler words usage"
            )
            fig.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Interaction Patterns
        st.markdown('<h3 class="section-header">🔄 Interaction Patterns</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_interruptions = filtered_interaction['interruption_rate'].mean() * 100
            st.metric(
                "Interruption Rate",
                f"{avg_interruptions:.1f}%",
                help="Percentage of utterances with interruptions"
            )
        
        with col2:
            avg_pauses = filtered_interaction['long_pauses_count'].mean()
            st.metric(
                "Long Pauses/Call",
                f"{avg_pauses:.1f}",
                help="Average number of long pauses (>3s) per call"
            )
        
        with col3:
            avg_balance = filtered_interaction['turn_taking_balance'].mean()
            st.metric(
                "Turn-Taking Balance",
                f"{avg_balance:.2f}",
                help="Balance of conversation (0=unbalanced, 1=perfectly balanced)"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Response Time Distribution")
            fig = px.histogram(
                filtered_interaction,
                x='agent_avg_response_delay',
                nbins=40,
                title="Distribution of Agent Response Times"
            )
            fig.update_traces(marker_color='#7DD3D3', marker_line_color='#5AB8B8', marker_line_width=1)
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Response Delay (seconds)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Turn-Taking Balance")
            fig = px.histogram(
                filtered_interaction,
                x='turn_taking_balance',
                nbins=40,
                title="Distribution of Conversation Balance"
            )
            fig.update_traces(marker_color='#E6458B', marker_line_color='#C73570', marker_line_width=1)
            fig.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Balance Score (0-1)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        return  # Exit early for summary view
    
    # ========================================
    # AGENT LEADERBOARD
    # ========================================
    elif view_mode == "🏆 Agent Leaderboard":
        from stta.dashboard.leaderboard import calculate_agent_scores, calculate_team_kpis
        
        st.markdown('<h2 class="section-header">🏆 Agent Performance Leaderboard</h2>', unsafe_allow_html=True)
        st.markdown("<div style='background: linear-gradient(120deg, #f0f7ff 0%, #fff0f7 100%); padding: 1rem; border-radius: 8px; margin-bottom: 2rem;'><b style='font-size: 1.1rem;'>Performance rankings based on quality, language, and interaction metrics</b></div>", unsafe_allow_html=True)
        
        # Calculate agent scores
        agent_scores = calculate_agent_scores(
            speaker_metrics_df,
            call_metrics_df,
            quality_metrics_df,
            text_stats_df,
            filler_words_df,
            interaction_metrics_df
        )
        
        # Team KPIs
        team_kpis = calculate_team_kpis(agent_scores)
        
        st.markdown('<h3 class="section-header">📊 Team Overview</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Avg Performance",
                f"{team_kpis['avg_performance_score']:.1f}/100",
                help="Team average performance score"
            )
        
        with col2:
            st.metric(
                "Outstanding",
                f"{team_kpis['outstanding_agents']}",
                help="Agents with score ≥85"
            )
        
        with col3:
            st.metric(
                "Needs Training",
                f"{team_kpis['needs_improvement']}",
                help="Agents with score <60"
            )
        
        with col4:
            st.metric(
                "Avg Quality",
                f"{team_kpis['avg_quality']:.1f}%"
            )
        
        with col5:
            st.metric(
                "Avg Response",
                f"{team_kpis['avg_response_time']:.2f}s"
            )
        
        # Performance breakdown
        st.markdown('<h3 class="section-header">📈 Performance Distribution</h3>', unsafe_allow_html=True)
        
        tier_counts = agent_scores['tier'].value_counts()
        tier_data = pd.DataFrame({
            'Tier': tier_counts.index.tolist(),
            'Count': tier_counts.values.tolist()
        })
        
        fig = px.bar(
            tier_data,
            x='Tier',
            y='Count',
            title="Agent Performance Tiers",
            color='Tier',
            color_discrete_map={
                '⭐ Outstanding': '#7DD3D3',
                '🟢 Excellent': '#90EE90',
                '🟡 Good': '#FFD700',
                '🔴 Needs Improvement': '#E6458B'
            }
        )
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 performers
        st.markdown('<h3 class="section-header">🏆 Top 10 Performers</h3>', unsafe_allow_html=True)
        
        top_10 = agent_scores.head(10)[[
            'rank', 'agent_id', 'performance_score', 'tier',
            'avg_quality_score', 'avg_filler_rate', 'avg_response_delay'
        ]].copy()
        
        top_10['avg_quality_score'] = (top_10['avg_quality_score'] * 100).round(1).astype(str) + '%'
        top_10['avg_filler_rate'] = (top_10['avg_filler_rate'] * 100).round(2).astype(str) + '%'
        top_10['avg_response_delay'] = top_10['avg_response_delay'].round(2).astype(str) + 's'
        top_10['performance_score'] = top_10['performance_score'].round(1)
        
        st.dataframe(
            top_10,
            column_config={
                'rank': 'Rank',
                'agent_id': 'Agent ID',
                'performance_score': 'Score',
                'tier': 'Tier',
                'avg_quality_score': 'Quality',
                'avg_filler_rate': 'Filler Rate',
                'avg_response_delay': 'Response Time'
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Bottom 10 (need improvement)
        st.markdown('<h3 class="section-header">🔴 Needs Improvement (Bottom 10)</h3>', unsafe_allow_html=True)
        
        bottom_10 = agent_scores.tail(10)[[
            'rank', 'agent_id', 'performance_score', 'tier',
            'avg_quality_score', 'avg_filler_rate', 'avg_response_delay'
        ]].copy()
        
        bottom_10['avg_quality_score'] = (bottom_10['avg_quality_score'] * 100).round(1).astype(str) + '%'
        bottom_10['avg_filler_rate'] = (bottom_10['avg_filler_rate'] * 100).round(2).astype(str) + '%'
        bottom_10['avg_response_delay'] = bottom_10['avg_response_delay'].round(2).astype(str) + 's'
        bottom_10['performance_score'] = bottom_10['performance_score'].round(1)
        
        st.dataframe(
            bottom_10,
            column_config={
                'rank': 'Rank',
                'agent_id': 'Agent ID',
                'performance_score': 'Score',
                'tier': 'Tier',
                'avg_quality_score': 'Quality',
                'avg_filler_rate': 'Filler Rate',
                'avg_response_delay': 'Response Time'
            },
            hide_index=True,
            use_container_width=True
        )
        
        return  # Exit early
    
    # ========================================
    # ALERTS & ISSUES
    # ========================================
    elif view_mode == "🚨 Alerts & Issues":
        from stta.dashboard.alerts import AlertSystem
        
        st.markdown('<h2 class="section-header">🚨 Alerts & Quality Issues</h2>', unsafe_allow_html=True)
        st.markdown("<div style='background: linear-gradient(120deg, #fff0f0 0%, #fff7f0 100%); padding: 1rem; border-radius: 8px; margin-bottom: 2rem;'><b style='font-size: 1.1rem;'>Automated detection of quality issues and performance anomalies</b></div>", unsafe_allow_html=True)
        
        # Initialize alert system
        alert_system = AlertSystem()
        
        # Filter by date range
        filtered_calls = calls_df[calls_df['call_id'].isin(filtered_call_ids)]
        filtered_call_metrics = call_metrics_df[call_metrics_df['call_id'].isin(filtered_call_ids)]
        filtered_quality = quality_metrics_df[quality_metrics_df['call_id'].isin(filtered_call_ids)]
        filtered_text_stats = text_stats_df[text_stats_df['call_id'].isin(filtered_call_ids)]
        filtered_filler_words = filler_words_df[filler_words_df['call_id'].isin(filtered_call_ids)]
        filtered_interaction = interaction_metrics_df[interaction_metrics_df['call_id'].isin(filtered_call_ids)]
        
        # Run all checks
        with st.spinner("Analyzing calls for issues..."):
            alerts = alert_system.run_all_checks(
                filtered_calls,
                filtered_call_metrics,
                filtered_quality,
                filtered_text_stats,
                filtered_filler_words,
                filtered_interaction
            )
        
        # Alert summary
        alert_summary = alert_system.get_alert_summary()
        
        st.markdown('<h3 class="section-header">📊 Alert Summary</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔴 Critical",
                alert_summary['critical'],
                help="Critical issues requiring immediate attention"
            )
        
        with col2:
            st.metric(
                "🟠 Errors",
                alert_summary['error'],
                help="Errors that should be addressed"
            )
        
        with col3:
            st.metric(
                "🟡 Warnings",
                alert_summary['warning'],
                help="Warnings to review"
            )
        
        with col4:
            st.metric(
                "🔵 Info",
                alert_summary['info'],
                help="Informational alerts"
            )
        
        # Critical calls (with multiple issues)
        critical_calls = alert_system.get_critical_calls(min_alerts=3)
        
        if len(critical_calls) > 0:
            st.markdown('<h3 class="section-header">⚠️ Critical Calls (Multiple Issues)</h3>', unsafe_allow_html=True)
            st.warning(f"Found {len(critical_calls)} calls with 3+ issues. These require immediate review.")
            
            critical_df = pd.DataFrame({'call_id': critical_calls})
            st.dataframe(critical_df, hide_index=True, use_container_width=True)
        
        # Alerts by category
        st.markdown('<h3 class="section-header">📋 Alerts by Category</h3>', unsafe_allow_html=True)
        
        alerts_by_cat = alert_system.get_alerts_by_category()
        
        for category, cat_alerts in alerts_by_cat.items():
            with st.expander(f"{category} ({len(cat_alerts)} alerts)"):
                alert_data = pd.DataFrame([alert.to_dict() for alert in cat_alerts[:50]])  # Limit to 50
                st.dataframe(alert_data, hide_index=True, use_container_width=True)
        
        return  # Exit early
    
    # ========================================
    # EXPORT REPORT
    # ========================================
    elif view_mode == "📄 Export Report":
        from stta.dashboard.pdf_export import generate_summary_report
        
        st.markdown('<h2 class="section-header">📄 Export PDF Report</h2>', unsafe_allow_html=True)
        st.markdown("<div style='background: linear-gradient(120deg, #f0fff7 0%, #f7f0ff 100%); padding: 1rem; border-radius: 8px; margin-bottom: 2rem;'><b style='font-size: 1.1rem;'>Generate branded PDF reports with comprehensive analytics</b></div>", unsafe_allow_html=True)
        
        st.markdown("### Report Options")
        
        report_name = st.text_input("Report Name", value="call_analytics_report")
        
        include_sections = st.multiselect(
            "Include Sections",
            options=[
                "KPI Summary",
                "Top Performers",
                "Quality Insights",
                "Language Analytics",
                "Interaction Patterns",
                "Detailed Tables"
            ],
            default=[
                "KPI Summary",
                "Top Performers",
                "Quality Insights"
            ]
        )
        
        if st.button("📥 Generate PDF Report", type="primary"):
            # Filter by date range
            filtered_calls = calls_df[calls_df['call_id'].isin(filtered_call_ids)]
            filtered_call_metrics = call_metrics_df[call_metrics_df['call_id'].isin(filtered_call_ids)]
            filtered_quality = quality_metrics_df[quality_metrics_df['call_id'].isin(filtered_call_ids)]
            filtered_text_stats = text_stats_df[text_stats_df['call_id'].isin(filtered_call_ids)]
            filtered_filler_words = filler_words_df[filler_words_df['call_id'].isin(filtered_call_ids)]
            filtered_interaction = interaction_metrics_df[interaction_metrics_df['call_id'].isin(filtered_call_ids)]
            
            with st.spinner("Generating PDF report..."):
                try:
                    filename = f"{report_name}.pdf"
                    pdf_path = generate_summary_report(
                        filtered_calls,
                        filtered_call_metrics,
                        filtered_quality,
                        filtered_text_stats,
                        filtered_filler_words,
                        filtered_interaction,
                        filename=filename
                    )
                    
                    st.success(f"✅ PDF report generated successfully: {pdf_path}")
                    
                    # Offer download
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download PDF",
                            data=f,
                            file_name=filename,
                            mime="application/pdf"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {e}")
        
        st.markdown("---")
        st.info("💡 **Tip:** PDF reports include Coworkers.ai branding and are perfect for client presentations or executive summaries.")
        
        return  # Exit early
    
    # ========================================
    # INDIVIDUAL CALL VIEW
    # ========================================
    
    # Filter data for selected call
    call_row = calls_df[calls_df['call_id'] == selected_call_id].iloc[0]
    call_utts = utterances_df[utterances_df['call_id'] == selected_call_id]
    call_metrics = call_metrics_df[call_metrics_df['call_id'] == selected_call_id].iloc[0]
    speaker_metrics = speaker_metrics_df[speaker_metrics_df['call_id'] == selected_call_id]
    quality_metrics = quality_metrics_df[quality_metrics_df['call_id'] == selected_call_id].iloc[0]
    
    # Speaker filter
    speakers = call_utts['speaker'].unique().tolist()
    selected_speakers = st.sidebar.multiselect(
        "Filter Speakers",
        options=speakers,
        default=speakers,
        help="Show only selected speakers"
    )
    
    # Filter utterances by speaker
    filtered_utts = call_utts[call_utts['speaker'].isin(selected_speakers)]
    
    # Time range filter
    st.sidebar.markdown("---")
    st.sidebar.subheader("Time Range")
    
    if call_metrics['total_duration'] > 0:
        time_range = st.sidebar.slider(
            "Time Range (seconds)",
            min_value=0.0,
            max_value=float(call_metrics['total_duration']),
            value=(0.0, float(call_metrics['total_duration'])),
            step=1.0
        )
        
        # Filter by time range
        filtered_utts = filtered_utts[
            (filtered_utts['start_sec'] >= time_range[0]) &
            (filtered_utts['end_sec'] <= time_range[1])
        ]
    
    # Call metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Call ID", selected_call_id)
    with col2:
        st.metric("Direction", call_row.get('direction', 'UNKNOWN'))
    with col3:
        st.metric("Source File", Path(call_row['source_file']).name)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "⏱️ Timeline",
        "👥 Speakers",
        "🔍 Quality",
        "📄 Details"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.header("Call Overview")
        
        # KPI Cards
        render_kpi_cards(call_metrics, speaker_metrics)
        
        st.markdown("---")
        
        # Storytelling
        st.subheader("📖 Narrative Summary")
        render_storytelling(call_metrics, speaker_metrics)
        
        st.markdown("---")
        
        # Speaking time distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Speaking Time Distribution")
            render_speaking_time_chart(speaker_metrics, "apportioned")
        
        with col2:
            st.subheader("Turn Count by Speaker")
            fig = px.bar(
                speaker_metrics,
                x='speaker',
                y='turn_count',
                color='speaker',
                color_discrete_map=create_speaker_colors(speakers),
                text='turn_count'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Timeline
    with tab2:
        st.header("Timeline Visualization")
        
        # Gantt chart
        render_timeline_gantt(filtered_utts, speaker_metrics)
        
        st.markdown("---")
        
        # Gaps histogram
        st.subheader("Gaps Between Utterances")
        render_gaps_histogram(call_utts)
    
    # Tab 3: Speakers
    with tab3:
        st.header("Speaker Analytics")
        
        # Speaker metrics table
        st.subheader("Speaker Metrics Summary")
        
        display_cols = [
            'speaker',
            'apportioned_speaking_time',
            'apportioned_proportion',
            'turn_count',
            'words_per_minute',
            'total_words'
        ]
        
        speaker_display = speaker_metrics[display_cols].copy()
        speaker_display.columns = [
            'Speaker',
            'Speaking Time (s)',
            'Proportion',
            'Turns',
            'WPM',
            'Total Words'
        ]
        
        st.dataframe(
            speaker_display.style.format({
                'Speaking Time (s)': '{:.2f}',
                'Proportion': '{:.1%}',
                'WPM': '{:.1f}'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Dialog balance
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Dialog Balance (Gini)",
                f"{speaker_metrics.iloc[0]['dialog_balance_gini']:.3f}",
                help="0 = perfect balance, 1 = one speaker dominates"
            )
        
        with col2:
            st.metric(
                "Speaker Switches",
                int(call_metrics['speaker_switches'])
            )
        
        # Words per minute comparison
        st.subheader("Words Per Minute by Speaker")
        fig = px.bar(
            speaker_metrics,
            x='speaker',
            y='words_per_minute',
            color='speaker',
            color_discrete_map=create_speaker_colors(speakers),
            text='words_per_minute'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Quality
    with tab4:
        st.header("Data Quality Metrics")
        
        # Quality score
        quality_score = quality_metrics['quality_score']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Overall Quality Score",
                f"{quality_score:.1%}",
                help="Weighted score based on data validity"
            )
        
        with col2:
            color = "green" if quality_score >= 0.9 else "orange" if quality_score >= 0.7 else "red"
            st.markdown(f"**Status:** :{color}[{'Excellent' if quality_score >= 0.9 else 'Good' if quality_score >= 0.7 else 'Poor'}]")
        
        with col3:
            st.metric(
                "Valid Utterances",
                f"{call_metrics['valid_utterances']}/{call_metrics['total_utterances']}"
            )
        
        st.markdown("---")
        
        # Quality flags
        st.subheader("Quality Flags")
        render_quality_flags(quality_metrics)
        
        st.markdown("---")
        
        # Invalid reason breakdown
        st.subheader("Invalid Timestamp Reasons")
        invalid_reasons = {
            'Missing Time': quality_metrics['invalid_reason_missing_time'],
            'Nonpositive Duration': quality_metrics['invalid_reason_nonpositive_duration'],
            'Negative Time': quality_metrics['invalid_reason_negative_time'],
            'Parse Error': quality_metrics['invalid_reason_parse_error']
        }
        
        reasons_df = pd.DataFrame(list(invalid_reasons.items()), columns=['Reason', 'Count'])
        reasons_df = reasons_df[reasons_df['Count'] > 0]
        
        if not reasons_df.empty:
            fig = px.bar(reasons_df, x='Reason', y='Count', text='Count')
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✓ No invalid timestamps")
    
    # Tab 5: Details
    with tab5:
        st.header("Detailed Utterances")
        
        # Utterance table
        display_utts = filtered_utts.copy()
        
        # Select columns
        detail_cols = [
            'utterance_index',
            'speaker',
            'start_sec',
            'end_sec',
            'duration_sec',
            'word_count',
            'text',
            'valid_time'
        ]
        
        display_utts = display_utts[detail_cols]
        
        st.dataframe(
            display_utts.style.format({
                'start_sec': '{:.2f}',
                'end_sec': '{:.2f}',
                'duration_sec': '{:.2f}'
            }),
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = display_utts.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{selected_call_id}_utterances.csv",
            mime="text/csv"
        )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**STT Analytics Platform v0.1.0**")
    st.sidebar.markdown("Phase 1: Core Metrics")


if __name__ == "__main__":
    main()
