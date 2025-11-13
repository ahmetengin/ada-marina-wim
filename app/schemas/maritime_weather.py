"""
Maritime Weather & Sea Conditions Schemas
Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class WeatherSourceEnum(str, Enum):
    """Weather data source"""
    PIRI_REIS = "piri_reis"
    POSEIDON = "poseidon"
    MANUAL = "manual"


class SeaConditionEnum(str, Enum):
    """Sea state conditions"""
    CALM = "calm"
    SLIGHT = "slight"
    MODERATE = "moderate"
    ROUGH = "rough"
    VERY_ROUGH = "very_rough"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MaritimeWeatherBase(BaseModel):
    """Base maritime weather schema"""
    source: WeatherSourceEnum
    forecast_time: datetime
    valid_from: datetime
    valid_to: datetime
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    wind_direction: Optional[str] = None
    wind_speed_knots: Optional[float] = Field(None, ge=0, le=200)
    wind_gust_knots: Optional[float] = Field(None, ge=0, le=250)
    beaufort_scale: Optional[int] = Field(None, ge=0, le=12)

    wave_height_meters: Optional[float] = Field(None, ge=0, le=30)
    wave_direction: Optional[str] = None
    wave_period_seconds: Optional[float] = Field(None, ge=0, le=30)
    sea_condition: Optional[SeaConditionEnum] = None

    air_temp_celsius: Optional[float] = Field(None, ge=-50, le=60)
    water_temp_celsius: Optional[float] = Field(None, ge=-5, le=40)
    visibility_km: Optional[float] = Field(None, ge=0, le=100)

    weather_description: Optional[str] = None
    weather_code: Optional[str] = None

    pressure_hpa: Optional[float] = Field(None, ge=900, le=1100)
    humidity_percent: Optional[float] = Field(None, ge=0, le=100)

    has_storm_warning: Optional[str] = "no"
    warning_level: Optional[str] = None
    warning_description: Optional[str] = None

    raw_data: Optional[Dict[str, Any]] = None


class MaritimeWeatherCreate(MaritimeWeatherBase):
    """Schema for creating maritime weather forecast"""
    pass


class MaritimeWeatherResponse(MaritimeWeatherBase):
    """Schema for maritime weather response"""
    id: int
    is_safe_for_departure: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaritimeCurrentsBase(BaseModel):
    """Base maritime currents schema"""
    forecast_time: datetime
    valid_from: datetime
    valid_to: datetime
    region: str
    latitude: float
    longitude: float
    depth_meters: Optional[float] = None

    current_speed_knots: Optional[float] = Field(None, ge=0, le=20)
    current_direction: Optional[str] = None

    water_temp_celsius: Optional[float] = Field(None, ge=-5, le=40)
    salinity_psu: Optional[float] = Field(None, ge=0, le=50)

    raw_data: Optional[Dict[str, Any]] = None


class MaritimeCurrentsCreate(MaritimeCurrentsBase):
    """Schema for creating currents forecast"""
    pass


class MaritimeCurrentsResponse(MaritimeCurrentsBase):
    """Schema for currents response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherSummary(BaseModel):
    """Summary of current and forecast weather"""
    current_conditions: Optional[MaritimeWeatherResponse] = None
    forecast_24h: list[MaritimeWeatherResponse] = []
    forecast_5day: list[MaritimeWeatherResponse] = []

    is_safe_for_operations: bool = True
    safety_warnings: list[str] = []

    last_update_piri_reis: Optional[datetime] = None
    last_update_poseidon: Optional[datetime] = None


class MarinaWeatherDashboard(BaseModel):
    """Complete weather dashboard for marina operations"""
    marina_name: str
    location: str
    current_time: datetime

    # Current conditions
    current_weather: Optional[MaritimeWeatherResponse] = None
    current_currents: Optional[MaritimeCurrentsResponse] = None

    # Forecasts
    weather_forecast: list[MaritimeWeatherResponse] = []
    currents_forecast: list[MaritimeCurrentsResponse] = []

    # Safety assessment
    overall_safety_status: str = "safe"  # safe, caution, warning, danger
    departure_recommended: bool = True
    arrival_recommended: bool = True

    # Alerts
    active_warnings: list[str] = []

    # Data sources status
    piri_reis_available: bool = False
    poseidon_available: bool = False
    last_update: datetime


class WeatherAlertSubscription(BaseModel):
    """Subscribe to weather alerts"""
    email: Optional[str] = None
    phone: Optional[str] = None
    berth_number: Optional[str] = None
    vessel_name: Optional[str] = None

    # Alert preferences
    alert_on_storm_warning: bool = True
    alert_on_high_wind: bool = True
    alert_on_poor_visibility: bool = True
    wind_threshold_knots: float = 20.0
    wave_threshold_meters: float = 2.0
