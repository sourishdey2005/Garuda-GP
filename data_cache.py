import streamlit as st
import pandas as pd
import numpy as np
from functools import lru_cache
from datetime import datetime, timedelta
import json
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class DataCache:
    """Manages data caching for fast performance"""
    
    @staticmethod
    def get_cache_file(key: str) -> Path:
        """Get cache file path"""
        return CACHE_DIR / f"{key}.parquet"
    
    @staticmethod
    def is_cache_valid(key: str, ttl_minutes: int = 60) -> bool:
        """Check if cache is still valid"""
        cache_file = DataCache.get_cache_file(key)
        if not cache_file.exists():
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(minutes=ttl_minutes)
    
    @staticmethod
    def load_cache(key: str) -> pd.DataFrame:
        """Load data from cache"""
        cache_file = DataCache.get_cache_file(key)
        if cache_file.exists():
            return pd.read_parquet(cache_file)
        return pd.DataFrame()
    
    @staticmethod
    def save_cache(key: str, data: pd.DataFrame):
        """Save data to cache"""
        cache_file = DataCache.get_cache_file(key)
        data.to_parquet(cache_file)
    
    @staticmethod
    def clear_cache(key: str):
        """Clear specific cache"""
        cache_file = DataCache.get_cache_file(key)
        if cache_file.exists():
            cache_file.unlink()

@st.cache_data(ttl=3600)
def get_cached_data(data_type: str, **kwargs) -> pd.DataFrame:
    """Get or fetch cached data"""
    from openf1_service import get_openf1_service
    
    service = get_openf1_service()
    cache_key = f"{data_type}_{hash(str(sorted(kwargs.items())))}"
    
    # Try cache first
    if DataCache.is_cache_valid(cache_key):
        return DataCache.load_cache(cache_key)
    
    # Fetch from API
    data = pd.DataFrame()
    
    if data_type == "sessions":
        data = service.get_sessions(kwargs.get('year', 2024))
    elif data_type == "meetings":
        data = service.get_meetings(kwargs.get('year', 2024))
    elif data_type == "drivers":
        data = service.get_drivers(kwargs.get('session_key'))
    elif data_type == "car_data":
        data = service.get_car_data(kwargs.get('session_key'))
    elif data_type == "laps":
        data = service.get_laps(kwargs.get('session_key'))
    elif data_type == "position":
        data = service.get_position(kwargs.get('session_key'))
    elif data_type == "weather":
        data = service.get_weather(kwargs.get('session_key'))
    
    # Save to cache
    if not data.empty:
        DataCache.save_cache(cache_key, data)
    
    return data

class TelemetryProcessor:
    """Process raw telemetry data"""
    
    @staticmethod
    def smooth_data(data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Smooth telemetry data using rolling window"""
        if len(data) < window_size:
            return data
        
        return np.convolve(
            data,
            np.ones(window_size) / window_size,
            mode='valid'
        )
    
    @staticmethod
    def calculate_delta(driver1_times: np.ndarray, driver2_times: np.ndarray) -> np.ndarray:
        """Calculate time delta between drivers"""
        min_len = min(len(driver1_times), len(driver2_times))
        return driver1_times[:min_len] - driver2_times[:min_len]
    
    @staticmethod
    def calculate_sector_times(lap_data: pd.DataFrame) -> dict:
        """Calculate sector times from lap data"""
        sectors = {}
        
        if 'sector_1_duration' in lap_data.columns:
            sectors['S1'] = lap_data['sector_1_duration'].mean()
        if 'sector_2_duration' in lap_data.columns:
            sectors['S2'] = lap_data['sector_2_duration'].mean()
        if 'sector_3_duration' in lap_data.columns:
            sectors['S3'] = lap_data['sector_3_duration'].mean()
        
        return sectors
    
    @staticmethod
    def detect_drs_activation(car_data: pd.DataFrame) -> list:
        """Detect DRS activation points"""
        drs_points = []
        
        if 'drs' in car_data.columns:
            drs_transitions = car_data['drs'].diff().fillna(0)
            drs_points = car_data[drs_transitions != 0].index.tolist()
        
        return drs_points

@st.cache_data(ttl=600)
def get_performance_metrics(driver_name: str, session_key: int) -> dict:
    """Calculate performance metrics for a driver"""
    from openf1_service import get_openf1_service
    
    service = get_openf1_service()
    
    laps_df = service.get_laps(session_key)
    car_data_df = service.get_car_data(session_key)
    
    metrics = {
        'avg_lap_time': 0,
        'best_lap_time': 0,
        'consistency': 0,
        'avg_speed': 0,
        'drs_activations': 0
    }
    
    # Filter by driver
    if 'driver_number' in laps_df.columns and not laps_df.empty:
        driver_laps = laps_df[laps_df['driver_number'] == int(driver_name.split()[-1])]
        
        if 'lap_duration' in driver_laps.columns:
            valid_times = pd.to_numeric(driver_laps['lap_duration'], errors='coerce').dropna()
            if not valid_times.empty:
                metrics['avg_lap_time'] = valid_times.mean()
                metrics['best_lap_time'] = valid_times.min()
                metrics['consistency'] = 1 - (valid_times.std() / valid_times.mean())
    
    return metrics
