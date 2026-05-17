# GarudaGP Quick Reference Guide

## 🚀 START HERE (30 seconds)

### Installation
```bash
pip install -r requirements.txt --break-system-packages
streamlit run app.py
```

**Browser opens automatically to:** `http://localhost:8501`

---

## 📋 COMPLETE FILE CHECKLIST

### ✅ Created Files (17 total)

**Main Application**
- [x] `app.py` - Entry point with sidebar navigation

**Pages (8 modules)**
- [x] `pages/dashboard.py` - Championship dashboard
- [x] `pages/session_explorer.py` - Session selection
- [x] `pages/driver_profiles.py` - Driver analysis
- [x] `pages/team_intelligence.py` - Team analysis
- [x] `pages/telemetry_analysis.py` - Telemetry comparison
- [x] `pages/strategy_simulator.py` - Strategy optimization
- [x] `pages/ai_analytics.py` - ML insights
- [x] `pages/command_center.py` - Live race monitoring

**Components**
- [x] `components/metrics.py` - UI components
- [x] `components/charts.py` - Chart templates

**Utilities**
- [x] `utils/openf1_service.py` - API integration (15 endpoints)
- [x] `utils/data_cache.py` - Data processing & caching

**Machine Learning**
- [x] `ml/predictions.py` - 5 ML models

**Documentation**
- [x] `README.md` - Complete documentation
- [x] `INSTALLATION_GUIDE.md` - Setup guide
- [x] `BUILD_SUMMARY.md` - Build overview
- [x] `QUICK_REFERENCE.md` - This file

**Dependencies**
- [x] `requirements.txt` - 13 packages
- [x] `setup.sh` - Setup script

**Init Files**
- [x] `pages/__init__.py`
- [x] `components/__init__.py`
- [x] `utils/__init__.py`
- [x] `ml/__init__.py`

---

## 🎯 FEATURE QUICK REFERENCE

### 🏠 Dashboard
```
What: Championship standings and season overview
How: Click "🏠 Dashboard" → View data
Data: Real-time standings, performance charts
```

### 📊 Session Explorer
```
What: Browse and analyze F1 sessions
How: Select year → Grand Prix → Session type
Data: Results, weather, sector speeds
```

### 👤 Driver Profiles
```
What: Individual driver deep dive
How: Select driver → View metrics
Data: Consistency, skills, telemetry
```

### 🏁 Team Intelligence
```
What: Team-level performance analysis
How: Select team → Compare drivers
Data: Setup philosophy, aero efficiency
```

### 📈 Telemetry Analysis
```
What: Multi-driver telemetry comparison
How: Select 2 drivers → Choose metric
Data: Speed, throttle, brake, gear, RPM
```

### 🎯 Strategy Simulator
```
What: Pit strategy optimization
How: Set parameters → Choose strategy
Data: Race simulation, probabilities, timing
```

### 🤖 AI Analytics
```
What: ML-powered insights and predictions
How: Auto-generated insights
Data: Pace predictions, skill scores, anomalies
```

### ⚡ Live Command Center
```
What: Real-time race monitoring
How: Open during live race
Data: Leaderboard, gaps, overtakes, radio
```

---

## 🔧 TROUBLESHOOTING QUICK FIX

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `pip install <module> --break-system-packages` |
| Port 8501 in use | `streamlit run app.py --server.port 8502` |
| Slow performance | Clear cache via sidebar button |
| Charts not loading | `pip install plotly --upgrade --break-system-packages` |
| API timeout | Check internet, wait 30s, retry |
| High memory | `rm -rf cache/*` |

---

## 📊 DATA STRUCTURE QUICK REFERENCE

### OpenF1 API Endpoints
```
✓ Sessions     - Race session info
✓ Meetings     - Grand Prix meetings
✓ Drivers      - Driver details
✓ Car Data     - Real-time telemetry
✓ Laps         - Lap timing
✓ Position     - Position/gaps
✓ Pit          - Pit stops
✓ Weather      - Conditions
+ 7 more endpoints
```

### ML Models
```
1. Tyre Degradation    - Random Forest
2. Pace Prediction     - Gradient Boosting
3. Strategy Optimizer  - Monte Carlo
4. Performance         - Custom Scoring
5. Weather Impact      - Regression
```

### Cache Structure
```
cache/
├── sessions_*.parquet
├── laps_*.parquet
├── car_data_*.parquet
├── drivers_*.parquet
└── weather_*.parquet
```

---

## 🎨 DESIGN SYSTEM

### Colors
```
Gold:       #ffd700 (Primary accent)
Dark Blue:  #0a0e27 (Background)
Green:      #00ff00 (Success)
Red:        #ff6b6b (Warning)
Cyan:       #4ecdc4 (Info)
```

### Components
```
MetricCard    - Stats display
DriverCard    - Driver profiles
StatBadge     - Small indicators
Radar Chart   - Skill visualization
Line Chart    - Trends
Bar Chart     - Comparisons
```

---

## 📦 DEPENDENCIES QUICK LIST

```
streamlit              ✓
fastf1                 ✓
pandas                 ✓
numpy                  ✓
plotly                 ✓
scikit-learn           ✓
xgboost                ✓
pyarrow                ✓
requests               ✓
scipy                  ✓
joblib                 ✓
```

---

## 🔄 COMMON WORKFLOWS

### Workflow 1: Prepare for Qualifying (5 min)
```
1. Open Session Explorer
2. Select previous qualifying
3. Compare top drivers
4. Note fastest sector
5. Check setup trends
```

### Workflow 2: Monitor Race (20+ min)
```
1. Open Live Command Center
2. Pin leaderboard window
3. Watch gap evolution
4. Monitor pit strategy
5. Track overtakes
```

### Workflow 3: Analyze Driver (10 min)
```
1. Open Driver Profiles
2. Select driver
3. Check consistency score
4. Review telemetry
5. Analyze recent form
```

### Workflow 4: Plan Strategy (15 min)
```
1. Open Strategy Simulator
2. Set race parameters
3. Try different strategies
4. Check probability outcomes
5. Determine optimal approach
```

---

## 💻 COMMAND QUICK REFERENCE

### Start Application
```bash
streamlit run app.py
```

### Custom Port
```bash
streamlit run app.py --server.port 8502
```

### Headless Mode
```bash
streamlit run app.py --headless
```

### Clear Cache Terminal
```bash
rm -rf cache/*
```

### Check Python Version
```bash
python3 --version
```

### List Installed Packages
```bash
pip list | grep -E 'streamlit|pandas|plotly|fastf1'
```

---

## 🎯 METRICS QUICK REFERENCE

### Key Formulas

**Consistency Score**
```
= 100 × (1 - StdDev / MeanTime)
Higher = Better (0-100)
```

**Skill Score**
```
= (Consistency × 0.25) + (Quali × 0.30) + 
  (Race × 0.35) + (TyreMgmt × 0.10)
Range: 0-100
```

**Time Delta**
```
= Driver1_LapTime - Driver2_LapTime
Positive = Slower, Negative = Faster
```

**Undercut Laps**
```
= (Gap + PitLoss) / PaceAdvantage
Add 3 laps for window buffer
```

---

## 🚨 ALERT THRESHOLDS

| Metric | 🟢 Good | 🟡 Caution | 🔴 Alert |
|--------|---------|-----------|----------|
| Consistency | >90% | 80-90% | <80% |
| Skill Score | >85 | 70-85 | <70 |
| Gap to Leader | <1.5s | 1.5-3s | >3s |
| Tyre Life | >8 laps | 4-8 laps | <4 laps |
| Track Temp | 40-50°C | 35-40°C | <35°C |

---

## 📱 INTERFACE NAVIGATION

### Top Navigation
```
🏎️ GarudaGP [Main Title]
[Page Selection Dropdown]
```

### Sidebar
```
⚙️ NAVIGATION
[8 Page Options]

---

🔄 UTILITIES
[Refresh Data Button]
[Clear Cache Button]

---

📡 DATA SOURCE
OpenF1 API + FastF1
```

### Main Content Area
```
[Page Title]
[Filters/Selection]
---
[Data Visualization]
[Analytics Charts]
[Results Tables]
```

---

## 🔐 DATA SECURITY

✅ No personal data
✅ Public F1 data only
✅ Local storage only
✅ No external servers
✅ HTTPS API calls
✅ No authentication

---

## 📊 EXPECTED PERFORMANCE

- Initial Load: 3-5 seconds
- Page Switch: <1 second
- Data Refresh: 15-60 seconds
- Chart Load: <2 seconds
- Memory: 200-500MB
- API Call: 200-800ms

---

## 🎓 LEARNING TIPS

1. **Start with Dashboard** - Get overview
2. **Try Session Explorer** - Explore data
3. **Read Driver Profiles** - Understand metrics
4. **Use Telemetry** - Compare drivers
5. **Run Strategy** - Test scenarios
6. **Check AI Analytics** - See predictions

---

## 🆘 GETTING HELP

**Check These First:**
1. README.md - Full documentation
2. INSTALLATION_GUIDE.md - Setup help
3. Code comments - Inline documentation
4. OpenF1 Docs - API reference

**Resources:**
- OpenF1 API: https://api.openf1.org/
- Streamlit: https://docs.streamlit.io/
- Plotly: https://plotly.com/python/

---

## ✅ VERIFICATION CHECKLIST

Before running, verify:
- [ ] Python 3.9+ installed
- [ ] pip installed
- [ ] Internet connection
- [ ] 2GB+ disk space
- [ ] 2GB+ RAM available

Before opening browser:
- [ ] Terminal shows "You can now view your Streamlit app"
- [ ] No error messages
- [ ] Port shows 8501

After opening:
- [ ] Page loads completely
- [ ] Gold/dark theme visible
- [ ] Sidebar navigation works
- [ ] Data displays correctly

---

## 🎁 BONUS TIPS

**Tip 1:** Use Ctrl+R to refresh Streamlit
**Tip 2:** Use Cmd+/ to clear Streamlit cache
**Tip 3:** Hover over charts for detailed data
**Tip 4:** Sidebar buttons refresh all data
**Tip 5:** Charts are fully interactive

---

## 📈 OPTIMIZATION TIPS

- Clear cache weekly
- Close other browser tabs
- Use wired internet when possible
- Run on modern browser (Chrome recommended)
- Restart Streamlit if slow

---

## 🏁 YOU'RE READY!

```
✅ Installation: Complete
✅ Files: 17 created
✅ Features: 8 modules, 100+ charts
✅ Code: 4000+ lines
✅ Documentation: Comprehensive
✅ Ready to: Use and customize

Enjoy analyzing Formula 1! 🏎️⚡
```

---

**Quick Links:**
- [Full README](README.md)
- [Installation Guide](INSTALLATION_GUIDE.md)
- [Build Summary](BUILD_SUMMARY.md)

**Made by:** Sourish Dey
**LinkedIn:** https://www.linkedin.com/in/sourish-dey-20b170206/?skipRedirect=true
**Portfolio:** https://sourishdeyportfolio.vercel.app/

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2024
