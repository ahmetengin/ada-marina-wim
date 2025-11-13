"""
Maritime Service - Main Integration Layer
Coordinates Piri Reis, Poseidon, and Coast Guard services
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.services.pirireis_service import PiriReisService
from app.services.poseidon_service import PoseidonService
from app.services.coast_guard_service import CoastGuardService
from app.models.maritime_weather import MaritimeWeatherForecast, MaritimeCurrentsForecast
from app.schemas.maritime_weather import MarinaWeatherDashboard, WeatherSummary

logger = logging.getLogger(__name__)


class MaritimeService:
    """
    Main maritime service coordinator

    Integrates data from:
    - Piri Reis (Turkish Meteorological Service)
    - Poseidon HCMR (Hellenic Centre for Marine Research)
    - Turkish Coast Guard

    Provides unified maritime intelligence for marina operations
    """

    # Marina location
    MARINA_NAME = "West Istanbul Marina"
    MARINA_LATITUDE = 40.9867
    MARINA_LONGITUDE = 28.7864
    MARINA_REGION_PIRI = "Marmara"
    MARINA_REGION_POSEIDON = "North Aegean"

    # Safety thresholds for marina operations
    SAFETY_THRESHOLDS = {
        "max_wind_knots": 25,
        "max_gust_knots": 35,
        "max_wave_height_meters": 2.5,
        "min_visibility_km": 1.0,
        "max_current_knots": 3.0
    }

    def __init__(self):
        self.piri_reis = PiriReisService()
        self.poseidon = PoseidonService()
        self.coast_guard = CoastGuardService()

    async def close(self):
        """Close all HTTP clients"""
        await self.piri_reis.close()
        await self.poseidon.close()

    def get_weather_dashboard(
        self,
        db: Session
    ) -> MarinaWeatherDashboard:
        """
        Get complete weather dashboard for marina

        Combines data from Piri Reis and Poseidon to provide
        comprehensive maritime intelligence.

        Args:
            db: Database session

        Returns:
            MarinaWeatherDashboard with all current and forecast data
        """
        now = datetime.utcnow()

        # Get latest forecasts from both sources
        piri_latest = self.piri_reis.get_latest_forecast(db, self.MARINA_REGION_PIRI)
        poseidon_latest = self.poseidon.get_latest_forecast(
            db,
            region=self.MARINA_REGION_POSEIDON,
            latitude=self.MARINA_LATITUDE,
            longitude=self.MARINA_LONGITUDE
        )
        poseidon_currents = self.poseidon.get_latest_currents(db, self.MARINA_REGION_POSEIDON)

        # Get forecasts for next 24 hours and 5 days
        piri_24h = self.piri_reis.get_forecast_24h(db, self.MARINA_REGION_PIRI)
        poseidon_5day = self.poseidon.get_forecast_5day(db, self.MARINA_REGION_POSEIDON)

        # Combine forecasts (prefer Piri Reis for Turkish waters, Poseidon for waves/currents)
        all_forecasts = piri_24h + poseidon_5day

        # Determine current conditions (prefer most recent)
        current_weather = piri_latest if piri_latest else poseidon_latest

        # Assess overall safety
        safety_status, warnings = self._assess_safety(
            current_weather,
            poseidon_currents,
            all_forecasts
        )

        # Determine departure and arrival recommendations
        departure_ok, arrival_ok = self._assess_vessel_movements(current_weather, poseidon_currents)

        dashboard = MarinaWeatherDashboard(
            marina_name=self.MARINA_NAME,
            location=f"{self.MARINA_LATITUDE}, {self.MARINA_LONGITUDE}",
            current_time=now,
            current_weather=current_weather,
            current_currents=poseidon_currents,
            weather_forecast=all_forecasts,
            currents_forecast=[poseidon_currents] if poseidon_currents else [],
            overall_safety_status=safety_status,
            departure_recommended=departure_ok,
            arrival_recommended=arrival_ok,
            active_warnings=warnings,
            piri_reis_available=piri_latest is not None,
            poseidon_available=poseidon_latest is not None,
            last_update=now
        )

        return dashboard

    def _assess_safety(
        self,
        current_weather: Optional[MaritimeWeatherForecast],
        current_currents: Optional[MaritimeCurrentsForecast],
        forecasts: List[MaritimeWeatherForecast]
    ) -> tuple[str, List[str]]:
        """
        Assess overall safety status and generate warnings

        Returns:
            Tuple of (status_string, list_of_warnings)
            Status: "safe", "caution", "warning", "danger"
        """
        warnings = []
        danger_level = 0  # 0=safe, 1=caution, 2=warning, 3=danger

        if not current_weather:
            warnings.append("No current weather data available")
            return "caution", warnings

        # Check current conditions
        if current_weather.has_storm_warning == "yes":
            warnings.append("⚠️ STORM WARNING ACTIVE")
            danger_level = max(danger_level, 3)

        if current_weather.wind_speed_knots:
            if current_weather.wind_speed_knots > self.SAFETY_THRESHOLDS["max_wind_knots"]:
                warnings.append(
                    f"⚠️ High wind: {current_weather.wind_speed_knots} knots "
                    f"(threshold: {self.SAFETY_THRESHOLDS['max_wind_knots']})"
                )
                danger_level = max(danger_level, 2)
            elif current_weather.wind_speed_knots > self.SAFETY_THRESHOLDS["max_wind_knots"] * 0.8:
                warnings.append(
                    f"⚡ Moderate wind: {current_weather.wind_speed_knots} knots - exercise caution"
                )
                danger_level = max(danger_level, 1)

        if current_weather.wave_height_meters:
            if current_weather.wave_height_meters > self.SAFETY_THRESHOLDS["max_wave_height_meters"]:
                warnings.append(
                    f"🌊 High waves: {current_weather.wave_height_meters}m "
                    f"(threshold: {self.SAFETY_THRESHOLDS['max_wave_height_meters']}m)"
                )
                danger_level = max(danger_level, 2)

        if current_weather.visibility_km:
            if current_weather.visibility_km < self.SAFETY_THRESHOLDS["min_visibility_km"]:
                warnings.append(
                    f"🌫️ Poor visibility: {current_weather.visibility_km}km "
                    f"(minimum: {self.SAFETY_THRESHOLDS['min_visibility_km']}km)"
                )
                danger_level = max(danger_level, 2)

        if current_currents and current_currents.current_speed_knots:
            if current_currents.current_speed_knots > self.SAFETY_THRESHOLDS["max_current_knots"]:
                warnings.append(
                    f"🌊 Strong currents: {current_currents.current_speed_knots} knots"
                )
                danger_level = max(danger_level, 1)

        # Check forecast for deteriorating conditions
        if forecasts:
            future_dangers = self._check_forecast_dangers(forecasts)
            warnings.extend(future_dangers)

        # Map danger level to status
        status_map = {
            0: "safe",
            1: "caution",
            2: "warning",
            3: "danger"
        }

        if not warnings:
            warnings.append("✅ All conditions normal")

        return status_map[danger_level], warnings

    def _check_forecast_dangers(
        self,
        forecasts: List[MaritimeWeatherForecast]
    ) -> List[str]:
        """Check forecasts for upcoming dangerous conditions"""
        warnings = []
        now = datetime.utcnow()
        next_24h = now + timedelta(hours=24)

        for forecast in forecasts:
            if forecast.valid_from > next_24h:
                continue

            hours_from_now = int((forecast.valid_from - now).total_seconds() / 3600)

            if forecast.has_storm_warning == "yes":
                warnings.append(
                    f"⚠️ Storm warning expected in {hours_from_now}h"
                )

            if forecast.wind_speed_knots and forecast.wind_speed_knots > self.SAFETY_THRESHOLDS["max_wind_knots"]:
                warnings.append(
                    f"⚡ High winds expected in {hours_from_now}h ({forecast.wind_speed_knots} knots)"
                )

        return warnings

    def _assess_vessel_movements(
        self,
        current_weather: Optional[MaritimeWeatherForecast],
        current_currents: Optional[MaritimeCurrentsForecast]
    ) -> tuple[bool, bool]:
        """
        Assess if vessel departures and arrivals are safe

        Returns:
            Tuple of (departure_safe, arrival_safe)
        """
        if not current_weather:
            return False, True  # Safer to stay/enter marina without data

        departure_safe = current_weather.is_safe_for_departure
        arrival_safe = True  # Generally safer to enter marina

        # Additional checks for arrival
        if current_weather.visibility_km and current_weather.visibility_km < 0.5:
            arrival_safe = False  # Very poor visibility unsafe for maneuvering

        if current_currents and current_currents.current_speed_knots:
            if current_currents.current_speed_knots > 4.0:
                arrival_safe = False  # Strong currents make docking dangerous
                departure_safe = False

        return departure_safe, arrival_safe

    def get_weather_summary(
        self,
        db: Session
    ) -> WeatherSummary:
        """
        Get weather summary with current and forecast data

        Args:
            db: Database session

        Returns:
            WeatherSummary object
        """
        # Get current conditions
        piri_current = self.piri_reis.get_latest_forecast(db, self.MARINA_REGION_PIRI)
        poseidon_current = self.poseidon.get_latest_forecast(
            db,
            region=self.MARINA_REGION_POSEIDON
        )

        current = piri_current if piri_current else poseidon_current

        # Get forecasts
        forecast_24h = self.piri_reis.get_forecast_24h(db, self.MARINA_REGION_PIRI)
        forecast_5day = self.poseidon.get_forecast_5day(db, self.MARINA_REGION_POSEIDON)

        # Assess safety
        is_safe = current.is_safe_for_departure if current else True
        safety_warnings = []

        if current:
            if current.has_storm_warning == "yes":
                is_safe = False
                safety_warnings.append("Storm warning active")

            if not current.is_safe_for_departure:
                safety_warnings.append("Conditions unsafe for departure")

        return WeatherSummary(
            current_conditions=current,
            forecast_24h=forecast_24h,
            forecast_5day=forecast_5day,
            is_safe_for_operations=is_safe,
            safety_warnings=safety_warnings,
            last_update_piri_reis=piri_current.forecast_time if piri_current else None,
            last_update_poseidon=poseidon_current.forecast_time if poseidon_current else None
        )

    def check_departure_safety(
        self,
        db: Session,
        vessel_length_meters: float,
        destination_region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if it's safe for a vessel to depart

        Args:
            db: Database session
            vessel_length_meters: Vessel length
            destination_region: Destination region if known

        Returns:
            Dictionary with safety assessment and recommendations
        """
        dashboard = self.get_weather_dashboard(db)

        # Adjust thresholds based on vessel size
        if vessel_length_meters < 12:
            wind_threshold = 20  # Smaller vessels more affected
            wave_threshold = 1.5
        elif vessel_length_meters < 20:
            wind_threshold = 25
            wave_threshold = 2.0
        else:
            wind_threshold = 30
            wave_threshold = 2.5

        is_safe = True
        reasons = []

        if dashboard.current_weather:
            w = dashboard.current_weather

            if w.has_storm_warning == "yes":
                is_safe = False
                reasons.append("Storm warning active")

            if w.wind_speed_knots and w.wind_speed_knots > wind_threshold:
                is_safe = False
                reasons.append(f"Wind speed too high for vessel size: {w.wind_speed_knots} knots")

            if w.wave_height_meters and w.wave_height_meters > wave_threshold:
                is_safe = False
                reasons.append(f"Wave height too high for vessel size: {w.wave_height_meters}m")

            if w.visibility_km and w.visibility_km < 1.0:
                is_safe = False
                reasons.append(f"Poor visibility: {w.visibility_km}km")

        if not reasons:
            reasons.append("All conditions suitable for departure")

        return {
            "is_safe": is_safe,
            "vessel_length_meters": vessel_length_meters,
            "current_conditions": dashboard.current_weather,
            "reasons": reasons,
            "recommendations": self._get_departure_recommendations(
                is_safe,
                dashboard.current_weather
            ),
            "coast_guard_emergency": self.coast_guard.EMERGENCY_NUMBER,
            "vhf_channel": self.coast_guard.MARINA_VHF
        }

    def _get_departure_recommendations(
        self,
        is_safe: bool,
        current_weather: Optional[MaritimeWeatherForecast]
    ) -> List[str]:
        """Generate departure recommendations"""
        if is_safe:
            return [
                "✅ Conditions are suitable for departure",
                "Monitor weather conditions continuously",
                "Keep VHF Channel 72 and 16 active",
                "Inform marina operations of your departure time",
                "Ensure all safety equipment is functional"
            ]
        else:
            return [
                "❌ Departure not recommended",
                "Wait for conditions to improve",
                "Monitor Piri Reis and marina updates",
                "Contact marina operations for updates",
                f"Coast Guard emergency: {self.coast_guard.EMERGENCY_NUMBER}",
                "Ensure vessel is properly secured in berth"
            ]
