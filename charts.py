import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st

def create_speed_trace(distance: np.ndarray, speed: np.ndarray, driver_name: str = "Driver") -> go.Figure:
    """Create speed trace chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distance,
        y=speed,
        mode='lines',
        name='Speed',
        line=dict(color='#ffd700', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 215, 0, 0.1)'
    ))
    
    fig.update_layout(
        title=f"{driver_name} - Speed Trace",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    
    return fig

def create_position_evolution(laps: np.ndarray, positions: dict) -> go.Figure:
    """Create position evolution chart"""
    fig = go.Figure()
    
    colors = ['#ffd700', '#ff6b6b', '#4ecdc4', '#00ff00', '#ff00ff']
    
    for idx, (driver, pos_data) in enumerate(positions.items()):
        fig.add_trace(go.Scatter(
            x=laps,
            y=pos_data,
            mode='lines',
            name=driver,
            line=dict(color=colors[idx % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title="Position Evolution",
        xaxis_title="Lap",
        yaxis_title="Position",
        yaxis=dict(autorange="reversed"),
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    
    return fig

def create_delta_chart(distance: np.ndarray, delta: np.ndarray) -> go.Figure:
    """Create delta/gap chart"""
    fig = go.Figure()
    
    colors = ['#ff6b6b' if d > 0 else '#00ff00' for d in delta]
    
    fig.add_trace(go.Scatter(
        x=distance,
        y=delta,
        mode='lines',
        name='Delta',
        fill='tozeroy',
        line=dict(color='#ff6b6b', width=2),
        fillcolor='rgba(255, 107, 107, 0.2)'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
    
    fig.update_layout(
        title="Time Delta",
        xaxis_title="Distance (m)",
        yaxis_title="Gap (seconds)",
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    
    return fig

def create_radar_chart(categories: list, values: list, driver_name: str = "Driver") -> go.Figure:
    """Create radar/spider chart"""
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=driver_name,
        line=dict(color='#ffd700'),
        fillcolor='rgba(255, 215, 0, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=True,
                linewidth=2,
                gridcolor='rgba(255, 215, 0, 0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 215, 0, 0.2)'
            )
        ),
        showlegend=False,
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_comparison_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create comparison bar chart"""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=y_col,
        color_continuous_scale=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    )
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        height=350,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    
    return fig

def create_heatmap(data: np.ndarray, x_labels: list, y_labels: list, title: str = "") -> go.Figure:
    """Create heatmap visualization"""
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='YlOrRd'
    ))
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
    )
    
    return fig

def create_multi_line_chart(data: dict, x_label: str = "X", y_label: str = "Y", title: str = "") -> go.Figure:
    """Create multi-line chart"""
    fig = go.Figure()
    
    colors = ['#ffd700', '#ff6b6b', '#4ecdc4', '#00ff00', '#ff00ff']
    
    for idx, (name, y_data) in enumerate(data.items()):
        fig.add_trace(go.Scatter(
            y=y_data,
            mode='lines',
            name=name,
            line=dict(color=colors[idx % len(colors)], width=2)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_dark',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    
    return fig
