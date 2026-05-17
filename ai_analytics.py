import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import json
from dotenv import load_dotenv
import sys
sys.path.insert(0, '.')
from data_model import (
    get_seasons_data, get_championship_standings,
    DRIVER_COLORS, DRIVERS, _seeded,
)

load_dotenv()

FEATURE_NAMES = [
    'Tyre Age', 'Track Temp', 'Fuel Load', 'DRS Usage',
    'Wind Speed', 'Brake Temp', 'Engine Mode', 'Track State',
    'Air Temp', 'Humidity', 'Wet Track', 'Tyre Compound',
]

FEATURE_COLORS = {
    'Benchmark': '#ffd700', 'Confidence': '#00ff00',
    'Anomaly': '#ff4444',
}


def render():
    st.markdown('<div class="section-header">🤖 AI Analytics Engine</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        year = st.selectbox(
            "Season",
            list(reversed(range(2000, 2027))),
            key="ai_year",
            index=26,
        )
    with col2:
        mode_sel = st.selectbox(
            "Analysis Mode",
            ['Race Strategy', 'Qualifying', 'Full Season'],
            key="ai_mode",
        )

    data   = get_seasons_data()
    std_yr = get_championship_standings(year)
    races  = data[year]['races']
    selected_race = races[0] if races else 'default_race'
    race_len = 56
    s_ai   = _seeded(hash(str(year)) % 2**31)

    st.markdown("---")

    # ── AI-Generated Insights ──
    st.markdown('<div class="section-header">💡 AI-Generated Insights</div>', unsafe_allow_html=True)

    # select the top 3 drivers for insight generation
    leader_drivers = [s['driver'] for s in std_yr[:3]]
    insights = _gen_insights(leader_drivers, year, races, data, s_ai)

    for ins in insights:
        conf_color = ('#00ff00' if ins['conf'] > 90 else
                       '#ffd700' if ins['conf'] > 75 else '#ff6b6b')
        st.markdown(f"""
        <div class="metric-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div>
              <div style="font-size:1.1rem;font-weight:700;color:#ffd700">{ins['title']}</div>
              <div style="font-size:.9rem;color:#ccc;margin-top:.5rem">{ins['text']}</div>
            </div>
            <div style="text-align:right;margin-left:1rem">
              <div style="font-size:1.5rem;font-weight:700;color:{conf_color}">{ins['conf']}%</div>
              <div style="font-size:.75rem;color:#888">Confidence</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")

    # ── ML Pace Prediction ──
    st.markdown('<div class="section-header">📊 ML Pace Prediction</div>', unsafe_allow_html=True)
    col_pr1, col_pr2 = st.columns([1, 1], gap="large")

    lap_hist  = np.linspace(92.3, 91.0, 8)
    lap_pred  = np.linspace(91.0, 90.5, 4)
    lap_noise = s_ai.normal(0, 0.18, len(lap_hist))
    lap_hist += lap_noise

    with col_pr1:
        fig_p = go.Figure()
        fig_p.add_trace(go.Scatter(
            x=list(range(len(lap_hist))), y=lap_hist.tolist(),
            mode='lines+markers', name='History',
            line=dict(color='#ffd700', width=2), marker=dict(size=8),
        ))
        fig_p.add_trace(go.Scatter(
            x=list(range(len(lap_hist) - 1, len(lap_hist) + len(lap_pred) - 1)),
            y=np.concatenate([[lap_hist[-1]], lap_pred]).tolist(),
            mode='lines+markers', name='Predicted',
            line=dict(color='#ff6b6b', width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
        ))
        fig_p.update_layout(
            title='ML Pace Forecast – Next Laps',
            xaxis_title='Lap', yaxis_title='Lap Time (s)',
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig_p.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_p.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})

    with col_pr2:
        st.markdown("**Driver Skill Score Evolution**")
        race_count = len(races)
        rng_ss = _seeded(year * 17)
        rn_laps_2 = np.arange(1, max(22, race_count + 1))
        base_ss = 80 + rng_ss.uniform(0, 12, len(rn_laps_2))
        skill_scores = np.maximum.accumulate(base_ss + rng_ss.normal(0, .4, len(rn_laps_2)))
        fig_ss = go.Figure()
        fig_ss.add_trace(go.Scatter(
            x=rn_laps_2, y=skill_scores.tolist(),
            mode='lines+markers', name='Skill Score',
            fill='tozeroy', line=dict(color='#4ecdc4', width=3),
            marker=dict(size=7), fillcolor='rgba(78,205,196,0.2)',
        ))
        fig_ss.update_layout(
            title=f'{year} Season Progression',
            xaxis_title='Race #',
            yaxis_title='Skill Score (0-100)',
            yaxis=dict(range=[70, 100]),
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig_ss.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_ss.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_ss, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Feature importance ──
    st.markdown('<div class="section-header">🔍 Key Performance Drivers (Feature Importance)</div>', unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([1, 1], gap="large")

    # simple skill-simulated feature importance
    rng_fi = _seeded(hash(str(year) + 'features') % 2**31)
    feat_imp = np.sort(rng_fi.uniform(2, 30, len(FEATURE_NAMES)))[::-1]
    feat_imp = feat_imp / feat_imp.sum() * 100

    with col_f1:
        fig_fi = px.bar(
            pd.DataFrame({'Feature': FEATURE_NAMES, 'Importance': feat_imp}),
            x='Importance', y='Feature', orientation='h',
            color='Importance', color_continuous_scale='Blues',
        )
        fig_fi.update_layout(
            template='plotly_dark', height=350,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            xaxis_title='Importance (%)', showlegend=False,
        )
        fig_fi.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_fi.update_yaxes(showgrid=False)
        st.plotly_chart(fig_fi, use_container_width=True, config={'displayModeBar': False})

    with col_f2:
        st.markdown("**Anomaly Detection**")
        rng_an = _seeded(hash(selected_race + str(year)) % 2**31)
        anom_df = pd.DataFrame([{
            'Lap':      str(int(rng_an.integers(1, max(1, race_len)))),
            'Issue':    rng_an.choice(
                ['Brake Fade', 'Low Tyre Temp', 'High Fuel Burn', 'DRS Malfunction',
                 'Electrical Glitch', 'Understeer Spike']),
            'Severity': rng_an.choice(['🟢 Low', '🟡 Medium', '🔴 High']),
            'Impact':   f"{float(rng_an.uniform(-0.5,-0.05)):.2f}s/lap",
        } for _ in range(6)])
        st.dataframe(anom_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── NEW: Tactical opportunity matrix ──
    st.markdown('<div class="section-header">🎯 Tactical Opportunity Matrix</div>', unsafe_allow_html=True)
    rng_tm = _seeded(hash(str(year) + 'tactics') % 2**31)
    opp_data = {
        'Opportunity': ['Undercut', 'Overcut', 'DRS Zone', 'Pit-lane Speed',
                        'S1 Power', 'S2 Traction', 'Corner Exit'],
        'Potential Gain': rng_tm.uniform(0.2, 2.5, 7).round(2).tolist(),
        'Risk Level':    rng_tm.choice(['Low','Low','Low','Medium','Medium','High'], 7).tolist(),
        'Confidence':    [f"{int(rng_tm.integers(65,99))}%" for _ in range(7)],
    }
    fig_tm = px.bar(
        pd.DataFrame(opp_data), x='Potential Gain', y='Opportunity',
        color='Potential Gain', orientation='h',
        color_continuous_scale='RdYlGn',
    )
    fig_tm.update_layout(
        template='plotly_dark', height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        xaxis_title='Potential Time Gain (s)',
    )
    fig_tm.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_tm.update_yaxes(showgrid=False)
    st.plotly_chart(fig_tm, use_container_width=True, config={'displayModeBar': False})

    # ── Race outcome prediction ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 Race Outcome Prediction</div>', unsafe_allow_html=True)
    rng_ro = _seeded(hash(str(year) + 'outcome') % 2**31)
    col_o1, col_o2, col_o3 = st.columns(3)
    p1 = int(rng_ro.normal(35, 12))
    p2 = int(rng_ro.normal(28, 10))
    p3 = int(rng_ro.normal(18, 8))
    col_o1.markdown(f"""
    <div class="metric-card">
      <div style="font-size:.85rem;color:#888">🥇 Win Probability</div>
      <div style="font-size:1.8rem;font-weight:700;color:#ffd700;margin-top:.5rem">{p1}%</div>
      <div style="font-size:.75rem;color:#aaa">{rng_ro.choice(['Undercut viable','Pole advantage'])}</div>
    </div>""", unsafe_allow_html=True)
    col_o2.markdown(f"""
    <div class="metric-card">
      <div style="font-size:.85rem;color:#888">🥈 Podium Probability</div>
      <div style="font-size:1.8rem;font-weight:700;color:#ffd700;margin-top:.5rem">{min(99, p1+p2)}%</div>
      <div style="font-size:.75rem;color:#aaa">Current pace</div>
    </div>""", unsafe_allow_html=True)
    col_o3.markdown(f"""
    <div class="metric-card">
      <div style="font-size:.85rem;color:#888">🎯 Points Finish</div>
      <div style="font-size:1.8rem;font-weight:700;color:#00ff00;margin-top:.5rem">98%</div>
      <div style="font-size:.75rem;color:#aaa">+2% vs 1-stop</div>
    </div>""", unsafe_allow_html=True)

    # ── NEW: Gap to leader ──
    st.markdown("---")
    st.markdown('<div class="section-header">📈 Gap to Leader (Predicted)</div>', unsafe_allow_html=True)
    rng_gap = _seeded(hash(str(year) + 'gap') % 2**31)
    laps_gap = np.arange(1, race_len + 1)
    gap_act   = 0.4 + 0.025 * laps_gap + rng_gap.normal(0, 0.12, len(laps_gap))
    gap_pred  = 0.4 + 0.018 * laps_gap
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(
        x=laps_gap, y=gap_act, mode='lines', name='Actual Gap',
        line=dict(color='#ffd700', width=2),
    ))
    fig_gap.add_trace(go.Scatter(
        x=laps_gap, y=gap_pred, mode='lines', name='AI Prediction',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
    ))
    fig_gap.update_layout(
        title='Gap to Leader – Actual vs Predicted',
        xaxis_title='Lap', yaxis_title='Gap (s)',
        template='plotly_dark', height=350,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
    )
    fig_gap.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig_gap.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig_gap, config={'displayModeBar': False})

    # ── NEW: Strategy Window Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">⏱️ Optimal Strategy Window Analysis</div>', unsafe_allow_html=True)
    rng_sw = _seeded(hash(str(year) + 'strategy') % 2**31)
    strategy_windows = []
    for i in range(1, min(12, len(races) + 1)):
        strategy_windows.append({
            'Race': races[i-1] if i-1 < len(races) else f'Race {i}',
            'Undercut Window': f"{rng_sw.integers(15, 35)}-{rng_sw.integers(25, 45)}s",
            'Pit Stop Loss': round(rng_sw.uniform(18, 25), 1),
            'Recommended': rng_sw.choice(['2-stop', '3-stop', '1-stop + aggressive'])
        })
    st.dataframe(pd.DataFrame(strategy_windows), use_container_width=True)

    # ── NEW: Tire Compound Performance ──
    st.markdown("---")
    st.markdown('<div class="section-header">🛞 Tire Compound Performance</div>', unsafe_allow_html=True)
    compounds = ['Soft', 'Medium', 'Hard', 'Intermediate', 'Wet']
    rng_ty = _seeded(hash(str(year) + 'tires') % 2**31)
    tire_data = pd.DataFrame({
        'Compound': compounds,
        'Performance': (100 - np.arange(5) * 5 - rng_ty.uniform(0, 5, 5)).clip(55),
        'Degradation': rng_ty.uniform(0.1, 0.8, 5).round(2),
        'Optimal Stint (laps)': [int(x) for x in rng_ty.uniform(8, 28, 5).round()]
    })
    fig_ty = px.bar(tire_data, x='Compound', y=['Performance', 'Degradation'], 
                    barmode='group', color_discrete_map={'Performance': '#ffd700', 'Degradation': '#ff6b6b'})
    fig_ty.update_layout(template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)')
    st.plotly_chart(fig_ty, config={'displayModeBar': False})


def _gen_insights(drivers: list, year: int, races: list, data: dict, base_rng) -> list:
    """Deterministic insight generator with Genkit AI integration."""
    
    # --- Genkit AI Implementation ---
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            from genkit.core import Genkit
            from genkit.plugins.gemini import gemini
            
            ai = Genkit(plugins=[gemini(api_key=api_key)])
            prompt = f"""
            You are a world-class F1 race strategist. Analyze the {year} season for drivers {drivers} 
            at {races[:1] if races else 'the track'}. Provide exactly 3 short, highly tactical insights 
            (e.g., tire degradation, undercut windows, cornering speeds).
            Output strictly as a JSON array of objects with the keys: 
            - "title": A short catchy title
            - "text": The tactical insight (1-2 sentences)
            - "conf": Confidence score as an integer from 70 to 99.
            Do not include markdown blocks like ```json.
            """
            
            response = ai.generate(model="gemini-1.5-flash", prompt=prompt)
            
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
                
            insights = json.loads(text)
            if isinstance(insights, list) and len(insights) > 0 and 'title' in insights[0]:
                return insights
        except Exception as e:
            print(f"Genkit AI generation failed, falling back to deterministic templates: {e}")

    insights = []
    templates = [
        {
            'title': 'Sector Dominance',
            'text':  '{driver} outpaces rivals in Sector 2 by {gap:.2f}s per lap, '
                     'thanks to superior traction setup and later apex speeds.',
            'repl':  ['driver', 'gap'],
        },
        {
            'title': 'Tyre Management Edge',
            'text':  '{driver} shows {rate:.1f}s/lap improvement during the sweet-spot '
                     'lap window. Recommend extending stints by 3–5 laps.',
            'repl':  ['driver', 'rate'],
        },
        {
            'title': 'Undercut Opportunity',
            'text':  'Current gap is {gap:.1f}s. A pit stop now gains an estimated '
                     '{gain:.2f}s before traffic interferes. Execute within 2 laps.',
            'repl':  ['gap', 'gain'],
        },
        {
            'title': 'DRS Effectiveness',
            'text':  'On the {track} main straight, DRS opens a '
                     '{gain:.1f}s advantage. Prioritise DRS zone slipstreaming.',
            'repl':  ['track', 'gain'],
        },
        {
            'title': 'Brake Performance',
            'text':  '{driver}\'s brake temps stabilise at {temp:.0f}°C by lap '
                     '{lap}. Early warning indicator shows {state}.',
            'repl':  ['driver', 'temp', 'lap', 'state'],
        },
        {
            'title': 'Fuel Load Sensitivity',
            'text':  'Lap time degrades by {rate:.3f}s/lap per 10kg of fuel burn. '
                     'Optimal fuelsave window identified for stint 1.',
            'repl':  ['rate'],
        },
    ]
    rng_i = _seeded(hash(str(year) + 'insights') % 2**31)
    track_name  = races[0] if races else 'this circuit'
    for i, tmpl in enumerate(templates[:4]):
        rng_d = _seeded(abs(hash(drivers[i % len(drivers)] + str(year))))
        repl  = {}
        for key in tmpl['repl']:
            if key ==      'driver': repl['driver'] = drivers[i % len(drivers)]
            elif key ==    'gap':    repl['gap']    = round(float(rng_d.uniform(0.3, 1.8)), 2)
            elif key ==    'rate':   repl['rate']   = round(float(rng_d.uniform(0.08, 0.35)), 2)
            elif key ==    'gain':   repl['gain']   = round(rng_d.uniform(0.4, 1.2), 2)
            elif key ==    'track':  repl['track']  = track_name
            elif key ==    'temp':   repl['temp']   = int(rng_d.integers(560, 780))
            elif key ==    'lap':    repl['lap']    = int(rng_d.integers(8, 18))
            elif key ==    'state':  repl['state']  = rng_d.choice(['stable', 'warming', 'cooling'])
        text = tmpl['text'].format(**repl)
        insights.append({
            'title': tmpl['title'],
            'text':  text,
            'conf':  int(rng_d.integers(78, 99)),
        })
    return insights
