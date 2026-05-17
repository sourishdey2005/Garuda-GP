import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import streamlit as st
from joblib import dump, load
from pathlib import Path

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

class TyreDegradationPredictor:
    """Predict tyre degradation and remaining life"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train tyre degradation model"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict tyre life remaining"""
        if not self.is_trained:
            return np.zeros(len(X))
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    @staticmethod
    def get_optimal_pit_lap(lap_times: np.ndarray, compound: str) -> int:
        """Get optimal pit lap based on degradation pattern"""
        # Fit polynomial to degradation
        x = np.arange(len(lap_times))
        z = np.polyfit(x, lap_times, 2)
        p = np.poly1d(z)
        
        # Find inflection point
        degradation_rate = np.gradient(p(x))
        critical_point = np.argmax(degradation_rate) + 5
        
        return min(int(critical_point), len(lap_times) - 5)

class PacePredictor:
    """Predict driver pace and lap times"""
    
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, features: pd.DataFrame, targets: np.ndarray):
        """Train pace prediction model"""
        X_scaled = self.scaler.fit_transform(features)
        self.model.fit(X_scaled, targets)
        self.is_trained = True
    
    def predict_next_laps(self, features: pd.DataFrame, n_laps: int = 5) -> np.ndarray:
        """Predict next N lap times"""
        if not self.is_trained:
            return np.zeros(n_laps)
        
        predictions = []
        current_features = features.copy()
        
        for _ in range(n_laps):
            X_scaled = self.scaler.transform(current_features)
            pred = self.model.predict(X_scaled)
            predictions.append(pred[0])
            
            # Update features with new prediction (simple approach)
            current_features.iloc[0, -1] = pred[0]
        
        return np.array(predictions)

class StrategyOptimizer:
    """Optimize pit strategy using ML"""
    
    @staticmethod
    def simulate_strategy(initial_fuel: float, pit_stops: int, tyre_compounds: list) -> dict:
        """Simulate race strategy"""
        race_laps = 56  # Example
        laps_per_stint = race_laps / (pit_stops + 1)
        
        stints = []
        lap_consumed = 0
        
        for i, compound in enumerate(tyre_compounds):
            stint_length = int(laps_per_stint)
            
            stints.append({
                'stint': i + 1,
                'compound': compound,
                'laps': stint_length,
                'start_lap': lap_consumed + 1,
                'end_lap': lap_consumed + stint_length,
                'tyre_age': stint_length
            })
            
            lap_consumed += stint_length
        
        return {
            'pit_stops': pit_stops,
            'stints': stints,
            'total_pit_time': pit_stops * 2.8,
            'estimated_race_time': 5400 + (pit_stops * 2.8)
        }
    
    @staticmethod
    def calculate_undercut_window(gap: float, pit_loss: float = 2.8) -> tuple:
        """Calculate undercut opportunity window"""
        pace_delta = 0.3  # Driver pace advantage
        laps_needed = (gap + pit_loss) / pace_delta
        
        return (int(laps_needed), int(laps_needed + 3))
    
    @staticmethod
    def calculate_overcut_window(gap: float, fuel_loss: float = 0.05) -> tuple:
        """Calculate overcut opportunity window"""
        pace_gain = 0.15 + fuel_loss  # Fresh tyre + lighter fuel
        laps_available = gap / pace_gain
        
        return (int(laps_available - 3), int(laps_available))

class PerformanceBenchmark:
    """Benchmark driver performance"""
    
    @staticmethod
    def calculate_consistency_score(lap_times: np.ndarray) -> float:
        """Calculate consistency score (0-100)"""
        if len(lap_times) < 3:
            return 0
        
        valid_times = lap_times[(lap_times > 0) & (lap_times < 300)]
        
        if len(valid_times) == 0:
            return 0
        
        mean_time = valid_times.mean()
        std_dev = valid_times.std()
        
        # Lower std dev = higher consistency
        consistency = max(0, 100 * (1 - std_dev / mean_time))
        
        return min(100, consistency)
    
    @staticmethod
    def calculate_skill_score(
        consistency: float,
        quali_performance: float,
        race_performance: float,
        tyre_management: float
    ) -> float:
        """Calculate overall driver skill score"""
        weights = {
            'consistency': 0.25,
            'quali': 0.30,
            'race': 0.35,
            'tyres': 0.10
        }
        
        score = (
            consistency * weights['consistency'] +
            quali_performance * weights['quali'] +
            race_performance * weights['race'] +
            tyre_management * weights['tyres']
        )
        
        return min(100, max(0, score))
    
    @staticmethod
    def compare_drivers(driver1_times: np.ndarray, driver2_times: np.ndarray) -> dict:
        """Compare two drivers"""
        min_len = min(len(driver1_times), len(driver2_times))
        
        times1 = driver1_times[:min_len]
        times2 = driver2_times[:min_len]
        
        delta = times2 - times1
        
        return {
            'avg_delta': delta.mean(),
            'max_delta': delta.max(),
            'min_delta': delta.min(),
            'delta_std': delta.std(),
            'driver1_ahead_laps': int((delta > 0).sum()),
            'driver2_ahead_laps': int((delta < 0).sum())
        }

class WeatherImpactPredictor:
    """Predict weather impact on performance"""
    
    @staticmethod
    def calculate_wet_grip_loss(rain_intensity: float) -> float:
        """Calculate grip loss due to rain (0-100%)"""
        # Fit curve: light rain = 5-10%, heavy = 25-40%
        return min(40, rain_intensity * 40)
    
    @staticmethod
    def predict_temperature_impact(track_temp: float, baseline_temp: float = 45) -> float:
        """Predict lap time impact of temperature change"""
        temp_delta = track_temp - baseline_temp
        
        # Approximately 0.05s per °C change
        impact = temp_delta * 0.05
        
        return impact
