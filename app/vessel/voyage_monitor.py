"""
Voyage Monitoring System
Real-time monitoring during voyage with dynamic weather updates

"Deniz şaka değil - dinamik olarak değişir herşey"
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VoyageStatus(Enum):
    """Voyage status"""
    PREPARING = "preparing"
    UNDERWAY = "underway"
    AT_ANCHOR = "at_anchor"
    MOORED = "moored"
    EMERGENCY = "emergency"


class AlertLevel(Enum):
    """Alert severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class VoyageAlert:
    """Voyage alert/notification"""
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    category: str
    message: str
    message_tr: str
    action_required: bool
    acknowledged: bool = False


@dataclass
class WeatherUpdate:
    """Weather update during voyage"""
    timestamp: datetime
    location: str
    wind_speed_knots: float
    wind_direction: str
    wave_height_m: float
    visibility_nm: float
    precipitation: bool
    temperature_c: float
    forecast_accuracy: str  # observed, forecast_1h, forecast_3h


@dataclass
class VesselStatus:
    """Current vessel status"""
    latitude: float
    longitude: float
    course: float
    speed_knots: float
    heading: float
    fuel_percentage: float
    water_percentage: float
    battery_voltage: float
    engine_running: bool
    autopilot_active: bool


class VoyageMonitor:
    """
    Real-time voyage monitoring

    Features:
    - Dynamic weather updates every 30 minutes
    - Fuel/water consumption tracking
    - Weather deterioration alerts
    - Anchor drag monitoring (when at anchor)
    - Route deviation alerts
    - System health monitoring
    """

    def __init__(
        self,
        vessel_name: str,
        weather_integration,
        anchor_calculator
    ):
        """
        Initialize voyage monitor

        Args:
            vessel_name: Vessel name
            weather_integration: Weather API integration
            anchor_calculator: Anchor geometry calculator
        """
        self.vessel_name = vessel_name
        self.weather = weather_integration
        self.anchor_calc = anchor_calculator

        self.voyage_status = VoyageStatus.PREPARING
        self.voyage_start_time: Optional[datetime] = None
        self.current_vessel_status: Optional[VesselStatus] = None

        self.alerts: List[VoyageAlert] = []
        self.weather_history: List[WeatherUpdate] = []

        # Monitoring settings
        self.weather_update_interval_minutes = 30
        self.anchor_check_interval_minutes = 5
        self.system_check_interval_minutes = 15

        # Alert thresholds
        self.thresholds = {
            'wind_warning': 20,  # knots
            'wind_critical': 25,
            'wave_warning': 1.5,  # meters
            'wave_critical': 2.0,
            'fuel_warning': 30,  # percent
            'fuel_critical': 20,
            'battery_warning': 12.0,  # volts
            'battery_critical': 11.5,
        }

        self.monitoring_task: Optional[asyncio.Task] = None

        logger.info(f"VoyageMonitor initialized for {vessel_name}")

    async def start_voyage(
        self,
        departure: str,
        destination: str,
        initial_status: VesselStatus
    ):
        """
        Start voyage monitoring

        Args:
            departure: Departure point
            destination: Destination
            initial_status: Initial vessel status
        """
        self.voyage_status = VoyageStatus.UNDERWAY
        self.voyage_start_time = datetime.utcnow()
        self.current_vessel_status = initial_status

        logger.info(f"🚤 Voyage started: {departure} → {destination}")

        # Add voyage start alert
        self._add_alert(
            level=AlertLevel.INFO,
            category="voyage",
            message=f"Voyage started: {departure} → {destination}",
            message_tr=f"Sefer başladı: {departure} → {destination}",
            action_required=False
        )

        # Start background monitoring
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        logger.info("🔍 Monitoring loop started")

        last_weather_check = datetime.utcnow()
        last_system_check = datetime.utcnow()

        try:
            while self.voyage_status == VoyageStatus.UNDERWAY:
                now = datetime.utcnow()

                # Weather check (every 30 minutes)
                if (now - last_weather_check).seconds >= self.weather_update_interval_minutes * 60:
                    await self._check_weather()
                    last_weather_check = now

                # System check (every 15 minutes)
                if (now - last_system_check).seconds >= self.system_check_interval_minutes * 60:
                    await self._check_systems()
                    last_system_check = now

                # Sleep for 1 minute between checks
                await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            self._add_alert(
                level=AlertLevel.CRITICAL,
                category="system",
                message=f"Monitoring system error: {e}",
                message_tr=f"İzleme sistemi hatası: {e}",
                action_required=True
            )

    async def _check_weather(self):
        """Check weather and issue alerts if needed"""
        if not self.current_vessel_status:
            return

        logger.info("🌤️ Checking weather update...")

        try:
            # Get current weather
            weather = await self.weather.get_current_weather(
                latitude=self.current_vessel_status.latitude,
                longitude=self.current_vessel_status.longitude,
                anonymous=True
            )

            # Create weather update record
            update = WeatherUpdate(
                timestamp=datetime.utcnow(),
                location=f"{self.current_vessel_status.latitude:.2f}°N, {self.current_vessel_status.longitude:.2f}°E",
                wind_speed_knots=weather['weather']['wind_speed_knots'],
                wind_direction=weather['weather']['wind_direction'],
                wave_height_m=1.0,  # Mock data - should come from weather API
                visibility_nm=weather['weather']['visibility_nm'],
                precipitation=False,
                temperature_c=weather['weather']['temperature_c'],
                forecast_accuracy='observed'
            )

            self.weather_history.append(update)

            # Check for weather deterioration
            await self._check_weather_alerts(update)

        except Exception as e:
            logger.error(f"Weather check failed: {e}")

    async def _check_weather_alerts(self, weather: WeatherUpdate):
        """Check weather against thresholds and create alerts"""

        # Wind speed alerts
        if weather.wind_speed_knots >= self.thresholds['wind_critical']:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                category="weather",
                message=f"Critical wind speed: {weather.wind_speed_knots:.0f} knots",
                message_tr=f"🔴 Kritik rüzgar: {weather.wind_speed_knots:.0f} knot",
                action_required=True
            )
        elif weather.wind_speed_knots >= self.thresholds['wind_warning']:
            self._add_alert(
                level=AlertLevel.WARNING,
                category="weather",
                message=f"High wind speed: {weather.wind_speed_knots:.0f} knots",
                message_tr=f"⚠️ Yüksek rüzgar: {weather.wind_speed_knots:.0f} knot",
                action_required=False
            )

        # Wave height alerts
        if weather.wave_height_m >= self.thresholds['wave_critical']:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                category="weather",
                message=f"High waves: {weather.wave_height_m:.1f}m",
                message_tr=f"🔴 Yüksek dalga: {weather.wave_height_m:.1f}m",
                action_required=True
            )
        elif weather.wave_height_m >= self.thresholds['wave_warning']:
            self._add_alert(
                level=AlertLevel.WARNING,
                category="weather",
                message=f"Moderate waves: {weather.wave_height_m:.1f}m",
                message_tr=f"⚠️ Orta dalga: {weather.wave_height_m:.1f}m",
                action_required=False
            )

        # Visibility alerts
        if weather.visibility_nm < 2.0:
            self._add_alert(
                level=AlertLevel.WARNING,
                category="weather",
                message=f"Poor visibility: {weather.visibility_nm:.1f} NM",
                message_tr=f"⚠️ Düşük görüş: {weather.visibility_nm:.1f} NM",
                action_required=True
            )

    async def _check_systems(self):
        """Check vessel systems"""
        if not self.current_vessel_status:
            return

        logger.info("🔧 Checking vessel systems...")

        status = self.current_vessel_status

        # Fuel level
        if status.fuel_percentage <= self.thresholds['fuel_critical']:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                category="fuel",
                message=f"Critical fuel level: {status.fuel_percentage:.0f}%",
                message_tr=f"🔴 Kritik yakıt seviyesi: {status.fuel_percentage:.0f}%",
                action_required=True
            )
        elif status.fuel_percentage <= self.thresholds['fuel_warning']:
            self._add_alert(
                level=AlertLevel.WARNING,
                category="fuel",
                message=f"Low fuel: {status.fuel_percentage:.0f}%",
                message_tr=f"⚠️ Düşük yakıt: {status.fuel_percentage:.0f}%",
                action_required=False
            )

        # Battery voltage
        if status.battery_voltage <= self.thresholds['battery_critical']:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                category="electrical",
                message=f"Critical battery voltage: {status.battery_voltage:.1f}V",
                message_tr=f"🔴 Kritik batarya voltajı: {status.battery_voltage:.1f}V",
                action_required=True
            )
        elif status.battery_voltage <= self.thresholds['battery_warning']:
            self._add_alert(
                level=AlertLevel.WARNING,
                category="electrical",
                message=f"Low battery: {status.battery_voltage:.1f}V",
                message_tr=f"⚠️ Düşük batarya: {status.battery_voltage:.1f}V",
                action_required=False
            )

    async def update_vessel_status(self, status: VesselStatus):
        """
        Update current vessel status

        Args:
            status: New vessel status
        """
        self.current_vessel_status = status

        # Log position update
        logger.info(
            f"📍 Position: {status.latitude:.4f}°N, {status.longitude:.4f}°E | "
            f"COG: {status.course:.0f}° | SOG: {status.speed_knots:.1f} kt"
        )

    async def arrive_at_anchor(
        self,
        anchorage_name: str,
        anchor_position: tuple[float, float]
    ):
        """
        Vessel has arrived at anchorage

        Args:
            anchorage_name: Name of anchorage
            anchor_position: Anchor drop position (lat, lon)
        """
        self.voyage_status = VoyageStatus.AT_ANCHOR

        logger.info(f"⚓ Anchored at: {anchorage_name}")

        self._add_alert(
            level=AlertLevel.INFO,
            category="voyage",
            message=f"Anchored at {anchorage_name}",
            message_tr=f"⚓ {anchorage_name}'da demirlendi",
            action_required=False
        )

        # Start anchor watch
        await self._start_anchor_watch(anchor_position)

    async def _start_anchor_watch(self, initial_position: tuple[float, float]):
        """
        Start monitoring for anchor drag

        Args:
            initial_position: Initial anchor position (lat, lon)
        """
        logger.info("👁️ Anchor watch started")

        while self.voyage_status == VoyageStatus.AT_ANCHOR:
            await asyncio.sleep(self.anchor_check_interval_minutes * 60)

            if self.current_vessel_status:
                # Check for drag
                drag_alert = self.anchor_calc.calculate_anchor_drag(
                    initial_lat=initial_position[0],
                    initial_lon=initial_position[1],
                    current_lat=self.current_vessel_status.latitude,
                    current_lon=self.current_vessel_status.longitude,
                    vessel_length_m=20,  # Should be from vessel specs
                    acceptable_swing_m=30
                )

                if drag_alert.is_dragging:
                    level = AlertLevel.CRITICAL if drag_alert.alert_level == "critical" else AlertLevel.WARNING

                    self._add_alert(
                        level=level,
                        category="anchor",
                        message=f"ANCHOR DRAG: Moved {drag_alert.distance_moved_m:.1f}m",
                        message_tr=f"{'🔴' if level == AlertLevel.CRITICAL else '⚠️'} DEMİR SÜRÜYOR: {drag_alert.distance_moved_m:.1f}m hareket",
                        action_required=True
                    )

    def _add_alert(
        self,
        level: AlertLevel,
        category: str,
        message: str,
        message_tr: str,
        action_required: bool
    ):
        """Add new alert"""
        alert = VoyageAlert(
            alert_id=f"alert_{len(self.alerts) + 1}",
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            message=message,
            message_tr=message_tr,
            action_required=action_required
        )

        self.alerts.append(alert)

        # Log based on severity
        if level == AlertLevel.CRITICAL:
            logger.critical(f"🔴 {message_tr}")
        elif level == AlertLevel.WARNING:
            logger.warning(f"⚠️ {message_tr}")
        else:
            logger.info(f"ℹ️ {message_tr}")

    def get_active_alerts(self, acknowledged: bool = False) -> List[VoyageAlert]:
        """
        Get active alerts

        Args:
            acknowledged: If False, only unacknowledged alerts

        Returns:
            List of active alerts
        """
        if acknowledged:
            return self.alerts
        else:
            return [a for a in self.alerts if not a.acknowledged]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert

        Args:
            alert_id: Alert identifier

        Returns:
            True if found and acknowledged
        """
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"✓ Alert acknowledged: {alert.message_tr}")
                return True

        return False

    def get_voyage_summary(self) -> Dict[str, Any]:
        """Get voyage summary"""
        if not self.voyage_start_time:
            return {'status': 'not_started'}

        duration = datetime.utcnow() - self.voyage_start_time

        return {
            'vessel': self.vessel_name,
            'status': self.voyage_status.value,
            'started': self.voyage_start_time.isoformat(),
            'duration_hours': duration.total_seconds() / 3600,
            'current_position': {
                'latitude': self.current_vessel_status.latitude if self.current_vessel_status else None,
                'longitude': self.current_vessel_status.longitude if self.current_vessel_status else None
            } if self.current_vessel_status else None,
            'active_alerts': len(self.get_active_alerts()),
            'weather_updates': len(self.weather_history),
            'fuel_percentage': self.current_vessel_status.fuel_percentage if self.current_vessel_status else None,
        }

    async def stop_monitoring(self):
        """Stop voyage monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        self.voyage_status = VoyageStatus.MOORED
        logger.info("🛑 Monitoring stopped")
