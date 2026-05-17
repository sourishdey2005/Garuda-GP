import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

class MetricCard:
    """Reusable metric card component"""
    
    @staticmethod
    def render(label: str, value: str, delta: str = "", status: str = "🟢"):
        """Render a metric card"""
        st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="font-size: 0.85rem; color: #888;">
                        {label}
                    </div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #ffd700; margin-top: 0.5rem;">
                        {value}
                    </div>
                    {f'<div style="font-size: 0.75rem; color: #aaa; margin-top: 0.3rem;">{delta}</div>' if delta else ''}
                </div>
                <div style="font-size: 1.5rem; margin-left: 1rem;">
                    {status}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_metric_grid(metrics: list, cols: int = 4):
    """Render multiple metrics in grid"""
    metric_cols = st.columns(cols)
    
    for idx, metric in enumerate(metrics):
        with metric_cols[idx % cols]:
            MetricCard.render(
                label=metric['label'],
                value=metric['value'],
                delta=metric.get('delta', ''),
                status=metric.get('status', '🟢')
            )

class DriverCard:
    """Reusable driver card component"""
    
    @staticmethod
    def render(driver_name: str, team: str, points: int, position: int, best_lap: str):
        """Render driver card"""
        st.markdown(f"""
        <div class="driver-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #ffd700;">
                        {position}. {driver_name}
                    </div>
                    <div style="font-size: 0.85rem; color: #888; margin-top: 0.3rem;">
                        {team}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #00ff00;">
                        {points}pts
                    </div>
                    <div style="font-size: 0.75rem; color: #888; margin-top: 0.2rem;">
                        {best_lap}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

class StatBadge:
    """Reusable stat badge"""
    
    @staticmethod
    def render(label: str, value: str, color: str = "#ffd700"):
        """Render stat badge"""
        st.markdown(f"""
        <span class="telemetry-badge" style="background: {color};">
            {label}: {value}
        </span>
        """, unsafe_allow_html=True)
