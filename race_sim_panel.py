import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from data_model import _seeded, DRIVER_COLORS


def _hex_from_rgb(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Convert HSL (0..360, 0..1, 0..1) to HEX for Plotly.
    """
    h = float(h) % 360.0
    s = float(max(0.0, min(1.0, s)))
    l = float(max(0.0, min(1.0, l)))

    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs(((h / 60.0) % 2.0) - 1.0))
    m = l - c / 2.0

    if 0.0 <= h < 60.0:
        rp, gp, bp = c, x, 0.0
    elif 60.0 <= h < 120.0:
        rp, gp, bp = x, c, 0.0
    elif 120.0 <= h < 180.0:
        rp, gp, bp = 0.0, c, x
    elif 180.0 <= h < 240.0:
        rp, gp, bp = 0.0, x, c
    elif 240.0 <= h < 300.0:
        rp, gp, bp = x, 0.0, c
    else:
        rp, gp, bp = c, 0.0, x

    r = int(round((rp + m) * 255))
    g = int(round((gp + m) * 255))
    b = int(round((bp + m) * 255))
    return _hex_from_rgb(r, g, b)


def _resolve_driver_color(drv: str) -> str:
    """
    Ensure every driver has a distinct, deterministic color.
    Uses data_model.DRIVER_COLORS when available; otherwise generates one
    using a stable hash -> HSL mapping (tuned for dark UI).
    """
    if drv in DRIVER_COLORS:
        return DRIVER_COLORS[drv]

    # Deterministic hue from driver name (golden angle spacing helps distinctness)
    # We keep S/L consistent so colors remain vivid on plotly_dark.
    h_rng = _seeded(hash(f"driver_color|{drv}") % 2**31)
    hue = float(h_rng.integers(0, 360))
    sat = 0.72
    lig = 0.52
    # golden-angle micro-jitter for slightly better spacing without randomness
    hue = (hue + 137.508) % 360.0
    return _hsl_to_hex(hue, sat, lig)


def _simulate_lap_positions(n_laps: int, drivers: list[str], *, seed: int) -> pd.DataFrame:
    """Return DataFrame: columns [lap, driver, pos, speed]. Position is 1..N (1 best)."""
    rng = _seeded(seed)
    n_drivers = max(2, len(drivers))

    # Start positions
    start_pos = np.linspace(n_drivers, 1, n_drivers)  # best driver starts near front
    rng.shuffle(start_pos)

    rows = []
    for i, drv in enumerate(drivers):
        base = float(start_pos[i])
        drift = rng.normal(0, 0.08, n_laps).cumsum() * 0.15
        # small pit-like jumps
        pit_lap = int(rng.integers(max(1, n_laps // 4), max(2, n_laps - n_laps // 4)))
        pit_jump = np.zeros(n_laps)
        if n_laps > 10:
            pit_jump[pit_lap:] += rng.normal(0, 0.6)

        pos_series = base + drift + pit_jump
        pos_series = np.clip(pos_series, 1, n_drivers)

        # Convert to rank per lap (so positions are unique-ish and look like a race)
        # We'll compute ranks after assembling speed.
        speed = 220 + 25 * np.sin(np.linspace(0, 3.1, n_laps) + i * 0.35) + rng.normal(0, 3, n_laps)
        for lap_idx in range(n_laps):
            rows.append({
                "lap": lap_idx + 1,
                "driver": drv,
                "pos_raw": float(pos_series[lap_idx]),
                "speed": float(speed[lap_idx]),
            })

    df = pd.DataFrame(rows)

    # Rank by pos_raw per lap (lower pos_raw => better)
    def _rank_one(g: pd.DataFrame) -> pd.DataFrame:
        g = g.copy()
        g["pos"] = g["pos_raw"].rank(method="first", ascending=True)
        g["pos"] = g["pos"].astype(int)
        return g

    df = df.groupby("lap", group_keys=False).apply(_rank_one)
    df.drop(columns=["pos_raw"], inplace=True)
    return df


def render_race_panel(*, year: int, race: str, drivers: list[str], n_laps: int) -> None:
    st.markdown('<div class="gg-section-header">🏎️ 3D Race Simulation (Lap-by-Lap)</div>', unsafe_allow_html=True)

    if not drivers:
        st.info("No drivers available for simulation.")
        return

    # Use only first 10 for readability/performance
    drivers = drivers[:10]

    # Stable per-session driver colors (ensures uniqueness even when DRIVER_COLORS is incomplete)
    driver_color_map = {drv: _resolve_driver_color(drv) for drv in drivers}

    seed = hash(f"race_sim|{year}|{race}|" + ",".join(drivers)) % 2**31
    df = _simulate_lap_positions(n_laps, drivers, seed=seed)

    # ── Panel A: Lap timeline (3D) ──
    fig_timeline = go.Figure()
    for drv in drivers:
        dfd = df[df["driver"] == drv]
        fig_timeline.add_trace(
            go.Scatter3d(
                x=dfd["lap"],
                y=dfd["pos"],
                z=dfd["speed"],
                mode="lines",
                name=drv,
                line=dict(color=driver_color_map[drv], width=4),
                hovertemplate=(
                    "<b>%{text}</b><br>Lap %{x}<br>Pos %{y}<br>Speed %{z:.0f} km/h"
                    "<extra></extra>"
                ),
                text=[drv] * len(dfd),
            )
        )

    fig_timeline.update_layout(
        template="plotly_dark",
        height=540,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.1)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=10)),
        scene=dict(
            xaxis_title="Lap",
            yaxis_title="Position (1=Leader)",
            zaxis_title="Speed (km/h)",
            yaxis=dict(autorange="reversed"),
            camera=dict(eye=dict(x=1.55, y=-1.75, z=0.95)),
        ),
    )

    st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})

    # ── Panel B: Moving 3D track + driver markers (by lap) ──
    st.markdown("---")
    st.markdown('<div class="gg-section-header">🗺️ Moving 3D Track (Timeline View)</div>', unsafe_allow_html=True)

    # Build a simple parametric 3D “track” (same style as Command Center)
    SCALE = 8.0
    NS = 260
    HW = 3.5
    t_arr = np.linspace(0, 2 * np.pi, NS)

    # Deterministic seed per race
    rng_tr = _seeded(hash(f"track_shape|{year}|{race}") % 2**31)
    ref_path_offset = float(rng_tr.normal(0, 0.12))

    K_STR = 2.8 + 0.25 * np.sin(ref_path_offset)
    K_TURN = 5.2 + 0.35 * np.cos(ref_path_offset)

    def _cx(t):
        return K_TURN * (np.sin(t) + 0.3 * np.sin(2 * t) - 0.1 * np.sin(3 * t))

    def _cy(t):
        return K_STR * (np.cos(t) - 0.15 * np.cos(2 * t) + 0.1 * np.cos(4 * t))

    def _cz(t):
        return 0.7 * np.sin(t) + 0.4 * np.cos(2 * t)

    tx = _cx(t_arr) * SCALE
    ty = _cy(t_arr) * SCALE
    tz = _cz(t_arr) * SCALE

    # Offset inner border for a more track-like ribbon
    gx, gy = np.gradient(tx), np.gradient(ty)
    gl = np.sqrt(gx**2 + gy**2)
    gl[gl == 0] = 1.0
    nx = -gy / gl
    ny = gx / gl

    tx_in = (tx + HW * nx).tolist()
    ty_in = (ty + HW * ny).tolist()

    road_x = tx.tolist() + tx_in[::-1] + [tx.tolist()[0]]
    road_y = ty.tolist() + ty_in[::-1] + [ty.tolist()[0]]
    road_z = tz.tolist() + tz[::-1].tolist() + [tz.tolist()[0]]

    # Create a “position along track” for each driver per lap
    # We use leader order to map faster progress to better positions.
    # Normalize position to progress (1=leader => more progress)
    progress_by_lap = {}
    for lap in range(1, n_laps + 1):
        dlap = df[df["lap"] == lap].sort_values("pos")
        # progress span 0..1 around lap
        # leader near 1.0, others spaced
        max_pos = max(1, len(dlap))
        for idx, row in enumerate(dlap.itertuples(index=False)):
            drv = row.driver
            # idx=0 leader => highest progress
            prog = float(1.0 - idx / max_pos)
            # also add small deterministic jitter based on driver/lap
            j_rng = _seeded(hash(f"prog|{drv}|{year}|{race}|{lap}") % 2**31)
            prog = float(np.clip(prog + j_rng.normal(0, 0.03), 0.02, 0.98))
            progress_by_lap[(lap, drv)] = prog

    # Helper: map progress 0..1 to track index
    def _progress_to_xy(lap, drv):
        prog = progress_by_lap[(lap, drv)]
        # phase around t
        ti = int(round(prog * (NS - 1)))
        return float(tx[ti]), float(ty[ti]), float(tz[ti])

    # Initial frame at lap=1
    init_lap = 1
    init_x, init_y, init_z, init_text = [], [], [], []
    for drv in drivers:
        x0, y0, z0 = _progress_to_xy(init_lap, drv)
        init_x.append(x0)
        init_y.append(y0)
        init_z.append(z0)
        init_text.append(drv)

    fig_track = go.Figure()
    # Track ribbon (dimmed so markers/readability stay professional)
    fig_track.add_trace(
        go.Scatter3d(
            x=road_x,
            y=road_y,
            z=road_z,
            mode="lines",
            line=dict(color="rgba(180,180,180,0.55)", width=3),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Centerline overlay for a more “track-like” professional look
    fig_track.add_trace(
        go.Scatter3d(
            x=tx.tolist() + [tx.tolist()[0]],
            y=ty.tolist() + [ty.tolist()[0]],
            z=tz.tolist() + [tz.tolist()[0]],
            mode="lines",
            line=dict(color="rgba(255,215,0,0.20)", width=2),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Frame traces (markers for drivers) - one trace per driver for stable legend/colors
    for drv in drivers:
        x0, y0, z0 = _progress_to_xy(init_lap, drv)
        fig_track.add_trace(
            go.Scatter3d(
                x=[x0],
                y=[y0],
                z=[z0],
                mode="markers+text",
                marker=dict(size=7, color=driver_color_map[drv], opacity=0.95),
                text=[drv],
                textposition="top center",
                name=drv,
                textfont=dict(color=driver_color_map[drv], size=10),
                hovertemplate="<b>%{text}</b><br>Lap %{customdata[0]}<br>x %{x:.1f}, y %{y:.1f}<extra></extra>",
                customdata=[[init_lap]],
                showlegend=True,
            )
        )

    # Animation frames per lap
    frames = []
    for lap in range(1, n_laps + 1):
        frame_traces = []
        for drv in drivers:
            x1, y1, z1 = _progress_to_xy(lap, drv)
            frame_traces.append(
                go.Scatter3d(
                    x=[x1],
                    y=[y1],
                    z=[z1],
                    mode="markers+text",
                    marker=dict(size=7, color=driver_color_map[drv], opacity=0.95),
                    text=[drv],
                    textposition="top center",
                    customdata=[[lap]],
                    showlegend=False,
                    hovertemplate="<b>%{text}</b><br>Lap %{customdata[0]}<br>x %{x:.1f}, y %{y:.1f}<extra></extra>",
                )

            )
        frames.append(go.Frame(data=frame_traces, name=str(lap)))


    fig_track.frames = frames

    # Build slider steps (keep functional but avoid an overly dense slider)
    slider_step_laps = [*range(1, n_laps + 1)]
    if n_laps > 24:
        slider_step_laps = list(range(1, n_laps + 1, 2))
        if slider_step_laps[-1] != n_laps:
            slider_step_laps.append(n_laps)

    fig_track.update_layout(
        template="plotly_dark",
        height=620,
        margin=dict(l=0, r=0, t=26, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.1)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
        ),
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            camera=dict(eye=dict(x=1.2, y=-1.45, z=0.85)),
            aspectmode="data",
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.02,
                y=0.02,
                xanchor="left",
                yanchor="bottom",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 70, "redraw": False}, "fromcurrent": True}],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[[str(lap)], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                        label=str(lap),
                    )
                    for lap in slider_step_laps
                ],
                x=0.06,
                y=0.00,
                currentvalue=dict(prefix="Lap: "),
                len=0.88,
                activebgcolor="rgba(255,215,0,0.25)",
            )
        ],
    )

    # Make markers slightly clearer (without cluttering too much text)
    for tr in fig_track.data:
        if getattr(tr, "mode", "") and "markers" in tr.mode:
            tr.textposition = "top center"
            tr.hoverlabel = dict(bgcolor="rgba(0,0,0,0.85)", bordercolor="rgba(255,215,0,0.25)")

    st.plotly_chart(fig_track, use_container_width=True, config={"displayModeBar": False})

    # ── Metrics panel (existing) ──
    last = df[df["lap"] == df["lap"].max()].sort_values("pos")
    leader = last.iloc[0]
    best_speed = df.sort_values("speed", ascending=False).iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Race Leader (final)", str(leader["driver"]), delta=f"Pos {int(leader['pos'])}")
    with col2:
        st.metric(
            "Fastest Avg Speed",
            str(best_speed["driver"]),
            delta=f"{df[df['driver']==best_speed['driver']]['speed'].mean():.0f} km/h",
        )
    with col3:
        st.metric("Laps Simulated", str(n_laps), delta=race)

    first = df[df["lap"] == 1][["driver", "pos"]].set_index("driver")
    last_pos = df[df["lap"] == n_laps][["driver", "pos"]].set_index("driver")
    delta = (first["pos"] - last_pos["pos"]).rename("pos_gain")
    delta_df = delta.reset_index().rename(columns={"driver": "Driver"})
    delta_df["pos_gain"] = delta_df["pos_gain"].astype(int)

    st.markdown("---")
    st.markdown("**Position Gain (Lap 1 → Final Lap)**")
    st.dataframe(
        delta_df.sort_values("pos_gain", ascending=False).head(10),
        use_container_width=True,
        hide_index=True,
    )


