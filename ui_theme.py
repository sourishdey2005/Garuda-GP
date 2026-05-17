import streamlit as st


# Centralized UI theme + reusable UI helpers for GarudaGP (Streamlit).


def inject_global_css() -> None:
    """Inject global CSS used across the whole app."""
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@500;700;800;900&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: #050816 !important;
        background-image: radial-gradient(circle at 15% 50%, rgba(0, 229, 255, 0.04), transparent 50%), 
                          radial-gradient(circle at 85% 30%, rgba(255, 208, 0, 0.04), transparent 50%) !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #081122 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif;
    }

    /* Headers / Sections */
    .gg-main-header {
        background: rgba(18, 25, 45, 0.65);
        border-left: 4px solid #FFD000;
        padding: 24px;
        border-radius: 22px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 208, 0, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid #FFD000;
        transition: all 0.3s ease;
    }
    
    .gg-main-header:hover {
        box-shadow: 0 8px 32px rgba(255, 208, 0, 0.15), inset 0 0 20px rgba(255, 208, 0, 0.05);
    }

    .gg-main-header h1 {
        color: #FFFFFF;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(255, 208, 0, 0.3);
        text-transform: uppercase;
    }

    .gg-main-header p {
        color: #B6C2D9;
        font-size: 1rem;
        margin-top: 0.5rem;
        letter-spacing: 0.5px;
    }

    .section-header, .gg-section-header {
        color: #00E5FF;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(0, 229, 255, 0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
    }

    .gg-subheader {
        color: rgba(255, 255, 255, 0.88);
        font-size: 1.05rem;
        font-weight: 600;
        margin: 1rem 0 0.75rem;
        font-family: 'Inter', sans-serif;
    }

    .gg-card, .metric-card, .driver-card {
        background: rgba(18, 25, 45, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    .gg-card:hover, .metric-card:hover, .driver-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 229, 255, 0.3);
        box-shadow: 0 12px 40px rgba(0, 229, 255, 0.15);
    }

    /* Streamlit Native Metrics override */
    [data-testid="stMetric"] {
        background: rgba(18, 25, 45, 0.85);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(16px);
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 208, 0, 0.3);
        box-shadow: 0 12px 40px rgba(255, 208, 0, 0.15);
    }
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #FFD000 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(255, 208, 0, 0.2);
    }
    [data-testid="stMetricLabel"] {
        color: #B6C2D9 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'Inter', sans-serif !important;
        color: #00FFB3 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Orbitron', sans-serif !important;
        color: #00E5FF !important;
        background: rgba(18, 25, 45, 0.85) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* Input fields */
    .stSelectbox > div > div {
        background: rgba(18, 25, 45, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div:hover {
        border-color: #00E5FF !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
    }
    .stSelectbox label {
        color: #B6C2D9 !important;
        font-size: 0.9rem !important;
    }

    /* Tabs */
    [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    [data-baseweb="tab"] {
        font-family: 'Orbitron', sans-serif !important;
        color: #6F7B96 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none !important;
        background-color: transparent !important;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00E5FF !important;
    }
    [aria-selected="true"] [data-baseweb="tab"] {
        color: #00E5FF !important;
        border-bottom: 2px solid #00E5FF !important;
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.4) !important;
    }

    /* Dataframes / Tables */
    [data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), rgba(0, 229, 255, 0.05)) !important;
        border: 1px solid rgba(0, 229, 255, 0.4) !important;
        color: #00E5FF !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: rgba(0, 229, 255, 0.2) !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4) !important;
        transform: translateY(-2px) !important;
        color: #FFF !important;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #050816;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 229, 255, 0.5);
    }

    /* Footer */
    .gg-footer {
        text-align: center;
        padding: 30px 20px;
        margin-top: 40px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        color: #6F7B96;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        backdrop-filter: blur(10px);
    }

    .gg-footer a {
        color: #00E5FF;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    .gg-footer a:hover {
        color: #FFD000;
        text-shadow: 0 0 10px rgba(255, 208, 0, 0.5);
    }
</style>
""",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str = "🏎️") -> None:
    st.markdown(
        f"""
<div class="gg-main-header">
  <h1>{icon} <span style="color:#FFFFFF">{title}</span></h1>
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
  <p style="font-family: 'Orbitron', sans-serif; color: #FFFFFF; font-weight: 600; letter-spacing: 1px;">GarudaGP © 2026</p>
  <p>AI-Powered Motorsport Intelligence &nbsp;•&nbsp; Telemetry Engine Active</p>
  <p style="margin-top: 10px;">
      <a href="https://www.linkedin.com/in/sourish-dey-20b170206/?skipRedirect=true" target="_blank">LinkedIn</a>
      &nbsp;|&nbsp;
      <a href="https://sourishdeyportfolio.vercel.app/" target="_blank">Portfolio</a>
  </p>
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
        font=dict(family="Inter, sans-serif", color="#B6C2D9")
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.06)", title_font=dict(color="#B6C2D9"))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.06)", title_font=dict(color="#B6C2D9"))
    return fig
