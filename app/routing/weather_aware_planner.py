"""
Weather-Aware Route Planning
Intelligent route planning with wind, weather, and vessel type consideration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VesselType(Enum):
    """Vessel type for route planning"""
    SAILING = "sailing"  # Yelkenli
    MOTOR = "motor"      # Motorlu
    MOTOR_SAILING = "motor_sailing"  # Motor-yelkenli


class WindDirection(Enum):
    """Wind direction (8-point compass)"""
    N = "N"    # Kuzey
    NE = "NE"  # Kuzeydoğu
    E = "E"    # Doğu
    SE = "SE"  # Güneydoğu
    S = "S"    # Güney
    SW = "SW"  # Güneybatı
    W = "W"    # Batı
    NW = "NW"  # Kuzeybatı


@dataclass
class WeatherConditions:
    """Weather conditions for route planning"""
    timestamp: datetime
    wind_speed_knots: float
    wind_direction: WindDirection
    gust_speed_knots: Optional[float]
    wave_height_m: float
    visibility_nm: float
    precipitation: bool
    temperature_c: float
    pressure_mb: float
    sea_state: str  # calm, moderate, rough, very_rough


@dataclass
class Anchorage:
    """Anchorage information with wind protection"""
    id: str
    name: str
    name_tr: str  # Turkish name
    latitude: float
    longitude: float
    depth_min_m: float
    depth_max_m: float
    bottom_type: str  # sand, mud, rock, weed
    holding: str  # excellent, good, fair, poor

    # Wind protection (which directions are sheltered)
    protected_from: List[WindDirection]
    exposed_to: List[WindDirection]

    # Facilities
    has_mooring_buoys: bool = False
    has_water: bool = False
    has_restaurant: bool = False
    has_electricity: bool = False

    # Capacity
    max_vessels: Optional[int] = None
    suitable_for_length: Optional[float] = None  # Max vessel length in feet

    # Rating
    rating: float = 0.0  # 0-5 stars
    review_count: int = 0


@dataclass
class RouteSegment:
    """Single segment of route"""
    from_point: str
    to_point: str
    distance_nm: float
    bearing: float
    estimated_time_hours: float
    weather_forecast: Optional[WeatherConditions]
    comfort_score: float  # 0-10 (10 = very comfortable)
    recommended: bool
    warnings: List[str]


@dataclass
class RouteRecommendation:
    """Complete route recommendation"""
    vessel_name: str
    vessel_type: VesselType
    departure: str
    destination: str
    segments: List[RouteSegment]
    overnight_anchorages: List[Anchorage]
    total_distance_nm: float
    total_time_hours: float
    overall_comfort_score: float
    weather_summary: str
    recommendations: List[str]
    warnings: List[str]

    # Safety assessment
    voyage_safe: bool = True
    cancellation_recommended: bool = False
    cancellation_reason: Optional[str] = None

    # Alternative routes (if main route unsafe)
    alternative_routes: Optional[List['RouteRecommendation']] = None

    # Captain override
    captain_override_required: bool = False
    captain_override_reason: Optional[str] = None


class WeatherAwareRoutePlanner:
    """
    Intelligent route planner with weather awareness

    Considers:
    - Wind speed and direction
    - Wave height
    - Vessel type (sailing vs motor)
    - Anchorage wind protection
    - Comfort factors
    - Safety margins
    """

    def __init__(self, weather_integration, navigation_integration):
        """
        Initialize route planner

        Args:
            weather_integration: WeatherIntegration instance
            navigation_integration: NavigationIntegration instance
        """
        self.weather = weather_integration
        self.navigation = navigation_integration

        # Comfort thresholds
        self.comfort_limits = {
            'wind_comfortable': 15,  # knots
            'wind_moderate': 20,
            'wind_uncomfortable': 25,
            'wave_comfortable': 1.0,  # meters
            'wave_moderate': 1.5,
            'wave_uncomfortable': 2.0,
        }

        # Safety thresholds (voyage cancellation)
        self.safety_limits = {
            'wind_dangerous': 30,  # knots - CANCEL voyage
            'wind_critical': 35,   # knots - ABSOLUTELY DO NOT GO
            'wave_dangerous': 2.5,  # meters - CANCEL
            'wave_critical': 3.0,   # meters - ABSOLUTELY DO NOT GO
            'visibility_minimum': 1.0,  # NM - below this, CANCEL
        }

        logger.info("WeatherAwareRoutePlanner initialized")

    async def plan_multi_day_route(
        self,
        vessel_name: str,
        vessel_type: VesselType,
        vessel_length: float,
        departure: Dict[str, Any],
        waypoints: List[Dict[str, Any]],
        nights: int,
        departure_date: datetime
    ) -> RouteRecommendation:
        """
        Plan multi-day route with weather-aware anchorage selection

        Args:
            vessel_name: Vessel name
            vessel_type: Sailing or motor
            vessel_length: Vessel length in feet
            departure: Departure point
            waypoints: List of destination waypoints
            nights: Number of nights
            departure_date: Planned departure date

        Returns:
            Complete route recommendation
        """
        logger.info(f"Planning {nights}-night route for {vessel_name} ({vessel_type.value})")

        # Get weather forecast for planning period
        weather_forecast = await self._get_extended_forecast(
            region=departure.get('region', 'Marmara'),
            days=nights + 1
        )

        # Get suitable anchorages along route
        suitable_anchorages = await self._find_suitable_anchorages(
            waypoints=waypoints,
            vessel_length=vessel_length,
            weather_forecast=weather_forecast
        )

        # Build route segments
        segments = []
        overnight_anchorages = []
        warnings = []
        recommendations = []

        current_point = departure

        for day in range(nights + 1):
            day_weather = weather_forecast[day] if day < len(weather_forecast) else None

            if day < nights:
                # Find best anchorage for tonight
                best_anchorage = await self._select_best_anchorage(
                    current_position=current_point,
                    candidates=suitable_anchorages,
                    tonight_weather=day_weather,
                    vessel_type=vessel_type
                )

                if best_anchorage:
                    overnight_anchorages.append(best_anchorage)

                    # Create segment to anchorage
                    segment = await self._create_segment(
                        from_point=current_point,
                        to_point=best_anchorage,
                        weather=day_weather,
                        vessel_type=vessel_type
                    )
                    segments.append(segment)

                    # Check for warnings
                    if segment.warnings:
                        warnings.extend(segment.warnings)

                    # Update current position
                    current_point = {
                        'name': best_anchorage.name,
                        'latitude': best_anchorage.latitude,
                        'longitude': best_anchorage.longitude
                    }

        # Calculate totals
        total_distance = sum(s.distance_nm for s in segments)
        total_time = sum(s.estimated_time_hours for s in segments)
        overall_comfort = sum(s.comfort_score for s in segments) / len(segments) if segments else 0

        # Generate recommendations
        recommendations = self._generate_recommendations(
            vessel_type=vessel_type,
            weather_forecast=weather_forecast,
            anchorages=overnight_anchorages
        )

        # CRITICAL: Check voyage safety
        safety_assessment = self._assess_voyage_safety(
            weather_forecast=weather_forecast,
            segments=segments
        )

        # Create base recommendation
        recommendation = RouteRecommendation(
            vessel_name=vessel_name,
            vessel_type=vessel_type,
            departure=departure['name'],
            destination=waypoints[-1]['name'],
            segments=segments,
            overnight_anchorages=overnight_anchorages,
            total_distance_nm=total_distance,
            total_time_hours=total_time,
            overall_comfort_score=overall_comfort,
            weather_summary=self._summarize_weather(weather_forecast),
            recommendations=recommendations,
            warnings=warnings,
            voyage_safe=safety_assessment['safe'],
            cancellation_recommended=safety_assessment['cancel_recommended'],
            cancellation_reason=safety_assessment['cancel_reason'],
            captain_override_required=safety_assessment['captain_override_required'],
            captain_override_reason=safety_assessment['override_reason']
        )

        # If unsafe, generate alternative routes
        if not safety_assessment['safe'] and safety_assessment['cancel_recommended']:
            logger.warning(f"🔴 VOYAGE UNSAFE: {safety_assessment['cancel_reason']}")

            # Try to find alternative routes
            alternatives = await self._generate_alternative_routes(
                vessel_name=vessel_name,
                vessel_type=vessel_type,
                vessel_length=vessel_length,
                departure=departure,
                waypoints=waypoints,
                nights=nights,
                departure_date=departure_date,
                avoid_reason=safety_assessment['cancel_reason']
            )

            recommendation.alternative_routes = alternatives

        return recommendation

    async def _get_extended_forecast(
        self,
        region: str,
        days: int
    ) -> List[WeatherConditions]:
        """
        Get extended weather forecast

        Args:
            region: Region name
            days: Number of days

        Returns:
            List of weather conditions
        """
        forecast = await self.weather.get_marine_forecast(
            region=region,
            days=days
        )

        # Convert to WeatherConditions objects
        conditions = []
        for day_forecast in forecast.get('forecast', []):
            # Parse wind direction and speed
            wind_parts = day_forecast.get('wind', '10 knots N').split()
            wind_speed = float(wind_parts[0].split('-')[0])
            wind_dir = WindDirection[wind_parts[-1]] if wind_parts[-1] in WindDirection.__members__ else WindDirection.N

            # Parse wave height
            wave_parts = day_forecast.get('wave_height', '1m').split('-')
            wave_height = float(wave_parts[0].replace('m', ''))

            conditions.append(WeatherConditions(
                timestamp=datetime.fromisoformat(day_forecast.get('date')),
                wind_speed_knots=wind_speed,
                wind_direction=wind_dir,
                gust_speed_knots=wind_speed * 1.3,  # Estimate gusts
                wave_height_m=wave_height,
                visibility_nm=10.0,  # Default
                precipitation=False,
                temperature_c=24.0,
                pressure_mb=1015,
                sea_state=day_forecast.get('conditions', 'moderate').lower()
            ))

        return conditions

    async def _find_suitable_anchorages(
        self,
        waypoints: List[Dict[str, Any]],
        vessel_length: float,
        weather_forecast: List[WeatherConditions]
    ) -> List[Anchorage]:
        """
        Find suitable anchorages along route

        Args:
            waypoints: Route waypoints
            vessel_length: Vessel length
            weather_forecast: Weather forecast

        Returns:
            List of suitable anchorages
        """
        # Get all anchorages in region
        all_anchorages = self._get_adalar_anchorages()

        # Filter by vessel length
        suitable = [
            a for a in all_anchorages
            if a.suitable_for_length is None or a.suitable_for_length >= vessel_length
        ]

        return suitable

    async def _select_best_anchorage(
        self,
        current_position: Dict[str, Any],
        candidates: List[Anchorage],
        tonight_weather: Optional[WeatherConditions],
        vessel_type: VesselType
    ) -> Optional[Anchorage]:
        """
        Select best anchorage based on weather and wind protection

        CRITICAL: Must be sheltered from tonight's wind direction

        Args:
            current_position: Current position
            candidates: Candidate anchorages
            tonight_weather: Tonight's weather forecast
            vessel_type: Vessel type

        Returns:
            Best anchorage or None
        """
        if not tonight_weather or not candidates:
            return candidates[0] if candidates else None

        wind_dir = tonight_weather.wind_direction
        wind_speed = tonight_weather.wind_speed_knots

        # Filter: MUST be protected from tonight's wind
        sheltered = [
            a for a in candidates
            if wind_dir in a.protected_from
        ]

        if not sheltered:
            logger.warning(f"No anchorages sheltered from {wind_dir.value} wind!")
            # Return least exposed
            return min(candidates, key=lambda a: len(a.exposed_to))

        # Score each sheltered anchorage
        scores = []
        for anchorage in sheltered:
            score = 0.0

            # Wind protection (most important)
            if wind_dir in anchorage.protected_from:
                score += 50.0

            # Holding quality
            holding_scores = {'excellent': 20, 'good': 15, 'fair': 10, 'poor': 5}
            score += holding_scores.get(anchorage.holding, 0)

            # Rating
            score += anchorage.rating * 5

            # Facilities
            if anchorage.has_water:
                score += 3
            if anchorage.has_restaurant:
                score += 2

            # Depth (prefer moderate depth 6-12m)
            if 6 <= anchorage.depth_min_m <= 12:
                score += 5

            scores.append((score, anchorage))

        # Return highest scored
        best = max(scores, key=lambda x: x[0])
        logger.info(f"Selected anchorage: {best[1].name_tr} (score: {best[0]:.1f})")

        return best[1]

    async def _create_segment(
        self,
        from_point: Dict[str, Any],
        to_point: Any,  # Could be dict or Anchorage
        weather: Optional[WeatherConditions],
        vessel_type: VesselType
    ) -> RouteSegment:
        """
        Create route segment with comfort analysis

        Args:
            from_point: Starting point
            to_point: Ending point
            weather: Weather conditions
            vessel_type: Vessel type

        Returns:
            Route segment
        """
        # Extract coordinates
        if isinstance(to_point, Anchorage):
            to_lat = to_point.latitude
            to_lon = to_point.longitude
            to_name = to_point.name_tr
        else:
            to_lat = to_point['latitude']
            to_lon = to_point['longitude']
            to_name = to_point['name']

        from_lat = from_point['latitude']
        from_lon = from_point['longitude']
        from_name = from_point['name']

        # Calculate distance (simple approximation)
        distance_nm = self._calculate_distance(from_lat, from_lon, to_lat, to_lon)

        # Calculate bearing
        bearing = self._calculate_bearing(from_lat, from_lon, to_lat, to_lon)

        # Estimate time (depends on vessel type and weather)
        if vessel_type == VesselType.SAILING and weather:
            # Sailing: depends on wind
            speed_knots = self._estimate_sailing_speed(weather, bearing)
        else:
            # Motor yacht: 8 knots average
            speed_knots = 8.0

        estimated_time = distance_nm / speed_knots

        # Comfort analysis
        comfort_score, warnings = self._analyze_comfort(weather, vessel_type)

        return RouteSegment(
            from_point=from_name,
            to_point=to_name,
            distance_nm=distance_nm,
            bearing=bearing,
            estimated_time_hours=estimated_time,
            weather_forecast=weather,
            comfort_score=comfort_score,
            recommended=comfort_score >= 6.0,
            warnings=warnings
        )

    def _analyze_comfort(
        self,
        weather: Optional[WeatherConditions],
        vessel_type: VesselType
    ) -> tuple[float, List[str]]:
        """
        Analyze passage comfort

        Returns:
            (comfort_score, warnings)
        """
        if not weather:
            return 7.0, []

        score = 10.0
        warnings = []

        # Wind analysis
        wind = weather.wind_speed_knots
        if wind > self.comfort_limits['wind_uncomfortable']:
            score -= 4.0
            warnings.append(f"⚠️ Kuvvetli rüzgar: {wind:.0f} knot")
        elif wind > self.comfort_limits['wind_moderate']:
            score -= 2.0
            warnings.append(f"⚠️ Orta kuvvette rüzgar: {wind:.0f} knot")

        # Wave analysis
        wave = weather.wave_height_m
        if wave > self.comfort_limits['wave_uncomfortable']:
            score -= 4.0
            warnings.append(f"⚠️ Yüksek dalga: {wave:.1f}m")
        elif wave > self.comfort_limits['wave_moderate']:
            score -= 2.0
            warnings.append(f"⚠️ Orta yükseklikte dalga: {wave:.1f}m")

        # Precipitation
        if weather.precipitation:
            score -= 1.0
            warnings.append("🌧️ Yağış bekleniyor")

        # Visibility
        if weather.visibility_nm < 2.0:
            score -= 3.0
            warnings.append(f"⚠️ Düşük görüş: {weather.visibility_nm:.1f} NM")

        return max(0.0, min(10.0, score)), warnings

    def _estimate_sailing_speed(
        self,
        weather: WeatherConditions,
        bearing: float
    ) -> float:
        """
        Estimate sailing speed based on wind

        Args:
            weather: Weather conditions
            bearing: Course bearing

        Returns:
            Estimated speed in knots
        """
        wind_speed = weather.wind_speed_knots

        # Simplified: ideal wind is 10-15 knots
        if 10 <= wind_speed <= 15:
            return 6.5
        elif 5 <= wind_speed < 10:
            return 4.5
        elif 15 < wind_speed <= 20:
            return 7.0
        elif wind_speed > 20:
            return 5.0  # Reef sails
        else:
            return 3.0  # Light wind

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance in nautical miles (simple approximation)"""
        import math

        lat_diff = abs(lat2 - lat1)
        lon_diff = abs(lon2 - lon1)

        # 1 degree latitude ≈ 60 NM
        # 1 degree longitude ≈ 60 * cos(latitude) NM

        lat_nm = lat_diff * 60
        lon_nm = lon_diff * 60 * math.cos(math.radians((lat1 + lat2) / 2))

        return math.sqrt(lat_nm**2 + lon_nm**2)

    def _calculate_bearing(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate bearing in degrees"""
        import math

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon_diff = math.radians(lon2 - lon1)

        x = math.sin(lon_diff) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff)

        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360

    def _generate_recommendations(
        self,
        vessel_type: VesselType,
        weather_forecast: List[WeatherConditions],
        anchorages: List[Anchorage]
    ) -> List[str]:
        """Generate voyage recommendations"""
        recommendations = []

        # Check overall weather
        avg_wind = sum(w.wind_speed_knots for w in weather_forecast) / len(weather_forecast)
        max_wind = max(w.wind_speed_knots for w in weather_forecast)

        if max_wind > 25:
            recommendations.append(f"⚠️ {max_wind:.0f} knot rüzgar bekleniyor - seferi ertelemeyi düşünün")
        elif avg_wind < 10 and vessel_type == VesselType.SAILING:
            recommendations.append("💡 Hafif rüzgar - motor kullanmanız gerekebilir")
        elif 15 <= avg_wind <= 20 and vessel_type == VesselType.SAILING:
            recommendations.append("✅ İdeal yelken koşulları")

        # Anchorage recommendations
        for i, anc in enumerate(anchorages, 1):
            if anc.rating >= 4.5:
                recommendations.append(f"⭐ {anc.name_tr} çok beğenilen bir demirlik")
            if anc.has_restaurant:
                recommendations.append(f"🍽️ {anc.name_tr}'da restoran mevcut")

        return recommendations

    def _summarize_weather(self, forecast: List[WeatherConditions]) -> str:
        """Create weather summary"""
        if not forecast:
            return "Hava durumu bilgisi yok"

        avg_wind = sum(w.wind_speed_knots for w in forecast) / len(forecast)
        max_wind = max(w.wind_speed_knots for w in forecast)
        avg_wave = sum(w.wave_height_m for w in forecast) / len(forecast)

        return (
            f"{len(forecast)} günlük tahmin: "
            f"Ortalama rüzgar {avg_wind:.0f} knot (max {max_wind:.0f}), "
            f"dalga {avg_wave:.1f}m"
        )

    def _get_adalar_anchorages(self) -> List[Anchorage]:
        """
        Get Adalar (Princes' Islands) anchorage database

        Real data for Istanbul islands with wind protection
        """
        return [
            # Büyükada
            Anchorage(
                id='buyukada_yorukali',
                name='Yörükali Bay',
                name_tr='Yörükali Koyu',
                latitude=40.8515,
                longitude=29.1202,
                depth_min_m=5,
                depth_max_m=12,
                bottom_type='sand_mud',
                holding='excellent',
                protected_from=[WindDirection.N, WindDirection.NE, WindDirection.NW],
                exposed_to=[WindDirection.S, WindDirection.SE, WindDirection.SW],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=True,
                suitable_for_length=80,
                rating=4.3,
                review_count=45
            ),
            Anchorage(
                id='buyukada_dilburnu',
                name='Dilburnu',
                name_tr='Dilburnu',
                latitude=40.8485,
                longitude=29.1145,
                depth_min_m=6,
                depth_max_m=15,
                bottom_type='sand',
                holding='good',
                protected_from=[WindDirection.E, WindDirection.NE, WindDirection.SE],
                exposed_to=[WindDirection.W, WindDirection.NW, WindDirection.SW],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=False,
                suitable_for_length=70,
                rating=4.0,
                review_count=32
            ),

            # Heybeliada
            Anchorage(
                id='heybeliada_degirmenburnu',
                name='Değirmenburnu Bay',
                name_tr='Değirmenburnu Koyu',
                latitude=40.8702,
                longitude=29.0947,
                depth_min_m=4,
                depth_max_m=10,
                bottom_type='sand',
                holding='excellent',
                protected_from=[WindDirection.W, WindDirection.SW, WindDirection.NW],
                exposed_to=[WindDirection.E, WindDirection.SE, WindDirection.NE],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=True,
                suitable_for_length=65,
                rating=4.7,
                review_count=67
            ),
            Anchorage(
                id='heybeliada_cam_limani',
                name='Çam Limanı',
                name_tr='Çam Limanı',
                latitude=40.8725,
                longitude=29.0890,
                depth_min_m=5,
                depth_max_m=12,
                bottom_type='sand',
                holding='good',
                protected_from=[WindDirection.N, WindDirection.NE, WindDirection.E],
                exposed_to=[WindDirection.S, WindDirection.SW, WindDirection.W],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=False,
                suitable_for_length=60,
                rating=4.2,
                review_count=28
            ),

            # Burgazada
            Anchorage(
                id='burgazada_madam_koyu',
                name='Madam Bay',
                name_tr='Madam Koyu',
                latitude=40.8795,
                longitude=29.0695,
                depth_min_m=3,
                depth_max_m=8,
                bottom_type='sand',
                holding='good',
                protected_from=[WindDirection.N, WindDirection.NE, WindDirection.NW],
                exposed_to=[WindDirection.S, WindDirection.SE, WindDirection.SW],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=True,
                suitable_for_length=55,
                rating=4.5,
                review_count=53
            ),
            Anchorage(
                id='burgazada_kalpazankaya',
                name='Kalpazankaya Bay',
                name_tr='Kalpazankaya Koyu',
                latitude=40.8810,
                longitude=29.0640,
                depth_min_m=4,
                depth_max_m=10,
                bottom_type='sand_mud',
                holding='excellent',
                protected_from=[WindDirection.E, WindDirection.SE, WindDirection.NE],
                exposed_to=[WindDirection.W, WindDirection.NW, WindDirection.SW],
                has_mooring_buoys=False,
                has_water=False,
                has_restaurant=False,
                suitable_for_length=50,
                rating=4.1,
                review_count=19
            ),
        ]

    def _assess_voyage_safety(
        self,
        weather_forecast: List[WeatherConditions],
        segments: List[RouteSegment]
    ) -> Dict[str, Any]:
        """
        Assess overall voyage safety

        CRITICAL: Check for dangerous weather that requires cancellation

        Args:
            weather_forecast: Weather forecast for voyage
            segments: Planned route segments

        Returns:
            Safety assessment
        """
        max_wind = max(w.wind_speed_knots for w in weather_forecast) if weather_forecast else 0
        max_wave = max(w.wave_height_m for w in weather_forecast) if weather_forecast else 0
        min_visibility = min(w.visibility_nm for w in weather_forecast) if weather_forecast else 10

        # Find which day has the problem
        dangerous_day = None
        for i, w in enumerate(weather_forecast, 1):
            if (w.wind_speed_knots >= self.safety_limits['wind_dangerous'] or
                w.wave_height_m >= self.safety_limits['wave_dangerous'] or
                w.visibility_nm < self.safety_limits['visibility_minimum']):
                dangerous_day = i
                break

        # CRITICAL conditions - ABSOLUTELY DO NOT GO
        if max_wind >= self.safety_limits['wind_critical']:
            return {
                'safe': False,
                'cancel_recommended': True,
                'cancel_reason': f"🔴 KRİTİK: {max_wind:.0f} knot fırtına bekleniyor (Gün {dangerous_day}). SEFERİ İPTAL EDİN!",
                'captain_override_required': True,
                'override_reason': 'critical_weather',
                'severity': 'CRITICAL'
            }

        if max_wave >= self.safety_limits['wave_critical']:
            return {
                'safe': False,
                'cancel_recommended': True,
                'cancel_reason': f"🔴 KRİTİK: {max_wave:.1f}m dalga bekleniyor (Gün {dangerous_day}). SEFERİ İPTAL EDİN!",
                'captain_override_required': True,
                'override_reason': 'critical_waves',
                'severity': 'CRITICAL'
            }

        # DANGEROUS conditions - STRONGLY RECOMMEND CANCELLATION
        if max_wind >= self.safety_limits['wind_dangerous']:
            return {
                'safe': False,
                'cancel_recommended': True,
                'cancel_reason': f"⚠️ TEHLİKELİ: {max_wind:.0f} knot rüzgar bekleniyor (Gün {dangerous_day}). Seferi ertelemenizi ÖNERİYORUM.",
                'captain_override_required': True,
                'override_reason': 'dangerous_weather',
                'severity': 'DANGEROUS'
            }

        if max_wave >= self.safety_limits['wave_dangerous']:
            return {
                'safe': False,
                'cancel_recommended': True,
                'cancel_reason': f"⚠️ TEHLİKELİ: {max_wave:.1f}m dalga bekleniyor (Gün {dangerous_day}). Seferi ertelemenizi ÖNERİYORUM.",
                'captain_override_required': True,
                'override_reason': 'dangerous_waves',
                'severity': 'DANGEROUS'
            }

        if min_visibility < self.safety_limits['visibility_minimum']:
            return {
                'safe': False,
                'cancel_recommended': True,
                'cancel_reason': f"⚠️ TEHLİKELİ: Düşük görüş mesafesi {min_visibility:.1f} NM (Gün {dangerous_day}). Seferi ertelemenizi ÖNERİYORUM.",
                'captain_override_required': True,
                'override_reason': 'poor_visibility',
                'severity': 'DANGEROUS'
            }

        # Safe to proceed
        return {
            'safe': True,
            'cancel_recommended': False,
            'cancel_reason': None,
            'captain_override_required': False,
            'override_reason': None,
            'severity': 'SAFE'
        }

    async def _generate_alternative_routes(
        self,
        vessel_name: str,
        vessel_type: VesselType,
        vessel_length: float,
        departure: Dict[str, Any],
        waypoints: List[Dict[str, Any]],
        nights: int,
        departure_date: datetime,
        avoid_reason: str
    ) -> Optional[List[RouteRecommendation]]:
        """
        Generate alternative routes when main route is unsafe

        Options:
        1. Delay departure by 24-48 hours
        2. Shorter route (skip some waypoints)
        3. Different anchorages with better protection

        Args:
            vessel_name: Vessel name
            vessel_type: Vessel type
            vessel_length: Vessel length
            departure: Departure point
            waypoints: Original waypoints
            nights: Number of nights
            departure_date: Original departure date
            avoid_reason: Why main route is unsafe

        Returns:
            List of alternative route recommendations
        """
        logger.info("Generating alternative routes...")

        alternatives = []

        # ALTERNATIVE 1: Delay by 24 hours
        try:
            delayed_route = await self.plan_multi_day_route(
                vessel_name=vessel_name,
                vessel_type=vessel_type,
                vessel_length=vessel_length,
                departure=departure,
                waypoints=waypoints,
                nights=nights,
                departure_date=departure_date + timedelta(days=1)
            )

            # Prevent infinite recursion
            delayed_route.alternative_routes = None

            if delayed_route.voyage_safe:
                logger.info("✅ Alternative found: Delay 24 hours")
                alternatives.append(delayed_route)
        except Exception as e:
            logger.error(f"Failed to generate delayed route: {e}")

        # ALTERNATIVE 2: Delay by 48 hours
        try:
            delayed_route_48h = await self.plan_multi_day_route(
                vessel_name=vessel_name,
                vessel_type=vessel_type,
                vessel_length=vessel_length,
                departure=departure,
                waypoints=waypoints,
                nights=nights,
                departure_date=departure_date + timedelta(days=2)
            )

            delayed_route_48h.alternative_routes = None

            if delayed_route_48h.voyage_safe:
                logger.info("✅ Alternative found: Delay 48 hours")
                alternatives.append(delayed_route_48h)
        except Exception as e:
            logger.error(f"Failed to generate 48h delayed route: {e}")

        # ALTERNATIVE 3: Shorter route (skip last waypoint)
        if len(waypoints) > 1:
            try:
                shorter_route = await self.plan_multi_day_route(
                    vessel_name=vessel_name,
                    vessel_type=vessel_type,
                    vessel_length=vessel_length,
                    departure=departure,
                    waypoints=waypoints[:-1],  # Skip last waypoint
                    nights=nights - 1,
                    departure_date=departure_date
                )

                shorter_route.alternative_routes = None

                if shorter_route.voyage_safe:
                    logger.info("✅ Alternative found: Shorter route")
                    alternatives.append(shorter_route)
            except Exception as e:
                logger.error(f"Failed to generate shorter route: {e}")

        if alternatives:
            logger.info(f"Found {len(alternatives)} alternative routes")
        else:
            logger.warning("No safe alternative routes found")

        return alternatives if alternatives else None

    def captain_override(
        self,
        recommendation: RouteRecommendation,
        captain_id: str,
        override_reason: str,
        force_majeure: bool = False
    ) -> Dict[str, Any]:
        """
        Captain overrides safety recommendation

        IMPORTANT: Captain has final authority, but override is logged

        Args:
            recommendation: Route recommendation
            captain_id: Captain identifier
            override_reason: Reason for override
            force_majeure: True if force majeure situation

        Returns:
            Override confirmation
        """
        logger.warning(f"⚠️ CAPTAIN OVERRIDE by {captain_id}")
        logger.warning(f"   Reason: {override_reason}")
        logger.warning(f"   Force Majeure: {force_majeure}")

        if recommendation.cancellation_recommended:
            logger.warning(f"   Original recommendation: CANCEL VOYAGE")
            logger.warning(f"   Cancellation reason: {recommendation.cancellation_reason}")

        # Log override
        override_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'captain_id': captain_id,
            'voyage': f"{recommendation.departure} → {recommendation.destination}",
            'original_recommendation': 'CANCEL' if recommendation.cancellation_recommended else 'PROCEED',
            'captain_decision': 'PROCEED',
            'override_reason': override_reason,
            'force_majeure': force_majeure,
            'weather_summary': recommendation.weather_summary,
            'cancellation_reason': recommendation.cancellation_reason,
            'acknowledged_risks': True
        }

        if force_majeure:
            logger.info("✅ Force majeure acknowledged - override accepted")
        else:
            logger.warning("⚠️ Captain proceeding against safety recommendation")

        return {
            'override_accepted': True,
            'override_log': override_log,
            'message_tr': f"Kaptan {captain_id} sorumluluğu üstleniyor. İyi seyirler ve dikkatli olun!",
            'message_en': f"Captain {captain_id} assumes responsibility. Safe travels and be careful!",
            'recommendations': [
                "✅ Çift demir kullanın (double anchor setup)",
                "✅ VHF Kanal 16'yı sürekli izleyin",
                "✅ Hava durumunu her 30 dakikada kontrol edin",
                "✅ En yakın güvenli limana hazır olun",
                "✅ Mürettebatı bilgilendirin"
            ]
        }
