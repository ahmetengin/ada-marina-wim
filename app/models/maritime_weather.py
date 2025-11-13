"""
Maritime Weather & Sea Conditions Models
Integrates Piri Reis and Poseidon HCMR data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum as SQLEnum, Text
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class WeatherSource(str, enum.Enum):
    """Weather data source"""
    PIRI_REIS = "piri_reis"  # Turkish Meteorological Service
    POSEIDON = "poseidon"     # HCMR Greek system
    MANUAL = "manual"         # Manually entered


class SeaCondition(str, enum.Enum):
    """Sea state conditions"""
    CALM = "calm"              # Dalga yüksekliği < 0.5m
    SLIGHT = "slight"          # 0.5-1.25m
    MODERATE = "moderate"      # 1.25-2.5m
    ROUGH = "rough"            # 2.5-4m
    VERY_ROUGH = "very_rough"  # 4-6m
    HIGH = "high"              # 6-9m
    VERY_HIGH = "very_high"    # > 9m


class MaritimeWeatherForecast(Base):
    """
    Maritime Weather Forecasts from Piri Reis and Poseidon

    Stores weather and sea condition forecasts for marina operations.
    Critical for vessel safety and operational planning.
    """
    __tablename__ = "maritime_weather_forecasts"

    id = Column(Integer, primary_key=True, index=True)

    # Source and timing
    source = Column(SQLEnum(WeatherSource), nullable=False, index=True)
    forecast_time = Column(DateTime(timezone=True), nullable=False, index=True)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=False)

    # Location
    region = Column(String(100), nullable=False, index=True)  # e.g., "Marmara", "North Aegean"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Wind conditions
    wind_direction = Column(String(20), nullable=True)  # e.g., "NE", "SW", "Poyraz"
    wind_speed_knots = Column(Float, nullable=True)
    wind_gust_knots = Column(Float, nullable=True)
    beaufort_scale = Column(Integer, nullable=True)  # 0-12 Beaufort

    # Wave conditions
    wave_height_meters = Column(Float, nullable=True)
    wave_direction = Column(String(20), nullable=True)
    wave_period_seconds = Column(Float, nullable=True)
    sea_condition = Column(SQLEnum(SeaCondition), nullable=True, index=True)

    # Temperature and visibility
    air_temp_celsius = Column(Float, nullable=True)
    water_temp_celsius = Column(Float, nullable=True)
    visibility_km = Column(Float, nullable=True)

    # Weather description
    weather_description = Column(Text, nullable=True)
    weather_code = Column(String(50), nullable=True)

    # Pressure and humidity
    pressure_hpa = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)

    # Storm warnings
    has_storm_warning = Column(SQLEnum(enum.Enum("YesNo", {"YES": "yes", "NO": "no"})), default="no")
    warning_level = Column(String(20), nullable=True)  # yellow, orange, red
    warning_description = Column(Text, nullable=True)

    # Raw data from source
    raw_data = Column(JSON, nullable=True)  # Original API response

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MaritimeWeather {self.source} - {self.region} @ {self.forecast_time}>"

    @property
    def is_safe_for_departure(self) -> bool:
        """
        Determine if conditions are safe for vessel departure
        Based on WIM regulations and maritime safety standards
        """
        # Basic safety checks
        if self.has_storm_warning == "yes":
            return False

        if self.wind_speed_knots and self.wind_speed_knots > 25:  # > 25 knots unsafe
            return False

        if self.wave_height_meters and self.wave_height_meters > 2.5:  # > 2.5m unsafe
            return False

        if self.visibility_km and self.visibility_km < 1.0:  # < 1km poor visibility
            return False

        return True


class MaritimeCurrentsForecast(Base):
    """
    Sea Currents & Hydrodynamic Data from Poseidon HCMR

    Critical for navigation and marina operations.
    Poseidon provides 5-day hydrodynamic forecasts for Aegean and Mediterranean.
    """
    __tablename__ = "maritime_currents_forecasts"

    id = Column(Integer, primary_key=True, index=True)

    # Source and timing
    forecast_time = Column(DateTime(timezone=True), nullable=False, index=True)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=False)

    # Location
    region = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth_meters = Column(Float, nullable=True)  # Water depth

    # Current data
    current_speed_knots = Column(Float, nullable=True)
    current_direction = Column(String(20), nullable=True)

    # Salinity and temperature
    water_temp_celsius = Column(Float, nullable=True)
    salinity_psu = Column(Float, nullable=True)  # Practical Salinity Units

    # Raw data
    raw_data = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MaritimeCurrents {self.region} @ {self.forecast_time}>"
