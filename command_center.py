import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
sys.path.insert(0, '.')
from data_model import (
    get_seasons_data, get_race_results, get_races,
    DRIVERS, DRIVER_COLORS,
    _seeded,
)

# F1 team colour palette — used for drivers not already in DRIVER_COLORS
_F1_COLORS = [
    '#3671C6',  # Red Bull
    '#27F4D2',  # Mercedes
    '#FF2800',  # Ferrari
    '#F58020',  # McLaren
    '#358C75',  # Aston Martin
    '#6676FF',  # RB
    '#2293D1',  # Alpine
    '#37BEDD',  # Williams
    '#B6BABD',  # Haas
    '#52E252',  # Sauber
]

# Fill a track-length lookup used in laps-distance
_TRACK_LEN = {
    'Bahrain GP': 5.412, 'Australian GP': 5.278,
    'Chinese GP': 5.451, 'Japanese GP': 5.807,
    'Monaco GP': 3.337, 'British GP': 5.891,
    'Italian GP': 5.793, 'Belgian GP': 7.004,
    'Singapore GP': 4.064, 'United States GP': 5.513,
    'Miami GP': 5.412, 'Spanish GP': 4.655,
    'Hungarian GP': 4.381, 'Dutch GP': 4.259,
}

def _gen_speed_prof(rng, drv_idx: int, track_len_m: float):
    dist = np.linspace(0, track_len_m, 80)
    base = 170 + 70 * np.sin(dist / 400 + drv_idx * 0.2)
    return np.clip(base + rng.normal(0, 5, len(dist)), 60, 360).tolist()

def render():
    st.markdown('<div class="section-header">⚡ Live Command Center</div>', unsafe_allow_html=True)

    # ── Year / Race selector ──
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        year = st.selectbox(
            "Season", list(reversed(range(2000, 2027))),
            key="cc_year", index=26,
        )
    with col_sel2:
        sel_race = st.selectbox(
            "Circuit / Session", get_races(year) if year else [],
            key="cc_race",
        )

    # Fetch results
    data   = get_seasons_data()
    res_cc = get_race_results(year, sel_race) if year else []
    races  = get_races(year) if year else []
    s_cc   = _seeded(hash(str(year) + sel_race + 'live') % 2**31)
    cur_lap = s_cc.integers(5, res_cc[0]['laps'] if res_cc else 56)
    total_lap = res_cc[0]['laps'] if res_cc else 56
    air_temp  = 18 + (year % 8) + (cur_lap % 14)
    trk_temp  = air_temp + 18 + (int(cur_lap * 0.37) % 12)
    wind_spd  = (cur_lap * 3 + year) % 35

    # ── Session status KPIs ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Session Status", "LIVE", delta_color="off")
    with col2:
        st.metric("Current Lap", f"{cur_lap}/{total_lap}", delta="+1")
    with col3:
        st.metric("Track Temp", f"{trk_temp}°C", delta=f"+{wind_spd%3}°C")
    with col4:
        remaining = max(1, total_lap - cur_lap)
        mins_rem  = remaining * 1.4
        st.metric("Time to Finish", f"{int(mins_rem)}m {int((mins_rem%1)*60):02d}s",
                  delta=f"-{int(np.random.uniform(0.5,2.0)*60)}s")

    st.markdown("---")

    # ── Live leaderboard ──
    st.markdown('<div class="section-header">🏁 Live Leaderboard</div>', unsafe_allow_html=True)
    if res_cc:
        s_lb = _seeded(hash(str(year) + sel_race) % 2**31)
        live_lb = pd.DataFrame({
            'Pos':         [r['position'] for r in res_cc],
            'Driver':      [r['driver']    for r in res_cc],
            'Team':        [r['team']      for r in res_cc],
            'Gap':         ['-' if i == 0 else
                            f"+{s_lb.uniform(.3,4.0,1)[0]:.1f}s"
                            for i in range(len(res_cc))],
            'Laps':        [cur_lap] * len(res_cc),
            'Last Lap':    [f"{r['best_lap']:.3f}s" for r in res_cc],
        })
        st.dataframe(live_lb, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── NEW: Full live telemetry heatmap ──
    st.markdown('<div class="section-header">📡 Live Telemetry – All Drivers</div>', unsafe_allow_html=True)
    track_len_m = _TRACK_LEN.get(sel_race, 5.5) * 1000
    pos_bins    = np.linspace(0, track_len_m, 80)
    s_th = _seeded(hash(sel_race + str(year)) % 2**31)
    heat_z = np.array([
        _gen_speed_prof(s_th, i, track_len_m)
        for i in range(min(20, len(res_cc) if res_cc else 20))
    ])
    heat_y_labels = [res_cc[i]['driver']
                     for i in range(heat_z.shape[0])] if res_cc else \
                   [f'Car {i+1}' for i in range(heat_z.shape[0])]
    fig_th = go.Figure(data=go.Heatmap(
        z=heat_z, colorscale='YlOrRd',
        x=[f'{int(x)}m' for x in pos_bins[::4]],
        y=heat_y_labels,
        colorbar=dict(title='Speed (km/h)'),
    ))
    fig_th.update_layout(
        template='plotly_dark',
        height=max(280, heat_z.shape[0] * 22),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Track Position', yaxis_title='',
    )
    st.plotly_chart(fig_th, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Real-time throttle/brake live trace ──
    st.markdown("---")
    st.markdown('<div class="section-header">🎮 Live Pedal Trace (Last Lap)</div>', unsafe_allow_html=True)
    dist_live = np.linspace(0, track_len_m, 400)
    s_lv = _seeded(hash(str(year) + sel_race + 'liveval') % 2**31)
    throttle_live = np.clip(50 + 40 * np.sin(dist_live / 420)
                            + s_lv.normal(0, 5, len(dist_live)), 0, 100)
    brake_live    = np.clip(40 * (1 - np.cos(dist_live / 420))
                            + s_lv.normal(0, 5, len(dist_live)), 0, 100)
    fig_lv = go.Figure()
    fig_lv.add_trace(go.Scatter(
        x=dist_live, y=throttle_live.tolist(),
        mode='lines', name='Throttle %',
        fill='tozeroy', line=dict(color='#00ff00', width=1.5),
        fillcolor='rgba(0,255,0,0.12)',
    ))
    fig_lv.add_trace(go.Scatter(
        x=dist_live, y=(-brake_live).tolist(),
        mode='lines', name='Brake %',
        fill='tozeroy', line=dict(color='#ff4444', width=1.5),
        fillcolor='rgba(255,68,68,0.12)',
    ))
    fig_lv.update_layout(
        xaxis_title='Distance (m)', yaxis_title='Pedal %',
        template='plotly_dark', height=320,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    fig_lv.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_lv.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_lv, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Gap tracking ──
    st.markdown('<div class="section-header">📊 Gap Tracking</div>', unsafe_allow_html=True)
    laps_gt = np.arange(1, cur_lap + 1)
    s_gt = _seeded(hash(str(year) + sel_race + 'gap') % 2**31)
    gap_l = 0.2 + 0.04 * laps_gt + s_gt.normal(0, 0.1, len(laps_gt))
    gap_p = 1.5 + 0.07 * laps_gt + s_gt.normal(0, 0.15, len(laps_gt))
    fig_g = go.Figure()
    fig_g.add_trace(go.Scatter(
        x=laps_gt, y=gap_l, mode='lines', name='Leader Gap',
        line=dict(color='#ff6b6b', width=2),
    ))
    fig_g.add_trace(go.Scatter(
        x=laps_gt, y=gap_p, mode='lines', name='P2 Gap',
        line=dict(color='#ffd700', width=2),
    ))
    fig_g.update_layout(
        title=f'Gap Evolution – {sel_race} {year}',
        xaxis_title='Lap', yaxis_title='Gap (s)',
        template='plotly_dark', height=380,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    fig_g.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_g.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: 3D Track Map ─────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌐 3D Track Map</div>', unsafe_allow_html=True)

    SCALE  = 8.0
    NS     = 220
    HW     = 3.5
    t_arr  = np.linspace(0, 2 * np.pi, NS)

    ref_drv = res_cc[0]['driver'] if res_cc else 'Car 1'

    K_STR  = 2.8
    K_TURN = 5.2

    def _cx(t):
        return K_TURN * (np.sin(t) + 0.3 * np.sin(2 * t) - 0.1 * np.sin(3 * t))

    def _cy(t):
        return K_STR * (np.cos(t) - 0.15 * np.cos(2 * t) + 0.1 * np.cos(4 * t))

    def _cz(t):
        return 0.7 * np.sin(t) + 0.4 * np.cos(2 * t)

    tx = _cx(t_arr) * SCALE
    ty = _cy(t_arr) * SCALE
    tz = _cz(t_arr) * SCALE

    gx, gy = np.gradient(tx), np.gradient(ty)
    gl = np.sqrt(gx**2 + gy**2)
    gl[gl == 0] = 1.0
    nx = -gy / gl
    ny =  gx / gl
    tx_in = (tx + HW * nx).tolist()
    ty_in = (ty + HW * ny).tolist()

    road_x = tx.tolist() + tx_in[::-1] + [tx.tolist()[0]]
    road_y = ty.tolist() + ty_in[::-1] + [ty.tolist()[0]]
    road_z = tz.tolist() + tz[::-1].tolist() + [tz.tolist()[0]]

    rng_tr  = _seeded(hash(ref_drv + str(year)) % 2**31)
    spd = np.clip(
        280 + 65 * np.sin(t_arr * 3.5) + rng_tr.normal(0, 5, NS),
        120.0, 345.0,
    )

    fig3d = go.Figure()
    
    # Track borders
    fig3d.add_trace(go.Scatter3d(
        x=road_x, y=road_y, z=road_z,
        mode='lines', line=dict(color='#888888', width=4),
        hoverinfo='skip', showlegend=False,
    ))
    
    # Start/Finish Line
    fig3d.add_trace(go.Scatter3d(
        x=[tx[0], tx_in[0]], y=[ty[0], ty_in[0]], z=[tz[0], tz[0]],
        mode='lines', line=dict(color='#ffffff', width=8),
        name='Start/Finish'
    ))
    
    # Racing line colored by speed
    fig3d.add_trace(go.Scatter3d(
        x=tx.tolist(), y=ty.tolist(), z=tz.tolist(),
        mode='lines',
        line=dict(
            color=spd.tolist(),
            colorscale='Turbo',
            width=8,
        ),
        hovertemplate=
        '<b>' + ref_drv + '</b><br>'
        'Speed: %{text} km/h<br>'
        'Pos: (%{x:.1f}, %{y:.1f})<extra></extra>',
        text=[f"{v:.0f}" for v in spd],
        showlegend=False,
        name=ref_drv,
    ))
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(visible=False, showbackground=False),
            camera=dict(
                eye=dict(x=1.2, y=-1.4, z=0.8),
                up=dict(x=0.0, y=0.0, z=1.0),
            ),
            aspectmode='data',
        ),
        template='plotly_dark',
        margin=dict(l=0, r=0, t=22, b=0),
        height=520,
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='🏁 ' + sel_race + ' ' + str(year) + ' – ' + ref_drv,
            font=dict(size=14, color='#ffd700'),
            x=0.5, xanchor='center',
        ),
    )
    st.plotly_chart(fig3d, use_container_width=True,
                    config={'displayModeBar': False})

    # ── NEW: Combined multi-track position ──
    st.markdown('<div class="section-header">🗜 Position Tracker – Multiple Drivers</div>', unsafe_allow_html=True)
    s_ps = _seeded(hash(str(year) + 'pos_tracker') % 2**31)
    fig_ps = go.Figure()
    drivers_in = [r['driver'] for r in res_cc[:6]] if res_cc else []
    for drv in drivers_in:
        drv_rng = _seeded(hash(drv + str(year)) % 2**31)
        pos = 1 + np.linspace(0, drv_rng.uniform(-2, 3), cur_lap)
        pos = np.clip(pos, 1, 20)
        fig_ps.add_trace(go.Scatter(
            x=np.arange(1, cur_lap + 1), y=pos.tolist(),
            mode='lines', name=drv,
            line=dict(color=DRIVER_COLORS.get(drv, '#888'), width=2),
        ))
    fig_ps.update_layout(
        title='Position Evolution',
        xaxis_title='Lap', yaxis_title='Position',
        yaxis=dict(autorange='reversed'),
        template='plotly_dark', height=360,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified',
    )
    fig_ps.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_ps.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_ps, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: 3D Race Simulation Panel (Players vs laps) ──
    # This creates a dedicated “web-app style” panel showing each player/driver evolution.
    st.markdown("---")
    st.markdown(
        '<div class="gg-section-header">🎮 3D Race Simulation Panel (Simulated)</div>',
        unsafe_allow_html=True,
    )

    race_drivers = [r['driver'] for r in res_cc[:8]] if res_cc else []
    from race_sim_panel import render_race_panel

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        year_sel = st.number_input("Simulation Season", min_value=2000, max_value=2027, value=int(year), step=1)
    with c2:
        race_sel = st.selectbox("Simulation Circuit / Session", options=races if races else [sel_race], index=0, key="sim_race_name")
    with c3:
        n_laps = st.slider("Simulated Laps", 20, 70, min(56, int(total_lap) if total_lap else 56), key="sim_laps")

    render_race_panel(
        year=year_sel,
        race=race_sel,
        drivers=race_drivers if race_drivers else (DRIVERS.get(year_sel, [])[:8] if hasattr(DRIVERS, 'get') else []),
        n_laps=int(n_laps),
    )

    # ═══════════════════════════════════════════════════
    #  NEW VISUALISATIONS  IDs 41-50  (command_center.py)
    # ═══════════════════════════════════════════════════

    # ─── NEW ID 41 · Live Incident Tracker ──────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🚨 Live Incident Tracker</div>', unsafe_allow_html=True)
    s_inc = _seeded(hash(str(year) + sel_race + 'incidents') % 2**31)
    track_len_km = _TRACK_LEN.get(sel_race, 5.5)
    inc_data = []
    cur_lap_inc = cur_lap
    for _inc_i in range(s_inc.integers(4, 10)):
        inc_lap = s_inc.integers(1, total_lap + 1)
        inc_loc = float(s_inc.uniform(0.05, 0.95))
        inc_types = ['Yellow Flag', 'Full Course Yellow', 'Virtual SC', 'Safety Car',
                     'Red Flag', 'TrackLimit Warning', 'Debris', 'Spin']
        inc_type = s_inc.choice(inc_types)
        inc_sev  = {'Yellow Flag': 1, 'Full Course Yellow': 2, 'Virtual SC': 3,
                    'Safety Car': 4, 'Red Flag': 5, 'TrackLimit Warning': 0,
                    'Debris': 2, 'Spin': 3}.get(inc_type, 1)
        inc_data.append({
            'Lap': inc_lap, 'Type': inc_type, 'Severity': inc_sev,
            'Location': f"T{int(inc_loc * 14) + 1}",
            'Track Pos': f"{inc_loc * track_len_km * 1000:.0f}m",
        })
    df_inc = pd.DataFrame(inc_data).sort_values('Lap').reset_index(drop=True)
    df_inc['Lap_Marker'] = df_inc['Lap'].astype(str) + '  (' + df_inc['Type'] + ')'
    sev_color_map = {0: '#ffffff', 1: '#ffd700', 2: '#ffa500', 3: '#ff4444', 4: '#ff00ff', 5: '#8b0000'}
    df_inc['Severity_Color'] = df_inc['Severity'].map(sev_color_map)
    col_inc_b, col_inc_a = st.columns([2, 1])
    with col_inc_b:
        fig_inc = go.Figure()
        fig_inc.add_trace(go.Scatter(
            x=df_inc['Lap_Marker'].tolist(),
            y=df_inc['Severity'].tolist(),
            mode='markers+text',
            marker=dict(size=df_inc['Severity'].map({0: 9, 1: 14, 2: 19, 3: 24, 4: 29, 5: 34}).tolist(),
                        color=df_inc['Severity_Color'].tolist(),
                        line=dict(width=1, color='white')),
            text=[f"📍{loc}" for loc in df_inc['Location']],
            textposition='top center', name='',
            hovertemplate='Lap: %{x}<br>Type: %{text}<extra></extra>',
        ))
        fig_inc.add_hline(y=3, line_dash='dash', line_color='#ff4444', opacity=0.7,
                           annotation_text="SC Threshold", annotation_position='left')
        fig_inc.update_layout(
            template='plotly_dark', height=310,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Lap', yaxis_title='Severity Level',
            title=f"Incident Severity — {sel_race} {year}",
        )
        fig_inc.update_xaxes(showgrid=False, tickangle=-35)
        st.plotly_chart(fig_inc, use_container_width=True, config={'displayModeBar': False})
    with col_inc_a:
        st.markdown("**Incident Log**")
        st.dataframe(df_inc[['Lap','Type','Location']], use_container_width=True,
                     hide_index=True, height=260)

    # ─── NEW ID 42 · 3D Live Circuit Hologram ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌐 3D Live Circuit Hologram</div>', unsafe_allow_html=True)
    track_len_m_42 = _TRACK_LEN.get(sel_race, 5.5) * 1000
    K_T_42 = 4.0
    K_S_42 = 6.5
    NS_42 = 260
    t_arr_42 = np.linspace(0, 2 * np.pi * 1.6, NS_42)
    def _cx_(t): return K_T_42 * (np.sin(t) + 0.28*np.sin(2*t) - 0.09*np.sin(3*t))
    def _cy_(t): return K_S_42 * (np.cos(t) - 0.12*np.cos(2*t) + 0.08*np.cos(4*t))
    tx_42 = _cx_(t_arr_42) * 5.5
    ty_42 = _cy_(t_arr_42) * 5.5
    tz_42 = 0.55 * np.sin(t_arr_42) + 0.35 * np.cos(2 * t_arr_42)
    gx42, gy42 = np.gradient(tx_42), np.gradient(ty_42)
    gl42 = np.sqrt(gx42**2 + gy42**2); gl42[gl42==0]=1.0
    hw42 = 2.5
    tx_in_42 = (tx_42 + hw42 * (-gy42/gl42)).tolist()
    ty_in_42 = (ty_42 + hw42 * ( gx42/gl42)).tolist()
    rng_42 = _seeded(hash(sel_race + str(year) + 'holo') % 2**31)
    spd_42 = np.clip(200 + 80*np.sin(t_arr_42*3.5) + rng_42.normal(0,5,NS_42), 60, 360)
    car_progress = (cur_lap / max(total_lap, 1))
    car_idx_pos  = int(car_progress * NS_42) % NS_42
    fig_holo = go.Figure()
    fig_holo.add_trace(go.Scatter3d(
        x=tx_42.tolist(), y=ty_42.tolist(), z=tz_42.tolist(),
        mode='lines', line=dict(color='rgba(255,255,255,0.25)', width=4), name='Track Border',
    ))
    fig_holo.add_trace(go.Scatter3d(
        x=tx_in_42 + [tx_in_42[0]], y=ty_in_42 + [ty_in_42[0]], z=tz_42.tolist() + [tz_42[0]],
        mode='lines', line=dict(color='rgba(100,100,100,0.5)', width=2), showlegend=False,
    ))
    fig_holo.add_trace(go.Scatter3d(
        x=[tx_42[car_idx_pos]], y=[ty_42[car_idx_pos]], z=[tz_42[car_idx_pos]],
        mode='markers+text', name=f'Leader (Lap {cur_lap})',
        marker=dict(size=12, color='#ffd700'), text=["🏎️"], textposition='middle center',
    ))
    fig_holo.add_trace(go.Scatter3d(
        x=tx_42.tolist(), y=ty_42.tolist(), z=tz_42.tolist(),
        mode='lines', line=dict(color=spd_42.tolist(), colorscale='Turbo', width=7),
        name='Racing Line', showlegend=False,
    ))
    fig_holo.update_layout(
        template='plotly_dark', height=520,
        paper_bgcolor='rgba(0,0,0,0)',
        scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                   aspectmode='data', bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=0,r=0,t=22,b=0),
        title=f'🌐 {sel_race} {year} — Circuit Hologram',
    )
    st.plotly_chart(fig_holo, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 43 · Driver Radio Sentiment Analysis ─────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📻 Driver Radio Sentiment Analysis</div>', unsafe_allow_html=True)
    s_sent = _seeded(hash(str(year) + sel_race + 'sentiment') % 2**31)
    top_drv_sent = [r['driver'] for r in res_cc[:6]] if res_cc else []
    sent_labels = ['Aggressive', 'Confident', 'Tired', 'Frustrated', 'Stressed', 'Positive']
    sent_data = []
    for drv_s in top_drv_sent:
        drv_ss = _seeded(hash(drv_s + str(year) + sel_race) % 2**31)
        for lbl_s in sent_labels:
            base_s = {'Aggressive':0.6,'Confident':0.7,'Tired':0.15,'Frustrated':0.2,
                      'Stressed':0.25,'Positive':0.65}.get(lbl_s, 0.4)
            score_s = float(np.clip(base_s + drv_ss.normal(0, 0.22), 0.0, 1.0))
            sent_data.append({'Driver': drv_s, 'Sentiment': lbl_s, 'Score': score_s})
    df_sent = pd.DataFrame(sent_data)
    pivot_sent = df_sent.pivot(index='Driver', columns='Sentiment', values='Score').fillna(0)
    fig_sent = go.Figure(data=go.Heatmap(
        z=pivot_sent.values,
        x=pivot_sent.columns, y=pivot_sent.index,
        colorscale='RdYlGn', colorbar=dict(title="Sentiment"),
        text=[[f"{v:.0%}" for v in row] for row in pivot_sent.values],
        texttemplate="%{text}", textfont=dict(size=10),
    ))
    fig_sent.update_layout(
        template='plotly_dark', height=max(240, len(pivot_sent) * 38),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Sentiment Category', yaxis_title='',
        title=f"Radio Sentiment Intensity — {sel_race} {year}",
    )
    st.plotly_chart(fig_sent, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 44 · Weather Evolution Radar ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌦️ Weather Evolution Radar</div>', unsafe_allow_html=True)
    s_wxr = _seeded(hash(str(year) + sel_race + 'wxradar') % 2**31)
    wx_cats = ['Track Temp', 'Air Temp', 'Rain', 'Wind Speed', 'Humidity', 'Visibility']
    base_wx = [float(np.clip(s_wxr.normal(0.72, 0.12), 0, 1)) for _ in wx_cats]
    mid_wx  = [float(np.clip(b + s_wxr.normal(0, 0.22), 0, 1)) for b in base_wx]
    end_wx  = [float(np.clip(m + s_wxr.normal(0, 0.22), 0, 1)) for m in mid_wx]
    fig_wxr = go.Figure()
    for lbl_wx, vals_wx, col_wx in [('Race Start', base_wx, '#ffd700'),
                                      ('Mid-Race',   mid_wx,  '#1f77b4'),
                                      ('Race End',   end_wx,  '#ff4444')]:
            vals_closed = vals_wx + [vals_wx[0]]
            hex_c = col_wx.lstrip('#')
            r255   = int(hex_c[0:2], 16)
            g255   = int(hex_c[2:4], 16)
            b255   = int(hex_c[4:6], 16)
            fig_wxr.add_trace(go.Scatterpolar(
                r=vals_closed, theta=wx_cats + [wx_cats[0]],
                fill='toself', name=lbl_wx,
                line=dict(color=col_wx), fillcolor=f'rgba({r255},{g255},{b255},0.18)',
            ))
    fig_wxr.update_layout(
        polar=dict(radialaxis=dict(range=[0,1], gridcolor='rgba(255,215,0,0.2)'),
                   angularaxis=dict(gridcolor='rgba(255,215,0,0.2)')),
        template='plotly_dark', height=380,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h'),
        title=f"Weather Radar — {sel_race} {year}",
    )
    st.plotly_chart(fig_wxr, config={'displayModeBar': False})

    # ─── NEW ID 45 · Live DRS Usage Monitor ──────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏎️ Live DRS Usage Monitor</div>', unsafe_allow_html=True)
    s_drs = _seeded(hash(str(year) + sel_race + 'drslive') % 2**31)
    n_drs_laps = min(30, total_lap)
    drs_active_proxy = np.clip(s_drs.normal(0.38, 0.22, n_drs_laps), 0, 1)
    drs_laps_x = list(range(1, n_drs_laps + 1))
    fig_drs = go.Figure()
    fig_drs.add_trace(go.Bar(
        x=drs_laps_x, y=drs_active_proxy.tolist(), name='DRS Active %',
        marker=dict(
            color=drs_active_proxy.tolist(), colorscale='YlGn',
            colorbar=dict(title="Activation"), opacity=0.85,
            line=dict(width=0.5, color='white'),
        ),
    ))
    fig_drs.add_trace(go.Scatter(
        x=drs_laps_x, y=[float(np.mean(drs_active_proxy))]*n_drs_laps,
        mode='lines', name=f'Avg: {np.mean(drs_active_proxy):.0%}',
        line=dict(color='#ff4444', width=2, dash='dash'),
    ))
    fig_drs.update_layout(
        xaxis_title='Lap', yaxis_title='DRS Active %', height=310,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"DRS Usage Monitor — {sel_race} {year}",
        yaxis=dict(tickformat='.0%'),
        hovermode='x unified',
    )
    fig_drs.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_drs.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_drs, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 46 · 3D Car Position Swarm ─────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🕸️ 3D Car Position Swarm</div>', unsafe_allow_html=True)

    n_swarm = min(8, len(res_cc) if res_cc else 8)
    swarm_drv = [res_cc[i]['driver'] for i in range(n_swarm)] if res_cc else [f'Car {i+1}' for i in range(n_swarm)]
    swarm_T   = 220

    used_colors = set()

    def _driver_color(drv):
        base = DRIVER_COLORS.get(drv)
        if base and base not in used_colors:
            used_colors.add(base)
            return base
        for alt in _F1_COLORS:
            if alt not in used_colors:
                used_colors.add(alt)
                return alt
        idx = abs(hash(drv)) % len(_F1_COLORS)
        return _F1_COLORS[idx]

    def _hex_to_rgba(hex_c, a):
        h = hex_c.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f'rgba({r},{g},{b},{a})'

    track_scale = 18.0
    ns_t = 200
    t_ell = np.linspace(0, 2 * np.pi * 2, ns_t)
    tx_ell = track_scale * np.cos(t_ell * 0.88)
    ty_ell = track_scale * np.sin(t_ell)
    HEIGHT_SCALE = 1.25
    tz_ell = 0.75 * np.sin(t_ell * 1.1) * HEIGHT_SCALE

    fig_sw = go.Figure()

    # Subtle track footprint guide
    fig_sw.add_trace(go.Scatter3d(
        x=tx_ell.tolist(), y=ty_ell.tolist(), z=tz_ell.tolist(),
        mode='lines', line=dict(color='rgba(80,80,100,0.35)', width=2),
        hoverinfo='skip', showlegend=False,
    ))

    for sdi, drv_sw in enumerate(swarm_drv):
        ssw = _seeded(hash(drv_sw + str(year) + sel_race + 'swarm') % 2**31)
        dcol = _driver_color(drv_sw)
        rgba_mid = _hex_to_rgba(dcol, 0.80)
        rgba_lo  = _hex_to_rgba(dcol, 0.04)
        rgba_hi  = _hex_to_rgba(dcol, 0.55)

        gap_adv  = float(ssw.uniform(-3.2, 3.6))
        lat_gap  = float(ssw.normal(0, 0.80))
        lat_osc  = float(ssw.normal(0, 0.55))
        spd_amp  = float(ssw.normal(0, 0.45))
        spd_tilt = float(ssw.normal(0, 0.60))

        ang_j  = (t_ell[:ns_t] + gap_adv * 0.14 + lat_osc).tolist()
        rad_j  = (track_scale + lat_gap +
                  ssw.normal(0, 0.55, ns_t).cumsum() * 0.035).tolist()
        ang_j  = list(ang_j)
        # convert polar→cartesian
        sw_x = [rad_j[i] * np.cos(ang_j[i]) for i in range(len(rad_j))]
        sw_y = [rad_j[i] * np.sin(ang_j[i]) for i in range(len(rad_j))]
        sw_z = (0.75 * np.sin(np.linspace(0, 2*np.pi*1.8, ns_t))
                * HEIGHT_SCALE + spd_amp * np.sin(t_ell[:ns_t]) + spd_tilt
                + ssw.normal(0, 0.06, ns_t)).tolist()

        # shorten lists to same length
        n_pt = min(len(sw_x), len(sw_y), len(sw_z))
        sw_x, sw_y, sw_z = sw_x[:n_pt], sw_y[:n_pt], sw_z[:n_pt]

        # Ghost trail (faded tail)
        fig_sw.add_trace(go.Scatter3d(
            x=sw_x, y=sw_y, z=sw_z,
            mode='lines',
            line=dict(color=rgba_lo, width=2),
            hoverinfo='skip', showlegend=False,
        ))

        # Main animated trail glow
        fig_sw.add_trace(go.Scatter3d(
            x=sw_x, y=sw_y, z=sw_z,
            mode='lines',
            line=dict(
                color=[rgba_hi if (i / max(n_pt - 1, 1)) > 0.45 else rgba_lo for i in range(n_pt)],
                width=4,
            ),
            hoverinfo='skip', showlegend=False,
        ))

        # Current car location — bright pin
        fig_sw.add_trace(go.Scatter3d(
            x=[sw_x[-1]], y=[sw_y[-1]], z=[sw_z[-1]],
            mode='markers+text',
            name=drv_sw,
            marker=dict(
                size=10, color=dcol,
                line=dict(width=2.5, color='white'),
                opacity=1.0,
            ),
            text=[drv_sw],
            textposition='top center',
            textfont=dict(size=11, color='white', family='Arial Bold'),
            hovertemplate=
            f'<b>{drv_sw}</b><br>'
            'X: %{x:.1f}<br>Y: %{y:.1f}<br>Z: %{z:.2f}<extra></extra>',
        ))

    fig_sw.update_layout(
        template='plotly_dark', height=560,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Car Position Swarm — {sel_race} {year}",
        scene=dict(
            xaxis=dict(visible=False, showbackground=False),
            yaxis=dict(visible=False, showbackground=False),
            zaxis=dict(
                visible=True,
                title=dict(text='Vertical Offset', font=dict(size=11, color='rgba(255,215,0,0.75)')),
                showbackground=False,
                gridcolor='rgba(255,215,0,0.08)',
            ),
            bgcolor='rgba(0,0,0,0)',
            aspectmode='data',
        ),
        legend=dict(
            orientation='h', x=0.5, y=0.0,
            xanchor='center', yanchor='top',
            font=dict(size=12, color='white'),
            bgcolor='rgba(0,0,0,0.45)',
            bordercolor='rgba(255,215,0,0.25)',
            borderwidth=1,
        ),
        margin=dict(l=12, r=12, t=38, b=30),
    )
    st.plotly_chart(fig_sw, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 47 · Track Dominance Zones ─────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 Track Dominance Zones</div>', unsafe_allow_html=True)
    s_dom = _seeded(hash(str(year) + sel_race + 'domzones') % 2**31)
    res_dom = res_cc if res_cc else []
    n_cars_ = 8
    track_pos_dom = np.linspace(0, track_len_m_42, 60)
    dom_z = np.zeros((n_cars_, len(track_pos_dom)))
    for cdi in range(n_cars_):
        rng_dc = _seeded(hash(sel_race + str(year) + f'dom{cdi}') % 2**31)
        base_dom = rng_dc.uniform(50, 95)
        corner_mod = 0.5 + 0.5 * np.sin(track_pos_dom / 280.0)
        dom_z[cdi, :] = base_dom + s_dom.normal(0, 9, len(track_pos_dom)) + corner_mod * rng_dc.uniform(-10, 10)
    dom_z = np.clip(dom_z, 0, 100)
    car_labels_td = [res_dom[i]['driver'] for i in range(n_cars_)] if res_dom else [f'Car {i+1}' for i in range(n_cars_)]
    dom_colorscale_td = s_dom.choice(['RdYlGn', 'Viridis', 'YlOrRd'])
    fig_dom = go.Figure(data=go.Heatmap(
        z=dom_z, x=[f"{int(x)}m" for x in track_pos_dom[::5]],
        y=car_labels_td, colorscale=dom_colorscale_td,
        colorbar=dict(title="Dominance %"),
    ))
    fig_dom.update_layout(
        template='plotly_dark', height=max(280, n_cars_ * 26),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Track Position', yaxis_title='',
        title=f"Track Dominance Zones — {sel_race} {year}",
    )
    st.plotly_chart(fig_dom, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 48 · Live Strategy Battle Matrix ────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⚔️ Live Strategy Battle Matrix</div>', unsafe_allow_html=True)
    s_bat = _seeded(hash(str(year) + sel_race + 'battle') % 2**31)
    strategies_b = ['Soft 1-Stop', 'Soft 2-Stop', 'Medium 1-Stop',
                    'Medium 2-Stop', 'Hard 1-Stop', 'Hard 2-Stop']
    n_strategies = len(strategies_b)
    batt_z = np.zeros((n_strategies, n_strategies))
    for si in range(n_strategies):
        for sj in range(n_strategies):
            score_mine  = s_bat.integers(1, 25)
            score_theirs = s_bat.integers(1, 25)
            batt_z[si, sj] = float(score_mine - score_theirs)
        batt_z[si, si] = 0.0
    fig_bat = go.Figure(data=go.Heatmap(
        z=batt_z, x=strategies_b, y=strategies_b,
        colorscale='RdYlGn', colorbar=dict(title="Position Delta"),
        text=[[f"{v:+.1f}" for v in row] for row in batt_z],
        texttemplate="%{text}", textfont=dict(size=10),
    ))
    fig_bat.add_trace(go.Scatter(
        x=strategies_b, y=strategies_b, mode='markers',
        marker=dict(size=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip',
    ))
    fig_bat.update_layout(
        template='plotly_dark', height=400,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Strategy Battle Matrix — {sel_race} – Your Car Advantage",
        xaxis_title='Opponent Strategy', yaxis_title='Your Strategy',
    )
    st.plotly_chart(fig_bat, use_container_width=True, config={'displayModeBar': False})
    best_strat_idx = np.argmax(batt_z.sum(axis=1))
    st.caption(f"✅ VERSATILE BEST YOURS: **{strategies_b[best_strat_idx]}**  |  Win rate vs each strategy indicated by colour")

    # ─── NEW ID 49 · Race Control Decision Stream ───────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🚦 Race Control Decision Stream</div>', unsafe_allow_html=True)
    s_49 = _seeded(hash(sel_race + str(year) + 'rc_stream') % 2**31)
    cur_time_min = int(total_lap * 1.35) if total_lap else 56
    rc_events = []
    seen_laps = set()
    while len(rc_events) < 18:
        lap_rc   = s_49.integers(1, total_lap + 1)
        m_rc     = s_49.integers(1, cur_time_min)
        dec_types = ['GREEN FLAG', 'YELLOW FLAG', 'DOUBLE YELLOW',
                     'SC DEPLOYED', 'SC ENDED', 'VSC - PHASE 1', 'VSC - PHAS E2',
                     'TRACK CLEAR', 'PIT LANE OPEN', 'RED FLAG']
        dec_type = s_49.choice(dec_types)
        sev_rc   = {'GREEN FLAG':0,'YELLOW FLAG':1,'DOUBLE YELLOW':2,
                     'SC DEPLOYED':4,'SC ENDED':0,'VSC - PHASE 1':3,'VSC - PHASE 2':2,
                     'TRACK CLEAR':0,'PIT LANE OPEN':0,'RED FLAG':5}.get(dec_type, 0)
        if lap_rc not in seen_laps:
            seen_laps.add(lap_rc)
            rc_events.append({'Lap': lap_rc, 'Time (min)': m_rc, 'Decision': dec_type, 'Severity': sev_rc})
    df_rc = pd.DataFrame(rc_events).sort_values('Lap')
    sev_rc_col = {0:'#00d2be',1:'#ffd700',2:'#ff8800',3:'#ff4444',4:'#ff00ff',5:'#8b0000'}
    df_rc['Color'] = df_rc['Severity'].map(sev_rc_col)
    fig_stream = go.Figure()
    colour_list = df_rc['Color'].tolist()
    for i_ev, row in df_rc.iterrows():
        fig_stream.add_trace(go.Scatter(
            x=[row['Lap']], y=[row['Severity']],
            mode='markers+text', name='',
            marker=dict(size=[12 + row['Severity']*3], color=row['Color'],
                        line=dict(width=1, color='white')),
            text=[row['Decision']], textposition='top center',
            hoverinfo='text',
            hovertemplate=f"<b>{row['Decision']}</b><br>Lap: {row['Lap']}<br>T+{row['Time (min)']}min<extra></extra>",
        ))
    fig_stream.update_layout(
        template='plotly_dark', height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Lap', yaxis_title='Severity (0=Green, 5=Red)',
        title=f"Race Control Stream — {sel_race} ({year})",
        showlegend=False, yaxis=dict(tickmode='array', tickvals=list(range(6)),
                                     ticktext=['GREEN','YELLOW','Dbl YEL','VSC','SC','RED']),
    )
    fig_stream.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_stream, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 50 · 3D Predictive Race Simulator ───────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏎️ 3D Predictive Race Simulator</div>', unsafe_allow_html=True)
    s_sim50 = _seeded(hash(str(year) + sel_race + 'sim50') % 2**31)
    N_50 = 60
    laps_50 = np.linspace(1, int(total_lap), N_50)
    pos_50  = np.linspace(1, 20, N_50)
    pit_var = float(np.clip(s_sim50.normal(3.5, 1.3), 0.5, 8.0))
    base_gr = 0.055
    X_50, Y_50 = np.meshgrid(laps_50, pos_50)
    Z_50 = (base_gr * X_50 + pit_var * np.sin(X_50 / 15.0) +
            s_sim50.normal(0, 0.45, X_50.shape))
    Z_pred_max = np.zeros_like(Z_50)
    for ri_50 in range(Z_50.shape[0]):
        Z_pred_max[ri_50, :] = np.maximum.accumulate(Z_50[ri_50, :])
    fig_sim50 = go.Figure()
    fig_sim50.add_trace(go.Surface(
        x=X_50, y=Y_50, z=Z_50,
        colorscale='RdBu_r', opacity=0.88,
        showscale=False, name='Projected Gap',
    ))
    type_line50 = 9.8 + s_sim50.normal(0, 2.2, N_50).cumsum() * 0.08
    type_line50 = np.clip(type_line50, 1, 20)
    fig_sim50.add_trace(go.Scatter3d(
        x=laps_50.tolist(), y=type_line50.tolist(), z=Z_50.mean(axis=0).tolist(),
        mode='lines', name='Pit Stop Zone',
        line=dict(color='#ffd700', width=5),
    ))
    fig_sim50.update_layout(
        template='plotly_dark', height=520,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"3D Race Predictor — {sel_race} ({year})",
        scene=dict(xaxis_title='Lap', yaxis_title='Position', zaxis_title='Gap (s)',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_sim50, use_container_width=True, config={'displayModeBar': False})

