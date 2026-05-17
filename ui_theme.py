import streamlit as st


# Centralized UI theme + reusable UI helpers for GarudaGP (Streamlit).


def inject_global_css() -> None:
    """Inject global CSS used across the whole app."""
    st.markdown(
        """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 20, 40, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 215, 0, 0.1);
    }

    /* Headers / Sections */
    .gg-main-header {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.05), rgba(255, 215, 0, 0.02));
        border-left: 4px solid #ffd700;
        padding: 1.4rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(255, 215, 0, 0.08);
        backdrop-filter: blur(10px);
    }

    .gg-main-header h1 {
        color: #ffd700;
        font-size: 2.35rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
        letter-spacing: -0.8px;
    }

    .gg-main-header p {
        color: #8a8a8a;
        font-size: 0.96rem;
        margin-top: 0.55rem;
    }

    .gg-section-header {
        color: #ffd700;
        font-size: 1.45rem;
        font-weight: 750;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.55rem;
        border-bottom: 2px solid rgba(255, 215, 0, 0.28);
        letter-spacing: 0.2px;
    }

    .gg-subheader {
        color: rgba(255, 255, 255, 0.88);
        font-size: 1.05rem;
        font-weight: 650;
        margin: 1rem 0 0.75rem;
    }

    .gg-card {
        background: linear-gradient(135deg, rgba(20, 30, 60, 0.75), rgba(30, 40, 70, 0.75));
        border: 1px solid rgba(255, 215, 0, 0.15);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 34px rgba(0, 0, 0, 0.30);
    }

    .gg-metric-card {
        padding: 1.2rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .gg-metric-card:hover {
        border-color: rgba(255, 215, 0, 0.42);
        box-shadow: 0 14px 48px rgba(255, 215, 0, 0.12);
        transform: translateY(-2px);
    }

    /* Input fields */
    input, select {
        background: rgba(30, 40, 70, 0.8) !important;
        border: 1px solid rgba(255, 215, 0, 0.2) !important;
        color: #e0e0e0 !important;
        border-radius: 6px !important;
    }

    input:focus, select:focus {
        border-color: #ffd700 !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.2) !important;
    }

    /* Tabs */
    [data-baseweb="tab-list"] {
        border-bottom: 2px solid rgba(255, 215, 0, 0.1) !important;
    }

    [data-baseweb="tab"] {
        color: #888 !important;
    }

    [aria-selected="true"] [data-baseweb="tab"] {
        color: #ffd700 !important;
        border-bottom: 3px solid #ffd700 !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 215, 0, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 215, 0, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 215, 0, 0.5);
    }

    /* Footer */
    .gg-footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 215, 0, 0.1);
        color: #6a6a6a;
        font-size: 0.85rem;
    }

    .gg-footer a {
        color: #ffd700;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    .gg-footer a:hover {
        color: #ffed4e;
        text-decoration: underline;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str = "🏎️") -> None:
    st.markdown(
        f"""
<div class="gg-main-header">
  <h1>{icon} {title}</h1>
  <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(text: str) -> None:
    st.markdown(
        f'<div class="gg-section-header">{text}</div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        """
<div class="gg-footer">
  <p><strong>Made by Sourish Dey</strong></p>
  <p>
    <a href="https://www.linkedin.com/in/sourish-dey-20b170206/?skipRedirect=true" target="_blank">LinkedIn</a>
    &nbsp;•&nbsp;
    <a href="https://sourishdeyportfolio.vercel.app/" target="_blank">Portfolio</a>
  </p>
  <p style="margin-top: 1rem; color: #555;">GarudaGP v1.0 - Premium F1 Telemetry Intelligence Platform</p>
</div>
""",
        unsafe_allow_html=True,
    )


def plotly_common_layout(fig, *, height: int = 360):
    """Apply common styling to Plotly figures (dark theme + grid colors)."""
    # Import kept local to avoid hard dependency during non-chart import.
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.1)",
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,215,0,0.1)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,215,0,0.1)")
    return fig

