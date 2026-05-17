import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.insert(0, '.')
from data_model import get_races, get_race_results, DRIVER_COLORS

# ─── Circuit registry ───
CIRCUIT_INFO = {
    'Bahrain GP':          ('Bahrain International Circuit', 'Bahrain',     5.412, 57),
    'Australian GP':       ('Albert Park Circuit',          'Australia',   5.278, 58),
    'Malaysian GP':        ('Sepang Circuit',                'Malaysia',    5.543, 56),
    'Chinese GP':          ('Shanghai International Circuit','China',       5.451, 56),
    'Spanish GP':          ('Circuit de Barcelona',          'Spain',       4.655, 66),
    'Monaco GP':           ('Circuit de Monaco',             'Monaco',      3.337, 78),
    'Turkish GP':          ('Istanbul Park',                 'Turkey',      5.338, 58),
    'British GP':          ('Silverstone Circuit',           'UK',          5.891, 52),
    'German GP':           ('Hockenheimring',                'Germany',     5.148, 60),
    'Hungarian GP':        ('Hungaroring',                   'Hungary',     4.381, 70),
    'Belgian GP':          ('Spa-Francorchamps',              'Belgium',     7.004, 44),
    'Italian GP':          ('Monza Circuit',                  'Italy',       5.793, 53),
    'Japanese GP':         ('Suzuka Circuit',                'Japan',       5.807, 53),
    'United States GP':    ('Circuit of the Americas',       'USA',         5.513, 56),
    'French GP':           ('Magny-Cours',                    'France',      4.611, 72),
    'Canadian GP':         ('Circuit Gilles Villeneuve',     'Canada',      4.421, 70),
    'Singapore GP':        ('Marina Bay Circuit',            'Singapore',   4.064, 61),
    'Korean GP':           ('Yeongnam Circuit',              'South Korea', 5.621, 55),
    'Indian GP':           ('Buddh International Circuit',   'India',       5.125, 60),
    'Abu Dhabi GP':        ('Yas Marina Circuit',            'UAE',         5.281, 55),
    'Russian GP':          ('Sochi Autodrom',                 'Russia',      5.848, 53),
    'Azerbaijan GP':       ('Baku City Circuit',             'Azerbaijan',  6.003, 51),
    'Austrian GP':         ('Red Bull Ring',                  'Austria',     4.318, 71),
    'Mexican GP':          ('Autódromo Hermanos Rodríguez',  'Mexico',      4.304, 71),
    'Brazilian GP':        ('Autódromo José Carlos Pace',    'Brazil',      4.309, 71),
    'Sao Paulo GP':        ('Interlagos Circuit',            'Brazil',      4.309, 71),
    'Miami GP':            ('Miami International Autodrome', 'USA',         5.412, 57),
    'Emilia Romagna GP':   ('Imola Circuit',                  'Italy',       4.909, 63),
    'Dutch GP':            ('Circuit Zandvoort',             'Netherlands', 4.259, 72),
    'Qatar GP':            ('Losail International Circuit',  'Qatar',       5.419, 57),
    'Las Vegas GP':        ('Las Vegas Strip Circuit',       'USA',         6.201, 50),
    'Saudi Arabian GP':    ('Jeddah Corniche Circuit',       'Saudi Arabia',6.174, 50),
    'Styrian GP':          ('Red Bull Ring',                  'Austria',     4.318, 71),
    '70th Anniversary GP': ('Silverstone Circuit',           'UK',          5.891, 52),
    'Mexico City GP':      ('Autódromo Hermanos Rodríguez',  'Mexico',      4.304, 71),
    'Sakhir GP':           ('Bahrain Outer Loop',            'Bahrain',     3.923, 87),
    'Mugello GP':          ('Mugello Circuit',               'Italy',       5.245, 59),
    'Portugal GP':         ('Algarve Circuit',               'Portugal',    4.653, 66),
    'Eifel GP':            ('Nürburgring GP',                 'Germany',     5.148, 60),
    'Tuscany GP':          ('Mugello Circuit',               'Italy',       5.245, 59),
    'Bahrain GP':          ('Bahrain International Circuit', 'Bahrain',     5.412, 57),
}

def _seeded(val):
    return np.random.default_rng(int(abs(val)) % (2**31))

def _race_index(year: int, race: str) -> int:
    try:
        return get_races(year).index(race)
    except ValueError:
        return 0

def _air_temp(year: int, race_idx: int) -> int:
    return 7 + (year % 8) + (race_idx % 14)

def _track_temp(air: int, race_idx: int) -> int:
    return air + 14 + (race_idx % 10)

def _humidity(year: int, race_idx: int) -> int:
    return 25 + (year % 5) * 8 + (race_idx % 20)

def _wind(year: int, race_idx: int) -> int:
    return (race_idx * 3 + year) % 35

def _speed_from_lap(lap: float) -> float:
    return max(155, 355 - (lap - 88) * 5)

def render():
    st.markdown('<div class="section-header">📊 Session Explorer</div>', unsafe_allow_html=True)

    # ── Year / Race / Session selectors ──
    col1, col2, col3 = st.columns(3)

    with col1:
        year = st.selectbox("Select Year", list(reversed(range(2000, 2027))), key="session_year")

    with col2:
        races = get_races(year)
        race = st.selectbox("Select Grand Prix", races, key="session_race")

    with col3:
        session_type = st.selectbox(
            "Select Session",
            ['Free Practice 1', 'Free Practice 2', 'Free Practice 3',
             'Sprint Qualifying', 'Sprint', 'Qualifying', 'Race'],
            key="session_type"
        )

    # fetch data — triggered immediately by any selectbox change
    results = get_race_results(year, race)
    ri = _race_index(year, race)
    air  = _air_temp(year, ri)
    trk  = _track_temp(air, ri)
    hum  = _humidity(year, ri)
    wind = _wind(year, ri)
    info = CIRCUIT_INFO.get(race, ('Unknown Circuit', 'Unknown', 5.5, 55))
    total_laps = results[0]['laps'] if results else info[3]
    start_hr  = 9 + (ri % 6)
    n_drivers = len(results) if results else 20
    data_pts  = total_laps * 10 * n_drivers
    s_main    = _seeded(year * 7 + hash(race) % 10000)

    st.markdown("---")

    # ── Session header info ──
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**📍 Circuit:** {info[0]}")
        st.markdown(f"**🌍 Country:** {info[1]}")
        st.markdown(f"**📏 Track Length:** {info[2]} km")
        st.markdown(f"**🔄 Estimated Laps:** {total_laps}")
    with col2:
        st.markdown(f"**🌡️ Track Temp:** {trk}°C")
        st.markdown(f"**🌤️ Air Temp:** {air}°C")
        st.markdown(f"**💨 Wind:** {wind} km/h")
        st.markdown(f"**💧 Humidity:** {hum}%")
    with col3:
        st.markdown(f"**🏁 Session Start:** {start_hr:02d}:00 UTC")
        st.markdown(f"**⏱️ Session End:** {start_hr+2:02d}:00 UTC")
        st.markdown(f"**🚗 Active Drivers:** {n_drivers}")
        st.markdown(f"**📊 Data Points:** {data_pts:,}")

    st.markdown("---")

    # ── Session results table ──
    st.markdown('<div class="section-header">🏁 Session Results</div>', unsafe_allow_html=True)
    if results:
        df_results = pd.DataFrame([{
            'Pos':   r['position'],
            'Driver': r['driver'],
            'Team':   r['team'],
            'Best Lap': f"{r['best_lap']:.3f}s",
            'Gap':  ('+' + f"{(r['best_lap'] - results[0]['best_lap']):.3f}s") if r['position'] > 1 else '-',
            'Pits': r['pit_stops'],
        } for r in results])
        st.dataframe(df_results, use_container_width=True, hide_index=True)
    else:
        st.info("No results available for this selection.")

    st.markdown("---")

    # ── Lap time progression ──
    st.markdown('<div class="section-header">📈 Lap Time Progression</div>', unsafe_allow_html=True)
    laps_arr = np.arange(1, total_laps + 1)
    fig = go.Figure()
    for drv_r in (results[:5] if results else []):
        off  = s_main.normal(0, 0.5, len(laps_arr)) + np.linspace(0, -0.7, len(laps_arr))
        base = drv_r['best_lap'] + 0.5
        fig.add_trace(go.Scatter(
            x=laps_arr, y=(base + off).tolist(),
            mode='lines', name=drv_r['driver'],
            line=dict(color=DRIVER_COLORS.get(drv_r['driver'], '#ffd700'), width=2),
        ))
    fig.update_layout(
        title="Lap Time Evolution",
        xaxis_title="Lap Number", yaxis_title="Lap Time (s)",
        template='plotly_dark', height=400,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        hovermode='x unified'
    )
    fig.update_xaxes(showgrid=True,  gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    fig.update_yaxes(showgrid=True,  gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")

    # ── Speed analysis ──
    st.markdown('<div class="section-header">⚡ Speed Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")

    s_speed = _seeded(year * 13 + hash(race) % 10000)

    with col1:
        st.markdown("**Top Speed by Driver (km/h)**")
        top5 = sorted(results, key=lambda r: -r['best_lap'])[:5] if results else []
        if top5:
            df_speed = pd.DataFrame({
                'Driver': [r['driver'] for r in top5],
                'Speed': [_speed_from_lap(r['best_lap']) + s_speed.integers(-5, 5) for r in top5],
            })
            fig = px.bar(df_speed, x='Driver', y='Speed', color='Speed',
                         color_continuous_scale=['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd'])
            fig.update_layout(
                template='plotly_dark', height=300, showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("**Average Speed by Sector (km/h)**")
        top_drv = [r['driver'] for r in top5]
        fig = go.Figure()
        for drv in top_drv[:3]:
            fig.add_trace(go.Bar(
                x=['S1', 'S2', 'S3'],
                y=[s_speed.uniform(142, 156), s_speed.uniform(176, 196), s_speed.uniform(152, 172)],
                name=drv
            ))
        fig.update_layout(
            template='plotly_dark', height=300, barmode='group',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Tyre compound usage ──
    st.markdown("---")
    st.markdown('<div class="section-header">🛞 Tyre Compound Usage</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    s3 = _seeded(year * 17 + hash(race) % 10000)

    with col1:
        st.markdown("**Stints per Compound (Top 5 Drivers)**")
        compounds = ['Soft', 'Medium', 'Hard', 'Intermediate', 'Wet']
        fig = go.Figure()
        for drv_r in (results[:5] if results else []):
            fig.add_trace(go.Bar(
                x=compounds,
                y=s3.integers(0, 6, len(compounds)),
                name=drv_r['driver'],
                marker_color=DRIVER_COLORS.get(drv_r['driver'], '#888'),
            ))
        fig.update_layout(
            template='plotly_dark', height=300, barmode='group',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("**Final Position vs Tyre Age**")
        if results:
            tyre_ages = [r['pit_stops'] * 17 + (total_laps % 18) for r in results]
            fig = px.scatter(
                pd.DataFrame({
                    'Driver':       [r['driver']       for r in results],
                    'Position':     [r['position']     for r in results],
                    'Tyre Age (lap)': tyre_ages,
                }),
                x='Tyre Age (lap)', y='Position', color='Position',
                color_continuous_scale='RdYlGn_r', hover_data=['Driver'],
            )
            fig.update_yaxes(autorange='reversed')
            fig.update_layout(
                template='plotly_dark', height=300,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
                xaxis_title='Tyre Age at Finish (lap)', yaxis_title='Position',
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Sector delta heatmap ──
    st.markdown("---")
    st.markdown('<div class="section-header">📉 Sector Delta Heatmap</div>', unsafe_allow_html=True)
    if results:
        s4 = _seeded(year * 19 + hash(race) % 10000)
        sectors = ['Sector 1', 'Sector 2', 'Sector 3']
        heat_matrix = [s4.normal(0, 0.40, len(sectors)).tolist() for _ in results[:15]]
        fig = go.Figure(data=go.Heatmap(
            z=heat_matrix,
            x=sectors,
            y=[results[i]['driver'] for i in range(len(heat_matrix))],
            colorscale='RdYlGn_r',
            colorbar=dict(title='Delta (s)'),
        ))
        fig.update_layout(
            title='Sector Delta vs Best Reference',
            template='plotly_dark', height=max(280, 20 * len(heat_matrix) + 100),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: Speed trace – fastest lap ──
    st.markdown("---")
    st.markdown('<div class="section-header">📡 Telemetry – Speed vs Distance (Fastest Lap)</div>', unsafe_allow_html=True)
    if results:
        lead = results[0]
        s5 = _seeded(hash(race + lead['driver'] + str(year)) % (2**31))
        dist_m = np.linspace(0, info[2] * 1000, 500)
        speed_prof = s5.uniform(130, 355, 500)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dist_m, y=speed_prof,
            mode='lines', name='Speed',
            line=dict(color='#ffd700', width=1.5),
            fill='tozeroy', fillcolor='rgba(255,215,0,0.06)'
        ))
        fig.update_layout(
            title=f"{lead['driver']} ({lead['team']}) – Fastest Lap",
            xaxis_title='Distance (m)', yaxis_title='Speed (km/h)',
            template='plotly_dark', height=360,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.1)',
            showlegend=False
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,215,0,0.1)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ── NEW: 3D Lap Time Distribution Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 3D Lap Time Distribution Analysis</div>', unsafe_allow_html=True)
    if results and len(results) >= 3:
        s6 = _seeded(year * 23 + hash(race) % 10000)
        
        # Create 3D scatter: Lap Time vs Tire Degradation vs Fuel Load
        lap_data = []
        for i, driver_result in enumerate(results[:10]):  # Top 10 drivers
            base_lap = driver_result['best_lap']
            for lap in range(1, min(21, total_laps + 1), 2):  # Every 2nd lap up to lap 20
                tire_deg = s6.uniform(0.1, 0.8) * (lap / total_laps)  # Increasing degradation
                fuel_effect = (total_laps - lap) / total_laps * 0.02  # Fuel load effect
                noise = s6.normal(0, 0.3)
                lap_time = base_lap + tire_deg + fuel_effect + noise
                lap_data.append({
                    'Driver': driver_result['driver'],
                    'Lap_Number': lap,
                    'Lap_Time': lap_time,
                    'Tire_Degradation': tire_deg,
                    'Fuel_Load_Effect': fuel_effect
                })
        
        df_lap_3d = pd.DataFrame(lap_data)
        
        fig_lap_3d = go.Figure(data=go.Scatter3d(
            x=df_lap_3d['Lap_Time'],
            y=df_lap_3d['Tire_Degradation'],
            z=df_lap_3d['Fuel_Load_Effect'],
            mode='markers',
            marker=dict(
                size=4,
                color=df_lap_3d['Lap_Number'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Lap Number")
            ),
            text=df_lap_3d['Driver']
        ))
        
        fig_lap_3d.update_layout(
            title='Lap Time vs Tire Degradation vs Fuel Load (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Lap Time (s)',
                yaxis_title='Tire Degradation',
                zaxis_title='Fuel Load Effect',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_lap_3d, use_container_width=True)

    # ── NEW: 3D Strategy Comparison ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏁 3D Strategy Comparison</div>', unsafe_allow_html=True)
    if results:
        s7 = _seeded(year * 29 + hash(race) % 10000)
        
        # Pit stop strategy visualization
        strategies = ['1-stop', '2-stop', '3-stop', '4+']
        compounds = ['Soft', 'Medium', 'Hard']
        
        # Create 3D bar data for strategy effectiveness
        z_data = []
        for strategy in strategies:
            row = []
            for compound in compounds:
                # Effectiveness based on strategy and compound
                effectiveness = s7.uniform(50, 95)
                row.append(effectiveness)
            z_data.append(row)
        
        fig_strategy_3d = go.Figure()
        
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        for i, strategy in enumerate(strategies):
            fig_strategy_3d.add_trace(go.Bar(
                x=compounds,
                y=z_data[i],
                name=strategy,
                marker_color=colors[i]
            ))
        
        fig_strategy_3d.update_layout(
            title='Strategy Effectiveness by Compound (3D Grouped Bar)',
            template='plotly_dark',
            barmode='group',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            scene=dict(
                xaxis_title='Tire Compound',
                yaxis_title='Effectiveness Score',
                zaxis_title='Strategy Type',
                bgcolor='rgba(0,0,0,0)'
            )
        )
        st.plotly_chart(fig_strategy_3d, use_container_width=True)

    # ── NEW: 3D Temperature Impact Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">🌡️ 3D Temperature Impact Analysis</div>', unsafe_allow_html=True)
    if results:
        s8 = _seeded(year * 31 + hash(race) % 10000)
        
        # Temperature vs performance analysis
        temp_data = []
        for driver_result in results[:8]:  # Top 8 drivers
            base_performance = s8.uniform(75, 95)
            for temp_range in ['Cool', 'Moderate', 'Hot', 'Very Hot']:
                temp_factor = {'Cool': 1.0, 'Moderate': 0.95, 'Hot': 0.88, 'Very Hot': 0.8}[temp_range]
                performance = base_performance * temp_factor + s8.normal(0, 3)
                temp_data.append({
                    'Driver': driver_result['driver'],
                    'Temperature_Range': temp_range,
                    'Base_Performance': base_performance,
                    'Adjusted_Performance': max(40, min(100, performance)),
                    'Temp_Value': {'Cool': 15, 'Moderate': 25, 'Hot': 35, 'Very Hot': 42}[temp_range]
                })
        
        df_temp_3d = pd.DataFrame(temp_data)
        
        fig_temp_3d = go.Figure(data=go.Scatter3d(
            x=df_temp_3d['Temp_Value'],
            y=df_temp_3d['Base_Performance'],
            z=df_temp_3d['Adjusted_Performance'],
            mode='markers',
            marker=dict(
                size=5,
                color=df_temp_3d['Adjusted_Performance'],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Performance Score")
            ),
            text=df_temp_3d['Driver'] + '<br>' + df_temp_3d['Temperature_Range']
        ))
        
        fig_temp_3d.update_layout(
            title='Temperature Impact on Driver Performance (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Temperature (°C)',
                yaxis_title='Base Performance',
                zaxis_title='Adjusted Performance',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_temp_3d, use_container_width=True)

    # ── NEW: 3D Corner Speed Analysis ──
    st.markdown("---")
    st.markdown('<div class="section-header">🏎️ 3D Corner Speed Analysis</div>', unsafe_allow_html=True)
    if results and info[2] > 0:  # Only if we have circuit info
        s9 = _seeded(year * 37 + hash(race) % 10000)
        
        # Generate corner data based on track length
        num_corners = max(8, int(info[2] * 3))  # Approximate corners based on track length
        corner_data = []
        
        for i, driver_result in enumerate(results[:6]):  # Top 6 drivers
            base_speed = s9.uniform(120, 280)  # Base corner speed
            for corner_num in range(1, num_corners + 1):
                # Speed variation based on corner characteristics
                corner_factor = 0.7 + 0.6 * np.sin(corner_num * 0.3)  # Oscillating factor
                variability = s9.normal(0, 15)  # Random variation
                corner_speed = base_speed * corner_factor + variability
                corner_speed = max(40, min(320, corner_speed))  # Reasonable bounds
                
                corner_data.append({
                    'Driver': driver_result['driver'],
                    'Corner_Number': corner_num,
                    'Corner_Speed': corner_speed,
                    'Speed_Variability': abs(variability),
                    'Grip_Level': s9.uniform(0.7, 1.2)
                })
        
        df_corner_3d = pd.DataFrame(corner_data)
        
        fig_corner_3d = go.Figure(data=go.Scatter3d(
            x=df_corner_3d['Corner_Number'],
            y=df_corner_3d['Corner_Speed'],
            z=df_corner_3d['Grip_Level'],
            mode='markers',
            marker=dict(
                size=4,
                color=df_corner_3d['Speed_Variability'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Speed Variability")
            ),
            text=df_corner_3d['Driver']
        ))
        
        fig_corner_3d.update_layout(
            title='Corner Speed Analysis (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Corner Number',
                yaxis_title='Corner Speed (km/h)',
                zaxis_title='Grip Level',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_corner_3d, use_container_width=True)

    # ── NEW: 3D Overtaking Opportunity Map ──
    st.markdown("---")
    st.markdown('<div class="section-header">🔄 3D Overtaking Opportunity Map</div>', unsafe_allow_html=True)
    if results and info[2] > 0:
        s10 = _seeded(year * 41 + hash(race) % 10000)
        
        # Create overtaking opportunity data around the track
        track_positions = np.linspace(0, info[2] * 1000, 50)  # Meters around track
        overtake_data = []
        
        for pos_idx, position in enumerate(track_positions):
            # Overtaking opportunity based on track geometry (simplified)
            straights = np.sin(position / (info[2] * 1000) * 4 * np.pi)  # Straight sections
            corners = np.cos(position / (info[2] * 1000) * 6 * np.pi)   # Corner sections
            opportunity = (straights * 0.6 + abs(corners) * 0.4) * 100  # 0-100 scale
            
            # Add some randomness and driver-specific factors
            for i, driver_result in enumerate(results[:5]):  # Top 5 drivers
                driver_factor = s10.normal(0, 15) + (5 - i) * 2  # Better drivers have slight edge
                final_opportunity = max(0, min(100, opportunity + driver_factor))
                
                overtake_data.append({
                    'Track_Position': position,
                    'Opp_Opportunity': final_opportunity,
                    'Driver_Rank': i + 1,
                    'Sector': int((pos_idx / len(track_positions)) * 3) + 1,  # Sector 1-3
                    'Difficulty': s10.uniform(0.2, 0.8)
                })
        
        df_overtake_3d = pd.DataFrame(overtake_data)
        
        fig_overtake_3d = go.Figure(data=go.Scatter3d(
            x=df_overtake_3d['Track_Position'],
            y=df_overtake_3d['Opp_Opportunity'],
            z=df_overtake_3d['Sector'],
            mode='markers',
            marker=dict(
                size=3,
                color=df_overtake_3d['Driver_Rank'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Driver Rank")
            ),
            text=df_overtake_3d.apply(lambda row: f"Pos: {row['Track_Position']:.0f}m<br>Opp: {row['Opp_Opportunity']:.1f}<br>Sector: {row['Sector']}", axis=1)
        ))
        
        fig_overtake_3d.update_layout(
            title='Overtaking Opportunity Map Around Track (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Track Position (m)',
                yaxis_title='Oppportunity Score',
                zaxis_title='Track Sector',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_overtake_3d, use_container_width=True)

    # ── NEW: 3D Lap Time Consistency Visualization ──
    st.markdown("---")
    st.markdown('<div class="section-header">⏱️ 3D Lap Time Consistency Visualization</div>', unsafe_allow_html=True)
    if results:
        s11 = _seeded(year * 43 + hash(race) % 10000)
        
        # Analyze lap time consistency for each driver
        consistency_data = []
        for driver_result in results[:8]:  # Top 8 drivers
            base_lap = driver_result['best_lap']
            lap_times = []
            
            # Generate a sequence of lap times showing consistency/degradation
            for lap in range(1, min(31, total_laps + 1)):
                # Base lap time with degradation and random variation
                degradation = (lap - 1) / total_laps * s11.uniform(0, 1.5)  # Tire degradation
                variation = s11.normal(0, 0.3)  # Random lap variation
                fuel_effect = (total_laps - lap) / total_laps * 0.8  # Fuel effect
                lap_time = base_lap + degradation + variation - fuel_effect
                lap_times.append(max(base_lap * 0.9, lap_time))  # Don't go too fast
            
            # Calculate consistency metrics
            avg_lap = np.mean(lap_times)
            std_lap = np.std(lap_times)
            consistency_score = max(0, 100 - (std_lap / avg_lap * 1000))  # Inverse of variation
            
            consistency_data.append({
                'Driver': driver_result['driver'],
                'Avg_Lap_Time': avg_lap,
                'Consistency_Score': consistency_score,
                'Total_Variation': std_lap * 10,  # Scale for visibility
                'Best_Lap': min(lap_times),
                'Worst_Lap': max(lap_times)
            })
        
        df_consistency_3d = pd.DataFrame(consistency_data)
        
        fig_consistency_3d = go.Figure(data=go.Scatter3d(
            x=df_consistency_3d['Avg_Lap_Time'],
            y=df_consistency_3d['Consistency_Score'],
            z=df_consistency_3d['Total_Variation'],
            mode='markers+text',
            marker=dict(
                size=8,
                color=df_consistency_3d['Consistency_Score'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Consistency Score")
            ),
            text=df_consistency_3d['Driver'],
            textposition="top center"
        ))
        
        fig_consistency_3d.update_layout(
            title='Lap Time Consistency Analysis (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Average Lap Time (s)',
                yaxis_title='Consistency Score (0-100)',
                zaxis_title='Lap Time Variation (x10)',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_consistency_3d, use_container_width=True)

    # ── NEW: 3D Sector Performance Comparison ──
    st.markdown("---")
    st.markdown('<div class="section-header">📊 3D Sector Performance Comparison</div>', unsafe_allow_html=True)
    if results:
        s12 = _seeded(year * 47 + hash(race) % 10000)
        
        # Sector time analysis for each driver
        sector_data = []
        for driver_result in results[:10]:  # Top 10 drivers
            # Base sector times (typically S1+S2+S3 ≈ best lap time)
            base_total = driver_result['best_lap']
            s1_base = base_total * s12.uniform(0.32, 0.38)
            s2_base = base_total * s12.uniform(0.33, 0.39)
            s3_base = base_total - s1_base - s2_base  # Remainder
            
            for sector_num, sector_name in enumerate(['Sector 1', 'Sector 2', 'Sector 3'], 1):
                sector_base = locals()[f's{sector_num}_base']
                # Add variations
                variation = s12.normal(0, sector_base * 0.02)  # 2% variation
                sector_time = max(sector_base * 0.8, sector_base + variation)  # Reasonable bounds
                
                sector_data.append({
                    'Driver': driver_result['driver'],
                    'Sector': sector_name,
                    'Sector_Time': sector_time,
                    'Time_Diff_From_Base': sector_time - sector_base,
                    'Performance_Score': 100 * (sector_base / sector_time)  # Inverse relationship
                })
        
        df_sector_3d = pd.DataFrame(sector_data)
        
        fig_sector_3d = go.Figure()
        
        # Add scatter points for each sector
        sector_names = ['Sector 1', 'Sector 2', 'Sector 3']
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        for i, sector in enumerate(sector_names):
            sector_df = df_sector_3d[df_sector_3d['Sector'] == sector]
            fig_sector_3d.add_trace(go.Scatter3d(
                x=sector_df['Driver'],
                y=[sector] * len(sector_df),
                z=sector_df['Sector_Time'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors[i],
                    symbol='circle',
                    line=dict(width=1, color='white')
                ),
                name=sector
            ))
        
        fig_sector_3d.update_layout(
            title='Sector Performance Comparison (3D Scatter)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Driver',
                yaxis_title='Sector',
                zaxis_title='Sector Time (s)',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_sector_3d, use_container_width=True)

    # ── NEW: 3D Tyre Strategy Heatmap ──
    st.markdown("---")
    st.markdown('<div class="section-header">🛞 3D Tyre Strategy Heatmap</div>', unsafe_allow_html=True)
    if results:
        s13 = _seeded(year * 53 + hash(race) % 10000)
        
        # Tyre strategy effectiveness over race distance
        compounds = ['Soft', 'Medium', 'Hard']
        stint_lengths = [10, 20, 30, 40, 50]  # Different stint lengths to test
        
        heatmap_data = []
        for compound_idx, compound in enumerate(compounds):
            row_data = []
            for stint_len in stint_lengths:
                # Base performance decreases with stint length (wear)
                base_performance = 90 - (stint_len / 60) * 30  # 90 to 60 over 60 laps
                # Compound performance characteristics
                compound_factor = {'Soft': 1.0, 'Medium': 0.92, 'Hard': 0.85}[compound]
                # Add strategic variation and noise
                strategy_variation = s13.uniform(-5, 10)
                noise = s13.normal(0, 3)
                final_score = base_performance * compound_factor + strategy_variation + noise
                final_score = max(30, min(100, final_score))  # Keep in reasonable bounds
                
                row_data.append(final_score)
            heatmap_data.append(row_data)
        
        fig_tyre_heatmap_3d = go.Figure(data=go.Surface(
            z=heatmap_data,
            x=stint_lengths,
            y=compounds,
            colorscale='Viridis',
            colorbar=dict(title="Performance Score")
        ))
        
        fig_tyre_heatmap_3d.update_layout(
            title='Tyre Strategy Performance Heatmap (3D Surface)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Stint Length (laps)',
                yaxis_title='Tyre Compound',
                zaxis_title='Performance Score',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_tyre_heatmap_3d, use_container_width=True)

    # ── NEW: 3D Driver Skill Matrix ──
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 3D Driver Skill Matrix</div>', unsafe_allow_html=True)
    if results:
        s14 = _seeded(year * 59 + hash(race) % 10000)
        
        # Create a 3D skill matrix for drivers
        skills = ['Qualifying', 'Race Pace', 'Tire Management', 'Overtaking', 'Defending']
        skill_data = []
        
        for driver_result in results[:8]:  # Top 8 drivers
            # Base skill level for this driver
            base_skill = s14.uniform(65, 95)
            for skill_idx, skill in enumerate(skills):
                # Each skill varies around the base with some specialization
                skill_variation = s14.normal(0, 8)  # Random variation
                specialization = s14.uniform(-5, 5)   # Some drivers better/worse at specific skills
                final_skill = base_skill + skill_variation + specialization
                final_skill = max(30, min(100, final_skill))  # Keep in bounds
                
                skill_data.append({
                    'Driver': driver_result['driver'],
                    'Skill': skill,
                    'Skill_Score': final_skill,
                    'Skill_Rank': skill_idx + 1,
                    'Consistency': s14.uniform(0.7, 1.0)  # How consistent this skill is
                })
        
        df_skill_3d = pd.DataFrame(skill_data)
        
        fig_skill_3d = go.Figure(data=go.Scatter3d(
            x=df_skill_3d['Skill_Score'],
            y=df_skill_3d['Skill_Rank'],
            z=df_skill_3d['Consistency'],
            mode='markers+text',
            marker=dict(
                size=6,
                color=df_skill_3d['Skill_Score'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="Skill Score")
            ),
            text=df_skill_3d['Driver'],
            textposition="top center"
        ))
        
        fig_skill_3d.update_layout(
            title='Driver Skill Matrix (3D)',
            template='plotly_dark',
            scene=dict(
                xaxis_title='Skill Score (0-100)',
                yaxis_title='Skill Rank',
                zaxis_title='Skill Consistency',
                bgcolor='rgba(0,0,0,0)'
            ),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_skill_3d, use_container_width=True)
