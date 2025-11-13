"""
Poseidon HCMR Marine Forecasting Service
Hellenic Centre for Marine Research
https://poseidon.hcmr.gr
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import httpx
from sqlalchemy.orm import Session

from app.models.maritime_weather import (
    MaritimeWeatherForecast,
    MaritimeCurrentsForecast,
    WeatherSource,
    SeaCondition
)

logger = logging.getLogger(__name__)


class PoseidonService:
    """
    Poseidon HCMR marine forecasting service

    Provides:
    - 5-day ocean forecasts for Aegean and Mediterranean
    - Hydrodynamic models (currents, temperature, salinity)
    - Wave forecasts
    - High-resolution Aegean Sea model (1/30°)
    - Integration with Copernicus CMEMS
    """

    BASE_URL = "https://poseidon.hcmr.gr"

    # Coverage area for Poseidon Aegean model
    AEGEAN_BOUNDS = {
        "min_lat": 30.4,
        "max_lat": 41.0,
        "min_lon": 19.5,
        "max_lon": 30.0
    }

    # Key forecast regions
    REGIONS = {
        "north_aegean": "North Aegean",
        "south_aegean": "South Aegean",
        "eastern_mediterranean": "Eastern Mediterranean",
        "marmara_dardanelles": "Marmara - Dardanelles"
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.session is None:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self.session

    async def close(self):
        """Close HTTP client"""
        if self.session:
            await self.session.aclose()
            self.session = None

    def _determine_sea_condition(self, wave_height: Optional[float]) -> Optional[SeaCondition]:
        """Determine sea condition from wave height"""
        if wave_height is None:
            return None

        if wave_height < 0.5:
            return SeaCondition.CALM
        elif wave_height < 1.25:
            return SeaCondition.SLIGHT
        elif wave_height < 2.5:
            return SeaCondition.MODERATE
        elif wave_height < 4.0:
            return SeaCondition.ROUGH
        elif wave_height < 6.0:
            return SeaCondition.VERY_ROUGH
        elif wave_height < 9.0:
            return SeaCondition.HIGH
        else:
            return SeaCondition.VERY_HIGH

    def is_location_in_coverage(self, latitude: float, longitude: float) -> bool:
        """
        Check if location is within Poseidon Aegean model coverage

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees

        Returns:
            True if location is covered
        """
        return (
            self.AEGEAN_BOUNDS["min_lat"] <= latitude <= self.AEGEAN_BOUNDS["max_lat"] and
            self.AEGEAN_BOUNDS["min_lon"] <= longitude <= self.AEGEAN_BOUNDS["max_lon"]
        )

    async def fetch_aegean_forecast(
        self,
        db: Session,
        latitude: float = 40.9867,
        longitude: float = 28.7864
    ) -> Optional[MaritimeWeatherForecast]:
        """
        Fetch Aegean Sea forecast for specific location

        Args:
            db: Database session
            latitude: Latitude (default: West Istanbul Marina)
            longitude: Longitude

        Returns:
            MaritimeWeatherForecast or None
        """
        try:
            logger.info(f"Fetching Poseidon forecast for {latitude}, {longitude}")

            # Check if location is in coverage
            if not self.is_location_in_coverage(latitude, longitude):
                logger.warning(f"Location {latitude}, {longitude} outside Poseidon coverage")
                return None

            # The Poseidon system requires either:
            # 1. Web scraping from the forecast pages
            # 2. Access to their data files (NetCDF/GRIB)
            # 3. API access (if available)

            # For production, implement one of these methods
            logger.warning("Poseidon API integration requires data access setup")
            logger.info("Forecast data available at: https://poseidon.hcmr.gr/services/forecast")

            return None

        except Exception as e:
            logger.error(f"Error fetching Poseidon forecast: {e}")
            return None

    async def fetch_currents_forecast(
        self,
        db: Session,
        latitude: float = 40.9867,
        longitude: float = 28.7864,
        depth_meters: Optional[float] = None
    ) -> Optional[MaritimeCurrentsForecast]:
        """
        Fetch sea currents forecast from Poseidon hydrodynamic model

        Args:
            db: Database session
            latitude: Latitude
            longitude: Longitude
            depth_meters: Water depth (None for surface)

        Returns:
            MaritimeCurrentsForecast or None
        """
        try:
            logger.info(f"Fetching Poseidon currents for {latitude}, {longitude}")

            # Currents data would come from Poseidon's hydrodynamic model
            # This requires accessing their model output files or API

            logger.warning("Poseidon currents data requires model output access")
            return None

        except Exception as e:
            logger.error(f"Error fetching Poseidon currents: {e}")
            return None

    def create_manual_forecast(
        self,
        db: Session,
        region: str = "North Aegean",
        latitude: float = 40.9867,
        longitude: float = 28.7864,
        wind_speed_knots: Optional[float] = None,
        wind_direction: Optional[str] = None,
        wave_height_meters: Optional[float] = None,
        wave_direction: Optional[str] = None,
        wave_period_seconds: Optional[float] = None,
        water_temp_celsius: Optional[float] = None,
        forecast_hours: int = 24
    ) -> MaritimeWeatherForecast:
        """
        Create manual Poseidon forecast entry

        Use this to manually enter data from Poseidon website.

        Args:
            db: Database session
            region: Region name
            latitude: Latitude
            longitude: Longitude
            wind_speed_knots: Wind speed
            wind_direction: Wind direction
            wave_height_meters: Significant wave height
            wave_direction: Wave direction
            wave_period_seconds: Wave period
            water_temp_celsius: Sea surface temperature
            forecast_hours: Forecast duration

        Returns:
            Created MaritimeWeatherForecast
        """
        now = datetime.utcnow()

        sea_condition = self._determine_sea_condition(wave_height_meters)

        forecast = MaritimeWeatherForecast(
            source=WeatherSource.POSEIDON,
            forecast_time=now,
            valid_from=now,
            valid_to=now + timedelta(hours=forecast_hours),
            region=region,
            latitude=latitude,
            longitude=longitude,
            wind_direction=wind_direction,
            wind_speed_knots=wind_speed_knots,
            wave_height_meters=wave_height_meters,
            wave_direction=wave_direction,
            wave_period_seconds=wave_period_seconds,
            sea_condition=sea_condition,
            water_temp_celsius=water_temp_celsius,
            has_storm_warning="no",
            raw_data={"source": "manual_entry", "model": "Poseidon HCMR"}
        )

        db.add(forecast)
        db.commit()
        db.refresh(forecast)

        logger.info(f"Created manual Poseidon forecast for {region}")
        return forecast

    def create_manual_currents(
        self,
        db: Session,
        region: str = "North Aegean",
        latitude: float = 40.9867,
        longitude: float = 28.7864,
        current_speed_knots: Optional[float] = None,
        current_direction: Optional[str] = None,
        water_temp_celsius: Optional[float] = None,
        salinity_psu: Optional[float] = None,
        depth_meters: Optional[float] = None,
        forecast_hours: int = 24
    ) -> MaritimeCurrentsForecast:
        """
        Create manual currents forecast entry

        Args:
            db: Database session
            region: Region name
            latitude: Latitude
            longitude: Longitude
            current_speed_knots: Current speed
            current_direction: Current direction
            water_temp_celsius: Water temperature
            salinity_psu: Salinity in PSU
            depth_meters: Depth
            forecast_hours: Forecast duration

        Returns:
            Created MaritimeCurrentsForecast
        """
        now = datetime.utcnow()

        currents = MaritimeCurrentsForecast(
            forecast_time=now,
            valid_from=now,
            valid_to=now + timedelta(hours=forecast_hours),
            region=region,
            latitude=latitude,
            longitude=longitude,
            depth_meters=depth_meters,
            current_speed_knots=current_speed_knots,
            current_direction=current_direction,
            water_temp_celsius=water_temp_celsius,
            salinity_psu=salinity_psu,
            raw_data={"source": "manual_entry", "model": "Poseidon HCMR"}
        )

        db.add(currents)
        db.commit()
        db.refresh(currents)

        logger.info(f"Created manual Poseidon currents for {region}")
        return currents

    def get_latest_forecast(
        self,
        db: Session,
        region: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[MaritimeWeatherForecast]:
        """Get latest Poseidon forecast from database"""
        query = db.query(MaritimeWeatherForecast).filter(
            MaritimeWeatherForecast.source == WeatherSource.POSEIDON,
            MaritimeWeatherForecast.valid_to > datetime.utcnow()
        )

        if region:
            query = query.filter(MaritimeWeatherForecast.region == region)

        if latitude and longitude:
            # Find nearest forecast (simple distance calc)
            # In production, use proper geospatial queries
            query = query.filter(
                MaritimeWeatherForecast.latitude.between(latitude - 0.5, latitude + 0.5),
                MaritimeWeatherForecast.longitude.between(longitude - 0.5, longitude + 0.5)
            )

        return query.order_by(MaritimeWeatherForecast.forecast_time.desc()).first()

    def get_latest_currents(
        self,
        db: Session,
        region: Optional[str] = None
    ) -> Optional[MaritimeCurrentsForecast]:
        """Get latest currents forecast from database"""
        query = db.query(MaritimeCurrentsForecast).filter(
            MaritimeCurrentsForecast.valid_to > datetime.utcnow()
        )

        if region:
            query = query.filter(MaritimeCurrentsForecast.region == region)

        return query.order_by(MaritimeCurrentsForecast.forecast_time.desc()).first()

    def get_forecast_5day(
        self,
        db: Session,
        region: str = "North Aegean"
    ) -> List[MaritimeWeatherForecast]:
        """Get 5-day forecast from database"""
        now = datetime.utcnow()
        future_5d = now + timedelta(days=5)

        forecasts = db.query(MaritimeWeatherForecast).filter(
            MaritimeWeatherForecast.source == WeatherSource.POSEIDON,
            MaritimeWeatherForecast.region == region,
            MaritimeWeatherForecast.valid_from >= now,
            MaritimeWeatherForecast.valid_from <= future_5d
        ).order_by(
            MaritimeWeatherForecast.valid_from
        ).all()

        return forecasts
