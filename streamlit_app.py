"""
Streamlit Cloud Entry Point for STT Analytics Dashboard
Directly executes the dashboard app.
"""

import streamlit as st
import sys
from pathlib import Path

# MUST be first Streamlit command
st.set_page_config(
    page_title="STT Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to path so stta module can be imported
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and execute main function
from stta.dashboard.app import main

# Run the dashboard
main()
