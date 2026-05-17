# GarudaGP Installation & Usage Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Installation](#detailed-installation)
3. [Running the Application](#running-the-application)
4. [First Time Setup](#first-time-setup)
5. [Troubleshooting](#troubleshooting)
6. [Feature Overview](#feature-overview)

---

## ⚡ Quick Start

### Fastest Way to Get Started (5 minutes)

```bash
# 1. Navigate to project directory
cd garudagp

# 2. Install dependencies
pip install -r requirements.txt --break-system-packages

# 3. Run the app
streamlit run app.py

# 4. Open browser
# Automatically opens at http://localhost:8501
```

---

## 🔧 Detailed Installation

### Step 1: System Requirements

**Minimum:**
- Python 3.9+
- 2GB RAM
- 500MB disk space
- Internet connection (for API calls)

**Recommended:**
- Python 3.10 or 3.11
- 4GB+ RAM
- 2GB disk space
- Stable internet (WiFi or wired)

### Step 2: Check Python Installation

```bash
# Verify Python version
python3 --version
# Should output: Python 3.9.x or higher

# Verify pip is installed
pip --version
# Should output: pip 22.x or higher
```

### Step 3: Create Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
# Basic installation
pip install -r requirements.txt

# If you get permission errors, use:
pip install -r requirements.txt --break-system-packages

# For specific Python versions:
pip3.11 install -r requirements.txt --break-system-packages
```

### Step 5: Verify Installation

```bash
# Test imports
python3 -c "import streamlit; print('✓ Streamlit OK')"
python3 -c "import pandas; print('✓ Pandas OK')"
python3 -c "import plotly; print('✓ Plotly OK')"
python3 -c "import fastf1; print('✓ FastF1 OK')"
```

---

## 🚀 Running the Application

### Basic Launch

```bash
streamlit run app.py
```

### With Custom Configuration

```bash
# Run on specific port
streamlit run app.py --server.port 8501

# Run in headless mode
streamlit run app.py --headless

# Run with remote access
streamlit run app.py --server.address 0.0.0.0
```

### What Happens on First Run

1. ✓ Creates `cache/` directory for data storage
2. ✓ Creates `models/` directory for ML models
3. ✓ Initializes Streamlit session state
4. ✓ Loads UI components
5. ✓ Browser opens automatically to http://localhost:8501

---

## 🎯 First Time Setup

### Initial Configuration

1. **Check Data Connection**
   - Sidebar shows "🔗 OpenF1 API + FastF1"
   - Internet connection verified

2. **Select Your First Session**
   - Click "📊 Session Explorer"
   - Select year: 2024
   - Select Grand Prix: Chinese GP
   - Select session: Qualifying
   - Click "📊 Load Session"

3. **Explore Dashboard**
   - View championship standings
   - Check recent race results
   - Review performance analytics

4. **Try Driver Profiles**
   - Click "👤 Driver Profiles"
   - Select "Max Verstappen"
   - View performance metrics
   - Check telemetry data

### Custom Cache Configuration

Edit cache settings in `utils/data_cache.py`:

```python
# Cache TTL (seconds)
TTL_SESSIONS = 3600      # 1 hour
TTL_CAR_DATA = 1800      # 30 minutes
TTL_REAL_TIME = 900      # 15 minutes
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install streamlit --break-system-packages
```

### Issue: "No module named 'fastf1'"

**Solution:**
```bash
pip install fastf1 --break-system-packages
```

### Issue: Port 8501 already in use

**Solution 1:** Use different port
```bash
streamlit run app.py --server.port 8502
```

**Solution 2:** Kill existing Streamlit process
```bash
# On Linux/Mac:
lsof -ti:8501 | xargs kill -9

# On Windows (PowerShell):
Get-Process streamlit | Stop-Process -Force
```

### Issue: API connection timeout

**Solution:**
- Check internet connection
- Wait 30 seconds and refresh
- Try a different F1 session
- Check OpenF1 API status

### Issue: Memory usage too high

**Solution:**
```bash
# Click "Clear Cache" button in sidebar
# Or from terminal:
rm -rf cache/*
```

### Issue: Slow performance

**Solutions:**
1. Close other applications
2. Clear browser cache
3. Reduce number of drivers in comparison
4. Use less data-intensive pages
5. Restart the application

### Issue: Charts not displaying

**Solution:**
```bash
pip install plotly --upgrade --break-system-packages
pip install kaleido --break-system-packages
```

---

## 📚 Feature Overview

### 🏠 Dashboard
**What it does:** Shows championship standings and season overview
**How to use:**
1. Click "🏠 Dashboard" in sidebar
2. View driver and team standings
3. Check recent race results
4. Review performance analytics

**Data updated:** Every 60 seconds during season

---

### 📊 Session Explorer
**What it does:** Browse and analyze individual racing sessions
**How to use:**
1. Select year (2024, 2023, etc.)
2. Select Grand Prix
3. Select session type (FP1, FP2, FP3, Q, R)
4. View results and lap data
5. Analyze speed by sector

**Pro tips:**
- Use same session across seasons to compare
- Check weather conditions for context
- Compare top 5 drivers for insights

---

### 👤 Driver Profiles
**What it does:** Deep dive into individual driver performance
**How to use:**
1. Select driver from dropdown
2. View overall metrics
3. Check sector performance
4. Review telemetry data (speed, throttle, brake)
5. Analyze recent form

**Key metrics:**
- Consistency Score: Lap-to-lap stability
- Skill Score: Overall performance rating
- Sector Dominance: Where they're fastest

---

### 🏁 Team Intelligence
**What it does:** Team-level performance analysis
**How to use:**
1. Select team
2. Compare team drivers
3. Check aero efficiency
4. Review setup philosophy
5. Analyze head-to-head vs competitors

**What to look for:**
- Driver performance gap
- Setup trends
- Competitive strengths/weaknesses

---

### 📈 Telemetry Analysis
**What it does:** Detailed comparison of driver inputs and outputs
**How to use:**
1. Select two drivers
2. Choose metric (Speed, Throttle, Brake, etc.)
3. View comparative charts
4. Analyze delta/gap
5. Study pedal usage

**Advanced:**
- Identify braking points
- Compare gear usage patterns
- Analyze DRS deployment

---

### 🎯 Strategy Simulator
**What it does:** Simulate different pit strategies
**How to use:**
1. Set race length
2. Choose initial tyre
3. Select pit strategy (1, 2, or 3-stop)
4. View simulated outcomes
5. Check Monte Carlo probabilities

**Outputs:**
- Expected race time
- Podium probability
- Win probability
- Strategy recommendations

---

### 🤖 AI Analytics
**What it does:** Machine learning insights and predictions
**How to use:**
1. View AI-generated insights
2. Check pace predictions
3. Review feature importance
4. Analyze driver evolution
5. Check race outcome predictions

**Key insights:**
- Next lap pace prediction
- Driver skill evolution
- Optimal strategy recommendations

---

### ⚡ Live Command Center
**What it does:** Real-time race monitoring (when race is live)
**How to use:**
1. View live leaderboard
2. Track gap evolution
3. Monitor overtakes
4. Check weather conditions
5. Review team radio

**During live race:**
- Updates every 15-30 seconds
- Shows real-time gaps
- Tracks DRS usage
- Monitors pit stops

---

## 🔄 Common Workflows

### Workflow 1: Prepare for Qualifying

1. Open Session Explorer
2. Select previous qualifying session
3. Analyze top drivers' speed traces
4. Check track conditions
5. Note sector performance

### Workflow 2: Monitor Race Progress

1. Open Live Command Center
2. Pin window with leaderboard
3. Monitor gaps and gaps
4. Track pit stop strategy
5. Watch for overtake opportunities

### Workflow 3: Compare Drivers

1. Open Telemetry Analysis
2. Select two drivers
3. Choose Speed metric
4. Analyze delta patterns
5. Review throttle/brake differences

### Workflow 4: Analyze Pit Strategy

1. Open Strategy Simulator
2. Set race parameters
3. Simulate different strategies
4. Check probability outcomes
5. Determine optimal approach

---

## 🎨 Customization

### Change Color Theme

In `app.py`, modify CSS variables:

```python
# Primary color (gold accent)
--primary: #ffd700;

# Background color
--bg: #0a0e27;

# Success color
--success: #00ff00;
```

### Add Custom Metrics

In `components/metrics.py`:

```python
class MyMetric(MetricCard):
    @staticmethod
    def render(label, value, custom_style):
        # Your custom implementation
        pass
```

### Extend ML Models

In `ml/predictions.py`:

```python
class MyModel:
    def train(self, X, y):
        # Training logic
        pass
    
    def predict(self, X):
        # Prediction logic
        pass
```

---

## 📊 Data Management

### Cache Structure

```
cache/
├── sessions_*.parquet          # Session data
├── laps_*.parquet              # Lap timing
├── car_data_*.parquet          # Telemetry
├── drivers_*.parquet           # Driver info
└── weather_*.parquet           # Weather data
```

### Clear Specific Cache

```bash
# Delete all cache
rm -rf cache/*

# Delete specific session cache
rm cache/sessions_*.parquet
```

---

## 🔐 Security Notes

- ✓ No personal data stored
- ✓ Only public F1 data used
- ✓ No authentication required
- ✓ Local-only operation
- ✓ HTTPS for API calls

---

## 💾 Backup & Export

### Export Session Data

```python
import pandas as pd

# Load from cache
df = pd.read_parquet('cache/sessions_*.parquet')
df.to_csv('my_session_data.csv')
```

### Backup Cache

```bash
cp -r cache cache_backup_$(date +%Y%m%d)
```

---

## 🆘 Getting Help

1. **Check README.md** - Full documentation
2. **Check code comments** - Inline documentation
3. **OpenF1 API Docs** - https://api.openf1.org/
4. **Streamlit Docs** - https://docs.streamlit.io/
5. **Plotly Docs** - https://plotly.com/python/

---

## 🎓 Learning Resources

- **F1 Telemetry Basics:** OpenF1 documentation
- **Streamlit Development:** Official tutorials
- **Data Science:** Scikit-learn and Pandas docs
- **Visualization:** Plotly interactive charts

---

## 📝 Keyboard Shortcuts (Streamlit)

- `R` - Rerun script
- `C` - Clear cache
- `Q` - Quit
- `Cmd/Ctrl + +` - Increase font size

---

## 🎯 Next Steps

1. ✓ Complete installation
2. ✓ Run `streamlit run app.py`
3. ✓ Explore Dashboard
4. ✓ Try Session Explorer
5. ✓ Compare drivers in Telemetry Analysis
6. ✓ Run strategy simulations
7. ✓ Monitor live races
8. ✓ Read full documentation

---

## ❓ FAQ

**Q: Is internet required?**
A: Yes, for OpenF1 API calls. Cached data works offline.

**Q: How often is data updated?**
A: Real-time during F1 sessions, 1-hour cache for historical data.

**Q: Can I run multiple instances?**
A: Yes, use different ports: `--server.port 8502`

**Q: Is this official F1?**
A: No, it's an educational fan project using official OpenF1 data.

**Q: Can I modify the code?**
A: Yes! It's designed to be customizable.

---

**Enjoy analyzing Formula 1! 🏁⚡**
