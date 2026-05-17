# Visualizations Added (Current UI Audit)

## What this file is
This file lists the **visualizations currently present in the 5 requested Streamlit sections**.

⚠️ Note: It does **not** guarantee that each item is part of the “+50 newly added” set, because the repo does not include a chart-by-chart manifest or a baseline diff to identify exactly which 50 were added.

---

## 👤 Driver Profiles (`driver_profiles.py`)

### Confirmed from current code
1. **Driver KPI cards** (Championship Pts, Wins, Poles, Quali Pace)
2. **Radar chart** — Driver Strengths
3. **Data table** — Sector Performance
4. **Data table** — Season Form (Selected Races)
5. **Line chart** — Speed Trace (Best Lap)
6. **Line chart** — Throttle & Brake (Best Lap)
7. **3D plot** — 3D Driver Performance Evolution
8. **3D plot** — 3D Skill Comparison Matrix
9. **3D plot** — 3D Lap Time Distribution Analysis
10. **3D plot** — 3D Championship Probability Map
11. **3D plot** — 3D Driver Personality & Style Analysis
12. (Optional) **Radar chart** comparison — Compare with teammate

---

## 🏁 Team Intelligence (`team_intelligence.py`)

### Confirmed from current code
1. **Data table** — Driver Comparison
2. **Scatter plot** — Straight-Line Speed vs Cornering Speed
3. **Line chart** — Season Pace Trend (Lap Pace Trend)
4. **Data table** — Head-to-Head vs Competitors
5. **Pie chart** — Tyre Compound Usage
6. **Histogram** — Pit Stop Time Distribution
7. **Box plot** — Lap Time Variability
8. **Heatmap** — Performance Consistency Heatmap
9. **Area/Line chart** — Season Points Progression
10. **Bar chart** — Championship Probability Distribution
11. **Waterfall chart** — Upgrade Impact Analysis
12. **Scatter plot** — Risk/Reward Scatter Plot
13. **Treemap** — Budget Distribution
14. **Gantt-like horizontal bar** — Development Timeline

---

## 📈 Telemetry Analysis (`telemetry_analysis.py`)

### Confirmed from current code
1. **Line chart** (dual-axis) — Telemetry Channel Comparison (d1 vs d2)
2. **Area/Line chart** — Time Delta (d1 − d2)
3. **Line chart** — Throttle Usage (d1)
4. **Line chart** — Brake Usage (d1)
5. **Bar chart** — Gear Usage Distribution
6. **Bar chart** — RPM Distribution
7. **Line chart** — Brake Temperature Trace (front/rear)
8. **KPI cards** — Advanced KPIs
9. **Expander** — Advanced 3D Visualizations
10. **3D scatter** — 3D Phase-Space (Throttle × Brake × Speed)
11. **3D surface(s)** — 3D Speed Evolution (Lap × Distance × Speed)
12. **3D surface** — 3D Brake Temp Map (Lap × Distance)
13. **3D scatter/line** — 3D Delta Rail (d1−d2)
14. **Heatmap** — Speed Heatmap (Lap × Distance)

---

## 🎯 Strategy Simulator (`strategy_simulator.py`)

### Confirmed from current code
1. **Data table** — Pace Predictions
2. **Line chart** — Tyre Degradation Forecast (compound pace decay)
3. **Data table** — Degradation Rate Comparison
4. **Line chart** — Simulated Position Evolution
5. **Metric cards** — Monte Carlo Simulation outputs (Win%, Podium%, Top5%)
6. **Data table** — Pit Stop Windows & Lap Counters
7. **Bar chart** — Optimal Pit Lap by Race
8. **Scatter plot** — Undercut Gain per Stop

---

## ⚡ Live Command Center (`command_center.py`)

### Confirmed from current code
1. **KPI cards** — Session status (Current Lap, Track Temp, Time to Finish, etc.)
2. **Data table** — Live Leaderboard
3. **Heatmap** — Live Telemetry (All Drivers)
4. **Line/area charts** — Live Pedal Trace (Last Lap)
5. **Line chart** — Gap Tracking
6. **3D plot** — 3D Track Map
7. **Multi-series line chart** — Position Tracker (Multiple Drivers)
8. **Panel render** — 3D Race Simulation Panel (Simulated) via `race_sim_panel.render_race_panel`

---

## Next step to make it exactly “the 50 newly added”
To produce an exact JSON list of only the **newly added** charts, the repo needs:
- a git commit/hash for the baseline *before* the +50 change, OR
- a dedicated chart manifest.

With a baseline commit, we can diff AST/strings around `st.plotly_chart(...)` and produce an exact list.

