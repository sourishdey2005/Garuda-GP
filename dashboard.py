import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
sys.path.insert(0, '.')
from data_model import (
    get_seasons_data, get_championship_standings, _seeded
)

def render():
    st.markdown('<div class="section-header">📊 Championship Dashboard</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        year = st.selectbox(
            "Select Season",
            list(range(2026, 1999, -1)),
            key="dash_year",
            index=26,
        )
    with col2:
        stats_view = st.selectbox(
            "View",
            ["Season Standings", "Full History", "Team Only"],
            key="dash_view",
        )

    data = get_seasons_data()
    standings = get_championship_standings(year)
    races     = data[year]['races']

    # ── KPI cards ──
    total_drivers = len(standings)
    total_teams   = len({s['team'] for s in standings})
    champion = standings[0]
    s_kpi    = _seeded(year * 31)
    total_pts = sum(s['points'] for s in standings[:10])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Season Races", str(len(races)), delta=str(year))
    with col2:
        st.metric("Teams", str(total_teams), delta="+0")
    with col3:
        st.metric("Drivers", str(total_drivers), delta="+0")
    with col4:
        st.metric("Data Points", f"{int(total_pts * 1200):,}+", delta="Real-time")

    st.markdown("---")

    # ── Drivers championship ──
    st.markdown('<div class="section-header">🏆 Drivers Championship</div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        points_list = [s['points'] for s in standings]
        drivers_list = [s['driver'] for s in standings]
        fig = px.bar(
            pd.DataFrame({'Driver': drivers_list, 'Points': points_list}),
            x='Points', y='Driver', orientation='h', color='Points',
            color_continuous_scale='YlOrBr',
        )
        fig.update_layout(
            template='plotly_dark', height=max(400, total_drivers * 22 + 50),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Championship Points',
            yaxis={'categoryorder': 'total ascending'},
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_r:
        st.markdown("**Points Distribution**")
        fig = px.histogram(
            pd.DataFrame({'Points': points_list}),
            x='Points', nbins=10, color_discrete_sequence=['#ffd700'],
        )
        fig.update_layout(
            template='plotly_dark', height=300,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Points', yaxis_title='Number of Drivers',
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Team points accumulation chart ──
    st.markdown('<div class="section-header">📈 Team Points Accumulation (Season)</div>', unsafe_allow_html=True)

    # Build a colour map that matches teams used in _ld_team()
    _all_teams_in_season = sorted({
        r['team']
        for race in races
        for r in (data[year]['seasons'].get(race, []))
    })
    _palette = [
        '#3671C6','#27F4D2','#FF2800','#F58020','#358C75',
        '#2293D1','#37BEDD','#6676FF','#B6BABD','#52E252',
        '#FF6B6B','#4ECDC4','#A855F7','#FFA500','#00CCFF',
    ]
    team_color_map = {t: _palette[i % len(_palette)]
                      for i, t in enumerate(_all_teams_in_season)}

    # Per-team cumulative points  (race_idx, cumul_pts)
    per_team = {t: [] for t in _all_teams_in_season}
    running = {t: 0 for t in _all_teams_in_season}
    for ri_idx2, race_nm in enumerate(races, start=1):
        for r in data[year]['seasons'].get(race_nm, []):
            running[r['team']] = running.get(r['team'], 0) + r['points']
        for t in _all_teams_in_season:
            per_team[t].append((ri_idx2, running.get(t, 0)))

    fig_e = go.Figure()
    for t in _all_teams_in_season:
        xs = [pt[0] for pt in per_team[t]]
        ys = [pt[1] for pt in per_team[t]]
        if max(ys) < 1:          # skip teams that never scored
            continue
        fig_e.add_trace(go.Scatter(
            x=xs, y=ys,
            mode='lines+markers', name=t,
            line=dict(color=team_color_map[t], width=2),
            marker=dict(size=5),
        ))

    fig_e.update_layout(
        title='Team Championship Points by Race',
        xaxis_title='Race #', yaxis_title='Cumulative Points',
        template='plotly_dark', height=420,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.04,
                    xanchor='center', x=0.5, font=dict(size=9)),
    )
    fig_e.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_e.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_e, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Season Pace Trend ──
    st.markdown('<div class="section-header">📊 Season Pace Trend</div>', unsafe_allow_html=True)
    col_pt, col_pr = st.columns([1, 1], gap="large")
    with col_pt:
        st.markdown("**Qualifying Pace by Race**")
        s_qp = _seeded(year * 17)
        qp_trend = []
        for ri_idx3, race_nm in enumerate(races, start=1):
            drift = 0.12 * np.sin(ri_idx3 * 0.55) + s_qp.normal(0, 0.18)
            qp_trend.append(round(92.3 + drift, 3))
        fig_qp = go.Figure(go.Scatter(
            x=list(range(1, len(qp_trend) + 1)),
            y=qp_trend,
            mode='lines+markers', name='Avg Qualifying Lap (s)',
            line=dict(color='#00d2be', width=2),
            marker=dict(size=7),
            fill='tozeroy', fillcolor='rgba(0,210,190,0.1)',
        ))
        fig_qp.update_layout(
            xaxis_title='Race #', yaxis_title='Avg Qualifying Lap (s)',
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False,
        )
        fig_qp.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.08)',
            tickmode='array', tickvals=list(range(1, len(qp_trend) + 1, max(1, len(races) // 7))),
        )
        fig_qp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.08)')
        st.plotly_chart(fig_qp, use_container_width=True, config={'displayModeBar': False})

    with col_pr:
        st.markdown("**Race Pace Trend**")
        s_rp = _seeded(year * 29)
        rp_trend = []
        for ri_idx4, race_nm in enumerate(races, start=1):
            drift = 0.15 * np.sin(ri_idx4 * 0.45 + 1.2) + s_rp.normal(0, 0.22)
            rp_trend.append(round(94.8 + drift, 3))
        fig_rp = go.Figure(go.Scatter(
            x=list(range(1, len(rp_trend) + 1)),
            y=rp_trend,
            mode='lines+markers', name='Avg Race Lap (s)',
            line=dict(color='#ffd700', width=2),
            marker=dict(size=7),
            fill='tozeroy', fillcolor='rgba(255,215,0,0.1)',
        ))
        fig_rp.update_layout(
            xaxis_title='Race #', yaxis_title='Avg Race Lap (s)',
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False,
        )
        fig_rp.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.08)',
            tickmode='array', tickvals=list(range(1, len(rp_trend) + 1, max(1, len(races) // 7))),
        )
        fig_rp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.08)')
        st.plotly_chart(fig_rp, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Grid Position Δ per Race ──
    st.markdown('<div class="section-header">🔢 Grid Position Δ per Race</div>', unsafe_allow_html=True)
    col_gd1, col_gd2 = st.columns([3, 1])
    with col_gd1:
        st.markdown("**Grid-to-Finish Position Change (Selected Drivers)**")
        s_gd = _seeded(year * 37)
        top_drivers = [s['driver'] for s in standings[:10]]
        season_races = races[:min(22, len(races))]
        fig_gd = go.Figure()
        for drv_c in top_drivers:
            s_d = _seeded(hash(drv_c + str(year)) % 2**31)
            delta_vals = [s_d.integers(-8, 9) for _ in season_races]
            fig_gd.add_trace(go.Scatter(
                x=season_races,
                y=delta_vals,
                mode='lines+markers',
                name=drv_c,
                line=dict(width=1.5),
                marker=dict(size=4),
            ))
        fig_gd.update_layout(
            xaxis_title='Race', yaxis_title='Grid → Finish Δ',
            template='plotly_dark', height=400,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            legend=dict(orientation='h', yanchor='top', y=-0.18,
                        xanchor='center', x=0.5, font=dict(size=9)),
            hovermode='x unified',
            xaxis=dict(tickangle=-40, nticks=min(22, len(season_races))),
        )
        fig_gd.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.07)')
        fig_gd.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.07)',
                              zeroline=True, zerolinewidth=2, zerolinecolor='rgba(255,255,255,0.25)')
        st.plotly_chart(fig_gd, use_container_width=True, config={'displayModeBar': False})

    with col_gd2:
        st.markdown("**Δ Legend & Summary**")
        s_gs = _seeded(year * 41)
        top5 = standings[:5]
        for drv_ent in top5:
            d_avg = int(s_gs.integers(-5, 4))
            arrow = '⚡' if abs(d_avg) <= 1 else ('⬆️' if d_avg > 0 else '⬇️')
            st.markdown(
                f"<span style='font-size:0.94rem; font-weight:600'>{drv_ent['driver']}</span>  "
                f"<span style='font-size:0.88rem'>{arrow} {d_avg:+d} avg Δ</span>  "
                f"<span style='font-size:0.85rem;color:#888'>Pts: {drv_ent['points']}</span>",
                unsafe_allow_html=True
            )
        st.markdown("---")
        st.markdown("**Δ Guide**")
        st.markdown(
            "<span style='color:#00ff00'>=0</span> Started & finished same position<br>"
            "<span style='color:#ffd700'>negative</span> Gains positions during race<br>"
            "<span style='color:#ff4444'>positive</span> Loses positions during race",
            unsafe_allow_html=True
        )

    # ── NEW: Performance Metrics Radar ──
    st.markdown('<div class="section-header">📊 Performance Metrics Radar</div>', unsafe_allow_html=True)
    s_radar = _seeded(year * 53)
    metrics = ['Pace', 'Consistency', 'Qualifying', 'Race Craft', 'Overtaking', 'Defending']
    radar_df = pd.DataFrame({
        'metric': metrics,
        'value': [s_radar.uniform(65, 95) for _ in metrics]
    })
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=radar_df['value'].tolist() + [radar_df['value'].iloc[0]],
        theta=metrics + [metrics[0]],
        fill='toself',
        line=dict(color='#ffd700'),
        fillcolor='rgba(255,215,0,0.3)',
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template='plotly_dark', height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        title='Season Performance Overview'
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})

    # ── Championship evolution for individual driver ──
    st.markdown('<div class="section-header">🏁 Season Race Winners</div>', unsafe_allow_html=True)
    rows = []
    s_win = _seeded(year * 3)
    for ri_idx, race_nm in enumerate(races[:min(12, len(races))]):
        res_list = data[year]['seasons'].get(race_nm, [])
        winner = res_list[0]['driver'] if res_list else 'TBD'
        rows.append({'Race': race_nm, 'Winner': winner, 'Round': ri_idx + 1})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── NEW: Championship history across years ──
    st.markdown('<div class="section-header">🕰️ Multi-Year Championship Comparison</div>', unsafe_allow_html=True)
    selected_years = st.multiselect(
        "Compare Seasons",
        list(range(2000, 2027)),
        default=[year, max(year - 1, 2000)],
        key="multi_year",
    )
    if selected_years:
        fig_hist = go.Figure()
        for yr in selected_years:
            stnd = get_championship_standings(yr)
            ylder = _seeded(yr * 7)
            marker_sym = 'circle' if yr == year else 'diamond'
            fig_hist.add_trace(go.Scatter(
                x=list(range(1, len(stnd) + 1)),
                y=[s['points'] for s in stnd],
                mode='lines+markers',
                name=str(yr),
                line=dict(width=2, color=('#ffd700' if yr == year else '#558')),
                marker=dict(symbol=marker_sym, size=7),
            ))
        fig_hist.update_layout(
            title='Championship Point Distribution by Season',
            xaxis_title='Position', yaxis_title='Points',
            template='plotly_dark', height=400,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig_hist.update_xaxes(
            showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)',
            tickmode='array', tickvals=list(range(1, 22)),
        )
        fig_hist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── NEW: Teams standings heatmap (⋮ × years) ──
    st.markdown('<div class="section-header">🔥 Team Points Heatmap (10 Seasons)</div>', unsafe_allow_html=True)
    view_years = st.multiselect(
        " Seasons to Include",
        list(range(2000, 2027)),
        default=sorted(range(2025, 2014, -1)),
        key="heatmap_years",
    )
    if view_years:
        all_teams = sorted({
            s['team']
            for yr in view_years
            for s in get_championship_standings(yr)
        })
        heat_z   = []
        heat_lbl = []
        for yr in view_years:
            stnd  = {s['driver']: s for s in get_championship_standings(yr)}
            team_pts = {}
            for _, drv_st in stnd.items():
                t = drv_st['team']
                team_pts[t] = team_pts.get(t, 0) + drv_st['points']
            heat_z.append([team_pts.get(t, 0) for t in all_teams])
            heat_lbl.append(str(yr))
        fig_hm = go.Figure(data=go.Heatmap(
            z=heat_z,
            x=all_teams,
            y=heat_lbl,
            colorscale='YlOrRd',
            colorbar=dict(title='Championship Pts'),
        ))
        fig_hm.update_layout(
            template='plotly_dark', height=max(280, len(view_years) * 35),
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Team', yaxis_title='Season',
        )
        st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Pole-to-Win conversion ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 Pole Position → Race Win Rate</div>', unsafe_allow_html=True)
    perf_data = []
    s_pole = _seeded(year * 11)
    for r in races[:min(16, len(races))]:
        res_list = data[year]['seasons'].get(r, [])
        if len(res_list) < 2:
            continue
        pole_drv  = res_list[0]['driver']
        pole_team = res_list[0]['team']
        winner    = res_list[0]['driver'] if s_pole.random() > 0.22 else res_list[1]['driver']
        perf_data.append({
            'Race':   r,
            'Pole':   pole_drv,
            'Winner': winner,
            'Converted': pole_drv == winner,
        })
    conv_rate = sum(1 for r in perf_data if r['Converted']) / max(len(perf_data), 1) * 100
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Pole → Win Rate", f"{conv_rate:.1f}%",
                  delta=f"{' Avg avg' if conv_rate > 55 else 'Below Avg'}")
    with col_b:
        fig_pw = px.bar(
            pd.DataFrame([{
                'Race': r['Race'],
                'Converted': '✅ Won from Pole' if r['Converted'] else '❌ Lost Pole',
            } for r in perf_data]),
            x='Race', color='Converted',
            color_discrete_map={'✅ Won from Pole': '#00ff00', '❌ Lost Pole': '#ff4444'},
        )
        fig_pw.update_layout(
            template='plotly_dark', height=280,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False,
        )
        fig_pw.update_xaxes(tickangle=-45, showgrid=False)
        fig_pw.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_pw, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Best lap comparison scatter ──
    st.markdown("---")
    st.markdown('<div class="section-header">⚡ Best Lap Time vs Final Position</div>', unsafe_allow_html=True)
    all_race_res = []
    s_bl = _seeded(year * 23)
    for r_nm in races[:min(12, len(races))]:
        res_list = data[year]['seasons'].get(r_nm, [])
        all_race_res.extend(res_list)
    if all_race_res:
        fig_bl = px.scatter(
            pd.DataFrame({
                'Driver':   [r['driver']   for r in all_race_res],
                'Position': [r['position'] for r in all_race_res],
                'Best Lap': [r['best_lap'] for r in all_race_res],
                'Team':     [r['team']     for r in all_race_res],
            }),
            x='Best Lap', y='Position', color='Team',
            hover_data=['Driver'],
            size='Best Lap', size_max=18,
        )
        fig_bl.update_yaxes(autorange='reversed')
        fig_bl.update_layout(
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Best Lap (s)', yaxis_title='Final Position',
        )
        fig_bl.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_bl.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_bl, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Driver Performance Matrix ──
    st.markdown("---")
    st.markdown('<div class="section-header">📈 Driver Performance Matrix</div>', unsafe_allow_html=True)
    s_dpm = _seeded(year * 61)
    perf_drivers = standings[:10]
    perf_matrix = []
    for d in perf_drivers:
        perf_matrix.append({
            'Driver': d['driver'],
            'Points': d['points'],
            'Avg Grid': s_dpm.integers(3, 8),
            'Avg Finish': s_dpm.integers(4, 9),
            'DNF Rate': round(s_dpm.uniform(2, 12), 1),
            'Fastest Laps': s_dpm.integers(0, 5),
        })
    st.dataframe(pd.DataFrame(perf_matrix).set_index('Driver'), use_container_width=True)

    # ── NEW: Overtaking Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏎️ Overtaking Analysis</div>', unsafe_allow_html=True)
    col_over1, col_over2 = st.columns([1, 2])
    with col_over1:
        overtake_counts = {}
        for d in standings[:12]:
            overtake_counts[d['driver']] = int(s_kpi.integers(5, 25))
        fig_over = px.bar(
            pd.DataFrame({'Driver': list(overtake_counts.keys()), 'Overtakes': list(overtake_counts.values())}),
            x='Overtakes', y='Driver', orientation='h', color='Overtakes',
            color_continuous_scale='Tealrose',
        )
        fig_over.update_layout(template='plotly_dark', height=400, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_over, use_container_width=True, config={'displayModeBar': False})
    with col_over2:
        corner_names = ['Turn 1', 'Turn 3', 'Turn 5', 'Turn 8', 'Turn 11', 'Turn 15']
        overtake_zones = pd.DataFrame({
            'Corner': corner_names,
            'Overtakes': [int(s_kpi.integers(20, 50)) for _ in corner_names]
        })
        fig_zone = px.bar(overtake_zones, x='Corner', y='Overtakes', color='Overtakes', color_continuous_scale='OrRd')
        fig_zone.update_layout(template='plotly_dark', height=400, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_zone, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Team Strategy Efficiency ──
    st.markdown("---")
    st.markdown('<div class="section-header">🔧 Team Strategy Efficiency</div>', unsafe_allow_html=True)
    teams_unique = sorted({s['team'] for s in standings})
    strat_data = []
    for t in teams_unique:
        strat_data.append({
            'Team': t,
            'Pit Stop Efficiency': round(s_kpi.uniform(85, 99), 1),
            'Strategy Calls Correct': int(s_kpi.integers(65, 92)),
            'Avg Position Gain': s_kpi.integers(-2, 5),
        })
    st.dataframe(pd.DataFrame(strat_data).set_index('Team'), use_container_width=True)

    # ── NEW: 3D Tire Performance Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏎️ 3D Tire Performance Analysis</div>', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([1, 1])
    
    with col_t1:
        st.markdown("**Tire Compound Performance vs Lap Time**")
        # Generate sample data for 3D scatter
        compounds = ['Soft', 'Medium', 'Hard']
        compound_map = {'Soft': 0, 'Medium': 1, 'Hard': 2}
        
        tire_data = []
        for compound in compounds:
            for _ in range(20):  # 20 samples per compound
                base_perf = {'Soft': 95, 'Medium': 85, 'Hard': 75}[compound]
                lap_time = np.random.normal(95 + (2 - compound_map[compound]) * 2, 1.5)
                degradation = np.random.uniform(0.1, 0.8)
                performance = base_perf - degradation * 10 + np.random.normal(0, 5)
                tire_data.append({
                    'Compound': compound,
                    'Compound_Index': compound_map[compound],
                    'Lap_Time': lap_time,
                    'Degradation': degradation,
                    'Performance': max(50, min(100, performance))
                })
        
        df_tire = pd.DataFrame(tire_data)
        
        fig_tire_3d = go.Figure(data=go.Scatter3d(
            x=df_tire['Lap_Time'],
            y=df_tire['Degradation'],
            z=df_tire['Performance'],
            mode='markers',
            marker=dict(
                size=5,
                color=df_tire['Compound_Index'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Compound")
            ),
            text=df_tire['Compound']
        ))
        
        fig_tire_3d.update_layout(
            template='plotly_dark',
            scene=dict(
                xaxis_title='Lap Time (s)',
                yaxis_title='Degradation',
                zaxis_title='Performance Score',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)'
        )
        st.plotly_chart(fig_tire_3d, use_container_width=True)
    
    with col_t2:
        st.markdown("**Tire Strategy Effectiveness**")
        # 3D bar strategy visualization
        strategies = ['1-stop', '2-stop', '3-stop']
        compounds_3d = ['Soft', 'Medium', 'Hard']
        
        # Create 3D bar data
        z_data = []
        for i, strategy in enumerate(strategies):
            row = []
            for j, compound in enumerate(compounds_3d):
                # Effectiveness score based on compound and strategy
                effectiveness = np.random.uniform(60, 95)
                row.append(effectiveness)
            z_data.append(row)
        
        fig_strategy_3d = go.Figure(data=[go.Bar(
            x=compounds_3d,
            y=z_data[0],
            name='1-stop',
            marker_color='#ff6b6b'
        ), go.Bar(
            x=compounds_3d,
            y=z_data[1],
            name='2-stop',
            marker_color='#4ecdc4'
        ), go.Bar(
            x=compounds_3d,
            y=z_data[2],
            name='3-stop',
            marker_color='#45b7d1'
        )])
        
        fig_strategy_3d.update_layout(
            title='Strategy Effectiveness by Compound',
            template='plotly_dark',
            barmode='group',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            scene=dict(
                xaxis_title='Tire Compound',
                yaxis_title='Effectiveness (%)',
                zaxis_title='Strategy Type',
                bgcolor='rgba(0,0,0,0)'
            )
        )
        st.plotly_chart(fig_strategy_3d, use_container_width=True)

    # ── NEW: 3D Track Evolution Map ──
    st.markdown("---")
    st.markdown('<div class="section-header">🗺️ 3D Track Evolution Map</div>', unsafe_allow_html=True)
    
    # Generate a 3D surface representing track grip evolution
    x = np.linspace(0, 10, 50)  # Track position
    y = np.linspace(0, 5, 30)   # Session time (laps)
    X, Y = np.meshgrid(x, y)
    
    # Create a surface with grip levels (higher = more grip)
    Z = np.sin(X/2) * np.cos(Y/3) * 10 + 70 + np.random.normal(0, 5, X.shape)
    Z = np.clip(Z, 50, 95)  # Grip percentage
    
    fig_track_3d = go.Figure(data=[go.Surface(
        x=X, y=Y, z=Z,
        colorscale='Hot',
        colorbar=dict(title="Grip Level (%)")
    )])
    
    fig_track_3d.update_layout(
        title='Track Surface Grip Evolution',
        template='plotly_dark',
        scene=dict(
            xaxis_title='Track Position',
            yaxis_title='Lap Number',
            zaxis_title='Grip Level (%)',
            bgcolor='rgba(0,0,0,0)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_track_3d, use_container_width=True)

    # ── NEW: 3D Overtake Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">🔄 3D Oretake Analysis by Corner and Lap</div>', unsafe_allow_html=True)
    
    # Generate data for overtakes by corner and lap
    corners = [f'Turn {i}' for i in range(1, 16)]
    laps = list(range(1, 51))  # 50 lap race
    
    # Create 3D histogram data
    hist_data = []
    for lap in laps[::2]:  # Every 2nd lap to reduce density
        for corner in corners:
            overtakes = np.random.poisson(3)  # Average 3 overtakes per corner per lap sample
            if overtakes > 0:
                hist_data.append({
                    'Lap': lap,
                    'Corner': corner,
                    'Overtakes': overtakes
                })
    
    df_overtake = pd.DataFrame(hist_data)
    
    # Create 3D scatter for overtakes
    fig_overtake_3d = go.Figure(data=go.Scatter3d(
        x=df_overtake['Lap'],
        y=[int(c.split()[1]) for c in df_overtake['Corner']],  # Extract turn number
        z=df_overtake['Overtakes'],
        mode='markers',
        marker=dict(
            size=df_overtake['Overtakes'] * 2,
            color=df_overtake['Overtakes'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Overtake Count"),
            opacity=0.7
        )
    ))
    
    fig_overtake_3d.update_layout(
        title='Overtakes Distribution by Lap and Corner',
        template='plotly_dark',
        scene=dict(
            xaxis_title='Lap Number',
            yaxis_title='Corner Number',
            zaxis_title='Overtake Count',
            bgcolor='rgba(0,0,0,0)'
        ),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_overtake_3d, use_container_width=True)

    # ── NEW: 3D Driver Performance Cube ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 3D Driver Performance Cube</div>', unsafe_allow_html=True)
    
    # Create a 3D scatter plot showing driver performance across three metrics
    top_drivers = [s['driver'] for s in standings[:8]]  # Top 8 drivers
    
    # Generate performance data
    performance_data = []
    for i, driver in enumerate(top_drivers):
        pace_score = np.random.uniform(70, 98)
        consistency_score = np.random.uniform(65, 95)
        racecraft_score = np.random.uniform(60, 90)
        performance_data.append({
            'Driver': driver,
            'Pace': pace_score,
            'Consistency': consistency_score,
            'Racecraft': racecraft_score
        })
    
    df_perf = pd.DataFrame(performance_data)
    
    fig_perf_3d = go.Figure()
    
    # Add 3D scatter points for each driver
    colors = px.colors.qualitative.Set3
    for idx, driver in enumerate(df_perf['Driver']):
        driver_data = df_perf[df_perf['Driver'] == driver].iloc[0]
        fig_perf_3d.add_trace(go.Scatter3d(
            x=[driver_data['Pace']],
            y=[driver_data['Consistency']],
            z=[driver_data['Racecraft']],
            mode='markers',
            marker=dict(
                size=12,
                color=colors[idx % len(colors)],
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            name=driver,
            text=f"{driver}<br>Pace: {driver_data['Pace']:.1f}<br>Consistency: {driver_data['Consistency']:.1f}<br>Racecraft: {driver_data['Racecraft']:.1f}"
        ))
    
    # Add reference lines for better 3D perception
    fig_perf_3d.add_trace(go.Scatter3d(
        x=[70, 98], y=[65, 95], z=[60, 90],
        mode='lines',
        line=dict(color='rgba(125,125,125,0.3)', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_perf_3d.update_layout(
        title='Driver Performance Across Key Metrics (3D)',
        template='plotly_dark',
        scene=dict(
            xaxis_title='Pace Score',
            yaxis_title='Consistency Score',
            zaxis_title='Racecraft Score',
            bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[60, 100]),
            yaxis=dict(range=[60, 100]),
            zaxis=dict(range=[50, 100])
        ),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_perf_3d, use_container_width=True)
