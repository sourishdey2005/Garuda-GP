import streamlit as st
import numpy as np
import plotly.graph_objects as go


DRIVER_COLORS = {
    "Max Verstappen": "#1E5BC6",
    "Lewis Hamilton": "#00D2BE",
    "Charles Leclerc": "#DC0000",
    "Lando Norris": "#FF8700"
}


VISUALIZATION_SPECS = [
    {"id": 1, "tab": "3D Performance Analytics", "name": "3D Lap Time Terrain"},
    {"id": 2, "tab": "3D Performance Analytics", "name": "3D Corner Speed Mesh"},
    {"id": 3, "tab": "3D Performance Analytics", "name": "3D Driver Consistency Sphere"},
    {"id": 4, "tab": "3D Performance Analytics", "name": "3D Sector Delta Volume"},
    {"id": 5, "tab": "3D Performance Analytics", "name": "3D Racing Line Evolution"},
    {"id": 6, "tab": "3D Telemetry Lab", "name": "3D Telemetry Tunnel"},
    {"id": 7, "tab": "3D Telemetry Lab", "name": "3D Brake Pressure Dynamics"},
    {"id": 8, "tab": "3D Telemetry Lab", "name": "3D Throttle Waveform"},
    {"id": 9, "tab": "3D Telemetry Lab", "name": "3D Gear Shift Matrix"},
    {"id": 10, "tab": "3D Telemetry Lab", "name": "3D RPM Energy Landscape"},
    {"id": 11, "tab": "3D Strategy Intelligence", "name": "3D Pit Window Optimizer"},
    {"id": 12, "tab": "3D Strategy Intelligence", "name": "3D Tyre Degradation Cube"},
    {"id": 13, "tab": "3D Strategy Intelligence", "name": "3D Undercut Advantage Model"},
    {"id": 14, "tab": "3D Strategy Intelligence", "name": "3D Safety Car Impact Field"},
    {"id": 15, "tab": "3D Strategy Intelligence", "name": "3D Fuel Load Predictor"},
    {"id": 16, "tab": "3D Aerodynamics", "name": "3D Airflow Simulation"},
    {"id": 17, "tab": "3D Aerodynamics", "name": "3D Downforce Heat Surface"},
    {"id": 18, "tab": "3D Aerodynamics", "name": "3D Drag Coefficient Analyzer"},
    {"id": 19, "tab": "3D Aerodynamics", "name": "3D Wind Tunnel Replay"},
    {"id": 20, "tab": "3D Aerodynamics", "name": "3D Aero Stability Grid"},
    {"id": 21, "tab": "3D Race Simulation", "name": "3D Real-Time Race Simulator"},
    {"id": 22, "tab": "3D Race Simulation", "name": "3D Car Swarm Tracker"},
    {"id": 23, "tab": "3D Race Simulation", "name": "3D Overtake Probability Cloud"},
    {"id": 24, "tab": "3D Race Simulation", "name": "3D DRS Activation Zones"},
    {"id": 25, "tab": "3D Race Simulation", "name": "3D Race Flow Dynamics"},
    {"id": 26, "tab": "3D AI & Predictive Systems", "name": "3D AI Championship Predictor"},
    {"id": 27, "tab": "3D AI & Predictive Systems", "name": "3D Neural Race Outcome Graph"},
    {"id": 28, "tab": "3D AI & Predictive Systems", "name": "3D Driver Risk Heatspace"},
    {"id": 29, "tab": "3D AI & Predictive Systems", "name": "3D Predictive Pace Engine"},
    {"id": 30, "tab": "3D AI & Predictive Systems", "name": "3D Strategic Decision Matrix"},
    {"id": 31, "tab": "3D Driver Biometrics", "name": "3D Heart Rate Stress Map"},
    {"id": 32, "tab": "3D Driver Biometrics", "name": "3D Eye Tracking Simulator"},
    {"id": 33, "tab": "3D Driver Biometrics", "name": "3D Reaction Time Sphere"},
    {"id": 34, "tab": "3D Driver Biometrics", "name": "3D Fatigue Evolution"},
    {"id": 35, "tab": "3D Driver Biometrics", "name": "3D Driver Cognitive Load"},
    {"id": 36, "tab": "3D Environment & Weather", "name": "3D Weather Evolution Globe"},
    {"id": 37, "tab": "3D Environment & Weather", "name": "3D Rainfall Density Map"},
    {"id": 38, "tab": "3D Environment & Weather", "name": "3D Track Temperature Grid"},
    {"id": 39, "tab": "3D Environment & Weather", "name": "3D Wind Direction Field"},
    {"id": 40, "tab": "3D Environment & Weather", "name": "3D Visibility Simulation"},
    {"id": 41, "tab": "3D Team Operations", "name": "3D Pit Crew Motion Capture"},
    {"id": 42, "tab": "3D Team Operations", "name": "3D Garage Operations Layout"},
    {"id": 43, "tab": "3D Team Operations", "name": "3D Logistics Supply Chain"},
    {"id": 44, "tab": "3D Team Operations", "name": "3D Communication Signal Flow"},
    {"id": 45, "tab": "3D Team Operations", "name": "3D Resource Allocation Matrix"},
    {"id": 46, "tab": "3D Experimental Concepts", "name": "Quantum Strategy Visualization"},
    {"id": 47, "tab": "3D Experimental Concepts", "name": "Holographic Circuit Projection"},
    {"id": 48, "tab": "3D Experimental Concepts", "name": "3D Time Distortion Replay"},
    {"id": 49, "tab": "3D Experimental Concepts", "name": "Neural Driver Twin Simulation"},
    {"id": 50, "tab": "3D Experimental Concepts", "name": "Metaverse Race Command Center"},
]

NOISE_CACHE = {}


def _rng(seed: int):
    if seed not in NOISE_CACHE:
        NOISE_CACHE[seed] = np.random.default_rng(seed)
    return NOISE_CACHE[seed]


def _fig_layout(title: str, height: int = 450):
    return dict(
        template="plotly_dark",
        height=height,
        paper_bgcolor="#0B1020",
        plot_bgcolor="#0B1020",
        title=title,
        font=dict(color="#FFFFFF"),
        margin=dict(l=30, r=30, t=50, b=30),
    )


def _plot_terrain(seed: int, driver: str):
    rng = _rng(seed)
    n_laps, n_sec = 10, 15
    x = np.linspace(0, 1, n_sec)
    y = np.linspace(1, n_laps, n_laps)
    X, Y = np.meshgrid(x, y)
    base = 1.0 + 0.08 * np.sin(2 * np.pi * X) + 0.03 * np.cos(3 * np.pi * X)
    drift = -0.08 * (Y - 1) / max(n_laps - 1, 1)
    Z = (base + drift) * 100
    Z += rng.normal(0, 2, Z.shape)
    Z = np.clip(Z, 70, 120)
    color = DRIVER_COLORS.get(driver, "#ffd700")
    fig = go.Figure(go.Surface(
        x=X * 100, y=Y, z=Z,
        colorscale=[(0, "#1f77b4"), (0.5, color), (1, "#ff6b6b")],
        opacity=0.92, showscale=False
    ))
    fig.update_layout(
        _fig_layout(f"3D Lap Time Terrain — {driver}", 420),
        scene=dict(xaxis_title="Sector %", yaxis_title="Lap #", zaxis_title="Lap Index")
    )
    return fig


def _plot_sphere(seed: int, driver: str):
    rng = _rng(seed)
    n = 120
    center = rng.uniform(-0.5, 0.5, 3)
    pts = rng.normal(0, 1, (n, 3)) * 0.7 + center
    dist = np.linalg.norm(pts - center, axis=1)
    size = np.clip(10 - dist * 4, 1, 6)
    col = np.clip(1 - dist / (np.max(dist) + 1e-9), 0, 1)
    fig = go.Figure(go.Scatter3d(
        x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
        mode="markers",
        marker=dict(size=size, color=col, colorscale="Turbo", opacity=0.85, showscale=False),
        name=driver
    ))
    fig.update_layout(
        _fig_layout(f"3D Driver Consistency Sphere — {driver}", 420),
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z")
    )
    return fig


def _plot_scatter(seed: int, title: str, driver: str, labels):
    rng = _rng(seed)
    n = 100
    x, y, z = rng.normal(0, 1, (3, n))
    col = np.clip((x + y + z) / 3.5 + 0.5, 0, 1)
    fig = go.Figure(go.Scatter3d(
        x=x, y=y, z=z, mode="markers",
        marker=dict(size=4, color=col, colorscale="RdYlGn", opacity=0.8)
    ))
    fig.update_layout(_fig_layout(title, 380), scene=dict(xaxis_title=labels[0], yaxis_title=labels[1], zaxis_title=labels[2]))
    return fig


def _plot_surface_grid(seed: int, title: str, labels=("X", "Y", "Z")):
    rng = _rng(seed)
    nx, ny = 12, 10
    xs = np.linspace(0, 1, nx)
    ys = np.linspace(0, 1, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = 0.6 + 0.3 * np.sin(2 * np.pi * X) * np.cos(2 * np.pi * Y) + 0.08 * rng.normal(0, 1, (ny, nx))
    Z = np.clip(Z, 0, 1.2)
    fig = go.Figure(go.Surface(x=X, y=Y, z=Z, colorscale="YlOrRd", opacity=0.9, showscale=False))
    fig.update_layout(_fig_layout(title, 420), scene=dict(xaxis_title=labels[0], yaxis_title=labels[1], zaxis_title=labels[2]))
    return fig


def _create_chart(vid, seed, driver, name):
    if vid == 1:
        return _plot_terrain(seed, driver)
    elif vid == 3:
        return _plot_sphere(seed, driver)
    elif vid in (2, 4, 5):
        return _plot_surface_grid(seed, name)
    elif vid in (6, 7, 8, 9, 10):
        return _plot_scatter(seed, name, driver, ("X", "Y", "Z"))
    else:
        if vid % 2 == 0:
            return _plot_surface_grid(seed, name)
        else:
            return _plot_scatter(seed, name, driver, ("X", "Y", "Z"))


def render():
    st.markdown("<div class=\"gg-section-header\">🧠 Advanced 3D Visualization Lab</div>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Controls", expanded=False):
        driver = st.selectbox("Driver", ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc", "Lando Norris"], index=0)
        year = st.selectbox("Season", list(reversed(range(2000, 2027))), index=25)
        quality = st.selectbox("Quality", ["Low", "Medium", "High"], index=1)
    
    seed = hash(driver + str(year) + quality) % (2**31)
    
    # To prevent browser WebGL context limits (which cause blank screens when 
    # rendering too many 3D charts at once), we use selectboxes instead of tabs.
    categories = list(dict.fromkeys(spec["tab"] for spec in VISUALIZATION_SPECS))
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Select Category", categories)
        
    specs_in_category = [s for s in VISUALIZATION_SPECS if s["tab"] == selected_category]
    with col2:
        selected_vis = st.selectbox("Select Visualization", [s["name"] for s in specs_in_category])
        
    spec = next(s for s in specs_in_category if s["name"] == selected_vis)
    vid = spec["id"]
    
    st.markdown(f"### {spec['name']}")
    with st.spinner("Rendering..."):
        try:
            fig = _create_chart(vid, seed + vid * 37, driver, spec["name"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "responsive": True})
        except Exception as e:
            st.error(f"Render error: {e}")