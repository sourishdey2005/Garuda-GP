import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.insert(0, '.')
from data_model import (
    DRIVERS, DRIVER_COLORS, get_driver_lap_data,
    get_race_results, get_races, _seeded,
)

def render():
    st.markdown('<div class="section-header">📈 Telemetry Analysis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    year = col1.selectbox(
        "Season",
        list(reversed(range(2000, 2027))),
        key="tel_year",
        index=25,
    )
    races = get_races(year)
    sel_race = col2.selectbox(
        "Race", races,
        key="tel_race",
    )
    drivers_in_year = DRIVERS.get(year, DRIVERS[2025])
    d1 = col3.selectbox(
        "Metric View", drivers_in_year,
        index=0, key="tel_metric",
    )

    # Motorsport telemetry always needs two drivers for comparison
    d2 = st.selectbox(
        f"Compare against",
        [dd for dd in drivers_in_year if dd != d1],
        index=1 if len(drivers_in_year) > 1 else 0,
        key="tel_d2",
    )

    metric_type = st.selectbox(
        "Telemetry Channel",
        ['Speed', 'Throttle', 'Brake', 'Gear', 'RPM', 'DRS'],
        key="tel_type",
    )
    generate = st.button("🔬 Generate Telemetry", key="tel_gen")

    # Fetch lap data
    ld1 = get_driver_lap_data(year, d1, sel_race)
    ld2 = get_driver_lap_data(year, d2, sel_race)
    res  = get_race_results(year, sel_race)
    info_t = {
        'Bahrain GP': ('Bahrain International Circuit', 5.412),
        'Australian GP': ('Albert Park Circuit', 5.278),
        'Chinese GP': ('Shanghai International Circuit', 5.451),
        'Japanese GP': ('Suzuka Circuit', 5.807),
        'Monaco GP': ('Circuit de Monaco', 3.337),
        'British GP': ('Silverstone Circuit', 5.891),
        'Italian GP': ('Monza Circuit', 5.793),
        'Belgian GP': ('Spa-Francorchamps', 7.004),
        'Singapore GP': ('Marina Bay Circuit', 4.064),
        'United States GP': ('CO Circuit of the Americas', 5.513),
    }
    track_name, track_len = info_t.get(sel_race, ('Unknown', 5.5))
    dist_arr = np.linspace(0, track_len * 1000, 500)

    s_tel = _seeded(hash(d1 + d2 + str(year) + sel_race + metric_type) % 2**31)

    # Map metric → generated arrays
    data1 = _channel(d1, metric_type, s_tel, track_len, ld1['best_lap'])
    data2 = _channel(d2, metric_type, s_tel, track_len, ld2['best_lap'])
    delta_arr = data1 - data2

    st.markdown("---")

    # ── Channel comparison ──
    st.markdown(f'<div class="section-header">⚡ {d1} vs {d2} – {metric_type}</div>', unsafe_allow_html=True)
    col_c1, col_c2 = st.columns([1, 1], gap="large")

    with col_c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=data1.tolist(),
            mode='lines', name=d1,
            line=dict(color=DRIVER_COLORS.get(d1, '#ffd700'), width=2),
        ))
        fig.add_trace(go.Scatter(
            x=dist_arr, y=data2.tolist(),
            mode='lines', name=d2,
            line=dict(color=DRIVER_COLORS.get(d2, '#00d2be'), width=2),
            yaxis='y2',
        ))
        fig.update_layout(
            title=f'{metric_type} Comparison',
            xaxis_title='Distance (m)',
            yaxis_title=f'{d1} {metric_type}',
            yaxis2=dict(title=f'{d2} {metric_type}', overlaying='y', side='right'),
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            hovermode='x unified',
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=delta_arr.tolist(),
            mode='lines', name='Gap',
            fill='tozeroy', line=dict(width=2, color='#ff6b6b'),
            fillcolor='rgba(255,107,107,0.3)',
        ))
        fig.add_hline(y=0, line_dash='dash', line_color='white', opacity=0.5)
        fig.update_layout(
            title='Time Delta',
            xaxis_title='Distance (m)',
            yaxis_title=f'Δ {metric_type}',
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False,
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Pedals ──
    st.markdown('<div class="section-header">🎮 Pedal Input Analysis</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns([1, 1], gap="large")
    s_ped = _seeded(hash(d1 + str(year)) % 2**31)
    throttle_arr = np.clip(50 + 40 * np.sin(dist_arr / 420) + s_ped.normal(0, 4, len(dist_arr)), 0, 100)
    brake_arr    = np.clip(40 * (1 - np.cos(dist_arr / 420)) + s_ped.normal(0, 4, len(dist_arr)), 0, 100)

    with col_p1:
        st.markdown(f"**Throttle Usage – {d1}**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=throttle_arr.tolist(),
            mode='lines', name='Throttle %',
            fill='tozeroy', line=dict(color='#00ff00', width=2),
            fillcolor='rgba(0,255,0,0.15)'
        ))
        fig.update_layout(
            xaxis_title='Distance (m)', yaxis_title='Throttle %',
            template='plotly_dark', height=320,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_p2:
        st.markdown(f"**Brake Usage – {d1}**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=brake_arr.tolist(),
            mode='lines', name='Brake %',
            fill='tozeroy', line=dict(color='#ff4444', width=2),
            fillcolor='rgba(255,68,68,0.15)'
        ))
        fig.update_layout(
            xaxis_title='Distance (m)', yaxis_title='Brake %',
            template='plotly_dark', height=320,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Powertrain ──
    st.markdown('<div class="section-header">⚙️ Powertrain Telemetry</div>', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns([1, 1], gap="large")
    s_eng = _seeded(hash(d1 + d2 + 'powertrain') % 2**31)
    gears   = ['1', '2', '3', '4', '5', '6', '7', '8']
    rpm_bin = ['≤8000', '8000-10000', '10000-12000', '12000-14000', '14000-16000', '16000+']

    with col_g1:
        st.markdown("**Gear Usage Distribution**")
        gear1 = s_eng.integers(1, 8, len(gears)).astype(float).tolist()
        gear2 = s_eng.integers(1, 8, len(gears)).astype(float).tolist()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=gears, y=gear1, name=d1,
                             marker_color=DRIVER_COLORS.get(d1, '#ffd700')))
        fig.add_trace(go.Bar(x=gears, y=gear2, name=d2,
                             marker_color=DRIVER_COLORS.get(d2, '#00d2be')))
        fig.update_layout(barmode='group', template='plotly_dark', height=320,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
                          xaxis_title='Gear', yaxis_title='Time in Gear (%)')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_g2:
        st.markdown("**RPM Distribution**")
        rpm1 = s_eng.integers(2, 45, len(rpm_bin)).tolist()
        rpm2 = s_eng.integers(2, 45, len(rpm_bin)).tolist()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rpm_bin, y=rpm1, name=d1,
                             marker_color=DRIVER_COLORS.get(d1, '#ffd700')))
        fig.add_trace(go.Bar(x=rpm_bin, y=rpm2, name=d2,
                             marker_color=DRIVER_COLORS.get(d2, '#00d2be')))
        fig.update_layout(barmode='group', template='plotly_dark', height=320,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
                          xaxis_title='RPM Range', yaxis_title='Time (%)')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Brake temp trace ──
    st.markdown("---")
    st.markdown('<div class="section-header">🌡️ Brake Temperature Trace</div>', unsafe_allow_html=True)
    s_brake = _seeded(hash(d1 + 'brake') % 2**31)
    laps_b = np.arange(0, max(len(ld1['laps']) if ld1['laps'] else 0, 50))
    bt_raw  = 580 + 80 * np.sin(laps_b / 8) + s_brake.normal(0, 18, len(laps_b))
    fig_brake = go.Figure()
    fig_brake.add_trace(go.Scatter(
        x=laps_b, y=bt_raw.tolist(),
        mode='lines', name='Front Brake Temp',
        line=dict(color='#ff4444', width=2),
        fill='tozeroy', fillcolor='rgba(255,68,68,0.1)',
    ))
    fig_brake.add_trace(go.Scatter(
        x=laps_b, y=(bt_raw * 0.82).tolist(),
        mode='lines', name='Rear Brake Temp',
        line=dict(color='#ffd700', width=2),
    ))
    fig_brake.update_layout(
        xaxis_title='Lap', yaxis_title='Brake Temp (°C)',
        template='plotly_dark', height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    fig_brake.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_brake.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_brake, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    st.markdown('<div class="section-header">⏱️ Lap Time Stats</div>', unsafe_allow_html=True)
    if ld1['laps']:
        lap_diff = np.diff(ld1['lap_times'])
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Best Lap",      f"{min(ld1['lap_times']):.2f}s")
        col_s2.metric("Avg Lap",       f"{np.mean(ld1['lap_times']):.2f}s")
        col_s3.metric("Consistency σ", f"{np.std(lap_diff):.3f}s")

    # ── Advanced KPIs ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 Advanced KPIs</div>', unsafe_allow_html=True)

    # Compute KPIs from the generated telemetry arrays (keep consistent with the 2D visuals)
    speed1 = np.asarray(data1, dtype=float)
    speed2 = np.asarray(data2, dtype=float)

    s_ped1 = _seeded(hash(d1 + str(year)) % 2**31)
    s_ped2 = _seeded(hash(d2 + str(year)) % 2**31)

    throttle1 = np.asarray(
        np.clip(50 + 40 * np.sin(dist_arr / 420) + s_ped1.normal(0, 4, len(dist_arr)), 0, 100),
        dtype=float,
    )
    brake1 = np.asarray(
        np.clip(40 * (1 - np.cos(dist_arr / 420)) + s_ped1.normal(0, 4, len(dist_arr)), 0, 100),
        dtype=float,
    )
    throttle2 = np.asarray(
        np.clip(50 + 40 * np.sin(dist_arr / 420) + s_ped2.normal(0, 4, len(dist_arr)), 0, 100),
        dtype=float,
    )
    brake2 = np.asarray(
        np.clip(40 * (1 - np.cos(dist_arr / 420)) + s_ped2.normal(0, 4, len(dist_arr)), 0, 100),
        dtype=float,
    )

    delta_arr = speed1 - speed2
    delta_max = float(np.max(delta_arr))
    delta_min = float(np.min(delta_arr))

    def _top_speed(s: np.ndarray) -> float:
        return float(np.max(s))

    def _braking_events(b: np.ndarray, thr: float = 65.0) -> int:
        heavy = b > thr
        return int(np.sum(heavy))

    def _conflict_score(t: np.ndarray, b: np.ndarray, thr_t: float = 60.0, thr_b: float = 55.0) -> float:
        both = (t > thr_t) & (b > thr_b)
        return float(np.mean(both) * 100.0)

    def _speed_spread(s: np.ndarray) -> float:
        p05 = float(np.percentile(s, 5))
        p95 = float(np.percentile(s, 95))
        return p95 - p05

    top_speed1 = _top_speed(speed1)
    top_speed2 = _top_speed(speed2)

    avg_throttle1 = float(np.mean(throttle1))
    avg_throttle2 = float(np.mean(throttle2))

    avg_brake1 = float(np.mean(brake1))
    avg_brake2 = float(np.mean(brake2))

    brake_events1 = _braking_events(brake1)
    brake_events2 = _braking_events(brake2)

    overlap1 = _conflict_score(throttle1, brake1)
    overlap2 = _conflict_score(throttle2, brake2)

    spread1 = _speed_spread(speed1)
    spread2 = _speed_spread(speed2)

    # KPI layout (4 per row)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"Top Speed — {d1}", f"{top_speed1:.1f} km/h")
    k2.metric(f"Top Speed — {d2}", f"{top_speed2:.1f} km/h")
    k3.metric(f"Avg Throttle — {d1}", f"{avg_throttle1:.1f}%")
    k4.metric(f"Avg Brake — {d1}", f"{avg_brake1:.1f}%")

    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Heavy Braking Samples", f"{brake_events1}")
    k6.metric("Throttle∩Brake Overlap", f"{overlap1:.1f}%")
    k7.metric(f"Speed Spread — {d1}", f"{spread1:.1f}")
    k8.metric("Δ Speed Extremes (d1-d2)", f"{delta_min:+.1f}…{delta_max:+.1f}")

    k9, k10, k11, k12 = st.columns(4)
    k9.metric("Avg Throttle — d2", f"{avg_throttle2:.1f}%")
    k10.metric("Avg Brake — d2", f"{avg_brake2:.1f}%")
    k11.metric("Heavy Braking Samples d2", f"{brake_events2}")
    k12.metric("Overlap d2", f"{overlap2:.1f}%")


    # ── Advanced 3D Visualizations ──
    with st.expander('🧊 Advanced 3D Visualizations (Plotly)', expanded=False):
        show_d2 = st.checkbox(f"Show {d2} in 3D", value=True)
        res_level = st.selectbox("3D Resolution", ["Low", "Medium", "High"], index=1)

        if res_level == "Low":
            n_dist_3d = 40
            n_laps_3d = 20
        elif res_level == "High":
            n_dist_3d = 70
            n_laps_3d = 35
        else:
            n_dist_3d = 55
            n_laps_3d = 28

        # Shared reduced distance axis
        dist3 = np.linspace(0, track_len * 1000, n_dist_3d)
        speed1_3 = np.interp(dist3, dist_arr, speed1)
        speed2_3 = np.interp(dist3, dist_arr, speed2)
        throttle1_3 = np.interp(dist3, dist_arr, throttle1)
        brake1_3 = np.interp(dist3, dist_arr, brake1)
        throttle2_3 = np.interp(dist3, dist_arr, throttle2)
        brake2_3 = np.interp(dist3, dist_arr, brake2)

        s3d = _seeded(hash(d1 + d2 + "3d" + str(year) + sel_race) % 2**31)

        # 3D Phase-space: Speed vs Throttle vs Brake
        st.markdown('<div class="section-header">🎛️ 3D Phase-Space (Speed×Throttle×Brake)</div>', unsafe_allow_html=True)
        phase_points = n_dist_3d

        fig_phase = go.Figure()
        fig_phase.add_trace(go.Scatter3d(
            x=throttle1_3,
            y=brake1_3,
            z=speed1_3,
            mode='markers',
            marker=dict(
                size=4,
                color=dist3,
                colorscale='Turbo',
                opacity=0.85,
                showscale=True,
                colorbar=dict(title='Distance (m)'),
            ),
            name=d1,
            text=[f"dist={int(x)}m" for x in dist3],
        ))
        if show_d2:
            fig_phase.add_trace(go.Scatter3d(
                x=throttle2_3,
                y=brake2_3,
                z=speed2_3,
                mode='markers',
                marker=dict(
                    size=4,
                    color=dist3,
                    colorscale='Turbo',
                    opacity=0.55,
                    showscale=False,
                ),
                name=d2,
                text=[f"dist={int(x)}m" for x in dist3],
            ))

        fig_phase.update_layout(
            template='plotly_dark', height=520,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            scene=dict(
                xaxis_title='Throttle %',
                yaxis_title='Brake %',
                zaxis_title='Speed (km/h)',
            ),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        )
        st.plotly_chart(fig_phase, use_container_width=True, config={'displayModeBar': False})

        # 3D Speed evolution surface: Lap × Distance × Speed
        st.markdown('<div class="section-header">📈 3D Speed Evolution (Lap × Distance Surface)</div>', unsafe_allow_html=True)
        n_laps_real = max(1, min(50, len(ld1['laps']) if ld1['laps'] else 20))
        n_laps_used = min(n_laps_3d, n_laps_real)
        laps_idx = np.arange(1, n_laps_used + 1)

        # Synthetic per-lap drift
        lap_drift = np.linspace(0, -0.12, n_laps_used).reshape(-1, 1)
        speed_surf1 = np.tile(speed1_3.reshape(1, -1), (n_laps_used, 1)) * (1 + lap_drift)
        speed_surf1 = speed_surf1 + s3d.normal(0, 2.5, size=speed_surf1.shape)
        speed_surf1 = np.clip(speed_surf1, 0, 380)

        fig_speed = go.Figure()
        fig_speed.add_trace(go.Surface(
            x=dist3,
            y=laps_idx,
            z=speed_surf1,
            colorscale='YlOrRd',
            opacity=0.95,
            showscale=False,
            name=d1,
        ))
        if show_d2:
            speed_surf2 = np.tile(speed2_3.reshape(1, -1), (n_laps_used, 1)) * (1 + lap_drift)
            speed_surf2 = speed_surf2 + s3d.normal(0, 2.5, size=speed_surf2.shape)
            speed_surf2 = np.clip(speed_surf2, 0, 380)
            fig_speed.add_trace(go.Surface(
                x=dist3,
                y=laps_idx,
                z=speed_surf2,
                colorscale='Tealrose',
                opacity=0.65,
                showscale=False,
                name=d2,
            ))

        fig_speed.update_layout(
            template='plotly_dark', height=620,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title='Speed Evolution Surface',
            scene=dict(
                xaxis_title='Distance (m)',
                yaxis_title='Lap #',
                zaxis_title='Speed (km/h)',
                camera=dict(eye=dict(x=1.6, y=1.6, z=1.1)),
            ),
        )
        st.plotly_chart(fig_speed, use_container_width=True, config={'displayModeBar': False})

        # 3D Brake temperature map: Lap × Distance × Temp
        st.markdown('<div class="section-header">🌡️ 3D Brake Temp Map (Lap × Distance)</div>', unsafe_allow_html=True)
        laps_b_local = np.arange(1, n_laps_used + 1)
        # base brake temp over laps
        bt_lap = 580 + 80 * np.sin(laps_b_local / 2.8)

        # distance dependence for “corners”
        corner_g = 0.5 + 0.5 * np.sin(dist3 / 240.0)
        brake_temp_surf = np.zeros((n_laps_used, n_dist_3d))
        for i in range(n_laps_used):
            # overall temp decays slightly
            decay = 1.0 - (i / max(1, n_laps_used - 1)) * 0.08
            brake_temp_surf[i, :] = (bt_lap[i] * decay) + 25 * corner_g + s3d.normal(0, 10, size=n_dist_3d)
        brake_temp_surf = np.clip(brake_temp_surf, 300, 900)

        fig_bt = go.Figure(data=[go.Surface(
            x=dist3,
            y=laps_b_local,
            z=brake_temp_surf,
            colorscale='Hot',
            showscale=True,
            colorbar=dict(title='Brake Temp (°C)'),
        )])
        fig_bt.update_layout(
            template='plotly_dark', height=620,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title='Brake Temperature Evolution (Synthetic)',
            scene=dict(
                xaxis_title='Distance (m)',
                yaxis_title='Lap #',
                zaxis_title='Temp (°C)',
                camera=dict(eye=dict(x=1.5, y=1.6, z=1.2)),
            ),
        )
        st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})

        # 3D Delta rail (distance × Δ)
        st.markdown('<div class="section-header">⚔️ 3D Delta Rail (d1−d2)</div>', unsafe_allow_html=True)
        y_delta = np.zeros_like(dist3) + 0.0
        # slight jitter in Y to give “tube” feel
        y_delta = 0.02 * np.sin(dist3 / 180.0)
        fig_delta3d = go.Figure()
        fig_delta3d.add_trace(go.Scatter3d(
            x=dist3,
            y=y_delta,
            z=np.interp(dist3, dist_arr, delta_arr),
            mode='lines',
            line=dict(color='#ff6b6b', width=5),
            name='Δ Speed',
        ))
        fig_delta3d.add_trace(go.Scatter3d(
            x=dist3,
            y=y_delta,
            z=np.interp(dist3, dist_arr, delta_arr),
            mode='markers',
            marker=dict(size=4, color=np.interp(dist3, dist_arr, delta_arr), colorscale='RdBu', opacity=0.85),
            name='Samples',
            showlegend=False,
        ))
        fig_delta3d.update_layout(
            template='plotly_dark', height=520,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title='Speed Delta Rail',
            scene=dict(
                xaxis_title='Distance (m)',
                yaxis_title='(fixed)',
                zaxis_title='Δ Speed (km/h)',
                camera=dict(eye=dict(x=1.8, y=0.8, z=1.3)),
            ),
        )
        st.plotly_chart(fig_delta3d, use_container_width=True, config={'displayModeBar': False})

    # ── Speed heatmap vs distance ──
    st.markdown("---")
    st.markdown('<div class="section-header">🌡️ Speed Heatmap (Lap × Distance)</div>', unsafe_allow_html=True)
    s_hm = _seeded(hash(d1 + str(year)) % 2**31)
    nLapsH  = min(10, len(ld1['laps']))
    dist_hm = np.linspace(0, track_len * 1000, 80)
    base_hm = 180 + 60 * np.sin(dist_hm / 500)
    hm_z = np.array([
        (base_hm + s_hm.normal(0, 3, len(dist_hm))).tolist()
        for _ in range(nLapsH)
    ])
    fig_hm = go.Figure(data=go.Heatmap(
        z=hm_z, colorscale='YlOrRd',
        y=[f'Lap {i+1}' for i in range(nLapsH)],
        colorbar=dict(title='Speed (km/h)'),
    ))
    fig_hm.update_layout(
        template='plotly_dark', height=max(280, nLapsH * 22),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Track Position', yaxis_title='',
    )
    st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})

    # ═══════════════════════════════════════════════════
    #  NEW VISUALISATIONS  IDs 21-30  (telemetry_analysis.py)
    # ═══════════════════════════════════════════════════

    # ─── NEW ID 21 · Suspension Compression Heatmap ───────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🛡️ Suspension Compression Heatmap</div>', unsafe_allow_html=True)
    s_susp = _seeded(hash(d1 + str(year) + 'suspension') % 2**31)
    n_d_susp = 80
    n_l_susp = min(20, len(ld1['laps']) if ld1['laps'] else 20)
    dist_susp = np.linspace(0, track_len * 1000, n_d_susp)
    z_susp = np.zeros((n_l_susp, n_d_susp))
    corner_g_s = 0.5 + 0.5 * np.sin(dist_susp / 200.0)
    base_comp  = 0.22
    for li in range(n_l_susp):
        wear = (li / max(n_l_susp - 1, 1)) * 0.12
        noise_l = s_susp.normal(0, 0.035, n_d_susp)
        z_susp[li, :] = np.clip(
            base_comp + 0.18 * corner_g_s + wear + noise_l, 0.0, 0.90
        )
    fig_susp = go.Figure(data=go.Heatmap(
        z=z_susp, x=[f"{int(x)}m" for x in dist_susp[::4]],
        y=[f"Lap {li+1}" for li in range(n_l_susp)],
        colorscale=[[0,'#2ecc71'],[0.35,'#f1c40f'],[0.65,'#e67e22'],[1,'#e74c3c']], colorbar=dict(title="Compression"),
    ))
    fig_susp.update_layout(
        template='plotly_dark', height=max(280, n_l_susp * 20),
        paper_bgcolor='rgba(0,0,0,0)', xaxis_title='Track Position', yaxis_title='',
        title=f"Suspension Compression — {d1}",
    )
    st.plotly_chart(fig_susp, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 22 · Steering Angle Dynamics ─────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Steering Angle Dynamics</div>', unsafe_allow_html=True)
    s_str = _seeded(hash(d1 + d2 + str(year) + 'steer') % 2**31)
    steer1 = np.clip(90 * np.sin(dist_arr / 320) + s_str.normal(0, 7, len(dist_arr)), -90, 90)
    steer2 = np.clip(88 * np.sin(dist_arr / 300) + s_str.normal(0, 7, len(dist_arr)), -90, 90)
    fig_str = go.Figure()
    fig_str.add_trace(go.Scatter(
        x=dist_arr, y=steer1.tolist(), mode='lines', name=d1,
        line=dict(color=DRIVER_COLORS.get(d1,'#ffd700'), width=2),
    ))
    fig_str.add_trace(go.Scatter(
        x=dist_arr, y=steer2.tolist(), mode='lines', name=d2,
        line=dict(color=DRIVER_COLORS.get(d2,'#00d2be'), width=2),
        yaxis='y2',
    ))
    fig_str.update_layout(
        title='Steering Angle vs Distance',
        xaxis_title='Distance (m)', yaxis_title=f'{d1} Steering (°)',
        yaxis2=dict(title=f'{d2} Steering (°)', overlaying='y', side='right'),
        template='plotly_dark', height=330,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified',
    )
    fig_str.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_str.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_str, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 23 · 3D Engine Load Simulation ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⚙️ 3D Engine Load Simulation</div>', unsafe_allow_html=True)
    s_el = _seeded(hash(d1 + str(year) + sel_race + 'eng_load') % 2**31)
    N_EL = 60
    rpm_el = np.linspace(8000, 15500, N_EL)
    th_el  = np.linspace(0,   100,  N_EL)
    Re, Te = np.meshgrid(rpm_el, th_el)
    Ze = 65.0 + 28.0 * np.sin(Re / 2200) * (Te / 100.0) + s_el.normal(0, 4.5, Re.shape)
    Ze = np.clip(Ze, 0, 102)
    fig_el = go.Figure(data=go.Surface(
        x=Re, y=Te, z=Ze, colorscale='Electric', opacity=0.93,
        showscale=True, colorbar=dict(title="Engine Load %"),
    ))
    fig_el.update_layout(
        template='plotly_dark', height=500,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"3D Engine Load — {d1} ({year} {sel_race})",
        scene=dict(xaxis_title='RPM', yaxis_title='Throttle (%)', zaxis_title='Load (%)',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_el, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 24 · Turbo Pressure Evolution ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌪️ Turbo Pressure Evolution</div>', unsafe_allow_html=True)
    s_tp = _seeded(hash(d1 + str(year) + sel_race + 'turbo') % 2**31)
    n_laps_tp = max(1, int(ld1['avg_lap'] / 10))
    laps_tp = np.arange(1, n_laps_tp + 1)
    base_tp_bar = 2.80
    tp_arr = base_tp_bar + s_tp.normal(0, 0.18, n_laps_tp) + np.clip(0.28 * np.sin(laps_tp / 8), 0, 0.5)
    tp_min = tp_arr - s_tp.uniform(0.05, 0.22, n_laps_tp)
    tp_max = tp_arr + s_tp.uniform(0.05, 0.22, n_laps_tp)
    fig_tp = go.Figure()
    fig_tp.add_trace(go.Scatter(
        x=laps_tp.tolist(), y=tp_max.tolist(), mode='lines',
        line=dict(width=0), showlegend=False, hoverinfo='skip',
    ))
    fig_tp.add_trace(go.Scatter(
        x=laps_tp.tolist(), y=tp_min.tolist(), mode='lines',
        name='Min / Max', line=dict(width=0),
        fill='tonexty', fillcolor='rgba(30,144,255,0.18)', hoverinfo='skip',
    ))
    fig_tp.add_trace(go.Scatter(
        x=laps_tp.tolist(), y=tp_arr.tolist(), mode='lines',
        name='Avg Turbo', line=dict(color='#00ff00', width=2.5),
    ))
    fig_tp.update_layout(
        xaxis_title='Lap', yaxis_title='Boost Pressure (bar)', height=320,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Turbo Pressure — {d1} ({year} {sel_race})",
        hovermode='x unified',
    )
    fig_tp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_tp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_tp, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 25 · Energy Recovery Deployment ──────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🔋 Energy Recovery Deployment</div>', unsafe_allow_html=True)
    s_ers = _seeded(hash(d1 + str(year) + sel_race + 'ers') % 2**31)
    n_stints = 3
    stints_ers = []
    sd_ers = (n_laps_tp if n_laps_tp > 0 else 56) // n_stints
    total_lap_ers = 0
    for _si in range(n_stints):
        s_laps = [12, 8, 12]
        de_laps = [max(4, s - 3) for s in s_laps]
        de_arr = np.zeros(s_laps[_si])
        de_arr[:de_laps[_si]] = 1.0
        np.random.shuffle(de_arr)
        by_lap = de_arr.tolist()
        for li_ers in range(s_laps[_si]):
            if by_lap[li_ers] == 1.0:
                total_lap_ers += 1
        stints_ers.append({
            'Stint':     f"Stint {_si + 1}",
            'Deployed': de_arr.tolist(),
        })
    fig_ers = go.Figure()
    ers_colors = ['#ffd700', '#00d2be', '#ff4444']
    for stint_idx, stint_d in enumerate(stints_ers):
        y_ers = [stint_idx] * len(stint_d['Deployed'])
        colors_ers = [ers_colors[stint_idx] if v > 0.5 else 'rgba(80,80,80,0.35)' for v in stint_d['Deployed']]
        fig_ers.add_trace(go.Scatter(
            x=list(range(1, len(stint_d['Deployed']) + 1)), y=y_ers,
            mode='markers',
            marker=dict(size=14, color=colors_ers, symbol='square', line=dict(width=1, color='white')),
            name=stint_d['Stint'],
        ))
    fig_ers.update_layout(
        xaxis_title='Lap in Stint', yaxis_title='Stint', height=280,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        yaxis=dict(tickmode='array', tickvals=[0, 1, 2], ticktext=['Stint 1', 'Stint 2', 'Stint 3']),
        title=f"ERS Deployment — {d1} ({year})",
    )
    fig_ers.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_ers.update_yaxes(showgrid=False)
    st.plotly_chart(fig_ers, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 26 · Brake Bias Transition Analysis ───────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🔴 Brake Bias Transition Analysis</div>', unsafe_allow_html=True)
    s_bb = _seeded(hash(d1 + str(year) + 'brake_bias') % 2**31)
    n_pts_bb = 60
    dist_bb = np.linspace(0, track_len * 1000, n_pts_bb)
    corner_st_mod = 0.5 + 0.5 * np.sin(dist_bb / 280.0)
    bb_front = np.clip(56.0 + 5.0 * corner_st_mod + s_bb.normal(0, 2.8, n_pts_bb), 48, 68)
    bb_rear = 100.0 - bb_front
    fig_bb = go.Figure()
    fig_bb.add_trace(go.Scatter(
        x=dist_bb.tolist(), y=bb_front.tolist(), mode='lines',
        name='Front Bias %', line=dict(color='#ff4444', width=2),
        fill='tozeroy', fillcolor='rgba(255,68,68,0.12)',
    ))
    fig_bb.add_trace(go.Scatter(
        x=dist_bb.tolist(), y=bb_rear.tolist(), mode='lines',
        name='Rear Bias %', line=dict(color='#00d2be', width=2),
        fill='tozeroy', fillcolor='rgba(0,210,190,0.12)',
    ))
    fig_bb.update_layout(
        xaxis_title='Distance (m)', yaxis_title='Brake Bias (%)', height=320,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Brake Bias — {d1} ({year} {sel_race})",
        hovermode='x unified',
    )
    fig_bb.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_bb.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_bb, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 27 · 3D Telemetry Tunnel ────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🎮 3D Telemetry Tunnel</div>', unsafe_allow_html=True)
    with st.expander('🧊 Advanced 3D Telemetry Tunnel', expanded=False):
        show_d2_3 = st.checkbox(f"Show {d2}", value=True, key='tunnel_show2')
        N_TT = 55
        dist3tt = np.linspace(0, track_len * 1000, N_TT)
        cam_rad = 3.5
        ang_tt  = np.linspace(0, 2 * np.pi * 4, N_TT)
        tx_tt   = dist3tt / max(track_len * 1000, 1.0)
        spd1_tt = np.interp(dist3tt, dist_arr, data1)
        spd2_tt = np.interp(dist3tt, dist_arr, data2)
        fig_tt = go.Figure()
        for lbl, spd_tt, col in [(d1, spd1_tt, DRIVER_COLORS.get(d1,'#ffd700')),
                                  (d2, spd2_tt, DRIVER_COLORS.get(d2,'#00d2be'))]:
            if not show_d2_3 and lbl != d1:
                continue
            tube_x = cam_rad * np.cos(ang_tt)
            tube_y = cam_rad * np.sin(ang_tt)
            tube_z = spd_tt / 380.0
            fig_tt.add_trace(go.Scatter3d(
                x=tube_x.tolist(), y=tube_y.tolist(), z=tube_z.tolist(),
                mode='lines', name=lbl,
                line=dict(color=col, width=6),
            ))
        fig_tt.update_layout(
            template='plotly_dark', height=480,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title='3D Telemetry Tunnel (Speed → radius)',
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False),
                       zaxis_title='Normalised Speed', bgcolor='rgba(0,0,0,0)',
                       aspectmode='data'),
            margin=dict(l=0, r=0, t=28, b=0),
        )
        st.plotly_chart(fig_tt, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 28 · Tyre Temperature Gradient ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌡️ Tyre Temperature Gradient</div>', unsafe_allow_html=True)
    s_tt = _seeded(hash(d1 + str(year) + sel_race + 'tyre_temp') % 2**31)
    n_lap_tt = 10
    n_t_tt   = 60
    dist_tt  = np.linspace(0, track_len * 1000, n_t_tt)
    z_tt_c = np.zeros((n_lap_tt, n_t_tt))
    corner_mod_tt = 0.5 + 0.5 * np.sin(dist_tt / 220.0)
    base_tt  = 88.0
    for lti in range(n_lap_tt):
        wear_t  = (lti / max(n_lap_tt - 1, 1)) * 18.0
        eff_c   = 0.92 + (s_tt.random() - 0.5) * 0.16
        z_tt_c[lti, :] = np.clip(
            base_tt + 22.0 * corner_mod_tt + wear_t * eff_c + s_tt.normal(0, 2.2, n_t_tt),
            58.0, 128.0,
        )
    fig_ttmp = go.Figure(data=go.Contour(
        z=z_tt_c, x=[f"{int(x)}m" for x in dist_tt[::6]],
        y=[f"Lap {li+1}" for li in range(n_lap_tt)],
        colorscale='Hot', colorbar=dict(title="Tyre Temp (°C)"),
        contours=dict(coloring='heatmap'),
    ))
    fig_ttmp.update_layout(
        template='plotly_dark', height=max(280, n_lap_tt * 22),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Track Position', yaxis_title='',
        title=f"Tyre Temperature Gradient — {d1} ({year} {sel_race})",
    )
    st.plotly_chart(fig_ttmp, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 29 · Real-Time Vibration Spectrum ─────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📳 Real-Time Vibration Spectrum</div>', unsafe_allow_html=True)
    s_vib = _seeded(hash(d1 + str(year) + sel_race + 'vibration') % 2**31)
    n_freq_bins = 128
    freq_ax = np.linspace(0, 500, n_freq_bins)
    domin_f = s_vib.uniform(18, 45)
    amp_dom = s_vib.uniform(0.55, 0.88)
    vib_signal = (
            0.42 * np.exp(-(freq_ax - domin_f) ** 2 / 110.0) +
            0.30 * np.exp(-(freq_ax - domin_f * 2.2) ** 2 / 240.0) +
            0.18 * np.exp(-(freq_ax - domin_f * 3.7) ** 2 / 480.0) +
            0.10 * np.exp(-(freq_ax - s_vib.uniform(80, 220)) ** 2 / 88.0) +
            s_vib.normal(0, 0.07, n_freq_bins)
    )
    vib_signal = np.clip(vib_signal, 0, 1.0)
    fig_vib = go.Figure()
    fig_vib.add_trace(go.Scatter(
        x=freq_ax.tolist(), y=vib_signal.tolist(),
        mode='lines', name='Vibration Spectrum', fill='tozeroy',
        line=dict(color='#ff4444', width=2),
        fillcolor='rgba(255,68,68,0.18)',
    ))
    peak_i = int(np.argmax(vib_signal))
    fig_vib.add_vline(x=freq_ax[peak_i], line_dash='dash', line_color='#ffd700',
                       annotation_text=f"Peak: {freq_ax[peak_i]:.1f} Hz",
                       annotation_position='top right')
    fig_vib.update_layout(
        xaxis_title='Frequency (Hz)', yaxis_title='Amplitude',
        template='plotly_dark', height=310,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Vibration Spectrum — {d1} ({year} {sel_race})",
    )
    fig_vib.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_vib.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_vib, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 30 · 3D G-Force Distribution ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌀 3D G-Force Distribution</div>', unsafe_allow_html=True)
    s_gf = _seeded(hash(d1 + str(year) + sel_race + 'gforce') % 2**31)
    N_GF = 220
    ang_radar = np.linspace(0, 2 * np.pi, N_GF)
    g_mag = np.abs(1.60 + 3.80 * np.sin(ang_radar * 5.0) + s_gf.normal(0, 0.55, N_GF))
    g_lat = g_mag * np.cos(ang_radar)
    g_long = g_mag * np.sin(ang_radar)
    fig_gf = go.Figure(data=go.Scatter3d(
        x=g_lat.tolist(), y=g_long.tolist(), z=g_mag.tolist(),
        mode='markers',
        marker=dict(
            size=4, color=g_mag.tolist(),
            colorscale='Viridis', showscale=True,
            colorbar=dict(title="|G|"),
            opacity=0.85,
        ),
    ))
    fig_gf.update_layout(
        template='plotly_dark', height=500,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"G-Force Distribution — {d1} ({year} {sel_race})",
        scene=dict(
            xaxis_title='Lateral G', yaxis_title='Longitudinal G', zaxis_title='|G|',
            bgcolor='rgba(0,0,0,0)',
        ),
    )
    st.plotly_chart(fig_gf, use_container_width=True, config={'displayModeBar': False})


def _channel(drv: str, metric: str, rng, track_len: float, best_lap: float):
    """Return synthetic telemetry array for (driver, channel)."""
    dist_x = np.linspace(0, track_len * 1000, 500)
    child = np.random.default_rng(int(abs(hash(drv + metric))) % (2**31))

    if metric == 'Speed':
        base = 140 + 170 * np.sin(dist_x / (track_len * 1000 / (2 * np.pi)))
        return np.clip(base + child.normal(0, 5, 500), 0, 380)
    elif metric == 'Throttle':
        return np.clip(child.uniform(0, 100, 500), 0, 100)
    elif metric == 'Brake':
        return np.clip(child.uniform(0, 100, 500), 0, 100)
    elif metric == 'Gear':
        return child.integers(1, 9, 500).astype(float)
    elif metric == 'RPM':
        return child.uniform(8000, 17000, 500)
    elif metric == 'DRS':
        return np.where(child.uniform(0, 1, 500) > 0.65, 1, 0)
    return np.zeros(500)
