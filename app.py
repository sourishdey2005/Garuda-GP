import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Configure Streamlit
st.set_page_config(
    page_title="GarudaGP - F1 Telemetry Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import ui_theme

# Global theme
ui_theme.inject_global_css()

# Initialize session state
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
if 'selected_driver' not in st.session_state:
    st.session_state.selected_driver = None
if 'selected_team' not in st.session_state:
    st.session_state.selected_team = None

# Main header
ui_theme.page_header(
    title="GARUDAGP",
    subtitle="AI-Powered Formula 1 Telemetry & Strategy Intelligence Platform",
    icon="🏎️",
)


# Sidebar navigation
with st.sidebar:
    st.markdown("### ⚙️ NAVIGATION")
    
    page = st.radio(
        "Select Module:",
        [
            "🏠 Dashboard",
            "📊 Session Explorer",
            "👤 Driver Profiles",
            "🏁 Team Intelligence",
            "📈 Telemetry Analysis",
            "🎯 Strategy Simulator",
            "🤖 AI Analytics",
            "⚡ Live Command Center",
            "🧪 Advanced 3D Visualization Lab"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🔄 UTILITIES")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Data"):
            st.session_state.refresh_counter += 1
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📡 DATA SOURCE")
    st.info("🔗 OpenF1 API + FastF1\n\nLive telemetry from official F1 sources")

# Import pages
import dashboard
import session_explorer
import driver_profiles
import team_intelligence
import telemetry_analysis
import strategy_simulator
import ai_analytics
import command_center
import advanced_3d_visualizations


# Route to pages
if page == "🏠 Dashboard":
    dashboard.render()
elif page == "📊 Session Explorer":
    session_explorer.render()
elif page == "👤 Driver Profiles":
    driver_profiles.render()
elif page == "🏁 Team Intelligence":
    team_intelligence.render()
elif page == "📈 Telemetry Analysis":
    telemetry_analysis.render()
elif page == "🎯 Strategy Simulator":
    strategy_simulator.render()
elif page == "🤖 AI Analytics":
    ai_analytics.render()
elif page == "⚡ Live Command Center":
    command_center.render()
elif page == "🧪 Advanced 3D Visualization Lab":
    advanced_3d_visualizations.render()

# Footer
ui_theme.footer()
