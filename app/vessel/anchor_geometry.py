"""
Anchor Geometry Calculator
Double anchor, bow anchor, and emergency anchoring calculations

"Çok zevkli geometri hesapları" - Captain knows! 🎯
"""

import logging
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AnchorType(Enum):
    """Anchor types"""
    MAIN = "main"  # Ana demir
    SECONDARY = "secondary"  # Yedek demir
    STERN = "stern"  # Kıç demiri


class BottomType(Enum):
    """Bottom types and holding"""
    SAND = "sand"  # Kum - excellent holding
    MUD = "mud"  # Çamur - excellent holding
    CLAY = "clay"  # Kil - good holding
    ROCK = "rock"  # Kaya - poor holding
    WEED = "weed"  # Yosun - poor holding
    CORAL = "coral"  # Mercan - fair holding (avoid!)


@dataclass
class AnchorSetup:
    """Anchor setup configuration"""
    anchor_type: AnchorType
    weight_kg: float
    chain_length_m: float
    rode_length_m: float  # Additional rope
    depth_m: float
    scope_ratio: float  # Chain length / depth ratio


@dataclass
class DoubleAnchorGeometry:
    """Double anchor configuration (V-shape)"""
    main_anchor: AnchorSetup
    secondary_anchor: AnchorSetup
    angle_between_degrees: float  # Typical: 45-60 degrees
    vessel_length_m: float
    estimated_swing_radius_m: float
    wind_direction: float  # Degrees (0 = North)
    recommendations: List[str]


@dataclass
class AnchorDragAlert:
    """Anchor drag detection"""
    initial_position: Tuple[float, float]  # lat, lon
    current_position: Tuple[float, float]
    distance_moved_m: float
    acceptable_radius_m: float
    is_dragging: bool
    alert_level: str  # ok, warning, critical


class AnchorGeometryCalculator:
    """
    Calculate anchor geometry for various scenarios

    Supports:
    - Single anchor scope calculation
    - Double anchor (V-shape) geometry
    - Stern anchor setup
    - Swing radius calculation
    - Anchor drag detection
    """

    def __init__(self):
        """Initialize calculator"""
        # Recommended scope ratios
        self.recommended_scope = {
            'all_chain': 3.0,  # All chain: 3:1 minimum
            'chain_rode': 5.0,  # Chain + rope: 5:1 minimum
            'storm': 7.0,  # Storm conditions: 7:1
        }

        # Holding factors by bottom type
        self.holding_factors = {
            BottomType.SAND: 1.0,
            BottomType.MUD: 1.0,
            BottomType.CLAY: 0.9,
            BottomType.CORAL: 0.7,
            BottomType.ROCK: 0.3,
            BottomType.WEED: 0.4,
        }

        logger.info("AnchorGeometryCalculator initialized")

    def calculate_required_scope(
        self,
        depth_m: float,
        is_all_chain: bool = True,
        storm_conditions: bool = False
    ) -> Dict[str, float]:
        """
        Calculate required anchor scope

        Args:
            depth_m: Water depth in meters
            is_all_chain: True if all chain, False if chain + rope
            storm_conditions: True if expecting storm

        Returns:
            Scope recommendations
        """
        if storm_conditions:
            ratio = self.recommended_scope['storm']
        elif is_all_chain:
            ratio = self.recommended_scope['all_chain']
        else:
            ratio = self.recommended_scope['chain_rode']

        required_length = depth_m * ratio

        return {
            'depth_m': depth_m,
            'scope_ratio': ratio,
            'required_chain_m': required_length,
            'minimum_safe': depth_m * (ratio - 1),  # Absolute minimum
            'recommended': required_length,
            'comfortable': depth_m * (ratio + 1),  # Extra safety
        }

    def calculate_swing_radius(
        self,
        chain_length_m: float,
        depth_m: float,
        vessel_length_m: float,
        freeboard_m: float = 1.5
    ) -> float:
        """
        Calculate swing radius (how much space vessel needs)

        Args:
            chain_length_m: Chain/rode length
            depth_m: Water depth
            vessel_length_m: Vessel length
            freeboard_m: Freeboard height

        Returns:
            Swing radius in meters
        """
        # Horizontal distance from anchor to bow
        horizontal_chain = math.sqrt(chain_length_m**2 - (depth_m + freeboard_m)**2)

        # Add vessel length
        swing_radius = horizontal_chain + vessel_length_m

        logger.info(f"Swing radius: {swing_radius:.1f}m (chain: {horizontal_chain:.1f}m + vessel: {vessel_length_m:.1f}m)")

        return swing_radius

    def calculate_double_anchor(
        self,
        depth_m: float,
        vessel_length_m: float,
        vessel_beam_m: float,
        main_chain_m: float,
        secondary_chain_m: float,
        angle_between: float = 45.0,
        wind_direction: float = 0.0
    ) -> DoubleAnchorGeometry:
        """
        Calculate double anchor (V-shape) geometry

        CRITICAL for strong wind/current situations

        Args:
            depth_m: Water depth
            vessel_length_m: Vessel length
            vessel_beam_m: Vessel beam (width)
            main_chain_m: Main anchor chain length
            secondary_chain_m: Secondary anchor chain length
            angle_between: Angle between anchors (typically 45-60°)
            wind_direction: Expected wind direction (degrees)

        Returns:
            Double anchor geometry
        """
        logger.info(f"Calculating double anchor setup (angle: {angle_between}°)")

        # Calculate scope for each anchor
        main_setup = AnchorSetup(
            anchor_type=AnchorType.MAIN,
            weight_kg=0,  # Not specified
            chain_length_m=main_chain_m,
            rode_length_m=0,
            depth_m=depth_m,
            scope_ratio=main_chain_m / depth_m
        )

        secondary_setup = AnchorSetup(
            anchor_type=AnchorType.SECONDARY,
            weight_kg=0,
            chain_length_m=secondary_chain_m,
            rode_length_m=0,
            depth_m=depth_m,
            scope_ratio=secondary_chain_m / depth_m
        )

        # Calculate swing radius (reduced with double anchor)
        single_swing = self.calculate_swing_radius(main_chain_m, depth_m, vessel_length_m)

        # Double anchor reduces swing radius significantly
        double_swing = single_swing * 0.4  # Roughly 40% of single anchor

        # Recommendations
        recommendations = []

        if angle_between < 30:
            recommendations.append("⚠️ Açı çok dar - minimum 45° önerilir")
        elif angle_between > 90:
            recommendations.append("⚠️ Açı çok geniş - maksimum 60° önerilir")
        else:
            recommendations.append("✅ Açı optimal (45-60°)")

        if main_setup.scope_ratio < 3.0:
            recommendations.append(f"⚠️ Ana demir scope yetersiz: {main_setup.scope_ratio:.1f}:1 (min 3:1)")
        else:
            recommendations.append(f"✅ Ana demir scope OK: {main_setup.scope_ratio:.1f}:1")

        if secondary_setup.scope_ratio < 3.0:
            recommendations.append(f"⚠️ Yedek demir scope yetersiz: {secondary_setup.scope_ratio:.1f}:1")
        else:
            recommendations.append(f"✅ Yedek demir scope OK: {secondary_setup.scope_ratio:.1f}:1")

        recommendations.append(f"💡 Sallanma yarıçapı: {double_swing:.1f}m (tek demirde: {single_swing:.1f}m)")
        recommendations.append(f"💡 İki demir arasındaki mesafe: {self._calculate_anchor_distance(main_chain_m, secondary_chain_m, angle_between):.1f}m")

        return DoubleAnchorGeometry(
            main_anchor=main_setup,
            secondary_anchor=secondary_setup,
            angle_between_degrees=angle_between,
            vessel_length_m=vessel_length_m,
            estimated_swing_radius_m=double_swing,
            wind_direction=wind_direction,
            recommendations=recommendations
        )

    def calculate_stern_anchor(
        self,
        depth_m: float,
        vessel_length_m: float,
        bow_chain_m: float,
        stern_chain_m: float,
        distance_to_shore_m: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate stern anchor setup (Mediterranean mooring)

        Used when anchoring close to shore

        Args:
            depth_m: Water depth
            vessel_length_m: Vessel length
            bow_chain_m: Bow anchor chain
            stern_chain_m: Stern line/chain
            distance_to_shore_m: Distance to shore

        Returns:
            Stern anchor geometry
        """
        logger.info("Calculating stern anchor (Mediterranean mooring)")

        # Bow anchor horizontal distance
        bow_horizontal = math.sqrt(bow_chain_m**2 - depth_m**2)

        # Stern line should be tight
        stern_horizontal = stern_chain_m

        # Total vessel footprint
        total_length = bow_horizontal + vessel_length_m + stern_horizontal

        warnings = []
        if distance_to_shore_m:
            clearance = distance_to_shore_m - total_length
            if clearance < 5:
                warnings.append(f"⚠️ Kıyıya çok yakın! Mesafe: {clearance:.1f}m")
            elif clearance < 10:
                warnings.append(f"⚠️ Dikkatli - kıyıya mesafe: {clearance:.1f}m")
            else:
                warnings.append(f"✅ Kıyıya mesafe OK: {clearance:.1f}m")

        return {
            'bow_chain_m': bow_chain_m,
            'bow_horizontal_m': bow_horizontal,
            'stern_line_m': stern_chain_m,
            'stern_horizontal_m': stern_horizontal,
            'total_footprint_m': total_length,
            'distance_to_shore_m': distance_to_shore_m,
            'shore_clearance_m': distance_to_shore_m - total_length if distance_to_shore_m else None,
            'warnings': warnings
        }

    def calculate_anchor_drag(
        self,
        initial_lat: float,
        initial_lon: float,
        current_lat: float,
        current_lon: float,
        vessel_length_m: float,
        acceptable_swing_m: Optional[float] = None
    ) -> AnchorDragAlert:
        """
        Detect if anchor is dragging

        Args:
            initial_lat: Initial latitude
            initial_lon: Initial longitude
            current_lat: Current latitude
            current_lon: Current longitude
            vessel_length_m: Vessel length
            acceptable_swing_m: Acceptable swing radius

        Returns:
            Drag alert
        """
        # Calculate distance moved (simple approximation)
        distance_m = self._haversine_distance(
            initial_lat, initial_lon,
            current_lat, current_lon
        )

        # Default acceptable swing: 1.5x vessel length
        if acceptable_swing_m is None:
            acceptable_swing_m = vessel_length_m * 1.5

        # Determine alert level
        if distance_m < acceptable_swing_m:
            is_dragging = False
            alert_level = "ok"
        elif distance_m < acceptable_swing_m * 1.5:
            is_dragging = True
            alert_level = "warning"
        else:
            is_dragging = True
            alert_level = "critical"

        if is_dragging:
            logger.warning(f"⚠️ ANCHOR DRAG ALERT: Moved {distance_m:.1f}m (limit: {acceptable_swing_m:.1f}m)")
        else:
            logger.info(f"✅ Anchor holding: {distance_m:.1f}m movement (OK)")

        return AnchorDragAlert(
            initial_position=(initial_lat, initial_lon),
            current_position=(current_lat, current_lon),
            distance_moved_m=distance_m,
            acceptable_radius_m=acceptable_swing_m,
            is_dragging=is_dragging,
            alert_level=alert_level
        )

    def calculate_bottom_holding_power(
        self,
        anchor_weight_kg: float,
        bottom_type: BottomType,
        scope_ratio: float
    ) -> Dict[str, float]:
        """
        Estimate anchor holding power

        Args:
            anchor_weight_kg: Anchor weight
            bottom_type: Bottom type
            scope_ratio: Scope ratio (chain_length / depth)

        Returns:
            Holding power estimates
        """
        # Base holding power (rule of thumb: 10-20x anchor weight for good bottom)
        base_holding = anchor_weight_kg * 15

        # Apply bottom type factor
        bottom_factor = self.holding_factors[bottom_type]

        # Apply scope factor (more scope = better holding)
        scope_factor = min(scope_ratio / 5.0, 1.5)  # Cap at 1.5x

        effective_holding = base_holding * bottom_factor * scope_factor

        return {
            'anchor_weight_kg': anchor_weight_kg,
            'bottom_type': bottom_type.value,
            'bottom_factor': bottom_factor,
            'scope_ratio': scope_ratio,
            'scope_factor': scope_factor,
            'base_holding_kg': base_holding,
            'effective_holding_kg': effective_holding,
            'rating': self._rate_holding_power(effective_holding)
        }

    def _calculate_anchor_distance(
        self,
        chain1_m: float,
        chain2_m: float,
        angle_degrees: float
    ) -> float:
        """
        Calculate distance between two anchors using law of cosines

        Args:
            chain1_m: First chain length
            chain2_m: Second chain length
            angle_degrees: Angle between chains

        Returns:
            Distance between anchors in meters
        """
        angle_rad = math.radians(angle_degrees)

        # Law of cosines: c² = a² + b² - 2ab*cos(C)
        distance = math.sqrt(
            chain1_m**2 + chain2_m**2 -
            2 * chain1_m * chain2_m * math.cos(angle_rad)
        )

        return distance

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two GPS coordinates

        Args:
            lat1, lon1: First position
            lat2, lon2: Second position

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _rate_holding_power(self, holding_kg: float) -> str:
        """Rate holding power"""
        if holding_kg > 500:
            return "excellent"
        elif holding_kg > 300:
            return "good"
        elif holding_kg > 150:
            return "fair"
        else:
            return "poor"
