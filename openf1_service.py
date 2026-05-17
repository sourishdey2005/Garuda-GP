import requests
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
import streamlit as st

BASE_URL = "https://api.openf1.org/v1"

class OpenF1Service:
    """OpenF1 API integration service"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = 10
    
    @st.cache_data(ttl=3600)
    def get_sessions(self, year: int, grand_prix: Optional[str] = None) -> pd.DataFrame:
        """Get F1 sessions"""
        try:
            params = {'year': year}
            if grand_prix:
                params['grand_prix'] = grand_prix
            
            response = requests.get(
                f"{self.base_url}/sessions",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching sessions: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_meetings(self, year: int) -> pd.DataFrame:
        """Get F1 meetings (races)"""
        try:
            response = requests.get(
                f"{self.base_url}/meetings",
                params={'year': year},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching meetings: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_drivers(self, session_key: Optional[int] = None) -> pd.DataFrame:
        """Get F1 drivers"""
        try:
            params = {}
            if session_key:
                params['session_key'] = session_key
            
            response = requests.get(
                f"{self.base_url}/drivers",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching drivers: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800)
    def get_car_data(self, session_key: int) -> pd.DataFrame:
        """Get car telemetry data"""
        try:
            response = requests.get(
                f"{self.base_url}/car_data",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Convert to numeric where possible
            numeric_cols = ['speed', 'rpm', 'throttle', 'brake', 'drs']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        except Exception as e:
            st.error(f"Error fetching car data: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800)
    def get_laps(self, session_key: int) -> pd.DataFrame:
        """Get lap data"""
        try:
            response = requests.get(
                f"{self.base_url}/laps",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Convert lap time to numeric
            if 'lap_duration' in df.columns:
                df['lap_duration'] = pd.to_numeric(df['lap_duration'], errors='coerce')
            
            return df
        except Exception as e:
            st.error(f"Error fetching laps: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=900)
    def get_position(self, session_key: int) -> pd.DataFrame:
        """Get position data"""
        try:
            response = requests.get(
                f"{self.base_url}/position",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching position data: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=900)
    def get_intervals(self, session_key: int) -> pd.DataFrame:
        """Get interval/gap data"""
        try:
            response = requests.get(
                f"{self.base_url}/intervals",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching intervals: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800)
    def get_pit_stops(self, session_key: int) -> pd.DataFrame:
        """Get pit stop data"""
        try:
            response = requests.get(
                f"{self.base_url}/pit",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching pit data: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800)
    def get_stints(self, session_key: int) -> pd.DataFrame:
        """Get stint data"""
        try:
            response = requests.get(
                f"{self.base_url}/stints",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching stints: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_weather(self, session_key: int) -> pd.DataFrame:
        """Get weather data"""
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching weather: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=1800)
    def get_session_result(self, session_key: int) -> pd.DataFrame:
        """Get session results"""
        try:
            response = requests.get(
                f"{self.base_url}/session_result",
                params={'session_key': session_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching session results: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_championship_drivers(self, year: int) -> pd.DataFrame:
        """Get drivers championship standings"""
        try:
            response = requests.get(
                f"{self.base_url}/championship_drivers",
                params={'year': year},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching drivers championship: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)
    def get_championship_teams(self, year: int) -> pd.DataFrame:
        """Get teams championship standings"""
        try:
            response = requests.get(
                f"{self.base_url}/championship_teams",
                params={'year': year},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching teams championship: {e}")
            return pd.DataFrame()

# Singleton instance
@st.cache_resource
def get_openf1_service() -> OpenF1Service:
    """Get cached OpenF1 service instance"""
    return OpenF1Service()
