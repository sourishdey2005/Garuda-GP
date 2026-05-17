import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.insert(0, '.')
from data_model import DRIVER_COLORS, get_driver_lap_data, DRIVER_TO_TEAM, _seeded, get_races

# ── Drivers indexed by year ──
YEAR_DRIVERS = {
    2000: ['Michael Schumacher','Mika Hakkinen','David Coulthard','Rubens Barrichello',
           'Ralf Schumacher','Giancarlo Fisichella','Jenson Button','Kimi Raikkonen',
           'Eddie Irvine','Mika Salo','Heinz-Harald Frentzen','Johnny Herbert',
           'Ricardo Zonta','Pedro de la Rosa','Marc Gené','Jarno Trulli',
           'Nick Heidfeld','Gastón Mazzacane','Tarso Marques','Alex Yoong'],
    2001: ['Michael Schumacher','Rubens Barrichello','David Coulthard','Mika Hakkinen',
           'Ralf Schumacher','Juan Pablo Montoya','Kimi Raikkonen','Jenson Button',
           'Eddie Irvine','Giancarlo Fisichella','Heinz-Harald Frentzen','Jarno Trulli',
           'Olivier Panis','Pedro de la Rosa','Jean Alesi','Nick Heidfeld',
           'Enrique Bernoldi','Jos Verstappen','Tarso Marques','Luciano Burti'],
    2002: ['Michael Schumacher','Rubens Barrichello','Juan Pablo Montoya','Kimi Raikkonen',
           'Ralf Schumacher','David Coulthard','Jenson Button','Jarno Trulli',
           'Eddie Irvine','Giancarlo Fisichella','Heinz-Harald Frentzen','Pedro de la Rosa',
           'Nick Heidfeld','Olivier Panis','Allan McNish','Mark Webber',
           'Alex Yoong','Anthony Davidson','Takuma Sato','Felipe Massa'],
    2003: ['Michael Schumacher','Rubens Barrichello','Kimi Raikkonen','Juan Pablo Montoya',
           'Ralf Schumacher','Jenson Button','David Coulthard','Jarno Trulli',
           'Giancarlo Fisichella','Heinz-Harald Frentzen','Nick Heidfeld','Olivier Panis',
           'Mark Webber','Felipe Massa','Jacques Villeneuve','Pedro de la Rosa',
           'Cristiano da Matta','Justin Wilson','Ralph Firman','Jos Verstappen'],
    2004: ['Michael Schumacher','Rubens Barrichello','Jenson Button','Jarno Trulli',
           'Fernando Alonso','Kimi Raikkonen','Juan Pablo Montoya','Giancarlo Fisichella',
           'David Coulthard','Nick Heidfeld','Mark Webber','Felipe Massa',
           'Heinz-Harald Frentzen','Olivier Panis','Pedro de la Rosa','Jacques Villeneuve',
           'Cristiano da Matta','Giorgio Pantano','Gianmaria Bruni','Zsolt Baumgartner'],
    2005: ['Fernando Alonso','Kimi Raikkonen','Michael Schumacher','Giancarlo Fisichella',
           'Juan Pablo Montoya','Jarno Trulli','Ralf Schumacher','David Coulthard',
           'Jenson Button','Nick Heidfeld','Mark Webber','Felipe Massa',
           'Rubens Barrichello','Jacques Villeneuve','Tiago Monteiro','Christijan Albers',
           'Patrick Friesacher','Vitantonio Liuzzi','Narain Karthikeyan','Juan Pablo Montoya'],
    2006: ['Fernando Alonso','Michael Schumacher','Felipe Massa','Kimi Raikkonen',
           'Giancarlo Fisichella','Jenson Button','Rubens Barrichello','Jarno Trulli',
           'Nick Heidfeld','David Coulthard','Mark Webber','Jacques Villeneuve',
           'Robert Kubica','Pedro de la Rosa','Scott Speed','Tiago Monteiro',
           'Yuji Ide','Christijan Albers','Franck Montagny','Robert Doornbos'],
    2007: ['Lewis Hamilton','Fernando Alonso','Kimi Raikkonen','Felipe Massa',
           'Nick Heidfeld','Heikki Kovalainen','Robert Kubica','Heinz-Harald Frentzen',
           'Giancarlo Fisichella','Jenson Button','Ralf Schumacher','David Coulthard',
           'Mark Webber','Vitantonio Liuzzi','Adrian Sutil','Takuma Sato',
           'Scott Speed','Sakon Yamamoto','Anthony Davidson','Alexander Wurz'],
    2008: ['Lewis Hamilton','Felipe Massa','Kimi Raikkonen','Fernando Alonso',
           'Robert Kubica','Nick Heidfeld','Heikki Kovalainen','Jarno Trulli',
           'Timo Glock','Sebastian Vettel','Nico Rosberg','David Coulthard',
           'Jenson Button','Mark Webber','Rubens Barrichello','Nelson Piquet Jr.',
           'Giancarlo Fisichella','Kazuki Nakajima','Adrian Sutil','Takuma Sato'],
    2009: ['Jenson Button','Sebastian Vettel','Rubens Barrichello','Mark Webber',
           'Fernando Alonso','Kimi Raikkonen','Lewis Hamilton','Heikki Kovalainen',
           'Nico Rosberg','Felipe Massa','Robert Kubica','Jarno Trulli',
           'Nick Heidfeld','Timo Glock','Giancarlo Fisichella','Sébastien Bourdais',
           'Adrian Sutil','Pedro de la Rosa','Kamui Kobayashi','Sakon Yamamoto'],
    2010: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Jenson Button','Nico Rosberg','Robert Kubica','Felipe Massa',
           'Rubens Barrichello','Michael Schumacher','Vitaly Petrov','Kamui Kobayashi',
           'Nico Hulkenberg','Pedro de la Rosa','Jaime Alguersuari','Sébastien Buemi',
           'Lucas di Grassi','Heikki Kovalainen','Jarno Trulli','Timo Glock','Bruno Senna'],
    2011: ['Sebastian Vettel','Jenson Button','Fernando Alonso','Mark Webber',
           'Lewis Hamilton','Felipe Massa','Michael Schumacher','Nico Rosberg',
           'Nico Hulkenberg','Robert Kubica','Vitaly Petrov','Kamui Kobayashi',
           'Rubens Barrichello','Jarno Trulli','Adrian Sutil','Sébastien Buemi',
           'Pastor Maldonado','Heikki Kovalainen','Jérôme d\'Ambrosio','Timo Glock'],
    2012: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Jenson Button','Felipe Massa','Kimi Raikkonen','Nico Rosberg',
           'Michael Schumacher','Sergio Perez','Nico Hulkenberg','Kamui Kobayashi',
           'Pastor Maldonado','Bruno Senna','Romain Grosjean','Heikki Kovalainen',
           'Pedro de la Rosa','Charles Pic','Timo Glock','Narain Karthikeyan','Vitaly Petrov'],
    2013: ['Sebastian Vettel','Fernando Alonso','Mark Webber','Lewis Hamilton',
           'Kimi Raikkonen','Felipe Massa','Romain Grosjean','Nico Rosberg',
           'Jenson Button','Paul di Resta','Sergio Perez','Nico Hulkenberg',
           'Esteban Gutierrez','Valtteri Bottas','Pastor Maldonado','Jules Bianchi',
           'Adrian Sutil','Jean-Eric Vergne','Charles Pic','Max Chilton','Giedo van der Garde'],
    2014: ['Lewis Hamilton','Nico Rosberg','Daniel Ricciardo','Fernando Alonso',
           'Valtteri Bottas','Sebastian Vettel','Felipe Massa','Jenson Button',
           'Nico Hulkenberg','Sergio Perez','Kevin Magnussen','Daniil Kvyat',
           'Jules Bianchi','Max Chilton','Esteban Gutierrez','Marcus Ericsson',
           'Pastor Maldonado','Kamui Kobayashi','Adrian Sutil','Jean-Eric Vergne'],
    2015: ['Lewis Hamilton','Nico Rosberg','Sebastian Vettel','Kimi Raikkonen',
           'Valtteri Bottas','Felipe Massa','Daniil Kvyat','Daniel Ricciardo',
           'Sergio Perez','Nico Hulkenberg','Max Verstappen','Carlos Sainz',
           'Marcus Ericsson','Felipe Nasr','Romain Grosjean','Pastor Maldonado',
           'Will Stevens','Roberto Merhi','Jolyon Palmer','Fernando Alonso'],
    2016: ['Nico Rosberg','Lewis Hamilton','Daniel Ricciardo','Max Verstappen',
           'Sebastian Vettel','Kimi Raikkonen','Valtteri Bottas','Nico Hulkenberg',
           'Daniil Kvyat','Sergio Perez','Fernando Alonso','Felipe Massa',
           'Jenson Button','Carlos Sainz','Kevin Magnussen','Jolyon Palmer',
           'Esteban Gutierrez','Pascal Wehrlein','Rio Haryanto','Marcus Ericsson'],
    2017: ['Lewis Hamilton','Sebastian Vettel','Valtteri Bottas','Kimi Raikkonen',
           'Daniel Ricciardo','Max Verstappen','Sergio Perez','Esteban Ocon',
           'Carlos Sainz','Nico Hulkenberg','Felipe Massa','Lance Stroll',
           'Esteban Ocon','Jenson Button','Romain Grosjean','Jolyon Palmer',
           'Pascal Wehrlein','Kevin Magnussen','Marcus Ericsson','Antonio Giovinazzi'],
    2018: ['Lewis Hamilton','Sebastian Vettel','Kimi Raikkonen','Valtteri Bottas',
           'Max Verstappen','Daniel Ricciardo','Nico Hulkenberg','Sergio Perez',
           'Kevin Magnussen','Carlos Sainz','Fernando Alonso','Esteban Ocon',
           'Charles Leclerc','Stoffel Vandoorne','Lance Stroll','Marcus Ericsson',
           'Pierre Gasly','Brendon Hartley','Sergey Sirotkin','Romain Grosjean'],
    2019: ['Lewis Hamilton','Valtteri Bottas','Charles Leclerc','Max Verstappen',
           'Sebastian Vettel','Carlos Sainz','Daniel Ricciardo','Kimi Raikkonen',
           'Nico Hulkenberg','Alexander Albon','Sergio Perez','Lance Stroll',
           'Pierre Gasly','Kevin Magnussen','Romain Grosjean','George Russell',
           'Robert Kubica','Antonio Giovinazzi','Daniil Kvyat','Nicholas Latifi'],
    2020: ['Lewis Hamilton','Valtteri Bottas','Max Verstappen','Sergio Perez',
           'Daniel Ricciardo','Carlos Sainz','Lando Norris','Charles Leclerc',
           'Alexander Albon','Pierre Gasly','Esteban Ocon','Lance Stroll',
           'Daniil Kvyat','Nico Hulkenberg','George Russell','Kevin Magnussen',
           'Kimi Raikkonen','Antonio Giovinazzi','Romain Grosjean','Nicholas Latifi'],
    2021: ['Max Verstappen','Lewis Hamilton','Valtteri Bottas','Sergio Perez',
           'Charles Leclerc','Carlos Sainz','Daniel Ricciardo','Pierre Gasly',
           'Lando Norris','Esteban Ocon','Sebastian Vettel','Yuki Tsunoda',
           'George Russell','Kimi Raikkonen','Mick Schumacher','Fernando Alonso',
           'Lance Stroll','Nicholas Latifi','Robert Kubica','Nikita Mazepin'],
    2022: ['Max Verstappen','Sergio Perez','Charles Leclerc','George Russell',
           'Lewis Hamilton','Carlos Sainz','Lando Norris','Fernando Alonso',
           'Esteban Ocon','Pierre Gasly','Daniel Ricciardo','Kevin Magnussen',
           'Yuki Tsunoda','Alexander Albon','Zhou Guanyu','Mick Schumacher',
           'Nicholas Latifi','Nico Hulkenberg','Brendon Hartley','Nyck De Vries'],
    2023: ['Max Verstappen','Sergio Perez','Charles Leclerc','Lewis Hamilton',
           'Carlos Sainz','Lando Norris','Fernando Alonso','George Russell',
           'Esteban Ocon','Pierre Gasly','Lance Stroll','Yuki Tsunoda',
           'Daniel Ricciardo','Oscar Piastri','Nico Hulkenberg','Kevin Magnussen',
           'Alexander Albon','Logan Sargeant','Valtteri Bottas','Zhou Guanyu','Nyck De Vries'],
    2024: ['Max Verstappen','Charles Leclerc','Lewis Hamilton','Carlos Sainz',
           'Lando Norris','George Russell','Oscar Piastri','Sergio Perez',
           'Fernando Alonso','Lance Stroll','Nico Hulkenberg','Pierre Gasly',
           'Alexander Albon','Esteban Ocon','Yuki Tsunoda','Daniel Ricciardo',
           'Kevin Magnussen','Zhou Guanyu','Valtteri Bottas','Logan Sargeant'],
    2025: ['Max Verstappen','Charles Leclerc','Lewis Hamilton','Carlos Sainz',
           'Lando Norris','George Russell','Oscar Piastri','Sergio Perez',
           'Fernando Alonso','Lance Stroll','Nico Hulkenberg','Pierre Gasly',
           'Alexander Albon','Esteban Ocon','Yuki Tsunoda','Daniel Ricciardo',
           'Kevin Magnussen','Zhou Guanyu','Valtteri Bottas','Logan Sargeant'],
}

def _seeded_rng(seed: int):
    return np.random.default_rng(int(abs(seed)) % (2**31))

def render():
    st.markdown('<div class="section-header">👤 Driver Profiles</div>', unsafe_allow_html=True)

    # Year selector
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        year = st.selectbox(
            "Season",
            list(reversed(range(2000, 2027))),
            key="driver_year",
            index=25,
        )

    drivers_in_year = YEAR_DRIVERS.get(year, YEAR_DRIVERS[2025])

    with col2:
        selected_driver = st.selectbox("Select Driver", drivers_in_year, key="driver_profile")

    with col3:
        compare_mode = st.checkbox("Compare with teammate", value=False, key="cmp_mode")

    st.markdown("---")

    # ── Driver bio / stats ──
    team = DRIVER_TO_TEAM.get(selected_driver, 'Unknown')
    drv_rng = _seeded_rng(hash(selected_driver + str(year)) % 2**31)
    wins     = int(drv_rng.integers(0, 14))
    podiums  = wins * 2 + int(drv_rng.integers(2, 20))
    poles    = int(drv_rng.integers(0, 10))
    fls      = int(drv_rng.integers(0, 10))
    chmp_pos = int(drv_rng.integers(1, 22))
    pts_yr   = int(drv_rng.integers(0, 460))
    quali_p  = round(drv_rng.normal(92.5, 1.2), 2)
    race_p   = round(quali_p + drv_rng.normal(0.5, 0.4), 2)
    consist  = round(drv_rng.uniform(82, 99), 1)
    tyre_m   = round(drv_rng.uniform(6.0, 9.8), 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Championship Pts", f"{pts_yr}", delta=f"#{chmp_pos} in {year}")
    with col2:
        st.metric("Wins", str(wins), delta=f"+{podiums - wins} podiums")
    with col3:
        st.metric("Poles", str(poles), delta=f"+{fls} fastest laps")
    with col4:
        st.metric("Quali Pace", f"{quali_p:.2f}s", delta="season avg")

    st.markdown("---")

    # ── Average speed & eco-rings ──
    st.markdown('<div class="section-header">📊 Performance Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    metrics = {
        col1: ('Avg Race Pace', f"{race_p:.2f}s",   '🟢'),
        col2: ('Consistency',   f"{consist}%",        '🟢'),
        col3: ('Tyre Mgmt',     f"{tyre_m}/10",       '🟢'),
        col4: ('Best Lap',      f"{quali_p - 0.5:.3f}s", '🟢'),
    }
    for col, (lbl, val, sts) in metrics.items():
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div style="font-size: 0.85rem; color:#888">{lbl}</div>
              <div style="font-size:1.5rem;font-weight:700;color:#ffd700;margin-top:.5rem">{val}</div>
              <div style="font-size:1.2rem;margin-top:.5rem">{sts}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Compare drivers if checkbox ON ──
    if compare_mode and year in YEAR_DRIVERS:
        teammates = [d for d in YEAR_DRIVERS[year] if d != selected_driver]
        if teammates:
            col_a, col_b = st.columns([1, 3])
            with col_a:
                cmp_drv = st.selectbox("Compare with", teammates, key="cmp_drv")
            with col_b:
                pass
            cmp_vals = [quali_p, race_p, consist, tyre_m]
            drv_b_rng = _seeded_rng(hash(cmp_drv + str(year)) % 2**31)
            cmp_vals2 = [
                round(drv_b_rng.normal(92.5, 1.2), 2),
                round(drv_b_rng.normal(92.5, 1.2) + 0.5, 2),
                round(drv_b_rng.uniform(82, 99), 1),
                round(drv_b_rng.uniform(6.0, 9.8), 1),
            ]
            cat_labels = ['Qualifying', 'Race Pace', 'Consistency', 'Tyre Mgmt', 'Cornering',
                          'Straight Speed', 'Overtaking', 'Defense']
            labels_fmt = ['Qualifying', 'Race Pace', 'Consistency', 'Tyre Mgmt',
                          'Cornering', 'Straight Speed', 'Overtaking', 'Defense']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=[cmp_vals[i] if i < 4 else drv_rng.integers(75, 100) for i in range(8)],
                theta=labels_fmt[:8], fill='toself', name=selected_driver,
                line=dict(color='#ffd700'), fillcolor='rgba(255,215,0,0.3)',
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[cmp_vals2[i] if i < 4 else drv_b_rng.integers(75, 100) for i in range(8)],
                theta=labels_fmt[:8], fill='toself', name=cmp_drv,
                line=dict(color='#00d2be'), fillcolor='rgba(0,210,190,0.2)',
            ))
            fig_radar.update_layout(
                template='plotly_dark', height=400,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                polar=dict(radialaxis=dict(range=[0,100],gridcolor='rgba(255,215,0,0.2)'),
                           angularaxis=dict(gridcolor='rgba(255,215,0,0.2)')),
                legend=dict(orientation='h'),
            )
            st.plotly_chart(fig_radar, config={'displayModeBar': False})
            st.markdown("---")

    # ── Radar chart ──
    st.markdown('<div class="section-header">🎯 Driver Strengths</div>', unsafe_allow_html=True)
    col1_rad, col2_rad = st.columns([1, 1], gap="large")
    rng_s = _seeded_rng(hash(selected_driver + str(year) + 'radar') % 2**31)
    cat_labels = ['Qualifying', 'Race Pace', 'Consistency', 'Tyre Mgmt',
                  'Cornering', 'Straight Speed', 'Overtaking', 'Defense']
    vals = [rng_s.integers(72, 99) for _ in range(8)]
    with col1_rad:
        fig = go.Figure(data=go.Scatterpolar(
            r=vals, theta=cat_labels[:8], fill='toself',
            name=selected_driver,
            line=dict(color='#ffd700'),
            fillcolor='rgba(255,215,0,0.3)'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(range=[0,100], showline=True, linewidth=2,
                                        gridcolor='rgba(255,215,0,0.2)'),
                       angularaxis=dict(gridcolor='rgba(255,215,0,0.2)')),
            template='plotly_dark', height=400,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
        )
        st.plotly_chart(fig, config={'displayModeBar': False})

    with col2_rad:
        st.markdown("**Sector Performance**")
        rng_sec = _seeded_rng(hash(str(year) + selected_driver) % 2**31)
        sec_df = pd.DataFrame({
            'Sector':  ['S1', 'S2', 'S3'],
            'Best Time': [f"{29.1+rng_sec.random():.3f}s",
                           f"{37.2+rng_sec.random():.3f}s",
                           f"{23.8+rng_sec.random():.3f}s"],
            'Avg Speed': [f"{145+rng_sec.integers(0,6)} km/h",
                           f"{182+rng_sec.integers(0,10)} km/h",
                           f"{158+rng_sec.integers(0,7)} km/h"],
        })
        st.dataframe(sec_df, hide_index=True)

        st.markdown("**Season Form (Selected Races)**")
        rng_f = _seeded_rng(hash(str(year) + selected_driver + 'form') % 2**31)
        races_tracked = max(10, len(drivers_in_year) if year in YEAR_DRIVERS else 10)
        form_df = pd.DataFrame({
            'Race #':  list(range(1, min(11, races_tracked + 1))),
            'Result':  rng_f.integers(1, 22, 10).tolist(),
            'Points':  [rng_f.integers(0, 26) for _ in range(10)],
            'Grid':    rng_f.integers(1, 22, 10).tolist(),
        })
        st.dataframe(form_df, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📈 Telemetry Analysis</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([1, 1], gap="large")
    lap_data = get_driver_lap_data(year, selected_driver)
    rng_telem = _seeded_rng(hash(selected_driver + str(year) + 'telem') % 2**31)
    dist_arr = np.linspace(0, 5451, 400)
    speed_arr = 200 + 50 * np.sin(dist_arr / 520) + rng_telem.normal(0, 3, len(dist_arr))
    throttle_arr = 50 + 40 * np.sin(dist_arr / 420)
    brake_arr = 40 * (1 - np.cos(dist_arr / 420))

    with col_t1:
        st.markdown(f"**Speed Trace – Best Lap ({selected_driver})**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=speed_arr,
            mode='lines', name='Speed',
            line=dict(color='#ffd700', width=2),
            fill='tozeroy', fillcolor='rgba(255,215,0,0.08)',
        ))
        fig.update_layout(
            xaxis_title='Distance (m)', yaxis_title='Speed (km/h)',
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, config={'displayModeBar': False})

    with col_t2:
        st.markdown(f"**Throttle & Brake ({selected_driver})**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_arr, y=throttle_arr,
            mode='lines', name='Throttle %',
            fill='tozeroy', line=dict(color='#00ff00', width=2),
            fillcolor='rgba(0,255,0,0.15)'
        ))
        fig.add_trace(go.Scatter(
            x=dist_arr, y=-brake_arr,
            mode='lines', name='Brake %',
            fill='tozeroy', line=dict(color='#ff4444', width=2),
            fillcolor='rgba(255,68,68,0.15)'
        ))
        fig.update_layout(
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, config={'displayModeBar': False})

    st.markdown("---")
    st.markdown('<div class="section-header">📰 Recent News & Facts</div>', unsafe_allow_html=True)
    rng_n = _seeded_rng(hash(selected_driver + str(year) + 'news') % 2**31)
    races = get_races(year)
    race_hint = races[rng_n.integers(0, len(races))] if races else ''
    headlines = [
        f"{selected_driver} tops FP1 at {race_hint}" if race_hint else
        f"{selected_driver} leads pre-season testing in {year}",
        f"Team principal praises {selected_driver}'s adaptation to new PU",
        f"{selected_driver} extends contract through {year + 2}",
        f"Strategy Analysis: {selected_driver}'s tyre management in focus for next round",
        f"Fastest sector: {selected_driver} sets benchmark in sector 2",
    ]
    for hl in headlines[:rng_n.integers(2, 6)]:
        st.markdown(f"> 📰 {hl}")

    # ── NEW: 3D Driver Performance Evolution ──
    st.markdown("---")
    st.markdown('<div class="section-header">📈 3D Driver Performance Evolution</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_perf = _seeded_rng(hash(selected_driver + str(year) + 'perf_evo') % 2**31)
        
        # Create performance data over a simulated season
        races_in_year = get_races(year)
        num_races = min(len(races_in_year), 16)  # Limit to 16 races for clarity
        
        performance_data = []
        for race_idx, race_name in enumerate(races_in_year[:num_races]):
            # Simulate performance trends throughout the season
            base_performance = s_perf.uniform(70, 95)
            # Add some race-to-race variability and seasonal trend
            race_variation = s_perf.normal(0, 8)
            seasonal_trend = (race_idx / num_races) * s_perf.uniform(-5, 10)  # Slope of improvement/decline
            consistency = s_perf.uniform(0.7, 0.95)  # How consistent the driver is
            
            # Calculate final performance score
            perf_score = base_performance + race_variation + seasonal_trend
            perf_score = max(40, min(100, perf_score))  # Keep in bounds
            
            performance_data.append({
                'Race_Number': race_idx + 1,
                'Race_Name': race_name,
                'Performance_Score': perf_score,
                'Consistency': consistency,
                'Points_Potential': perf_score * 0.8 + s_perf.integers(0, 20)  # Rough points estimate
            })
        
        df_perf_evo = pd.DataFrame(performance_data)
        
        fig_perf_evo = go.Figure(data=go.Scatter3d(
            x=df_perf_evo['Race_Number'],
            y=df_perf_evo['Performance_Score'],
            z=df_perf_evo['Consistency'],
            mode='markers+lines',
            marker=dict(
                size=6,
                color=df_perf_evo['Points_Potential'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Points Potential")
            ),
            text=df_perf_evo['Race_Name'],
            line=dict(color='#ffd700', width=3)
        ))
        
        fig_perf_evo.update_layout(
            title='Driver Performance Evolution Through Season (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Race Number',
                yaxis_title='Performance Score (0-100)',
                zaxis_title='Consistency Factor',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_perf_evo)

    # ── NEW: 3D Skill Comparison Matrix ──
    st.markdown("---")
    st.markdown('<div class="section-header">⚖️ 3D Skill Comparison Matrix</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_skill = _seeded_rng(hash(selected_driver + str(year) + 'skill_cmp') % 2**31)
        
        # Compare selected driver with teammates and rivals
        teammates = [d for d in YEAR_DRIVERS[year] if d != selected_driver][:3]  # Top 3 teammates
        rivals = [d for d in YEAR_DRIVERS[year] if d != selected_driver and d not in teammates][:3]  # Top 3 rivals
        comparison_drivers = [selected_driver] + teammates + rivals
        
        skills = ['Qualifying', 'Race Pace', 'Consistency', 'Tire Management', 'Overtaking', 'Defending']
        skill_data = []
        
        for driver in comparison_drivers:
            driver_hash = hash(driver + str(year))
            drv_rng = _seeded_rng(driver_hash % 2**31)
            
            # Base skill level varies by driver
            base_skill = drv_rng.uniform(60, 90)
            
            for skill_idx, skill in enumerate(skills):
                # Each skill has some variation around base with specialization
                skill_variation = drv_rng.normal(0, 7)
                # Specialization: some drivers better at specific skills
                if skill == 'Qualifying' and driver == selected_driver:
                    specialization = drv_rng.uniform(5, 15)  # Selected driver might be better
                elif skill == 'Race Pace' and driver in teammates:
                    specialization = drv_rng.uniform(-5, 5)  # Teammates similar
                else:
                    specialization = drv_rng.uniform(-8, 8)
                
                final_skill = base_skill + skill_variation + specialization
                final_skill = max(30, min(100, final_skill))  # Keep in bounds
                
                skill_data.append({
                    'Driver': driver,
                    'Skill': skill,
                    'Skill_Score': final_skill,
                    'Is_Selected': driver == selected_driver,
                    'Skill_Index': skill_idx
                })
        
        df_skill_cmp = pd.DataFrame(skill_data)
        
        fig_skill_cmp = go.Figure()
        
        # Add scatter points for each skill instead of bars
        for skill_idx, skill in enumerate(skills):
            skill_df = df_skill_cmp[df_skill_cmp['Skill'] == skill]
            # Color selected driver differently
            colors = ['#ffd700' if is_sel else '#1f77b4' for is_sel in skill_df['Is_Selected']]
            
            fig_skill_cmp.add_trace(go.Scatter3d(
                x=skill_df['Driver'],
                y=[skill] * len(skill_df),
                z=skill_df['Skill_Score'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors,
                    symbol='circle',
                    line=dict(width=1, color='white')
                ),
                name=skill
            ))
        
        fig_skill_cmp.update_layout(
            title='3D Skill Comparison: Selected Driver vs Teammates & Rivals',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Driver',
                yaxis_title='Skill Type',
                zaxis_title='Skill Score (0-100)',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_skill_cmp)

    # ── NEW: 3D Lap Time Distribution Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">⏱️ 3D Lap Time Distribution Analysis</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_lap = _seeded_rng(hash(selected_driver + str(year) + 'lap_dist') % 2**31)
        
        # Simulate lap time data for analysis
        lap_data = []
        num_laps = 50  # Analyze a typical stint
        
        base_lap_time = s_lap.uniform(88, 105)  # Base lap time for this driver/car combo
        
        for lap in range(1, num_laps + 1):
            # Factors affecting lap time:
            # 1. Fuel load (heavier early in stint = slower)
            fuel_effect = (num_laps - lap) / num_laps * s_lap.uniform(0, 1.8)
            # 2. Tire degradation (worsens throughout stint)
            tire_deg = (lap - 1) / num_laps * s_lap.uniform(0, 2.2)
            # 3. Random variation (traffic, mistakes, etc.)
            random_var = s_lap.normal(0, 0.3)
            # 4. Learning/rhythm factor (gets better then worse)
            rhythm_factor = np.sin(lap / num_laps * np.pi) * s_lap.uniform(0, 0.4)
            
            lap_time = base_lap_time + fuel_effect + tire_deg + random_var + rhythm_factor
            lap_time = max(base_lap_time * 0.92, lap_time)  # Don't get unrealistically fast
            
            lap_data.append({
                'Lap_Number': lap,
                'Lap_Time': lap_time,
                'Fuel_Load_Effect': fuel_effect,
                'Tire_Degradation': tire_deg,
                'Random_Variation': abs(random_var),
                'Stint_Progress': lap / num_laps
            })
        
        df_lap_dist = pd.DataFrame(lap_data)
        
        fig_lap_dist = go.Figure(data=go.Scatter3d(
            x=df_lap_dist['Lap_Time'],
            y=df_lap_dist['Fuel_Load_Effect'],
            z=df_lap_dist['Tire_Degradation'],
            mode='markers',
            marker=dict(
                size=4,
                color=df_lap_dist['Lap_Number'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Lap Number")
            ),
            text=df_lap_dist.apply(lambda row: f"Lap {row['Lap_Number']}<br>Time: {row['Lap_Time']:.3f}s", axis=1)
        ))
        
        fig_lap_dist.update_layout(
            title='Lap Time vs Fuel Effect vs Tire Degradation (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Lap Time (s)',
                yaxis_title='Fuel Load Effect (s)',
                zaxis_title='Tire Degradation (s)',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_lap_dist)

    # ── NEW: 3D Championship Probability Map ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏆 3D Championship Probability Map</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_champ = _seeded_rng(hash(selected_driver + str(year) + 'champ_prob') % 2**31)
        
        # Create a 3D visualization of championship chances based on various factors
        champ_data = []
        
        # Simulate different scenarios throughout the season
        races_in_year = get_races(year)
        num_scenarios = min(len(races_in_year), 12)  # Key race points
        
        for scenario_idx, race_name in enumerate(races_in_year[:num_scenarios]):
            # Factors affecting championship probability:
            points_scored = s_champ.integers(0, 26)  # Points for this race
            consistency_factor = s_champ.uniform(0.7, 0.98)  # How consistent performer
            pressure_handling = s_champ.uniform(0.6, 0.95)  # How well under pressure
            # Calculate championship probability (simplified)
            champ_prob = (points_scored / 26) * consistency_factor * pressure_handling * 100
            champ_prob = max(0, min(100, champ_prob))
            
            champ_data.append({
                'Scenario_Index': scenario_idx + 1,
                'Race_Name': race_name,
                'Points_Scored': points_scored,
                'Championship_Probability': champ_prob,
                'Consistency_Factor': consistency_factor,
                'Pressure_Handling': pressure_handling
            })
        
        df_champ = pd.DataFrame(champ_data)
        
        fig_champ = go.Figure(data=go.Scatter3d(
            x=df_champ['Points_Scored'],
            y=df_champ['Championship_Probability'],
            z=df_champ['Consistency_Factor'],
            mode='markers+text',
            marker=dict(
                size=8,
                color=df_champ['Pressure_Handling'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Pressure Handling")
            ),
            text=df_champ['Race_Name'],
            textposition="top center"
        ))
        
        fig_champ.update_layout(
            title='Championship Probability Analysis (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Points Scored',
                yaxis_title='Championship Probability (%)',
                zaxis_title='Consistency Factor',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_champ)

    # ── NEW: 3D Driver Personality & Style Radar ──
    st.markdown("---")
    st.markdown('<div class="section-header">🎭 3D Driver Personality & Style Analysis</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_pers = _seeded_rng(hash(selected_driver + str(year) + 'personality') % 2**31)
        
        # Analyze driver personality traits and driving style
        traits = ['Aggressiveness', 'Consistency', 'Adaptability', 'Race Craft', 
                 'Qualifying Skill', 'Tire Management', 'Feedback', 'Mental Strength']
        
        personality_data = []
        for trait_idx, trait in enumerate(traits):
            # Base trait level with some randomization
            base_trait = s_pers.uniform(40, 90)
            # Add some variability
            trait_variation = s_pers.normal(0, 8)
            final_trait = base_trait + trait_variation
            final_trait = max(20, min(100, final_trait))  # Keep in reasonable bounds
            
            personality_data.append({
                'Trait': trait,
                'Trait_Score': final_trait,
                'Trait_Index': trait_idx,
                'Development_Potential': s_pers.uniform(0.6, 0.95),  # Room for growth
                'Consistency': s_pers.uniform(0.7, 0.98)  # How consistent this trait is
            })
        
        df_personality = pd.DataFrame(personality_data)
        
        fig_personality = go.Figure(data=go.Scatter3d(
            x=df_personality['Trait_Score'],
            y=df_personality['Development_Potential'],
            z=df_personality['Consistency'],
            mode='markers+text',
            marker=dict(
                size=8,
                color=df_personality['Trait_Score'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Trait Score")
            ),
            text=df_personality['Trait'],
            textposition="top center"
        ))
        
        fig_personality.update_layout(
            title='Driver Personality & Style Analysis (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Trait Score (0-100)',
                yaxis_title='Development Potential',
                zaxis_title='Trait Consistency',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_personality)

    # ═══════════════════════════════════════════════════
    #  NEW VISUALISATIONS  IDs 1-10  (driver_profiles.py)
    # ═══════════════════════════════════════════════════

    # ─── NEW ID 1 · Driver Aggression Index ───────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">⚡ Driver Aggression Index</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_agg = _seeded_rng(hash(selected_driver + str(year) + 'aggression') % 2**31)
        agg_score = float(np.clip(s_agg.normal(68, 18), 0, 100))
        g_color = '#00d2be' if agg_score < 50 else '#ffd700' if agg_score < 75 else '#ff4444'
        fig_agg = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(agg_score, 1),
            title={'text': f"Aggression Score — {selected_driver}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': g_color},
                'steps': [
                    {'range': [0, 50],  'color': "rgba(0,210,190,0.3)"},
                    {'range': [50, 75], 'color': "rgba(255,215,0,0.3)"},
                    {'range': [75, 100],'color': "rgba(255,68,68,0.3)"},
                ],
                'threshold': {'line': {'color': "white", 'width': 2},
                              'thickness': 0.75, 'value': float(np.clip(s_agg.normal(72, 12), 0, 100))},
            },
        ))
        fig_agg.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)',
                               template='plotly_dark', margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_agg, config={'displayModeBar': False})
        if agg_score >= 75:
            st.caption("⚠️ High aggression — more aggressive qualifying and racecraft moves expected.")
        elif agg_score >= 50:
            st.caption("⚖️ Balanced aggression — measured but decisive overtaking.")
        else:
            st.caption("🛡️ Low aggression — conservative wheel-to-wheel approach.")

    # ─── NEW ID 2 · Overtake Success Network ──────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🕸️ Overtake Success Network</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_net = _seeded_rng(hash(selected_driver + str(year) + 'overtake_net') % 2**31)
        adj   = {d: 0.0 for d in YEAR_DRIVERS[year][:14]}
        frac  = s_net.random()
        if selected_driver in adj:
            adj.pop(selected_driver)
        for k in adj:
            s_net.local_state
        nodes_plot = [selected_driver] + list(adj.keys())
        n = len(nodes_plot)
        raw_w = np.clip(s_net.normal(0, 1.5, (n, n)), 0, None)
        for i in range(n):
            raw_w[i, i] = 0
        row_s = raw_w.sum(axis=1, keepdims=True)
        row_s[row_s == 0] = 1.0
        avail = raw_w / row_s
        connects = min(5, n - 1)
        top_idx = np.argsort(-avail[0])[1:1 + connects]
        edge_x, edge_y, edge_c = [], [], []
        s_min, s_max = 0.3, 1.0
        for tx in top_idx:
            ew = float(avail[0, tx])
            if ew < s_min:
                continue
            norm_w = (ew - s_min) / max(s_max - s_min, 0.01)
            ew_norm = s_min + norm_w * (s_max - s_min)
            edge_x += [0, tx, None]
            edge_y += [0, tx, None]
            edge_c.append(norm_w)
            edge_c.append(norm_w)
            edge_c.append(None)
        edge_c = [c for c in edge_c if c is not None]
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        radius = 1.0
        nx_v = radius * np.cos(angles)
        ny_v = radius * np.sin(angles)
        fig_net = go.Figure()
        if edge_x:
            fig_net.add_trace(go.Scatter(
                x=edge_x, y=edge_y, mode='lines',
                line=dict(width=[max(0.5, w * 5) for w in edge_c] + [0.5] * (len(edge_x) // 3),
                          color='rgba(255,215,0,0.5)', shape='spline'),
                name='', hoverinfo='skip', showlegend=False,
            ))
        fig_net.add_trace(go.Scatter(
            x=nx_v.tolist(), y=ny_v.tolist(),
            mode='markers+text',
            marker=dict(size=[20] + [12] * (n - 1), color=['#ffd700'] + ['#1f77b4'] * (n - 1),
                        line=dict(width=2, color='white'), opacity=0.95),
            text=[nodes_plot[0]] + ['' if i > 3 else nodes_plot[i] for i in range(1, n)],
            textposition="top center", name='', hoverinfo='skip', showlegend=False,
        ))
        fig_net.update_layout(
            template='plotly_dark', height=360, width=500,
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor='x', scaleratio=1),
            margin=dict(l=20, r=20, t=30, b=20),
            title=f"Overtake Avatar — {selected_driver} ({year}) → Top {connects} Rivals",
        )
        st.plotly_chart(fig_net, config={'displayModeBar': False})
        st.caption("Node size ∝ overtake success vs selected driver  ·  edge thickness ∝ win-rate delta")

    # ─── NEW ID 3 · Corner Entry vs Exit Speed ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 Corner Entry vs Exit Speed</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_ce = _seeded_rng(hash(selected_driver + str(year) + 'corner_entry') % 2**31)
        n_c  = 14
        entry_spd = np.clip(s_ce.normal(162, 24, n_c), 90, 230)
        exit_norm  = s_ce.normal(0, 8, n_c)
        exit_spd   = entry_spd * (1 + exit_norm / 100)
        accel      = np.clip(exit_spd - entry_spd, 0, 90)
        c_label    = [f"Corner {i + 1}" for i in range(n_c)]
        fig_ce = go.Figure()
        max_acc = float(accel.max()) if len(accel) else 1.0
        fig_ce.add_trace(go.Scatter(
            x=entry_spd, y=exit_spd, mode='markers+text',
            text=c_label, textposition='top center',
            marker=dict(size=10, color=float(accel[0]) / max(max_acc, 1) * np.arange(n_c) if n_c > 0 else accel,
                        colorscale='Viridis', showscale=True,
                        colorbar=dict(title="Acceleration", x=1.02)),
            name=selected_driver,
        ))
        mn, mx = float(min(entry_spd.min(), exit_spd.min()) - 10), float(max(entry_spd.max(), exit_spd.max()) + 10)
        fig_ce.add_shape(type='line', x0=mn, y0=mn, x1=mx, y1=mx,
                         line=dict(color='rgba(255,255,255,0.3)', width=1.5, dash='dash'))
        fig_ce.update_layout(
            xaxis_title='Entry Speed (km/h)', yaxis_title='Exit Speed (km/h)',
            template='plotly_dark', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Corner Performance — {selected_driver} ({year})",
        )
        fig_ce.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_ce.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_ce, config={'displayModeBar': False})

    # ─── NEW ID 4 · Driver Reaction Time Analysis ─────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🧠 Driver Reaction Time Analysis</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_rt  = _seeded_rng(hash(selected_driver + str(year) + 'reaction') % 2**31)
        ev_rt = float(np.clip(s_rt.normal(0.215, 0.032), 0.13, 0.38))
        cl_rt = float(np.clip(s_rt.normal(0.248, 0.045), 0.16, 0.55))
        sc_rt = float(np.clip(s_rt.normal(0.268, 0.052), 0.18, 0.62))
        m_rt  = float(np.clip(s_rt.normal(0.225, 0.038), 0.15, 0.45))
        vp_df = pd.DataFrame({
            'Condition': ['Green Light', 'Yellow Flag', 'Safety Car', 'Mid-Race Incident'],
            'Reaction Time (s)': [ev_rt, cl_rt, sc_rt, m_rt],
            'Driver': [selected_driver] * 4,
        })
        fig_rt = px.violin(
            pd.concat([vp_df, pd.DataFrame({
                'Condition': [c for c in vp_df['Condition']],
                'Reaction Time (s)': [float(np.clip(s_rt.normal(v, abs(s_rt.normal(0, 0.03))), 0.10, 0.70)) for v in [ev_rt, cl_rt, sc_rt, m_rt]],
                'Driver': ['Grid Average'] * 4,
            })], ignore_index=True),
            x='Condition', y='Reaction Time (s)', color='Driver', box=True, points='suspensionoutliers',
            template='plotly_dark', height=360, violinmode='overlay',
        )
        fig_rt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)')
        st.plotly_chart(fig_rt, config={'displayModeBar': False})
        fastest = min(ev_rt, cl_rt, sc_rt, m_rt)
        cond    = ['Green Light','Yellow Flag','Safety Car','Mid-Race Incident'][[ev_rt, cl_rt, sc_rt, m_rt].index(fastest)]
        st.caption(f"🏎️ Best: {fastest:.3f}s in **{cond}** — Average Grid: {round((ev_rt + cl_rt + sc_rt + m_rt) / 4, 3):.3f}s")

    # ─── NEW ID 5 · Tyre Preservation Efficiency ──────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🛞 Tyre Preservation Efficiency</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_te  = _seeded_rng(hash(selected_driver + str(year) + 'tyre_eff') % 2**31)
        tp_bm = np.clip(s_te.normal(1.11, 0.085), 0.91, 1.34)
        tp_rc = np.clip(s_te.normal(1.07, 0.072), 0.88, 1.28)
        tp_so = np.clip(s_te.normal(1.04, 0.058), 0.85, 1.22)
        compounds = ['Medium', 'Racing Soft', 'Soft']
        base_pace = [93.0, 91.5, 90.8]
        deg_rates = [0.065, 0.095, 0.135]
        n_laps_eff = 42
        fig_te = go.Figure()
        tpe_colors = ['#ffd700', '#1f77b4', '#ff4444']
        for idx, comp in enumerate(compounds):
            av  = base_pace[idx]
            dr  = deg_rates[idx]
            eff = [tp_bm, tp_rc, tp_so][idx]
            deg = dr * np.log(np.arange(1, n_laps_eff + 1)) / np.log(n_laps_eff)
            laps_arr = np.arange(n_laps_eff)
            moved  = (laps_arr * dr * 0.15) / 2
            noise  = s_te.normal(0, 0.18, n_laps_eff)
            raw    = av + deg + moved + noise
            norm_r = (laps_arr * dr) / n_laps_eff
            new_laps = raw - norm_r * (eff - 1) * dr
            lbl = f"{comp} — TPE={eff:.2f}x  ·  Deg={dr:.3f}s/lap"
            fig_te.add_trace(go.Scatter(
                x=np.arange(1, n_laps_eff + 1), y=new_laps.tolist(),
                mode='lines', name=lbl, line=dict(color=tpe_colors[idx], width=2),
            ))
        fig_te.update_layout(
            xaxis_title='Lap in Stint', yaxis_title='Lap Time (s)', height=360,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top', bgcolor='rgba(0,0,0,0.4)', font=dict(size=10)),
        )
        fig_te.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_te.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_te, config={'displayModeBar': False})

    # ─── NEW ID 6 · 3D Driver Focus Map ──────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🧭 3D Driver Focus Map</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_fm  = _seeded_rng(hash(selected_driver + str(year) + 'focus_map') % 2**31)
        fx_lo, fx_hi = 0.0, 1.0
        fy_lo, fy_hi = 0.0, 1.0
        fx = np.linspace(fx_lo, fx_hi, 60)
        fy = np.linspace(fy_lo, fy_hi, 60)
        X, Y = np.meshgrid(fx, fy)
        pks   = [s_fm.uniform(0.1, 0.9) for _ in range(4)]
        x_ctr = s_fm.uniform(0.35, 0.65)
        y_ctr = s_fm.uniform(0.30, 0.70)
        Z_base = np.exp(-((X - x_ctr) ** 2 + (Y - y_ctr) ** 2) * 4.0) * 0.80
        for (px, py) in pks:
            amp  = s_fm.uniform(0.12, 0.35) * (0.60 + s_fm.random() * 0.40)
            dist = np.sqrt((X - px) ** 2 + (Y - py) ** 2)
            Z_base = Z_base + amp * np.exp(-dist ** 2 * 8.0)
        Z_s  = np.clip(Z_base * 0.98 + s_fm.normal(0, 0.012, X.shape), 0, 1)
        fig_fm = go.Figure(data=[go.Surface(
            x=X, y=Y, z=Z_s, colorscale='Viridis', opacity=0.90,
            showscale=True, colorbar=dict(title="Focus"),
        )])
        fig_fm.update_layout(
            template='plotly_dark', height=500,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Driver Focus Map — {selected_driver} ({year})",
            scene=dict(xaxis_title='Focus X', yaxis_title='Focus Y', zaxis_title='Intensity',
                        bgcolor='rgba(0,0,0,0)'),
        )
        st.plotly_chart(fig_fm, config={'displayModeBar': False})

    # ─── NEW ID 7 · 3D Racing Line Deviation ─────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📐 3D Racing Line Deviation</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_rl = _seeded_rng(hash(selected_driver + str(year) + 'racing_line') % 2**31)
        N_RL = 500
        tr_s  = _seeded_rng(hash('track_shape' + str(year)) % 2**31)
        K_T   = 4.0
        K_S   = 6.5
        t_r   = np.linspace(0, 2 * np.pi * 1.6, N_RL)
        tx_r = K_T * (np.sin(t_r) + 0.28 * np.sin(2 * t_r) - 0.09 * np.sin(3 * t_r))
        ty_r = K_S * (np.cos(t_r) - 0.12 * np.cos(2 * t_r) + 0.08 * np.cos(4 * t_r))
        tz_r = 0.55 * np.sin(t_r) + 0.35 * np.cos(2 * t_r)
        gx_r, gy_r = np.gradient(tx_r), np.gradient(ty_r)
        gl_r = np.sqrt(gx_r ** 2 + gy_r ** 2)
        gl_r[gl_r == 0] = 1.0
        nx_r, ny_r = -gy_r / gl_r, gx_r / gl_r
        HW_RL  = 2.80
        amp_dv = np.clip(s_rl.normal(0, 1.0, N_RL), -HW_RL, HW_RL)
        rlv_x = tx_r + nx_r * amp_dv
        rlv_y = ty_r + ny_r * amp_dv
        rlv_z = tz_r + 0.45 * amp_dv / HW_RL
        dev_col = np.abs(amp_dv)
        fig_rl = go.Figure()
        fig_rl.add_trace(go.Scatter3d(
            x=tx_r.tolist(), y=ty_r.tolist(), z=tz_r.tolist(),
            mode='lines', name='Optimal Line',
            line=dict(color='#888888', width=3, dash='dash'), hoverinfo='skip',
        ))
        fig_rl.add_trace(go.Scatter3d(
            x=rlv_x.tolist(), y=rlv_y.tolist(), z=rlv_z.tolist(),
            mode='lines', name=f'{selected_driver} Actual',
            line=dict(color=float(dev_col[0]), colorscale='RdBu',
                      width=5, cmin=float(dev_col.min()), cmax=float(dev_col.max())),
            text=[f"Dev: {v:.2f} m" for v in amp_dv],
        ))
        fig_rl.update_layout(
            template='plotly_dark', height=520,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Racing Line Deviation — {selected_driver} vs Optimal ({year})",
            scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                        aspectmode='data', bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=0, r=0, t=36, b=0),
        )
        st.plotly_chart(fig_rl, config={'displayModeBar': False})

    # ─── NEW ID 8 · Driver Confidence Momentum ────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Driver Confidence Momentum</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_cm = _seeded_rng(hash(selected_driver + str(year) + 'conf_momentum') % 2**31)
        rs = get_races(year)
        n_r = min(22, len(rs))
        r_names = rs[:n_r]
        prev_pct = s_cm.integers(25, 80)
        conf_arr = []
        for ri2 in range(n_r):
            drift  = s_cm.normal(0, 9)
            bounce = (s_cm.random() - 0.5) * 16
            if ri2 == 0:
                conf_arr.append(float(np.clip(prev_pct + drift, 0, 100)))
            else:
                conf_arr.append(float(np.clip(conf_arr[-1] + drift * 0.55 + bounce, 0, 100)))
        df_cm = pd.DataFrame({
            'Race_Index': list(range(1, n_r + 1)),
            'Confidence': conf_arr,
            'Confidence_Max': [min(100.0, c + s_cm.uniform(5, 22)) for c in conf_arr],
            'Confidence_Min': [max(0.0, c - s_cm.uniform(5, 22)) for c in conf_arr],
        })
        fig_cm = go.Figure()
        fig_cm.add_trace(go.Scatter(
            x=df_cm['Race_Index'].tolist(), y=df_cm['Confidence_Max'].tolist(),
            mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip',
        ))
        fig_cm.add_trace(go.Scatter(
            x=df_cm['Race_Index'].tolist(), y=df_cm['Confidence_Min'].tolist(),
            mode='lines', name='Confidence Band',
            line=dict(width=0), fill='tonexty',
            fillcolor='rgba(255,215,0,0.22)', hoverinfo='skip',
        ))
        fig_cm.add_trace(go.Scatter(
            x=df_cm['Race_Index'].tolist(), y=df_cm['Confidence'].tolist(),
            mode='lines+markers', name='Confidence', line=dict(color='#ffd700', width=2.5),
            marker=dict(size=6),
        ))
        fig_cm.update_layout(
            xaxis_title='Race Number', yaxis_title='Confidence (%)', height=360,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            hovermode='x unified', title=f"Confidence Momentum — {selected_driver} ({year})",
        )
        fig_cm.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_cm.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_cm, config={'displayModeBar': False})

    # ─── NEW ID 9 · Qualifying Pressure Performance ──────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🟣 Qualifying Pressure Performance</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_qp = _seeded_rng(hash(selected_driver + str(year) + 'qual_press') % 2**31)
        sess_df_list = []
        bub_sessions = ['Q1 Early', 'Q1 Late', 'Q2 Early', 'Q2 Late', 'Q3']
        base_qs = 92.0
        for si3, ssn in enumerate(bub_sessions):
            rows_b = []
            for _i3 in range(9):
                sl   = float(s_qp.normal(0, 0.75))
                prs  = float(s_qp.normal(si3 * 0.22, 0.10))
                tm   = float(np.clip(base_qs + sl * 0.18 + prs * 0.12, 88.0, 97.0))
                rows_b.append({'Session': ssn, 'Lap_Time': tm, 'Pressure': prs})
            sess_df_list.append(pd.DataFrame(rows_b))
        df_qp = pd.concat(sess_df_list, ignore_index=True)
        df_qp['Session_cat'] = pd.Categorical(df_qp['Session'], categories=bub_sessions, ordered=True)
        df_qp = df_qp.sort_values('Session_cat')
        qp_color_map = {s: r for s, r in zip(bub_sessions,
            ['#4ecdc4','#45b7d1','#1f77b4','#3671C6','#ffd700'])}
        df_qp['Color'] = df_qp['Session'].map(qp_color_map)
        fig_qp = go.Figure()
        for _, (_, sub_qp) in enumerate(df_qp.groupby('Session_cat', sort=False)):
            cc = qp_color_map.get(sub_qp['Session_cat'].iloc[0], '#ffffff')
            fig_qp.add_trace(go.Scatter(
                x=sub_qp['Lap_Time'], y=sub_qp['Pressure'],
                mode='markers', name=sub_qp['Session_cat'].iloc[0],
                marker=dict(size=9, color=cc, opacity=0.82, line=dict(width=1, color='white')),
                customdata=sub_qp['Pressure'] * 100,
                hovertemplate='Session: %{fullData.name}<br>'
                               'Lap Time: %{x:.3f}s<br>'
                               'Pressure: %{customdata:.0f}%<extra></extra>',
            ))
        fig_qp.update_layout(
            xaxis_title='Lap Time (s)', yaxis_title='Subjective Pressure (0-1)', height=420,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Qualifying Pressure — {selected_driver} ({year})",
            legend=dict(x=0.02, y=0.98, xanchor='left', yanchor='top', bgcolor='rgba(0,0,0,0.4)'),
        )
        fig_qp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig_qp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_qp, config={'displayModeBar': False})

    # ─── NEW ID 10 · Wet vs Dry Pace Comparison ─────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">🌧️ Wet vs Dry Pace Comparison</div>', unsafe_allow_html=True)
    if year in YEAR_DRIVERS:
        s_wd = _seeded_rng(hash(selected_driver + str(year) + 'wet_dry') % 2**31)
        races_list = rs
        w_r = [r for r in races_list if 'Wet' in r or 'Monaco' in r or 'Belgian' in r or 'British' in r]
        if len(w_r) < 2:
            w_r = races_list[:5]
        n_wr = min(8, len(w_r))
        wt = np.clip(s_wd.normal(94.2, 2.1, n_wr), 89, 104)
        dt = np.clip(s_wd.normal(91.8, 1.6, n_wr), 87, 99)
        wet_rrace = w_r[:n_wr]
        df_wd = pd.DataFrame({'Race': wet_rrace,
                              'Wet Lap (s)': np.round(wt, 3).tolist(),
                              'Dry Lap (s)': np.round(dt, 3).tolist()})
        dt_s = float(np.mean(dt))
        wt_s = float(np.mean(wt))
        fig_wd = go.Figure()
        fig_wd.add_trace(go.Bar(
            name='Dry Lap', x=wet_rrace, y=df_wd['Dry Lap (s)'].tolist(),
            marker=dict(color='rgba(255,215,0,0.82)', line=dict(width=1.5, color='white')),
            text=[f"{v:.2f}s" for v in df_wd['Dry Lap (s)']], textposition='outside',
        ))
        fig_wd.add_trace(go.Bar(
            name='Wet Lap', x=wet_rrace, y=df_wd['Wet Lap (s)'].tolist(),
            marker=dict(color='rgba(30,144,255,0.82)', line=dict(width=1.5, color='white')),
            text=[f"{v:.2f}s" for v in df_wd['Wet Lap (s)']], textposition='outside',
        ))
        fig_wd.add_hline(y=dt_s, line_dash='dash', line_color='rgba(255,215,0,0.5)',
                          annotation_text=f"Avg Dry: {dt_s:.2f}s", annotation_position='top right')
        fig_wd.add_hline(y=wt_s, line_dash='dash', line_color='rgba(30,144,255,0.5)',
                          annotation_text=f"Avg Wet: {wt_s:.2f}s", annotation_position='bottom right')
        fig_wd.update_layout(
            barmode='group', xaxis_title='Race', yaxis_title='Lap Time (s)', height=380,
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            title=f"Wet vs Dry Pace — {selected_driver} ({year})",
            legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top', bgcolor='rgba(0,0,0,0.4)'),
        )
        fig_wd.update_xaxes(showgrid=False, tickangle=-35)
        fig_wd.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig_wd, config={'displayModeBar': False})
        gap_wd = wt_s - dt_s
        if gap_wd > 4.0:
            st.caption(f"⚠️ Significant wet-weather delta: **+{gap_wd:.2f}s/lap** slower in wet conditions.")
        elif gap_wd > 2.0:
            st.caption(f"⚖️ Moderate wet-weather delta: **+{gap_wd:.2f}s/lap** — adaptable in rain.")
        else:
            st.caption(f"🟢 Elite wet weather: only **+{gap_wd:.2f}s/lap** slower in wet conditions!")


def race_in_year(yr: int, race: str) -> bool:
    from data_model import get_races
    return race in get_races(yr)
