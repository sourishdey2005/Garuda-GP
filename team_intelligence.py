import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.insert(0, '.')
from data_model import (
    get_seasons_data, get_team_cumulative,
    DRIVER_COLORS, TEAM_COLORS, _seeded,
    get_championship_standings,
)
from data_model import get_championship_standings as _standings

ALL_TEAMS = [
    'Red Bull Racing', 'Mercedes', 'Ferrari', 'McLaren',
    'Aston Martin', 'Haas', 'Alpine', 'Williams',
    'RB', 'Sauber', 'AlphaTauri', 'Racing Point',
    'Alfa Romeo', 'Toro Rosso',
]

def _i(rng, lo, hi):         # single int
    return int(rng.integers(lo, hi))

def _f(rng, lo, hi):         # single float
    return float(rng.uniform(lo, hi))

def _n(rng, loc=0, scale=1): # single float normal
    return float(rng.normal(loc, scale))

def render():
    st.markdown('<div class="section-header">🏁 Team Intelligence</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        year = st.selectbox(
            "Season", list(reversed(range(2000, 2027))),
            key="team_year", index=25,
        )
    with col2:
        selected_team = st.selectbox("Select Team", ALL_TEAMS, key="team_select")

    data   = get_seasons_data()
    full_std = get_championship_standings(year)
    races  = data[year]['races']
    s_team = _seeded(hash(selected_team + str(year)) % 2**31)

    team_drivers = [r['driver'] for r in full_std
                    if DRIVER_TO_TEAM_LOOKUP(r['driver']) == selected_team]
    chmp_pts  = sum(r['points'] for r in full_std
                    if DRIVER_TO_TEAM_LOOKUP(r['driver']) == selected_team)
    wins      = _i(s_team, 0, 14)
    podiums   = int(wins * 2.3 + _i(s_team, 1, 12))
    quali     = round(_n(s_team, 93.0, 1.1), 2)
    constr_p  = _i(s_team, 0, 21) + 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Championship Pts", str(chmp_pts), delta=str(year))
    with col2:
        st.metric("Wins", str(wins), delta="+%d podiums" % (wins * 2))
    with col3:
        st.metric("Avg Quali Pace", "%.2fs" % quali, delta="p%d" % _i(s_team, 1, 10))
    with col4:
        st.metric("Constructor Rank", "#%d" % constr_p, delta="🏁")

    st.markdown("---")

    # ── Driver comparison ──
    st.markdown('<div class="section-header">👥 Driver Comparison</div>', unsafe_allow_html=True)

    if team_drivers:
        d1, d2 = team_drivers[0], team_drivers[1] if len(team_drivers) > 1 else team_drivers[0]
        drv_rng_a = _seeded(hash(d1 + str(year)) % 2**31)
        drv_rng_b = _seeded(hash(d2 + str(year)) % 2**31)
        cmp_df = pd.DataFrame({
            'Metric': ['Qualifying Avg', 'Race Avg', 'Consistency', 'Best Lap',
                       'Quali Wins', 'Race Wins', 'Podiums', 'Champ Points'],
            d1: [
                "%.3fs" % _n(drv_rng_a, 93, 1),
                "%.3fs" % _n(drv_rng_a, 93.5, 1),
                "%.1f%%" % _f(drv_rng_a, 84, 99),
                "%.3fs" % _n(drv_rng_a, 91, 1),
                str(_i(drv_rng_a, 0, 8)),
                str(_i(drv_rng_a, 0, 6)),
                str(_i(drv_rng_a, 0, 14)),
                str(next((r['points'] for r in full_std if r['driver'] == d1), 0)),
            ],
            d2: [
                "%.3fs" % _n(drv_rng_b, 93, 1),
                "%.3fs" % _n(drv_rng_b, 93.5, 1),
                "%.1f%%" % _f(drv_rng_b, 84, 99),
                "%.3fs" % _n(drv_rng_b, 91, 1),
                str(_i(drv_rng_b, 0, 8)),
                str(_i(drv_rng_b, 0, 6)),
                str(_i(drv_rng_b, 0, 14)),
                str(next((r['points'] for r in full_std if r['driver'] == d2), 0)),
            ],
        })
        st.dataframe(cmp_df, hide_index=True)
    else:
        st.info("No drivers found for this team in the selected season.")

    st.markdown("---")

    # ── Performance scatter ──
    st.markdown('<div class="section-header">📊 Performance Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("**Straight-Line Speed vs Cornering Speed**")
        fig = go.Figure()
        for t in ALL_TEAMS[:8]:
            tr = _seeded(hash(t + str(year)) % 2**31)
            x  = float(_n(tr, 330, 8))
            y  = float(_n(tr, 185, 7))
            is_sel = t == selected_team
            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode='markers+text',
                text=[t], textposition='top center',
                marker=dict(size=18 if is_sel else 12,
                            color=TEAM_COLORS.get(t, '#888'), opacity=1.0 if is_sel else 0.7),
                name=t,
            ))
        fig.update_layout(
            xaxis_title='Straight-Line Speed (km/h)',
            yaxis_title='Corner Speed (km/h)',
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, config={'displayModeBar': False})

    st.markdown("---")

    # ── Season performance trend ──
    st.markdown('<div class="section-header">📊 Season Pace Trend</div>', unsafe_allow_html=True)
    team_race_results = []
    for r_nm in races:
        res = data[year]['seasons'].get(r_nm, [])
        team_res = [e for e in res if DRIVER_TO_TEAM_LOOKUP(e['driver']) == selected_team]
        if team_res:
            team_race_results.append({
                'race': r_nm,
                'position': team_res[0]['position'],
                'best_lap': team_res[0]['best_lap'],
                'points':   team_res[0]['points'],
            })
    if team_race_results:
        rng_t = _seeded(hash(selected_team + str(year)) % 2**31)
        lap_trend = [tr['best_lap'] + _n(rng_t, 0, .35)
                     for tr in team_race_results]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1, len(lap_trend) + 1)), y=lap_trend,
            mode='lines+markers', name='Best Lap/Race',
            line=dict(color='#ffd700', width=2), marker=dict(size=8),
            fill='tozeroy', fillcolor='rgba(255,215,0,0.08)',
        ))
        fig.update_layout(
            title='Lap Pace Trend',
            xaxis_title='Race #', yaxis_title='Lap Time (s)',
            template='plotly_dark', height=340,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, config={'displayModeBar': False})

    # ── Head-to-head vs competitor ──
    st.markdown("---")
    st.markdown('<div class="section-header">⚔️ Head-to-Head vs Competitors</div>', unsafe_allow_html=True)
    competitors = [t for t in ALL_TEAMS if t != selected_team][:6]
    h2h_rows = []
    for comp in competitors:
        s_c = _seeded(hash(comp + str(year)) % 2**31)
        h2h_rows.append({
            'Competitor':     comp,
            'Quali Advantage': (f"+{_f(s_c, 0.10, 0.65):.2f}s" if s_c.random() > .5
                               else f"-{_f(s_c, 0.10, 0.65):.2f}s"),
            'Race Pace Avg':  (f"+{_f(s_c, 0.05, 0.40):.2f}s" if s_c.random() > .5
                               else f"-{_f(s_c, 0.05, 0.40):.2f}s"),
            'Wins vs Comp':   _i(s_c, 0, 9),
            'Podiums vs Comp':_i(s_c, 0, 15),
        })
    st.dataframe(pd.DataFrame(h2h_rows), hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🧪 Engineering Notes</div>', unsafe_allow_html=True)
    col_e1, col_e2, col_e3 = st.columns(3)
    s_note = _seeded(hash(selected_team + str(year) + 'notes') % 2**31)
    level = s_note.choice(['Low','Low','Medium','Medium','High'])
    sets  = ['High-speed circuits','Technical tracks','Mixed circuits']
    notes = [
        "Downforce: %s on %s" % (['Low','Medium','High'][_i(s_note, 0, 3)],
                                  s_note.choice(sets)),
        "Engine mode: %s" % s_note.choice(['Qualifying','Race','Power Saving']),
        "Rear-wing update: %.2fs/lap improvement" % _f(s_note, 0.1, 0.5),
    ]
    col_e1.markdown("### Suspension / Aero\n- " + "\n- ".join(notes[:2]))
    col_e2.markdown("### Power Unit\n- " + notes[2])
    col_e3.markdown("### Strategy\n- Pit strategy data available post-session")


    # ── NEW: Tyre Strategy Distribution ──
    st.markdown('<div class="section-header">🛞 Tyre Strategy Distribution</div>', unsafe_allow_html=True)
    col_ty1, col_ty2 = st.columns([1, 1])
    
    with col_ty1:
        st.markdown("**Tyre Compound Usage**")
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Soft', 'Medium', 'Hard', 'Intermediate', 'Wet'],
            values=[_i(s_team, 20, 40), _i(s_team, 25, 35), _i(s_team, 15, 30), 
                    _i(s_team, 0, 10), _i(s_team, 0, 5)],
            hole=.3,
            marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7']
        )])
        fig_pie.update_layout(
            template='plotly_dark',
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=True
        )
        st.plotly_chart(fig_pie)

    with col_ty2:
        st.markdown("**Pit Stop Duration Distribution**")
        # Generate pit stop time data
        pit_times = [_n(s_team, 2.5, 0.3) for _ in range(50)]  # 50 pit stops
        fig_hist = go.Figure(data=[go.Histogram(
            x=pit_times,
            nbinsx=15,
            marker_color='#ffd700'
        )])
        fig_hist.update_layout(
            title="Pit Stop Time Distribution (seconds)",
            template='plotly_dark',
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title="Pit Stop Time (s)",
            yaxis_title="Frequency"
        )
        st.plotly_chart(fig_hist)

    # ── NEW: Performance Consistency Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Performance Consistency Analysis</div>', unsafe_allow_html=True)
    col_con1, col_con2 = st.columns([1, 1])
    
    with col_con1:
        st.markdown("**Lap Time Variability (Box Plot)**")
        # Generate lap time data for different runs
        lap_data = []
        for run in range(5):  # 5 different practice/qualifying sessions
            base_time = _n(s_team, 92.5, 0.5)
            lap_times = [_n(s_team, base_time, 0.8) for _ in range(20)]  # 20 laps per session
            lap_data.append(lap_times)
        
        fig_box = go.Figure()
        for i, run_data in enumerate(lap_data):
            fig_box.add_trace(go.Box(
                y=run_data,
                name=f'Session {i+1}',
                marker_color=px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)]
            ))
        fig_box.update_layout(
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            yaxis_title="Lap Time (s)"
        )
        st.plotly_chart(fig_box)
    
    with col_con2:
        st.markdown("**Performance Consistency Heatmap**")
        # Create a heatmap showing performance across different metrics
        metrics = ['Qualifying', 'Race Pace', 'Consistency', 'Tyre Mgmt', 'Quali Wins', 'Race Wins']
        races_sample = races[:8] if len(races) >= 8 else races
        if not races_sample:
            races_sample = ['Race 1', 'Race 2', 'Race 3', 'Race 4', 'Race 5', 'Race 6', 'Race 7', 'Race 8']
        
        # Generate performance data
        z_data = []
        for metric in metrics:
            row = [_n(s_team, 70, 20) for _ in races_sample]  # Performance scores
            z_data.append(row)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=z_data,
            x=races_sample,
            y=metrics,
            colorscale='Viridis',
            colorbar=dict(title="Performance Score")
        ))
        fig_heatmap.update_layout(
            title='Performance Across Races and Metrics',
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)'
        )
        st.plotly_chart(fig_heatmap)

    # ── NEW: Championship Probability Evolution ──
    st.markdown("---")
    st.markdown('<div class="section-header">📈 Championship Probability Evolution</div>', unsafe_allow_html=True)
    col_prob1, col_prob2 = st.columns([1, 1])
    
    with col_prob1:
        st.markdown("**Season Points Progression (Area Chart)**")
        # Points accumulation through the season
        points_evolution = []
        cumulative = 0
        for race_idx, race_name in enumerate(races[:12]):  # First 12 races
            points_race = _i(s_team, 0, 25)
            cumulative += points_race
            points_evolution.append(cumulative)
        
        fig_area = go.Figure()
        fig_area.add_trace(go.Scatter(
            x=list(range(1, len(points_evolution) + 1)),
            y=points_evolution,
            fill='tozeroy',
            fillcolor='rgba(255,215,0,0.3)',
            line=dict(color='#ffd700', width=3),
            name='Cumulative Points'
        ))
        fig_area.update_layout(
            template='plotly_dark',
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Race Number',
            yaxis_title='Cumulative Points'
        )
        st.plotly_chart(fig_area)
    
    with col_prob2:
        st.markdown("**Championship Probability vs Competitors**")
        # Probability of finishing in different positions
        positions = ['1st', '2nd', '3rd', '4th-5th', '6th-10th', '11th-15th', '16th+']
        probabilities = [_n(s_team, 30, 15) for _ in positions]
        # Normalize to make somewhat realistic
        total = sum(probabilities)
        if total > 0:
            probabilities = [p/total*100 for p in probabilities]
        
        fig_prob = go.Figure(data=[go.Bar(
            x=positions,
            y=probabilities,
            marker_color=['#ffd700', '#c0c0c0', '#cd7f32', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        )])
        fig_prob.update_layout(
            title='Championship Probability Distribution',
            template='plotly_dark',
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            yaxis_title='Probability (%)',
            yaxis=dict(range=[0, 50])
        )
        st.plotly_chart(fig_prob)

    # ── NEW: Engineering Risk/Reward Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">⚖️ Engineering Risk/Reward Analysis</div>', unsafe_allow_html=True)
    col_risk1, col_risk2 = st.columns([1, 1])
    
    with col_risk1:
        st.markdown("**Upgrade Impact Analysis (Waterfall Chart)**")
        # Show how different upgrades contribute to performance
        upgrades = ['Baseline', 'Aero Package', 'Engine Update', 'Suspension', 'Tyre Allocation', 'Strategy']
        # Start with baseline performance
        baseline = 75
        impacts = [baseline, 
                  baseline + _n(s_team, 3, 2),   # Aero Package
                  baseline + _n(s_team, 5, 2) + _n(s_team, 2, 1),   # Engine Update
                  baseline + _n(s_team, 4, 2) + _n(s_team, 3, 1),   # Suspension
                  baseline + _n(s_team, 2, 1) + _n(s_team, 1, 1),   # Tyre Allocation
                  baseline + _n(s_team, 4, 2) + _n(s_team, 2, 1)]   # Strategy
        
        fig_waterfall = go.Figure(go.Waterfall(
            name = "Performance Impact", 
            orientation = "v",
            measure = ["absolute"] + ["relative"]*4 + ["total"],
            x = upgrades,
            textposition = "outside",
            text = [f"{v:.1f}" for v in impacts],
            y = impacts,
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        fig_waterfall.update_layout(
            title = "Performance Impact of Upgrades",
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)'
        )
        st.plotly_chart(fig_waterfall)
    
    with col_risk2:
        st.markdown("**Risk/Reward Scatter Plot**")
        # Different strategies with risk vs reward
        strategies = ['Conservative', 'Balanced', 'Aggressive', 'High Risk', 'All-In']
        risk_levels = [_n(s_team, 20, 8) for _ in strategies]  # Lower is less risk
        reward_levels = [_n(s_team, 60, 15) for _ in strategies]  # Higher is more reward
        
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=risk_levels,
            y=reward_levels,
            mode='markers+text',
            text=strategies,
            textposition="top center",
            marker=dict(
                size=12,
                color=['#00ff00', '#90ee90', '#ffd700', '#ff6b6b', '#ff0000'],
                opacity=0.8
            )
        ))
        fig_scatter.update_layout(
            title='Strategy Risk vs Reward Analysis',
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Risk Level (Lower = Less Risk)',
            yaxis_title='Reward Potential (Higher = More Reward)'
        )
        fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_scatter)

    # ── NEW: Resource Allocation Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Resource Allocation Analysis</div>', unsafe_allow_html=True)
    col_res1, col_res2 = st.columns([1, 1])
    
    with col_res1:
        st.markdown("**Budget Distribution (Treemap)**")
        # Show how budget is allocated across different areas
        fig_treemap = go.Figure(go.Treemap(
            labels=['Aerodynamics', 'Power Unit', 'Chassis', 'Electronics', 'Personnel', 'Facilities', 'Logistics'],
            parents=['', '', '', '', '', '', ''],
            values=[_i(s_team, 15, 30), _i(s_team, 20, 35), _i(s_team, 10, 20), 
                    _i(s_team, 8, 15), _i(s_team, 25, 40), _i(s_team, 5, 15), 
                    _i(s_team, 3, 10)],
            branchvalues="total",
        ))
        fig_treemap.update_layout(
            title="Team Budget Allocation",
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)'
        )
        st.plotly_chart(fig_treemap)
    
    with col_res2:
        st.markdown("**Development Timeline (Gantt Chart)**")
        # Show development timeline for upgrades
        fig_gantt = go.Figure()
        tasks = ['Wind Tunnel Testing', 'CFD Simulations', 'Part Production', 'Track Testing', 'Race Deployment']
        start_dates = [1, 15, 30, 45, 60]  # Days from season start
        durations = [10, 20, 15, 12, 5]   # Duration in days
        
        fig_gantt.add_trace(go.Bar(
            x=durations,
            y=tasks,
            base=start_dates,
            orientation='h',
            marker_color='rgba(255,215,0,0.7)'
        ))
        fig_gantt.update_layout(
            title="Upgrade Development Timeline",
            template='plotly_dark',
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Days from Season Start',
            yaxis_title='Development Task',
            barmode='overlay'
        )
        st.plotly_chart(fig_gantt)

    # ═══════════════════════════════════════════════════
    #  NEW VISUALISATIONS  IDs 11-20  (team_intelligence.py)
    # ═══════════════════════════════════════════════════

    # ─── NEW ID 11 · Aerodynamic Efficiency Matrix ────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌬️ Aerodynamic Efficiency Matrix</div>', unsafe_allow_html=True)
    s_aero = _seeded(hash(selected_team + str(year) + 'aero_eff') % 2**31)
    comp_teams = [t for t in ALL_TEAMS if t != selected_team][:6]
    teams_mat   = [selected_team] + comp_teams
    circs_mat   = ['Bahrain','Monaco','Silverstone','Spa','Monza','Singapore','Austin']
    z_data_aero = []
    for t in teams_mat:
        ts = _seeded(hash(t + str(year) + 'aero') % 2**31)
        row = [float(np.clip(ts.normal(72, 12), 40, 98)) for _ in circs_mat]
        z_data_aero.append(row)
    fig_aero = go.Figure(data=go.Heatmap(
        z=z_data_aero, x=circs_mat, y=teams_mat,
        colorscale='RdYlGn', colorbar=dict(title="Aero Eff."),
    ))
    fig_aero.update_layout(
        title=f"Aero Efficiency — {selected_team} vs Rivals ({year})",
        template='plotly_dark', height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
    )
    st.plotly_chart(fig_aero, config={'displayModeBar': False})

    # ─── NEW ID 12 · 3D Wind Tunnel Simulation ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌪️ 3D Wind Tunnel Simulation</div>', unsafe_allow_html=True)
    s_wt = _seeded(hash(selected_team + str(year) + 'wind_tunnel') % 2**31)
    NS_WT = 50
    XV_WT = np.linspace(0.0, 3.0, NS_WT)
    YV_WT = np.linspace(0.0, 1.5, NS_WT)
    XW, YW = np.meshgrid(XV_WT, YV_WT)
    ZW = 1.20 + 0.55 * np.exp(-((XW - s_wt.uniform(0.4, 1.2)) ** 2 / 0.42 + (YW - s_wt.uniform(0.25, 0.85)) ** 2 / 0.18))
    ZW = np.clip(ZW + s_wt.normal(0, 0.04, XW.shape), 0.0, 2.4)
    fig_wt = go.Figure(data=go.Surface(
        x=XW, y=YW, z=ZW, colorscale='YlOrRd', opacity=0.93,
        showscale=True, colorbar=dict(title="Pressure Coeff."),
    ))
    fig_wt.update_layout(
        template='plotly_dark', height=520,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Wind Tunnel Pressure Field — {selected_team} ({year})",
        scene=dict(xaxis_title='Chord X', yaxis_title='Span Y', zaxis_title='Cp',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_wt, config={'displayModeBar': False})

    # ─── NEW ID 13 · Team Synergy Correlation ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🤝 Team Synergy Correlation</div>', unsafe_allow_html=True)
    s_syn = _seeded(hash(selected_team + str(year) + 'synergy') % 2**31)
    if team_drivers and len(team_drivers) >= 2:
        dA, dB = team_drivers[0], team_drivers[1] if len(team_drivers) > 1 else team_drivers[0]
        n_syn   = 380
        qA      = np.clip(s_syn.normal(93.0, 1.2, n_syn), 89, 101)
        rA      = np.clip(s_syn.normal(93.8, 1.5, n_syn), 89, 104)
        qB      = np.clip(s_syn.normal(92.8, 1.3, n_syn), 89, 101)
        rB      = np.clip(s_syn.normal(93.5, 1.5, n_syn), 89, 104)
        meta_df = pd.DataFrame({
            f'Quali — {dA}': qA, f'Race — {dA}': rA,
            f'Quali — {dB}': qB, f'Race — {dB}': rB,
            'Avg Gap (s)': np.abs(qA - qB) + np.abs(rA - rB) * 0.5,
        })
        corr_m = meta_df.corr()
        fig_syn = go.Figure(data=go.Heatmap(
            z=corr_m.values, x=corr_m.columns, y=corr_m.index,
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation"),
            text=[[f"{v:.2f}" for v in row] for row in corr_m.values],
            texttemplate="%{text}", textfont=dict(size=10),
        ))
        fig_syn.update_layout(
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Driver Correlation Matrix — {selected_team} ({year})",
        )
        st.plotly_chart(fig_syn, config={'displayModeBar': False})
        top_pair = corr_m.columns[np.argsort(-corr_m.values.flatten())[1]]
        st.caption(f"🔗 Strongest pair: **{top_pair}**  |  Target: > 0.75 synergy flags pit-stop & strategy optimisation.")
    else:
        st.info("Need at least 2 drivers in team for synergy analysis.")

    # ─── NEW ID 14 · Fuel Efficiency Timeline ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⛽ Fuel Efficiency Timeline</div>', unsafe_allow_html=True)
    s_fuel = _seeded(hash(selected_team + str(year) + 'fuel_eff') % 2**31)
    rs_f   = races[:min(12, len(races))]
    fuel_data = []
    base_fuel_eff = s_fuel.uniform(2.5, 3.2)
    for ri4, rn4 in enumerate(rs_f):
        dev_f = s_fuel.normal(0, 0.28)
        eff_f = base_fuel_eff + dev_f + (ri4 / max(len(rs_f), 1)) * s_fuel.uniform(-0.22, 0.45)
        fuel_data.append({'Race': rn4, 'Fuel Eff. (kg/km)': eff_f })
    df_fuel = pd.DataFrame(fuel_data)
    fig_fuel = go.Figure()
    fig_fuel.add_trace(go.Scatter(
        x=df_fuel['Race'].tolist(), y=df_fuel['Fuel Eff. (kg/km)'].tolist(),
        mode='lines+markers', name=selected_team,
        line=dict(color='#ffd700', width=2.5), marker=dict(size=7),
        fill='tozeroy', fillcolor='rgba(255,215,0,0.12)',
    ))
    avg_fe = float(df_fuel['Fuel Eff. (kg/km)'].mean())
    fig_fuel.add_hline(y=avg_fe, line_dash='dash', line_color='white', opacity=0.6,
                        annotation_text=f"Season Avg: {avg_fe:.2f} kg/km", annotation_position='top right')
    fig_fuel.update_layout(
        xaxis_title='Race', yaxis_title='Fuel Efficiency (kg/km)',  height=340,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        title=f"Fuel Efficiency — {selected_team} ({year})",
    )
    fig_fuel.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)', tickangle=-45)
    fig_fuel.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_fuel, config={'displayModeBar': False})

    # ─── NEW ID 15 · Pit Crew Performance Radar ──────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🔧 Pit Crew Performance Radar</div>', unsafe_allow_html=True)
    s_pit = _seeded(hash(selected_team + str(year) + 'pit_crew') % 2**31)
    pit_labels = ['Front Jack', 'Rear Jack', 'Gun Oper.',
                  'Refuelling', 'Wheel Change', 'Car Release']
    total_crew = min(len(pit_labels), 6)
    drA2 = _seeded(hash((team_drivers[0] if team_drivers else 'dummy') + str(year)) % 2**31)
    drB2 = _seeded(hash((team_drivers[1] if len(team_drivers) > 1 else 'dummy') + str(year)) % 2**31)
    fig_pit = go.Figure()
    fig_pit.add_trace(go.Scatterpolar(
        r=[float(np.clip(s_pit.normal(82, 13), 40, 100)) for _ in pit_labels],
        theta=pit_labels, fill='toself', name='Crew Avg.', line=dict(color='#ffd700'),
        fillcolor='rgba(255,215,0,0.28)',
    ))
    if team_drivers:
        fig_pit.add_trace(go.Scatterpolar(
            r=[float(np.clip(drA2.normal(85, 11), 40, 100)) for _ in pit_labels],
            theta=pit_labels, fill='toself', name=f"Crew — {team_drivers[0]}",
            line=dict(color='#1f77b4'), fillcolor='rgba(31,119,180,0.22)',
        ))
        if len(team_drivers) > 1:
            fig_pit.add_trace(go.Scatterpolar(
                r=[float(np.clip(drB2.normal(83, 13), 40, 100)) for _ in pit_labels],
                theta=pit_labels, fill='toself', name=f"Crew — {team_drivers[1]}",
                line=dict(color='#00d2be'), fillcolor='rgba(0,210,190,0.18)',
            ))
    fig_pit.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], gridcolor='rgba(255,215,0,0.2)'),
                   angularaxis=dict(gridcolor='rgba(255,215,0,0.2)')),
        template='plotly_dark', height=400,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h'),
    )
    st.plotly_chart(fig_pit, config={'displayModeBar': False})

    # ─── NEW ID 16 · Upgrade ROI Analysis ───────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">💰 Upgrade ROI Analysis</div>', unsafe_allow_html=True)
    s_roi = _seeded(hash(selected_team + str(year) + 'roi') % 2**31)
    upg_labels_roi = ['Baseline', 'New Front Wing', 'Sidepod Update',
                      'Rear Suspension', 'Floor Update', 'Power Unit Map',
                      'Latest Spec']
    base_r = 72.0
    roi_vals = [base_r]
    imp_vals = []
    for ui6 in range(len(upg_labels_roi) - 1):
        imp = float(s_roi.normal(2.1, 1.5))
        roi_vals.append(float(np.clip(roi_vals[-1] + imp, 40, 105)))
        imp_vals.append(imp)
    imp_vals.append(0.0)
    fig_roi = go.Figure(go.Waterfall(
        name="Perf.", orientation="v",
        measure=["absolute"] + ["relative"] * (len(upg_labels_roi) - 2) + ["total"],
        x=upg_labels_roi,
        text=[f"{v:.1f}" for v in roi_vals],
        textposition="outside",
        y=roi_vals,
        connector={"line": {"color": "rgb(63,63,63)"}},
        increasing=dict(marker=dict(color='rgba(78,205,196,0.85)')),
        decreasing=dict(marker=dict(color='rgba(255,107,107,0.85)')),
    ))
    fig_roi.update_layout(
        title=f"Upgrade ROI — {selected_team} Season {year}",
        template='plotly_dark', height=360,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        yaxis_title="Performance Index",
    )
    fig_roi.update_xaxes(showgrid=False)
    fig_roi.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_roi, config={'displayModeBar': False})

    # ─── NEW ID 17 · 3D Aero Balance Analyzer ───────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">✈️ 3D Aero Balance Analyzer</div>', unsafe_allow_html=True)
    s_ab = _seeded(hash(selected_team + str(year) + 'aero_bal') % 2**31)
    N_AB = 60
    sv_arr  = np.linspace(170, 330, N_AB)
    df_arr  = np.linspace(0.8, 1.6, N_AB)
    xrv, yrv = np.meshgrid(sv_arr, df_arr)
    zrv_bal = 50.0 + 26.0 * np.sin(xrv / 55) + 14.0 * np.sin(yrv * 1.6) + s_ab.normal(0, 2.8, xrv.shape)
    zrv_bal = np.clip(zrv_bal, 0.0, 100.0)
    fig_ab = go.Figure(data=go.Surface(
        x=xrv, y=yrv, z=zrv_bal,
        colorscale='Jet', opacity=0.92, showscale=True,
        colorbar=dict(title="Downforce (kg)"),
    ))
    fig_ab.update_layout(
        title=f"Aero Balance — {selected_team} ({year})",
        template='plotly_dark', height=520,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        scene=dict(xaxis_title='Corner Speed (km/h)', yaxis_title='DF Level', zaxis_title='Balance %',
                    bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_ab, config={'displayModeBar': False})

    # ─── NEW ID 18 · Component Reliability Forecast ──────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🔩 Component Reliability Forecast</div>', unsafe_allow_html=True)
    s_rf = _seeded(hash(selected_team + str(year) + 'reliabil') % 2**31)
    N_RF = 240
    step_days = np.arange(0, N_RF)
    base_rf = 98.5
    cur_rf  = np.zeros(N_RF)
    cur_rf[0] = base_rf
    for i8 in range(1, N_RF):
        if s_rf.random() < 0.04:
            cur_rf[i8] = float(np.clip(cur_rf[i8 - 1] - s_rf.uniform(1.5, 12.0), 70.0, 99.8))
        else:
            recovery   = s_rf.uniform(0.1, 0.7)
            cur_rf[i8] = float(np.clip(cur_rf[i8 - 1] + recovery, base_rf, 99.8 if s_rf.random() > 0.05 else 99.8))
    lb_rf = np.clip(cur_rf - s_rf.uniform(0.6, 2.2, N_RF), 0, 100)
    ub_rf = np.clip(cur_rf + s_rf.uniform(0.6, 2.2, N_RF), 0, 100)
    fig_rf = go.Figure()
    fig_rf.add_trace(go.Scatter(
        x=step_days.tolist(), y=ub_rf.tolist(), mode='lines',
        line=dict(width=0), showlegend=False, hoverinfo='skip',
    ))
    fig_rf.add_trace(go.Scatter(
        x=step_days.tolist(), y=lb_rf.tolist(), mode='lines',
        name='±1σ', line=dict(width=0), fill='tonexty',
        fillcolor='rgba(255,107,107,0.18)', hoverinfo='skip',
    ))
    fig_rf.add_trace(go.Scatter(
        x=step_days.tolist(), y=cur_rf.tolist(), mode='lines',
        name='Mean Reliability', line=dict(color='#ffd700', width=2.5),
    ))
    fig_rf.update_layout(
        xaxis_title='Days into Season', yaxis_title='Reliability (%)', height=340,
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified',
        title=f"Reliability Forecast — {selected_team} (Season {year})",
    )
    fig_rf.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_rf.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_rf, config={'displayModeBar': False})

    # ─── NEW ID 19 · Team Communication Efficiency ──────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📻 Team Communication Efficiency</div>', unsafe_allow_html=True)
    s_com = _seeded(hash(selected_team + str(year) + 'comm') % 2**31)

    # Bar chart — reliability signal per channel
    comm_channels = ['Race Engineering', 'Driver ↔ Engineer', 'Strategy',
                     'Data Analytics', 'Radio Channel', 'Pit Wall']
    comm_latency   = [float(np.clip(s_com.normal(0.72, 0.21), 0.0, 1.0)) for _ in comm_channels]
    comm_bandwidth = [float(np.clip(s_com.normal(0.78, 0.16), 0.0, 1.0)) for _ in comm_channels]
    comm_efficiency = [0.5 * (la + bw) for la, bw in zip(comm_latency, comm_bandwidth)]
    comm_df = pd.DataFrame({
        'Channel':      comm_channels * 3,
        'Efficiency':   comm_latency + comm_bandwidth + comm_efficiency,
        'Metric':       (['Reliability Signal'] * len(comm_channels) +
                         ['Bandwidth'] * len(comm_channels) +
                         ['Composite'] * len(comm_channels)),
    })
    fig_com = go.Figure()
    for _, (metric, grp) in enumerate(comm_df.groupby('Metric')):
        m_color = {'Reliability Signal':'#ffd700', 'Bandwidth':'#1f77b4', 'Composite':'#ff4444'}[metric]
        fig_com.add_trace(go.Bar(
            name=metric, x=grp['Channel'], y=grp['Efficiency'],
            marker=dict(color=m_color, opacity=0.82 if metric != 'Composite' else 0.98,
                        line=dict(width=1.5, color='white') if metric == 'Composite' else None),
        ))
    fig_com.update_layout(
        barmode='group', template='plotly_dark', height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Channel', yaxis_title='Efficiency (normalised to 1)',
        title=f"Team Communication Efficiency — {selected_team} ({year})",
        legend=dict(x=0.01, y=0.98, xanchor='left', yanchor='top', bgcolor='rgba(0,0,0,0.4)'),
    )
    fig_com.update_xaxes(showgrid=False, tickangle=-30)
    fig_com.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)', range=[0, 1.1])
    st.plotly_chart(fig_com, config={'displayModeBar': False})

    # ─── NEW ID 20 · Strategy Decision Tree ─────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌳 Strategy Decision Tree</div>', unsafe_allow_html=True)
    s_dt  = _seeded(hash(selected_team + str(year) + 'strategy_tree') % 2**31)
    tire_wear = float(np.clip(s_dt.normal(0.4, 0.28), 0.0, 1.0))
    rain_prob = float(np.clip(s_dt.normal(0.15, 0.22), 0.0, 1.0))
    gap_st    = float(np.clip(s_dt.normal(8.5, 7.2), 0.0, 30.0))
    under_prob   = float(np.clip(s_dt.normal(0.60, 0.22) * (1.0 - tire_wear), 0.0, 1.0))
    overcut_prob = float(np.clip(s_dt.normal(0.38, 0.20) * tire_wear, 0.0, 1.0))
    push_prob    = float(np.clip(s_dt.normal(0.55, 0.25) * (gap_st / 30.0), 0.0, 1.0))
    cons_prob    = float(np.clip(s_dt.normal(0.72, 0.16) * (1.0 - gap_st / 30.0), 0.0, 1.0))
    wet_1s = float(np.clip(s_dt.normal(0.62, 0.28), 0.0, 1.0))
    wet_2s = float(np.clip(s_dt.normal(0.48, 0.30), 0.0, 1.0))
    wet_3s = float(np.clip(s_dt.normal(0.31, 0.26), 0.0, 1.0))
    inter_2s = float(np.clip(s_dt.normal(0.68, 0.22), 0.0, 1.0))
    inter_3s = float(np.clip(s_dt.normal(0.52, 0.26), 0.0, 1.0))
    wet_stint_opt = {float(wet_1s): "1-Stop", float(wet_2s): "2-Stop", float(wet_3s): "3-Stop"}
    inter_stint_opt = {float(inter_2s): "2-Stop", float(inter_3s): "3-Stop"}
    # Find best path
    def _node_label(prob, lbl):
        pstr = f"{prob:.0%}"
        return f"{lbl}<br><sub>P={pstr}</sub>"
    # Best strategy
    all_strats = {
        'Push': push_prob, 'Conserve': cons_prob,
        'Undercut': under_prob, 'Overcut': overcut_prob,
    }
    if tire_wear < 0.35:
        best1 = max(all_strats, key=all_strats.get)
        best2 = 'Dry Compounds'
    elif tire_wear < 0.70:
        best1 = max(['Undercut','Overcut'], key=lambda k: all_strats.get(k, 0))
        best2 = 'Medium & Hard'
    else:
        best1 = 'Push'
        best2 = 'Soft Where Possible'
    wet_strat_best = max(wet_stint_opt)
    inter_strat_best = max(inter_stint_opt)
    fig_dt_data = []
    fig_dt_data.append(dict(
        Node='Root<br><sub>Track Status</sub>', Parent='',
        Value=1.0, Color='rgba(255,215,0,0.85)',
    ))
    if rain_prob < 0.35:
        fig_dt_data.append(dict(
            Node=f"Dry Stint<br><sub>Tire Wear={tire_wear:.0%}</sub>", Parent='Root<br><sub>Track Status</sub>',
            Value=0.65, Color='rgba(78,205,196,0.85)',
        ))
        fig_dt_data.append(dict(
            Node=f"⚡ **{best1}**<br>({best2})", Parent=f"Dry Stint<br><sub>Tire Wear={tire_wear:.0%}</sub>",
            Value=float(all_strats.get(best1, push_prob)), Color='rgba(255,215,0,0.85)',
        ))
        best_dry_parent = f"Dry Stint<br><sub>Tire Wear={tire_wear:.0%}</sub>"
        for strat_k, strat_opt in [('Undercut', f"Undercut<br>Risk={under_prob:.0%}"), ('Overcut', f"Overcut<br>Reward={overcut_prob:.0%}")]:
            fig_dt_data.append(dict(
                Node=strat_opt, Parent=best_dry_parent,
                Value=float(all_strats.get(strat_k, 0.3)), Color='rgba(30,144,255,0.82)',
            ))
    else:
        fig_dt_data.append(dict(
            Node=f"Wet Stint<br><sub>Rain: {rain_prob:.0%}</sub>", Parent='Root<br><sub>Track Status</sub>',
            Value=0.65, Color='rgba(30,144,255,0.85)',
        ))
        w_path = wet_stint_opt.get(wet_strat_best, "1-Stop")
        fig_dt_data.append(dict(
            Node=f"Wet Strategy<br><sub>→ {w_path}</sub>", Parent=f"Wet Stint<br><sub>Rain: {rain_prob:.0%}</sub>",
            Value=wet_strat_best, Color='rgba(30,144,255,0.82)',
        ))
        i_path = wet_stint_opt.get(inter_strat_best, "Wet→Inter")
        fig_dt_data.append(dict(
            Node=f"→ Inter → Switch<br><sub>{inter_strat_best:.0%}</sub>", Parent=f"Wet Strategy<br><sub>→ {w_path}</sub>",
            Value=inter_strat_best, Color='rgba(78,205,196,0.82)',
        ))
    if gap_st > 12.0:
        fig_dt_data.append(dict(
            Node=f'Aggressive<br><sub>Gap={gap_st:.1f}s</sub>', Parent=fig_dt_data[-2]['Node'],
            Value=0.45, Color='rgba(255,107,107,0.82)',
        ))
    else:
        fig_dt_data.append(dict(
            Node=f'Conservative<br><sub>Gap={gap_st:.1f}s</sub>', Parent=fig_dt_data[-2]['Node'],
            Value=0.55, Color='rgba(78,205,196,0.82)',
        ))
    df_dt = pd.DataFrame(fig_dt_data)
    node_ids = {n: i for i, n in enumerate(df_dt['Node'].unique())}
    df_dt['source'] = df_dt['Parent'].map(node_ids)
    df_dt['target'] = df_dt['Node'].map(node_ids)
    df_dt = df_dt.dropna(subset=['source','target'])
    df_dt['source'] = df_dt['source'].astype(int)
    df_dt['target'] = df_dt['target'].astype(int)
    fig_dt = go.Figure(go.Sankey(
        node=dict(
            label=df_dt['Node'].tolist(),
            color=df_dt['Color'].tolist(),
            line=dict(width=0.2, color='rgba(255,255,255,0.25)'),
            pad=12,
        ),
        link=dict(
            source=df_dt['source'].tolist(),
            target=df_dt['target'].tolist(),
            value=df_dt['Value'].tolist(),
            color=df_dt['Color'].tolist(),
        ),
    ))
    fig_dt.update_layout(
        template='plotly_dark', height=480, font=dict(size=12),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        title=f"Strategy Decision Tree — {selected_team} ({year})",
    )
    st.plotly_chart(fig_dt, config={'displayModeBar': False})

    # ═══════════════════════════════════════════════════

# helper lookup — covers full 2000–2025 grid
_LOOKUP = {
    'Michael Schumacher':'Ferrari','Mika Hakkinen':'McLaren',
    'David Coulthard':'McLaren','Rubens Barrichello':'Ferrari',
    'Ralf Schumacher':'Williams','Giancarlo Fisichella':'Jordan',
    'Jenson Button':'Benetton','Kimi Raikkonen':'Sauber',
    'Eddie Irvine':'Jaguar','Mika Salo':'Ferrari',
    'Heinz-Harald Frentzen':'Jordan','Johnny Herbert':'Stewart',
    'Ricardo Zonta':'BAR','Pedro de la Rosa':'Arrows',
    'Marc Gene':'Minardi','Jarno Trulli':'Jordan',
    'Nick Heidfeld':'Prost','Gastón Mazzacane':'Minardi',
    'Tarso Marques':'Minardi','Alex Yoong':'Minardi',
    'Juan Pablo Montoya':'Williams','Jacques Villeneuve':'BAR',
    'Alain Prost':'Prost','Enrique Bernoldi':'Arrows',
    'Jos Verstappen':'Arrows','Luciano Burti':'Prost',
    'Mark Webber':'Jaguar','Felipe Massa':'Sauber',
    'Cristiano da Matta':'Toyota','Justin Wilson':'Minardi',
    'Ralph Firman':'Jordan','Giorgio Pantano':'Jordan',
    'Gianmaria Bruni':'Minardi','Zsolt Baumgartner':'Minardi',
    'Tiago Monteiro':'Jordan','Christijan Albers':'Minardi',
    'Patrick Friesacher':'Minardi','Vitantonio Liuzzi':'Red Bull',
    'Narain Karthikeyan':'Jordan','Yuji Ide':'Super Aguri',
    'Franck Montagny':'Super Aguri','Robert Doornbos':'Red Bull',
    'Heikki Kovalainen':'Renault','Adrian Sutil':'Spyker Force',
    'Sakon Yamamoto':'Super Aguri','Anthony Davidson':'Super Aguri',
    'Alexander Wurz':'Williams','Timo Glock':'BMW',
    'Nelson Piquet Jr.':'Renault','Kazuki Nakajima':'Williams',
    'Sébastien Bourdais':'Toro Rosso','Jean Alesi':'Prost',
    'Robbie Kerr':'Minardi','Scott Speed':'Toro Rosso',
    'Vitaly Petrov':'Renault','Kamui Kobayashi':'BMW',
    'Nico Hulkenberg':'Williams','Jaime Alguersuari':'Toro Rosso',
    'Sébastien Buemi':'Toro Rosso','Lucas di Grassi':'Virgin',
    'Bruno Senna':'HRT','Paul di Resta':'Force India',
    'Esteban Gutierrez':'Sauber','Valtteri Bottas':'Williams',
    'Pastor Maldonado':'Williams','Jules Bianchi':'Marussia',
    'Jean-Eric Vergne':'Toro Rosso','Max Chilton':'Marussia',
    'Giedo van der Garde':'Caterham','Daniil Kvyat':'Toro Rosso',
    'Marcus Ericsson':'Caterham','Felipe Nasr':'Sauber',
    'Romain Grosjean':'Lotus','Will Stevens':'Marussia',
    'Roberto Merhi':'Marussia','Jolyon Palmer':'Lotus',
    'Pascal Wehrlein':'Manor','Rio Haryanto':'Manor',
    'Stoffel Vandoorne':'McLaren','Antonio Giovinazzi':'Haas',
    'Brendon Hartley':'Toro Rosso','Sergey Sirotkin':'Williams',
    'George Russell':'Williams','Robert Kubica':'Williams',
    'Nicholas Latifi':'Williams','Daniil Kvyat':'AlphaTauri',
    'Mick Schumacher':'Haas','Nikita Mazepin':'Haas',
    'Nyck De Vries':'Williams','Logan Sargeant':'Williams',
    'Daniel Ricciardo':'AlphaTauri','Oscar Piastri':'McLaren',
    'Max Verstappen':'Red Bull Racing','Sergio Perez':'Red Bull Racing',
    'Lewis Hamilton':'Mercedes','Charles Leclerc':'Ferrari',
    'Carlos Sainz':'Ferrari','Lando Norris':'McLaren',
    'Fernando Alonso':'Aston Martin','Lance Stroll':'Aston Martin',
    'Pierre Gasly':'Alpine','Esteban Ocon':'Alpine',
    'Alexander Albon':'Williams','Yuki Tsunoda':'RB',
    'Kevin Magnussen':'Haas','Nico Hulkenberg':'Haas',
    'Valtteri Bottas':'Sauber','Guanyu Zhou':'Sauber',
}

def DRIVER_TO_TEAM_LOOKUP(drv: str):
    return _LOOKUP.get(drv, 'Unknown')
