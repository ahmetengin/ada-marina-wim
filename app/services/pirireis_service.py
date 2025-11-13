"""
Piri Reis Maritime Weather Service
MGM Meteoroloji Genel Müdürlüğü - Piri Reis Denizcilik Sayfaları
https://pirireis.mgm.gov.tr
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import httpx
from sqlalchemy.orm import Session

from app.models.maritime_weather import MaritimeWeatherForecast, WeatherSource, SeaCondition
from app.schemas.maritime_weather import MaritimeWeatherCreate

logger = logging.getLogger(__name__)


class PiriReisService:
    """
    Piri Reis weather service integration

    Provides maritime weather forecasts for Turkish waters:
    - 24-hour forecasts
    - 3-day and 5-day forecasts
    - Specific marina forecasts
    - Wind, wave, visibility data
    """

    BASE_URL = "https://pirireis.mgm.gov.tr"

    # Marina specific endpoints (West Istanbul Marina)
    MARINA_IDS = {
        "west_istanbul": 100,  # Example ID - needs to be verified
        "marmara_region": "marmara"
    }

    # Turkish wind directions to international
    WIND_DIRECTION_MAP = {
        "Poyraz": "NE",
        "Gündoğusu": "E",
        "Keşişleme": "SE",
        "Lodos": "SW",
        "Günbatısı": "W",
        "Karayel": "NW",
        "Yıldız": "N",
        "Kıble": "S"
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

    def _parse_wind_direction(self, direction_tr: str) -> str:
        """Convert Turkish wind direction to international"""
        return self.WIND_DIRECTION_MAP.get(direction_tr, direction_tr)

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

    async def fetch_marmara_forecast(self, db: Session) -> Optional[MaritimeWeatherForecast]:
        """
        Fetch Marmara region weather forecast

        Returns latest forecast for Marmara Sea region
        """
        try:
            logger.info("Fetching Piri Reis forecast for Marmara region")

            # Since we can't directly access the API, we'll create a mock/template
            # In production, this would make actual HTTP requests to Piri Reis API
            # The API structure would need to be determined from documentation

            # For now, we'll return None to indicate data should be fetched manually
            # or through an alternative method

            logger.warning("Piri Reis API integration requires authentication/API key")
            logger.info("Weather data should be fetched manually from https://pirireis.mgm.gov.tr")

            return None

        except Exception as e:
            logger.error(f"Error fetching Piri Reis forecast: {e}")
            return None

    async def fetch_marina_forecast(
        self,
        marina_id: int,
        db: Session
    ) -> Optional[MaritimeWeatherForecast]:
        """
        Fetch marina-specific weather forecast

        Args:
            marina_id: Marina ID in Piri Reis system
            db: Database session

        Returns:
            MaritimeWeatherForecast object or None
        """
        try:
            logger.info(f"Fetching Piri Reis forecast for marina {marina_id}")

            # URL would be: https://pirireis.mgm.gov.tr/marinalar/{marina_id}
            # This requires parsing the HTML or using an API if available

            logger.warning("Direct API access not available - manual data entry required")
            return None

        except Exception as e:
            logger.error(f"Error fetching marina forecast: {e}")
            return None

    def create_manual_forecast(
        self,
        db: Session,
        region: str = "Marmara",
        wind_direction: Optional[str] = None,
        wind_speed_knots: Optional[float] = None,
        wave_height_meters: Optional[float] = None,
        visibility_km: Optional[float] = None,
        weather_description: Optional[str] = None,
        forecast_hours: int = 24
    ) -> MaritimeWeatherForecast:
        """
        Create a manual weather forecast entry

        Use this when automatic fetching is not available.
        Data should be manually entered from Piri Reis website.

        Args:
            db: Database session
            region: Region name (e.g., "Marmara")
            wind_direction: Wind direction
            wind_speed_knots: Wind speed in knots
            wave_height_meters: Wave height in meters
            visibility_km: Visibility in kilometers
            weather_description: Text description
            forecast_hours: Forecast duration in hours

        Returns:
            Created MaritimeWeatherForecast object
        """
        now = datetime.utcnow()

        # Convert Turkish wind direction if needed
        if wind_direction and wind_direction in self.WIND_DIRECTION_MAP:
            wind_direction = self._parse_wind_direction(wind_direction)

        # Determine sea condition
        sea_condition = self._determine_sea_condition(wave_height_meters)

        # Create forecast
        forecast = MaritimeWeatherForecast(
            source=WeatherSource.PIRI_REIS,
            forecast_time=now,
            valid_from=now,
            valid_to=now + timedelta(hours=forecast_hours),
            region=region,
            latitude=40.9867,  # West Istanbul Marina approximate
            longitude=28.7864,
            wind_direction=wind_direction,
            wind_speed_knots=wind_speed_knots,
            wave_height_meters=wave_height_meters,
            sea_condition=sea_condition,
            visibility_km=visibility_km,
            weather_description=weather_description,
            has_storm_warning="no",
            raw_data={"source": "manual_entry", "entry_time": now.isoformat()}
        )

        db.add(forecast)
        db.commit()
        db.refresh(forecast)

        logger.info(f"Created manual Piri Reis forecast for {region}")
        return forecast

    def get_latest_forecast(
        self,
        db: Session,
        region: str = "Marmara"
    ) -> Optional[MaritimeWeatherForecast]:
        """
        Get latest forecast from database

        Args:
            db: Database session
            region: Region name

        Returns:
            Latest forecast or None
        """
        forecast = db.query(MaritimeWeatherForecast).filter(
            MaritimeWeatherForecast.source == WeatherSource.PIRI_REIS,
            MaritimeWeatherForecast.region == region,
            MaritimeWeatherForecast.valid_to > datetime.utcnow()
        ).order_by(
            MaritimeWeatherForecast.forecast_time.desc()
        ).first()

        return forecast

    def get_forecast_24h(
        self,
        db: Session,
        region: str = "Marmara"
    ) -> List[MaritimeWeatherForecast]:
        """
        Get all forecasts for next 24 hours

        Args:
            db: Database session
            region: Region name

        Returns:
            List of forecasts
        """
        now = datetime.utcnow()
        future_24h = now + timedelta(hours=24)

        forecasts = db.query(MaritimeWeatherForecast).filter(
            MaritimeWeatherForecast.source == WeatherSource.PIRI_REIS,
            MaritimeWeatherForecast.region == region,
            MaritimeWeatherForecast.valid_from >= now,
            MaritimeWeatherForecast.valid_from <= future_24h
        ).order_by(
            MaritimeWeatherForecast.valid_from
        ).all()

        return forecasts
