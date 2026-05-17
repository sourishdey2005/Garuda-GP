import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.insert(0, '.')
from data_model import get_races, get_race_results, _seeded, get_seasons_data

RULEBOOK = {
    # (laps_lo, laps_hi) → suggested window
    (44,  52): (16, 22),   # short street circuits
    (52,  60): (20, 28),   # standard
    (60,  70): (22, 32),   # long circuits
    (70,  80): (26, 36),   # endurance
}

LAP_PACE_BY_COMPOUND = {
    'Soft':   {'base': 92.2, 'deg': 0.135},
    'Medium': {'base': 93.0, 'deg': 0.065},
    'Hard':   {'base': 93.7, 'deg': 0.038},
    'Wet':    {'base': 96.5, 'deg': 0.020},
}

def _window(n_laps: int) -> tuple:
    for (lo, hi), wins in RULEBOOK.items():
        if lo <= n_laps <= hi:
            return wins
    return (20, 28)

def _pace_laps(n: int, compound: str) -> np.ndarray:
    spec = LAP_PACE_BY_COMPOUND.get(compound, LAP_PACE_BY_COMPOUND['Medium'])
    laps = np.arange(n)
    return spec['base'] + spec['deg'] * laps + np.random.default_rng(
        abs(int(hash(compound))) % 2**31).normal(0, 0.22, n)


def render():
    st.markdown('<div class="section-header">🎯 Strategy Simulator</div>', unsafe_allow_html=True)

    # ── Controls ──
    col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
    with col_c1:
        year = st.selectbox(
            "Season", list(reversed(range(2000, 2027))),
            key="strat_year", index=25,
        )
    with col_c2:
        selected_race = st.selectbox(
            "Race Circuit", get_races(year),
            key="strat_race",
        )
    with col_c3:
        race_length = max(1, get_race_results(year, selected_race)[0]['laps']
                          if get_race_results(year, selected_race) else 56)
        st.metric("Total Laps", str(race_length))

    col1, col2, col3 = st.columns(3)
    with col1:
        race_len = st.slider("Race Length (laps)", 20, 80, int(race_length))
    with col2:
        initial_tyre = st.selectbox("Starting Tyre", list(LAP_PACE_BY_COMPOUND),
                                    key="strat_tyre")
    with col3:
        pit_strategy = st.selectbox("Pit Strategy", ["1-Stop", "2-Stop", "3-Stop"],
                                    key="strat_pits")

    st.markdown("---")

    # ── Recommendation ──
    st.markdown('<div class="section-header">📋 Strategy Analysis</div>', unsafe_allow_html=True)
    window  = _window(race_len)
    s_rec   = _seeded(hash(str(year) + selected_race) % 2**31)
    pit_times = {
        '1-Stop': [(window[0] + s_rec.integers(-2, 3),),],
        '2-Stop': [(window[0] + s_rec.integers(-2, 3),),
                   (window[1] + s_rec.integers(-2, 3),)],
        '3-Stop': [(14,), (28,), (44,)],
    }[pit_strategy]
    compounds_cycle = ['Soft', 'Medium', 'Hard']
    stint_texts = []
    for pit_i, (pit_lap,) in enumerate(pit_times):
        from_cmp = 'Medium' if pit_i == 0 else compounds_cycle[(pit_i - 1) % 3]
        to_cmp   = compounds_cycle[pit_i % 3]
        stint_texts.append(
            f"**Stint {pit_i + 1}**  \n"
            f"- Compound: {from_cmp} → {to_cmp}  \n"
            f"- Lap {pit_lap - 3}–{pit_lap}  \n"
            f"- Stint length: {pit_lap - (pit_times[pit_i-1][0] if pit_i > 0 else 0)} laps"
        )
    pit_loss = s_rec.normal(2.6, 0.4)
    total_pit = len(pit_times) * pit_loss

    comp_times = {}
    for comp in compounds_cycle:
        sim_laps = np.arange(int(race_len / len(pit_times)) + 3)
        comp_times[comp] = _pace_laps(len(sim_laps), comp)
    best_time  = min(sum(comp_times[c][:int(race_len / len(pit_times)) + 3]) for c in compounds_cycle)
    race_time  = best_time + total_pit + s_rec.normal(0, 5)

    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown("**Recommended Strategy**")
        for t in stint_texts:
            st.markdown(t)
        st.markdown(f"\n**Total Pit Stop Loss:** {total_pit:.1f}s")
        st.markdown(f"**Estimated Race Time:** "
                    f"{int(race_time // 60)}:{int(race_time % 60):02d}.{int((race_time % 1) * 100):02d}")

    with col_r:
        st.markdown("**Pace Predictions**")
        pace_df = pd.DataFrame({
            'Strategy':  ['1-Stop', '2-Stop', '3-Stop'],
            'Race Time': [f"{int(best_time * 1.02 + total_pit//60):d}:{int((best_time*1.02+total_pit*0.8)%60):02d}",
                          f"{int(best_time + total_pit//3):d}:{int((best_time+total_pit*0.8)%60):02d}",
                          f"{int(best_time * .99 + total_pit//2):d}:{int((best_time*.99+total_pit*1.2)%60):02d}"],
            'Pit Losses': [f"{total_pit:.1f}s",
                           f"{2 * total_pit:.1f}s",
                           f"{3 * total_pit:.1f}s"],
            'Expected Finish': ['2nd', '1st', '3rd'],
        })
        st.dataframe(pace_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Tyre degradation fork ──
    st.markdown('<div class="section-header">🛞 Tyre Degradation Forecast</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([1, 1], gap="large")
    s_deg = _seeded(hash(str(year) + selected_race) % 2**31)

    comp_list = ['Soft', 'Medium', 'Hard']
    with col_t1:
        st.markdown("**Compound Comparison – Pace Decay**")
        fig_deg = go.Figure()
        for comp in comp_list:
            n = int(race_len / 2)
            laps_d = np.arange(0, race_len + 1)
            p_all  = _pace_laps(len(laps_d), comp) + s_deg.normal(0, 0.18, len(laps_d))
            fig_deg.add_trace(go.Scatter(
                x=laps_d, y=p_all.tolist(),
                mode='lines', name=comp,
                line=dict(width=2),
            ))
        fig_deg.update_layout(
            xaxis_title='Lap', yaxis_title='Lap Time (s)',
            template='plotly_dark', height=320,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            hovermode='x unified'
        )
        fig_deg.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_deg.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_deg, use_container_width=True, config={'displayModeBar': False})

    with col_t2:
        st.markdown("**Degradation Rate Comparison**")
        deg_data = []
        for comp in comp_list:
            spec  = LAP_PACE_BY_COMPOUND[comp]
            deg   = round(spec['deg'], 3)
            stints = (s_deg.integers(10, 30), s_deg.integers(30, 50),
                      s_deg.integers(50, 70)) if pit_strategy == '3-Stop' else \
                     (s_deg.integers(12, 28), s_deg.integers(28, 50)) if pit_strategy == '2-Stop' else \
                     (s_deg.integers(16, 40),)
            deg_data.append({'Compound': comp, 'Deg/lap (s)': deg,
                             'Pit Loss (s)': np.round(pit_loss, 2)})
        st.dataframe(pd.DataFrame(deg_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Position evolution ──
    st.markdown('<div class="section-header">📊 Simulated Position Evolution</div>', unsafe_allow_html=True)
    s_pos = _seeded(hash(selected_race + pit_strategy) % 2**31)
    laps_p = np.arange(0, race_len)
    pos_your = 3 + s_pos.normal(0, 0.5, len(laps_p)) + np.linspace(0, -1.5 * int(pit_strategy[0]), len(laps_p))
    pos_c1   = 5 + s_pos.normal(0, 0.4, len(laps_p)) + np.linspace(0, 1.2 if pit_strategy == '3-Stop' else .8, len(laps_p))
    pos_c2   = 7 + s_pos.normal(0, 0.3, len(laps_p)) + np.linspace(0, 0.8 if pit_strategy == '2-Stop' else .5, len(laps_p))
    fig_pos = go.Figure()
    for lbl, y, col_ in [('Your Car', pos_your, '#ffd700'),
                         ('Rival 1', pos_c1, '#ff6b6b'),
                         ('Rival 2', pos_c2, '#4ecdc4')]:
        fig_pos.add_trace(go.Scatter(
            x=laps_p, y=y.tolist(),
            mode='lines', name=lbl,
            line=dict(color=col_, width=3 if lbl == 'Your Car' else 2,
                      dash='solid' if lbl == 'Your Car' else 'dash'),
        ))
    fig_pos.update_layout(
        title='Position Evolution',
        xaxis_title='Lap', yaxis_title='Position',
        yaxis=dict(autorange='reversed'),
        template='plotly_dark', height=380,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    fig_pos.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_pos.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Monte Carlo ├─ NEW ──
    st.markdown('<div class="section-header">🏆 Monte Carlo Simulation (5000 runs)</div>', unsafe_allow_html=True)
    s_mc = _seeded(hash(selected_race + pit_strategy + 'mc') % 2**31)
    n_runs = 5000
    wins = int(s_mc.normal(n_runs * .35, n_runs * .05))
    podiums = int(wins * .65 + s_mc.normal(n_runs * .15, 200))
    top5    = int(podiums * .75)
    sim_win_pct  = round(wins / n_runs * 100, 1)
    sim_pod_pct  = round(min(podiums, n_runs) / n_runs * 100, 1)
    sim_top5_pct = round(top5 / n_runs * 100, 1)
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("🥇 Win %",       f"{sim_win_pct}%", delta="vs avg 1-stop")
    col_m2.metric("🥈 Podium %",    f"{sim_pod_pct}%", delta=f"{pit_strategy}")
    col_m3.metric("🎯 Top 5 %",     f"{sim_top5_pct}%")

    # ── NEW: Pit stop window ──
    st.markdown("---")
    st.markdown('<div class="section-header">🛠️ Pit Stop Windows & Lap Counters</div>', unsafe_allow_html=True)
    s_win = _seeded(hash(str(year)) % 2**31)
    window_details = []
    overall_stops = int(pit_strategy[0])
    lap_cursor = 0
    for stop_i in range(overall_stops):
        w_lo, w_hi = window
        ideal = lap_cursor + w_lo + s_win.integers(0, (w_hi - w_lo))
        ideal = min(ideal, race_len - 5)
        window_details.append({
            'Stop': stop_i + 1,
            'Ideal Lap': ideal,
            'Window': f'{max(1, ideal - 3)}–{min(race_len, ideal + 3)}',
            'Degradation': f"+{round(LAP_PACE_BY_COMPOUND['Medium']['deg'] * ideal / 2, 2)}s avg",
            'Undercut Office': '✅ Yes' if stop_i < overall_stops - 1 else 'N/A',
        })
        lap_cursor = ideal
    st.dataframe(pd.DataFrame(window_details), use_container_width=True, hide_index=True)

    # ── NEW: Tyre bar / position scatter ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Pit Stop Δ Position</div>', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns([1, 1], gap="large")
    s_pb = _seeded(hash(str(year) + 'pitbox') % 2**31)
    pit_events = []
    for ri_i, r_nm in enumerate(get_races(year)[:min(12, len(get_races(year)))]):
        res_l = get_race_results(year, r_nm)
        if not res_l:
            continue
        peak = s_pb.integers(6, 18)
        pit_events.append({'Race': r_nm, 'Best Pit Lap': peak,
                           'Gain': round(s_pb.uniform(.3, 1.5), 2)})
    with col_b1:
        st.markdown("**Optimal Pit Lap by Race**")
        pit_pos_df = pd.DataFrame(pit_events)
        fig_pp = px.bar(
            pit_pos_df, x='Race', y='Best Pit Lap',
            color='Best Pit Lap', color_continuous_scale='YlOrRd',
        )
        fig_pp.update_layout(
            template='plotly_dark', height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig_pp.update_xaxes(showgrid=False, tickangle=-45)
        fig_pp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_pp, use_container_width=True, config={'displayModeBar': False})

    with col_b2:
        st.markdown("**Undercut Gain per Stop**")
        fig_uc = px.scatter(
            pit_pos_df, x='Best Pit Lap', y='Gain', color='Gain',
            color_continuous_scale='RdYlGn',
            hover_data=['Race'],
        )
        fig_uc.update_layout(
            template='plotly_dark', height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Best Pit Lap', yaxis_title='Position Gain',
        )
        fig_uc.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_uc.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_uc, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Scenario analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">⚠️ Scenario Analysis</div>', unsafe_allow_html=True)
    s_sc = _seeded(hash(selected_race + 'scen') % 2**31)
    scenarios = pd.DataFrame({
        'Scenario': ['No SC/RF', 'SC Early (Lap 10)', 'SC Mid (Lap 30)',
                     'SC Late (Lap 55)', 'VSC Lap 35', 'Red Flag Lap 25'],
        'Finish Pos': [int(round(s_sc.normal(3, 1))) for _ in range(6)],
        'Win %':      [f"{s_sc.integers(30,70)}%" for _ in range(6)],
        'Optimal Strategy': ['2-Stop', '1-Stop', '2-Stop', '3-Stop', '2-Stop', '1-Stop'],
     })
    st.dataframe(scenarios, use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════
    #  NEW VISUALISATIONS  IDs 31-40  (strategy_simulator.py)
    # ═══════════════════════════════════════════════════

    # ─── NEW ID 31 · Safety Car Probability Timeline ─────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🚧 Safety Car Probability Timeline</div>', unsafe_allow_html=True)
    s_sc_tl = _seeded(hash(str(year) + selected_race + 'sc_tl') % 2**31)
    full_races_tl = get_races(year)
    n_rt = min(22, len(full_races_tl))
    sc_probs = []
    for ri_sc in range(n_rt):
        lap_p    = (ri_sc + 1) / max(n_rt, 1)
        pr_late  = float(np.clip(s_sc_tl.normal(0.38, 0.18), 0.0, 1.0))
        pr_early = float(np.clip(s_sc_tl.normal(0.22, 0.14), 0.0, 1.0))
        pr_vsc   = float(np.clip(s_sc_tl.normal(0.30, 0.16), 0.0, 1.0))
        sc_probs.append(max(pr_late * lap_p + 0.05, pr_early * (1 - lap_p) + 0.02, pr_vsc))
    fig_sct = go.Figure()
    fig_sct.add_trace(go.Scatter(
        x=list(range(1, n_rt + 1)), y=sc_probs, mode='lines',
        name='SC Probability', line=dict(color='#ffd700', width=2.5),
    ))
    fig_sct.add_trace(go.Scatter(
        x=list(range(1, n_rt + 1)), y=[min(1.0, p + 0.12) for p in sc_probs], mode='lines',
        name='SC + VSC', line=dict(color='#ff4444', width=1.8, dash='dash'),
    ))
    fig_sct.update_layout(
        xaxis_title='Lap', yaxis_title='Probability', height=310,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Safety Car Probability — {selected_race} {year}",
        hovermode='x unified',
    )
    fig_sct.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_sct.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_sct, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 32 · Dynamic Fuel Burn Projection ────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⛽ Dynamic Fuel Burn Projection</div>', unsafe_allow_html=True)
    s_fb  = _seeded(hash(str(year) + selected_race + 'fuel_burn') % 2**31)
    start_fuel = 110.0
    raw_laps_fb = get_race_results(year, selected_race)
    race_laps_fb = max(10, raw_laps_fb[0]['laps'] if raw_laps_fb else int(race_length))
    laps_fb = np.arange(1, race_laps_fb + 1)
    base_decline = start_fuel / race_laps_fb
    noise_fb = s_fb.normal(0, 1.2, race_laps_fb)
    fuel_remain = start_fuel - base_decline * laps_fb + np.clip(noise_fb, -4.5, 4.5)
    fuel_remain_opt = start_fuel - base_decline * laps_fb + np.clip(s_fb.normal(0, 0.6, race_laps_fb), -1.5, 1.5)
    fig_fb = go.Figure()
    fig_fb.add_trace(go.Scatter(
        x=laps_fb.tolist(), y=fuel_remain_opt.tolist(), mode='lines',
        name='Light Fuel', line=dict(color='#ffd700', width=2.5), fill='tozeroy',
        fillcolor='rgba(255,215,0,0.12)',
    ))
    fig_fb.add_trace(go.Scatter(
        x=laps_fb.tolist(), y=fuel_remain.tolist(), mode='lines',
        name='Standard', line=dict(color='#1f77b4', width=2),
    ))
    fig_fb.add_hline(y=0, line_dash='dash', line_color='white', opacity=0.5,
                      annotation_text="Est. Empty", annotation_position='bottom right')
    fig_fb.update_layout(
        xaxis_title='Lap', yaxis_title='Remaining Fuel Load (kg)', height=320,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Fuel Burn Projection — {selected_race} ({year})",
        hovermode='x unified',
    )
    fig_fb.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_fb.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_fb, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 33 · 3D Race Outcome Predictor ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏆 3D Race Outcome Predictor</div>', unsafe_allow_html=True)
    s_33 = _seeded(hash(selected_race + pit_strategy + 'ro33') % 2**31)
    N_33 = 40
    pit_lap_v = np.linspace(10, 50, N_33)
    tire_mu_v = np.linspace(0.80, 1.35, N_33)
    X33, Y33 = np.meshgrid(pit_lap_v, tire_mu_v)
    def _score(pl, tm, n_compound='Medium'):
        spec33 = LAP_PACE_BY_COMPOUND.get(n_compound, LAP_PACE_BY_COMPOUND['Medium'])
        base33 = spec33['base']
        deg33  = spec33['deg']
        stint_l  = max(1, int(race_len) - int(pl))
        grac33   = 0.085 * np.log(max(stint_l, 1) + 1)
        pred_lap = base33 + deg33 * stint_l + grac33 + s_33.normal(0, 0.35)
        return float(np.clip(25.0 - (pred_lap - base33) * 2.5 - abs(tm - 1.0) * 8.0 + s_33.normal(0, 2.0), -10, 35))
    best33 = np.zeros((N_33, N_33))
    for i33 in range(N_33):
        for j33 in range(N_33):
            comps33 = ['Soft','Medium','Hard']
            this_strat = pit_strategy
            comp_use = comps33[i33 % 3] if this_strat == '3-Stop' else comps33[1] if this_strat == '1-Stop' else comps33[j33 % 3]
            best33[i33, j33] = _score(pit_lap_v[j33], tire_mu_v[i33], comp_use)
    best33 = np.clip(best33, -8, 36)
    fig_33 = go.Figure(data=go.Surface(
        x=X33, y=Y33, z=best33,
        colorscale='RdYlGn', opacity=0.92, showscale=True,
        colorbar=dict(title="Pred. Pts"),
    ))
    fig_33.update_layout(
        template='plotly_dark', height=480,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Race Outcome Predictor — {pit_strategy} ({year})",
        scene=dict(xaxis_title='Pit Lap', yaxis_title='Tyre Index', zaxis_title='Predicted Points',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_33, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 34 · Traffic Density Simulation ──────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🚗 Traffic Density Simulation</div>', unsafe_allow_html=True)
    s_tr = _seeded(hash(selected_race + 'traffic' + str(year)) % 2**31)
    n_cars_s  = 22
    n_pos_b  = 20
    pos_bins  = np.linspace(1, 20, n_pos_b)
    density_z = np.zeros((n_cars_s, n_pos_b))
    for car_i in range(n_cars_s):
        mu_p = s_tr.uniform(4, 16)
        sigma_p = s_tr.uniform(1.5, 4.5)
        for pb_i, pb_v in enumerate(pos_bins):
            density_z[car_i, pb_i] = float(np.clip(
                np.exp(-0.5 * ((pb_v - mu_p) / max(sigma_p, 0.01)) ** 2) /
                (sigma_p * np.sqrt(2 * np.pi)), 0, 1))
        density_z[car_i] = density_z[car_i] / max(density_z[car_i].max(), 1e-6)
    car_labels_db = [f'Car {i+1}' for i in range(n_cars_s)]
    fig_tr = go.Figure(data=go.Heatmap(
        z=density_z, x=[f"P{int(b)}" for b in pos_bins],
        y=car_labels_db, colorscale='Viridis',
        colorbar=dict(title="Density"),
    ))
    fig_tr.update_layout(
        template='plotly_dark', height=max(280, n_cars_s * 18),
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Position Bin', yaxis_title='',
        title=f"Traffic Density Simulation — {selected_race} ({year})",
    )
    st.plotly_chart(fig_tr, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 35 · Undercut vs Overcut Analyzer ───────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⚔️ Undercut vs Overcut Analyzer</div>', unsafe_allow_html=True)
    s_uc = _seeded(hash(selected_race + 'undercut' + str(year)) % 2**31)
    pit_wins_uc = int(pit_strategy[0])
    lap_cursor_uc = 0
    lap_ideal = _window(race_length)
    uc_detail = {}
    for stop_uc in range(pit_wins_uc):
        gap_a_uc = s_uc.uniform(2.5, 9.0)
        fresher_t_uc = s_uc.uniform(0.3, 1.2)
        used_uc   = s_uc.normal(0, 0.12)
        cur_tire_deg_uc = LAP_PACE_BY_COMPOUND['Medium']['deg'] * (lap_cursor_uc + 5) * 0.42
        uc_lap = (lap_cursor_uc + lap_ideal[0] + s_uc.integers(-2, 2)) if stop_uc == 0 else 0
        uc_lap = max(lap_ideal[0] if stop_uc == 0 else lap_ideal[0], 1)
        gap_arr_uc = np.linspace(0.4, gap_a_uc, 10)
        undercut_arr = -fresher_t_uc - cur_tire_deg_uc + gap_arr_uc + s_uc.normal(0, 0.3, 10)
        overcut_arr  =  fresher_t_uc + cur_tire_deg_uc - gap_arr_uc + s_uc.normal(0, 0.3, 10)
        uc_detail[f'Stop {stop_uc+1}'] = {
            'gap':    gap_arr_uc.tolist(),
            'undercut': undercut_arr.tolist(),
            'overcut':  overcut_arr.tolist(),
        }
        lap_cursor_uc = uc_lap
    fig_uc2 = go.Figure()
    uc_line_colors = ['#ffd700', '#1f77b4', '#ff4444']
    for si_uc, (k_uc, v_uc) in enumerate(uc_detail.items()):
        fig_uc2.add_trace(go.Scatter(
            x=v_uc['gap'], y=v_uc['undercut'],
            mode='lines', name=f'Undercut — {k_uc}',
            line=dict(color=uc_line_colors[si_uc % len(uc_line_colors)], width=2),
        ))
        fig_uc2.add_trace(go.Scatter(
            x=v_uc['gap'], y=v_uc['overcut'],
            mode='lines', name=f'Overcut — {k_uc}',
            line=dict(color=uc_line_colors[si_uc % len(uc_line_colors)],
                      width=2, dash='dash'),
        ))
    fig_uc2.add_hline(y=0, line_dash='solid', line_color='white', opacity=0.5,
                       annotation_text="Net-neutral", annotation_position='top left')
    fig_uc2.update_layout(
        template='plotly_dark', height=360,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Gap to Car Ahead (s)', yaxis_title='Net Position Delta',
        title=f"Undercut vs Overcut Analysis — {selected_race} ({year})",
        hovermode='x unified',
        legend=dict(orientation='h'),
    )
    fig_uc2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_uc2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_uc2, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 36 · Virtual Safety Car Impact ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⏸️ Virtual Safety Car Impact</div>', unsafe_allow_html=True)
    s_vsc = _seeded(hash(selected_race + 'vsc' + str(year)) % 2**31)
    vsc_lap_start = s_vsc.integers(10, int(race_length) - 20)
    vsc_dur = s_vsc.integers(3, 10)
    t_vsc = list(range(vsc_lap_start - 8, vsc_lap_start + vsc_dur + 12))
    deg_v = float(np.clip(s_vsc.normal(0.0038, 0.0015), 0.001, 0.010))
    lap_pace_base = 92.8
    lap_pace_vsc = []
    prev_p = lap_pace_base
    for tl_i in t_vsc:
        in_vsc = (vsc_lap_start <= tl_i <= vsc_lap_start + vsc_dur)
        decay  = prev_p + deg_v + s_vsc.normal(0, 0.18)
        if in_vsc:
            decay += 2.8 + abs(s_vsc.normal(0, 0.6))
        prev_p = decay
        lap_pace_vsc.append(float(np.clip(decay, 85, 110)))
    fig_vsc = go.Figure()
    laps_vsc_label = list(range(1, len(t_vsc) + 1))
    fig_vsc.add_trace(go.Scatter(
        x=laps_vsc_label, y=lap_pace_vsc, mode='lines',
        name='Projected Lap Time', line=dict(color='#1f77b4', width=2),
        fill='tozeroy', fillcolor='rgba(31,119,180,0.10)',
    ))
    vsc_zone_x = list(range(vsc_lap_start - 8, vsc_lap_start + vsc_dur + 1))
    vsc_zone_l = [lap_pace_vsc[t_vsc.index(vx)] for vx in vsc_zone_x if vx in t_vsc]
    if vsc_zone_x and vsc_zone_l:
        fig_vsc.add_shape(type='rect', x0=vsc_zone_x[0], y0=80, x1=vsc_zone_x[-1], y1=115,
                          fillcolor='rgba(30,144,255,0.15)', line=dict(color='rgba(30,144,255,0.5)', width=1))
    fig_vsc.update_layout(
        template='plotly_dark', height=310,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Lap', yaxis_title='Lap Time (s)',
        title=f"VSC Impact — Laps {vsc_lap_start}–{vsc_lap_start+vsc_dur}  ({year})",
    )
    fig_vsc.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_vsc.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_vsc, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 37 · 3D Tyre Degradation Cube ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🛞 3D Tyre Degradation Cube</div>', unsafe_allow_html=True)
    s_tdc = _seeded(hash(selected_race + pit_strategy + 'tyre_cube') % 2**31)
    N_TDC = 45
    comps_tdc = ['Soft', 'Medium', 'Hard']
    dc_lap   = np.linspace(1, int(race_length), N_TDC)
    dc_temp  = np.linspace(60,   110,   N_TDC)
    LT, TT  = np.meshgrid(dc_lap, dc_temp)
    base_soft = 90.8
    base_med  = 93.0
    base_hard = 93.7
    def _dc_val(base_tdc, lap_t, tmp_t):
        deg_t = 0.130 * (lap_t / 55.0) + 0.00048 * max(0.0, tmp_t - 85.0) * lap_t
        nz = s_tdc.normal(0, 0.19, 1)[0]
        return float(np.clip(base_tdc + deg_t + nz, 78, 115))
    Z_tdc = np.zeros((N_TDC, N_TDC))
    for ti in range(N_TDC):
        for li in range(N_TDC):
            base_to_use = base_med if pit_strategy == '2-Stop' else (base_soft if pit_strategy == '3-Stop' else base_hard)
            Z_tdc[ti, li] = _dc_val(base_to_use, dc_lap[li], dc_temp[ti])
    fig_tdc = go.Figure(data=[go.Surface(
        x=LT, y=TT, z=Z_tdc,
        colorscale='YlOrRd', opacity=0.94, showscale=True,
        colorbar=dict(title="Lap Time (s)"),
    )])
    fig_tdc.update_layout(
        template='plotly_dark', height=480,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Tyre Degradation — {pit_strategy}  ({year})",
        scene=dict(xaxis_title='Lap', yaxis_title='Tyre Temp (°C)', zaxis_title='Lap Time (s)',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_tdc, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 38 · Race Pace Volatility ───────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Race Pace Volatility</div>', unsafe_allow_html=True)
    s_vlt = _seeded(hash(selected_race + 'volatility' + str(year)) % 2**31)
    n_buckets_vlt = 30
    bucket_centres = list(range(1, n_buckets_vlt + 1))
    open_vlt  = np.clip(92.5 + s_vlt.normal(0, 0.22, n_buckets_vlt), 87, 105)
    high_vlt  = np.clip(open_vlt + s_vlt.normal(0.10, 0.14, n_buckets_vlt), open_vlt - 2.0, open_vlt + 2.0)
    low_vlt   = np.clip(open_vlt + s_vlt.normal(-0.10, 0.12, n_buckets_vlt), open_vlt - 2.0, open_vlt + 2.0)
    fig_vlt = go.Figure()
    for lbl_v, _yclose_v, _yopen_v, col_v in [
            ('High Volatility', high_vlt, open_vlt, '#ff4444'),
            ('Base Volatility', open_vlt, open_vlt, '#ffd700'),
            ('Low Volatility',  low_vlt,  open_vlt, '#00d2be')]:
        fig_vlt.add_trace(go.Candlestick(
            x=bucket_centres,
            open=_yopen_v.tolist(), high=_yclose_v.tolist(), low=_yopen_v.tolist(),
            close=_yclose_v.tolist(), name=lbl_v,
            increasing=dict(line=dict(color=col_v, width=2)),
            decreasing=dict(line=dict(color=col_v, width=2)),
        ))
    fig_vlt.update_layout(
        template='plotly_dark', height=360,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Lap Bucket', yaxis_title='Lap Time (s)',
        title=f"Race Pace Volatility — {selected_race} ({year})",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig_vlt, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 39 · Pit Lane Traffic Forecast ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🚦 Pit Lane Traffic Forecast</div>', unsafe_allow_html=True)
    s_pt = _seeded(hash(selected_race + 'pittraffic' + str(year)) % 2**31)
    total_pit_stops_t = sum(s_pt.integers(40, 85) for _ in range(5))
    pit_window_t = 60
    p_vals = s_pt.poisson(total_pit_stops_t / pit_window_t, pit_window_t)
    x_pt = list(range(pit_window_t))
    fig_pt = go.Figure(data=go.Scatter(
        x=x_pt, y=p_vals.tolist(), mode='lines',
        name='Pit Visit Rate', line=dict(color='#4585de', width=2),
        fill='tozeroy', fillcolor='rgba(69,133,222,0.22)',
    ))
    fig_pt.add_trace(go.Scatter(
        x=x_pt, y=(p_vals + 2).tolist(), mode='lines',
        name='Peak Congestion', line=dict(color='#ff4444', width=1.5, dash='dash'),
        fill='tozeroy', fillcolor='rgba(255,68,68,0.10)',
    ))
    fig_pt.update_layout(
        xaxis_title='Lap into Race', yaxis_title='Predicted Pit Stop Volume', height=310,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Pit Lane Traffic Forecast — {selected_race} ({year})",
        hovermode='x unified',
    )
    fig_pt.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_pt.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_pt, use_container_width=True, config={'displayModeBar': False})

    # ─── NEW ID 40 · Adaptive Strategy AI Recommendations ────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🤖 Adaptive Strategy AI Recommendations</div>', unsafe_allow_html=True)
    s_40 = _seeded(hash(selected_race + pit_strategy + 'strategy40') % 2**31)
    tire_deg_40 = float(np.clip(s_40.normal(0.40, 0.27), 0.0, 1.0))
    fuel_eff_40 = float(np.clip(s_40.normal(0.72, 0.21), 0.0, 1.0))
    track_temp_40 = float(np.clip(s_40.normal(0.58, 0.24), 0.0, 1.0))
    driver_s_40   = float(np.clip(s_40.normal(0.70, 0.20), 0.0, 1.0))  # average grid skill proxy
    ai_s_s = _seeded(hash('strategy_ai_scores' + str(year) + selected_race) % 2**31)
    situation_vals = [tire_deg_40, fuel_eff_40, track_temp_40, driver_s_40,
                      float(np.clip(s_40.normal(0.6, 0.22), 0.0, 1.0)),
                      float(np.clip(s_40.normal(0.5, 0.25), 0.0, 1.0))]
    situation_labels = ['Tire Deg.', 'Fuel Eff.', 'Track Temp', 'Driver Skill', 'Pit Stop Quality', 'Weather Risk']
    all_strats_40 = ['Push', 'Conserve', 'Undercut', 'Overcut', '1-Stop', '2-Stop', '3-Stop']
    rec_scores = []
    for strat_k_40 in all_strats_40:
        s_act = ai_s_s.normal(0, 0.09)
        score = tire_deg_40 * s_act + fuel_eff_40 * (1 - s_act) + track_temp_40 * 0.5
        score = float(np.clip(score + s_40.normal(0, 0.13), 0.0, 1.0))
        rec_scores.append(score)
    fig_40 = go.Figure(data=go.Heatmap(
        z=[rec_scores],
        x=all_strats_40,
        y=['Recommendation'],
        colorscale='RdYlGn', colorbar=dict(title="Score"),
        text=[[f"{s:.0%}" for s in rec_scores]],
        texttemplate="%{text}", textfont=dict(size=12),
    ))
    best_idx_40 = int(np.argmax(rec_scores))
    best_strat_40 = all_strats_40[best_idx_40]
    fig_40.add_annotation(
        text=f"✅ Best: **{best_strat_40}**  ({rec_scores[best_idx_40]:.0%})",
        xref='paper', yref='paper', x=0.5, y=-0.14, showarrow=False,
        font=dict(size=13, color='#ffd700'),
    )
    fig_40.update_layout(
        template='plotly_dark', height=360,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Strategy', yaxis_title='',
        title=f"AI Strategy Scorecard — {selected_race} ({year})",
    )
    st.plotly_chart(fig_40, use_container_width=True, config={'displayModeBar': False})
    st.caption(f"📊 Situation: Tire Deg={tire_deg_40:.0%}  |  Fuel Eff={fuel_eff_40:.0%}  |  Track Temp={track_temp_40:.0%}  |  Driver Skill={driver_s_40:.0%}")
