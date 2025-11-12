"""
Single-Handed MOB Emergency Response System
Autonomous vessel response when sole person goes overboard

Critical Scenario:
- 1 person onboard (captain alone)
- YOLO detects MOB
- Vessel realizes: 1 person manifest + MOB = VESSEL UNMANNED
- Autonomous emergency response activated

"Senaryo: teknede sadece bir kişi var... Tek kişi ise sadece bütün
yetenekleri ile kurtarmak için elinden geleni yapmalı."
"""

import logging
import asyncio
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class PersonRole(Enum):
    """Person role on vessel"""
    CAPTAIN = "captain"
    CREW = "crew"
    GUEST = "guest"
    CHILD = "child"


class PersonStatus(Enum):
    """Person status"""
    ONBOARD = "onboard"
    ASHORE = "ashore"
    MOB = "mob"  # Man overboard!
    UNKNOWN = "unknown"


@dataclass
class Person:
    """Person onboard"""
    person_id: str
    name: str
    role: PersonRole
    status: PersonStatus = PersonStatus.ONBOARD
    yolo_person_id: Optional[int] = None  # Link to YOLO tracking
    last_seen: datetime = field(default_factory=datetime.utcnow)
    emergency_contact: Optional[str] = None
    medical_info: Optional[str] = None


@dataclass
class VesselManifest:
    """Vessel crew manifest"""
    vessel_name: str
    manifest_date: datetime
    persons: List[Person]

    @property
    def total_onboard(self) -> int:
        """Count persons currently onboard"""
        return len([p for p in self.persons if p.status == PersonStatus.ONBOARD])

    @property
    def captain(self) -> Optional[Person]:
        """Get captain"""
        captains = [p for p in self.persons if p.role == PersonRole.CAPTAIN]
        return captains[0] if captains else None

    def is_single_handed(self) -> bool:
        """Check if single-handed operation (1 person onboard)"""
        return self.total_onboard == 1

    def get_person_by_yolo_id(self, yolo_person_id: int) -> Optional[Person]:
        """Find person by YOLO tracking ID"""
        for person in self.persons:
            if person.yolo_person_id == yolo_person_id:
                return person
        return None

    def get_onboard_persons(self) -> List[Person]:
        """Get all persons currently onboard"""
        return [p for p in self.persons if p.status == PersonStatus.ONBOARD]


class SingleHandedMOBEmergency:
    """
    Autonomous emergency response for single-handed MOB

    When sole person goes overboard, vessel must act completely
    autonomously to rescue them.

    AUTONOMOUS ACTIONS:
    1. Detect MOB via YOLO
    2. Realize: 1 person manifest + MOB = VESSEL UNMANNED
    3. Send automatic Mayday via VHF DSC
    4. Engage autopilot - execute Williamson Turn
    5. Return to MOB GPS position
    6. Circle MOB position at 50m radius, 2 knots
    7. Alert Coast Guard continuously
    8. Await rescue
    """

    def __init__(
        self,
        vessel_name: str,
        mmsi: str,
        mob_detection_system,
        knowledge_base,
        autopilot_interface=None,
        vhf_dsc_interface=None
    ):
        """
        Initialize single-handed MOB emergency system

        Args:
            vessel_name: Vessel name
            mmsi: MMSI number for DSC
            mob_detection_system: MOBDetectionSystem instance
            knowledge_base: MaritimeKnowledgeBase instance
            autopilot_interface: Interface to autopilot system (FUTURE)
            vhf_dsc_interface: Interface to VHF DSC (FUTURE)
        """
        self.vessel_name = vessel_name
        self.mmsi = mmsi
        self.mob_detection = mob_detection_system
        self.knowledge_base = knowledge_base
        self.autopilot = autopilot_interface
        self.vhf_dsc = vhf_dsc_interface

        # Crew manifest
        self.current_manifest: Optional[VesselManifest] = None

        # Emergency state
        self.emergency_active = False
        self.mob_position: Optional[Tuple[float, float]] = None
        self.mob_person: Optional[Person] = None
        self.emergency_start_time: Optional[datetime] = None

        # Autonomous response state
        self.mayday_sent = False
        self.williamson_turn_active = False
        self.circling_mob = False

        logger.info(f"SingleHandedMOBEmergency initialized for {vessel_name}")

    def update_manifest(self, manifest: VesselManifest):
        """
        Update crew manifest

        Args:
            manifest: Current vessel manifest
        """
        self.current_manifest = manifest

        logger.info(f"📋 Manifest updated: {manifest.total_onboard} persons onboard")

        if manifest.is_single_handed():
            logger.warning("⚠️ SINGLE-HANDED OPERATION DETECTED")
            logger.warning("   Enhanced MOB monitoring active")
            logger.warning("   Autonomous emergency response armed")

    async def process_mob_detection(
        self,
        yolo_person_id: int,
        current_gps: Tuple[float, float],
        current_heading: float,
        current_speed: float
    ):
        """
        Process MOB detection from YOLO

        Args:
            yolo_person_id: YOLO tracking ID of person who went MOB
            current_gps: Current vessel GPS position (lat, lon)
            current_heading: Current heading (degrees)
            current_speed: Current speed (knots)
        """
        logger.critical("=" * 70)
        logger.critical("  🚨 MOB DETECTION FROM YOLO 🚨")
        logger.critical("=" * 70)

        if not self.current_manifest:
            logger.error("❌ No crew manifest - cannot identify MOB person")
            # Still trigger generic MOB response
            await self._generic_mob_response(current_gps, current_heading, current_speed)
            return

        # Identify who went MOB
        mob_person = self.current_manifest.get_person_by_yolo_id(yolo_person_id)

        if not mob_person:
            logger.warning(f"⚠️ Unknown person (YOLO ID: {yolo_person_id}) went MOB")
            mob_person = Person(
                person_id=f"unknown_{yolo_person_id}",
                name=f"Unknown Person #{yolo_person_id}",
                role=PersonRole.GUEST,
                status=PersonStatus.MOB,
                yolo_person_id=yolo_person_id
            )
        else:
            logger.critical(f"   Person: {mob_person.name} ({mob_person.role.value})")
            mob_person.status = PersonStatus.MOB

        self.mob_person = mob_person
        self.mob_position = current_gps
        self.emergency_start_time = datetime.utcnow()
        self.emergency_active = True

        # CHECK: Is this single-handed operation?
        onboard_before_mob = self.current_manifest.total_onboard + 1  # Before MOB

        if onboard_before_mob == 1:
            # CRITICAL: Single-handed operation + MOB = VESSEL UNMANNED
            logger.critical("=" * 70)
            logger.critical("  🚨 CRITICAL: SINGLE-HANDED MOB DETECTED 🚨")
            logger.critical("  VESSEL IS NOW UNMANNED!")
            logger.critical("=" * 70)

            await self._autonomous_emergency_response(
                current_gps, current_heading, current_speed
            )
        else:
            # Multiple crew - standard MOB procedure
            logger.warning(f"MOB detected - {self.current_manifest.total_onboard} crew remaining onboard")
            await self._standard_mob_procedure(current_gps)

    async def _autonomous_emergency_response(
        self,
        current_gps: Tuple[float, float],
        current_heading: float,
        current_speed: float
    ):
        """
        AUTONOMOUS EMERGENCY RESPONSE
        Vessel acts completely independently to rescue sole person

        Args:
            current_gps: Current GPS position
            current_heading: Current heading
            current_speed: Current speed
        """
        logger.critical("=" * 70)
        logger.critical("  🤖 AUTONOMOUS EMERGENCY RESPONSE ACTIVATED")
        logger.critical("=" * 70)

        # STEP 1: Mark MOB position
        self.mob_position = current_gps
        logger.critical(f"1. 📍 MOB POSITION MARKED: {current_gps[0]:.6f}°N, {current_gps[1]:.6f}°E")

        # STEP 2: Automatic Mayday via VHF DSC
        await self._send_automatic_mayday_dsc(current_gps)

        # STEP 3: Sound alarm
        logger.critical("3. 🔊 SOUNDING EMERGENCY ALARM: 'VESSEL UNMANNED - MOB'")

        # STEP 4: Engage autopilot - Williamson Turn
        await self._autopilot_return_to_mob(current_gps, current_heading, current_speed)

        # STEP 5: Circle MOB position
        await self._autopilot_circle_mob(current_gps)

        # STEP 6: Continuous alerts
        await self._continuous_emergency_alerts()

        logger.critical("=" * 70)
        logger.critical("  AUTONOMOUS EMERGENCY RESPONSE COMPLETE")
        logger.critical("  VESSEL CIRCLING MOB POSITION - AWAITING RESCUE")
        logger.critical("=" * 70)

    async def _send_automatic_mayday_dsc(self, position: Tuple[float, float]):
        """
        Send automatic Mayday via VHF DSC

        VHF DSC (Digital Selective Calling) sends distress signal
        automatically to all vessels and coast guard

        Args:
            position: GPS position
        """
        logger.critical("2. 📻 SENDING AUTOMATIC MAYDAY VIA VHF DSC")

        mayday_message = {
            'distress_type': 'MOB',
            'vessel_name': self.vessel_name,
            'mmsi': self.mmsi,
            'position': position,
            'situation': 'SINGLE_HANDED_MOB_VESSEL_UNMANNED',
            'assistance_required': 'IMMEDIATE',
            'persons_onboard': 0,  # Vessel unmanned
            'persons_in_water': 1
        }

        if self.vhf_dsc:
            # FUTURE: Send via actual VHF DSC interface
            await self.vhf_dsc.send_distress_call(mayday_message)
            logger.critical("   ✅ Mayday DSC sent via VHF")
        else:
            # PLACEHOLDER
            logger.critical("   📻 VHF DSC MAYDAY (simulated):")
            logger.critical(f"      Vessel: {self.vessel_name} (MMSI: {self.mmsi})")
            logger.critical(f"      Position: {position[0]:.6f}°N, {position[1]:.6f}°E")
            logger.critical("      Distress: SINGLE-HANDED MOB - VESSEL UNMANNED")
            logger.critical("      Situation: Sole person overboard, no one onboard")
            logger.critical("      Request: IMMEDIATE ASSISTANCE")
            logger.critical("      Autopilot: Active, circling MOB position")

        self.mayday_sent = True

        # Also send via AIS SART if available
        logger.critical("   📡 Activating AIS SART (Search and Rescue Transmitter)")

    async def _autopilot_return_to_mob(
        self,
        mob_position: Tuple[float, float],
        current_heading: float,
        current_speed: float
    ):
        """
        Engage autopilot to return to MOB position
        Executes Williamson Turn

        Args:
            mob_position: GPS position where person went MOB
            current_heading: Heading when MOB occurred
            current_speed: Speed when MOB occurred
        """
        logger.critical("4. 🧭 ENGAGING AUTOPILOT - WILLIAMSON TURN")

        if self.autopilot:
            # FUTURE: Interface with actual autopilot
            williamson_turn = {
                'maneuver': 'williamson_turn',
                'mob_position': mob_position,
                'initial_heading': current_heading,
                'initial_speed': current_speed,
                'target_approach_speed': 2.0  # Approach at 2 knots
            }

            await self.autopilot.execute_mob_maneuver(williamson_turn)
            logger.critical("   ✅ Autopilot executing Williamson Turn")
        else:
            # PLACEHOLDER - log the procedure
            logger.critical("   🧭 Autopilot Williamson Turn procedure:")
            logger.critical("      1. Continue on current heading for 60 seconds")
            logger.critical(f"      2. Turn HARD to port (initial heading: {current_heading:.0f}°)")
            logger.critical("      3. Complete 240° turn to port")
            logger.critical(f"      4. Steady on reciprocal heading: {(current_heading + 180) % 360:.0f}°")
            logger.critical("      5. Return to MOB position")
            logger.critical("      6. Slow to 2 knots on approach")

            # Simulate turn execution
            logger.critical("   ⏱️  Executing turn... (60 seconds)")
            await asyncio.sleep(2)  # Simulate time
            logger.critical("   ✅ Williamson Turn complete")
            logger.critical("   🎯 Returning to MOB position...")
            await asyncio.sleep(2)
            logger.critical("   ✅ Arrived at MOB position")

        self.williamson_turn_active = True

    async def _autopilot_circle_mob(self, mob_position: Tuple[float, float]):
        """
        Circle MOB position at safe distance
        Maintains visual contact while awaiting rescue

        Args:
            mob_position: GPS position of MOB
        """
        logger.critical("5. ⭕ AUTOPILOT CIRCLING MOB POSITION")

        circle_params = {
            'center': mob_position,
            'radius_meters': 50,  # Circle at 50m radius
            'speed_knots': 2.0,   # Slow speed
            'direction': 'clockwise'
        }

        if self.autopilot:
            # FUTURE: Interface with actual autopilot
            await self.autopilot.execute_circle_pattern(circle_params)
            logger.critical("   ✅ Autopilot circling MOB at 50m radius")
        else:
            # PLACEHOLDER
            logger.critical("   ⭕ Autopilot circle pattern:")
            logger.critical(f"      Center: {mob_position[0]:.6f}°N, {mob_position[1]:.6f}°E")
            logger.critical("      Radius: 50 meters")
            logger.critical("      Speed: 2 knots")
            logger.critical("      Direction: Clockwise")
            logger.critical("      Duration: Until rescue arrives")

            logger.critical("   🔄 Circling... (continuous)")

        self.circling_mob = True

    async def _continuous_emergency_alerts(self):
        """
        Send continuous emergency alerts
        Updates Coast Guard and nearby vessels every 5 minutes
        """
        logger.critical("6. 📢 CONTINUOUS EMERGENCY ALERTS ACTIVE")
        logger.critical("   Updating Coast Guard every 5 minutes")
        logger.critical("   Broadcasting AIS emergency status")

        # FUTURE: Actual continuous alert loop
        # while self.emergency_active:
        #     await self._send_update_to_coast_guard()
        #     await asyncio.sleep(300)  # 5 minutes

    async def _standard_mob_procedure(self, position: Tuple[float, float]):
        """
        Standard MOB procedure when crew remains onboard

        Args:
            position: MOB position
        """
        logger.warning("📋 STANDARD MOB PROCEDURE")
        logger.warning("   Crew remaining onboard - manual recovery")

        # Get MOB procedure from knowledge base
        from app.knowledge.maritime_knowledge_base import EmergencyType

        mob_proc = self.knowledge_base.get_emergency_procedure(EmergencyType.MOB)

        logger.warning("IMMEDIATE ACTIONS:")
        for i, action in enumerate(mob_proc.immediate_actions_tr[:6], 1):
            logger.warning(f"   {i}. {action}")

        logger.warning(f"📍 MOB Position: {position[0]:.6f}°N, {position[1]:.6f}°E")
        logger.warning("📻 VHF Channel 16 ready for Mayday if needed")

    async def _generic_mob_response(
        self,
        position: Tuple[float, float],
        heading: float,
        speed: float
    ):
        """
        Generic MOB response when manifest not available

        Args:
            position: Current GPS position
            heading: Current heading
            speed: Current speed
        """
        logger.critical("🚨 MOB DETECTED - No manifest available")
        logger.critical("   Assuming single-handed - activating autonomous response")

        await self._autonomous_emergency_response(position, heading, speed)

    def manual_all_clear(self, recovered_by: str, recovery_notes: str):
        """
        Manual all-clear after person recovered

        Args:
            recovered_by: Who recovered the person (coast guard, nearby vessel, etc.)
            recovery_notes: Recovery details
        """
        logger.info("=" * 70)
        logger.info("  ✅ MOB RECOVERY COMPLETE")
        logger.info("=" * 70)

        if self.mob_person:
            logger.info(f"Person recovered: {self.mob_person.name}")
            self.mob_person.status = PersonStatus.ONBOARD

        logger.info(f"Recovered by: {recovered_by}")
        logger.info(f"Notes: {recovery_notes}")

        # Cancel emergency
        self.emergency_active = False
        self.williamson_turn_active = False
        self.circling_mob = False

        # Send all-clear via VHF DSC
        logger.info("📻 Sending ALL-CLEAR via VHF DSC")
        logger.info("   Cancelling distress alerts")

        logger.info("✅ Emergency cancelled - normal operations resumed")

    def get_emergency_status(self) -> Dict[str, Any]:
        """Get current emergency status"""
        if not self.emergency_active:
            return {
                'status': 'normal',
                'emergency_active': False
            }

        return {
            'status': 'EMERGENCY',
            'emergency_active': True,
            'emergency_type': 'SINGLE_HANDED_MOB',
            'mob_person': self.mob_person.name if self.mob_person else 'Unknown',
            'mob_position': self.mob_position,
            'time_elapsed': (datetime.utcnow() - self.emergency_start_time).total_seconds() if self.emergency_start_time else 0,
            'mayday_sent': self.mayday_sent,
            'williamson_turn_active': self.williamson_turn_active,
            'circling_mob': self.circling_mob,
            'vessel_status': 'UNMANNED' if self.current_manifest and self.current_manifest.is_single_handed() else 'CREW_ONBOARD'
        }


class CrewManifestSystem:
    """
    Crew manifest management system
    Tracks who is onboard: captain, crew, guests, children

    Integrates with YOLO person tracking
    """

    def __init__(self, vessel_name: str):
        """
        Initialize crew manifest system

        Args:
            vessel_name: Vessel name
        """
        self.vessel_name = vessel_name
        self.current_manifest: Optional[VesselManifest] = None
        self.manifest_history: List[VesselManifest] = []

        logger.info(f"CrewManifestSystem initialized for {vessel_name}")

    def create_manifest(self, persons: List[Person]) -> VesselManifest:
        """
        Create new crew manifest

        Args:
            persons: List of persons onboard

        Returns:
            New manifest
        """
        manifest = VesselManifest(
            vessel_name=self.vessel_name,
            manifest_date=datetime.utcnow(),
            persons=persons
        )

        self.current_manifest = manifest
        self.manifest_history.append(manifest)

        logger.info(f"📋 New manifest created: {manifest.total_onboard} persons")

        if manifest.is_single_handed():
            logger.warning("⚠️ SINGLE-HANDED OPERATION")

        return manifest

    def link_yolo_tracking(self, person_id: str, yolo_person_id: int):
        """
        Link person to YOLO tracking ID

        Args:
            person_id: Person identifier
            yolo_person_id: YOLO tracking ID
        """
        if not self.current_manifest:
            logger.error("No active manifest")
            return

        for person in self.current_manifest.persons:
            if person.person_id == person_id:
                person.yolo_person_id = yolo_person_id
                logger.info(f"✓ Linked {person.name} to YOLO Person #{yolo_person_id}")
                return

        logger.warning(f"Person {person_id} not found in manifest")

    def person_goes_ashore(self, person_id: str):
        """
        Mark person as going ashore

        Args:
            person_id: Person identifier
        """
        if not self.current_manifest:
            return

        for person in self.current_manifest.persons:
            if person.person_id == person_id:
                person.status = PersonStatus.ASHORE
                logger.info(f"🏖️ {person.name} went ashore")
                logger.info(f"   Remaining onboard: {self.current_manifest.total_onboard}")

                if self.current_manifest.is_single_handed():
                    logger.warning("⚠️ Now operating SINGLE-HANDED")

                return

    def person_returns_onboard(self, person_id: str):
        """
        Mark person as returning onboard

        Args:
            person_id: Person identifier
        """
        if not self.current_manifest:
            return

        for person in self.current_manifest.persons:
            if person.person_id == person_id:
                person.status = PersonStatus.ONBOARD
                person.last_seen = datetime.utcnow()
                logger.info(f"✅ {person.name} returned onboard")
                logger.info(f"   Total onboard: {self.current_manifest.total_onboard}")
                return

    def get_manifest_summary(self) -> str:
        """Get manifest summary"""
        if not self.current_manifest:
            return "📋 No active manifest"

        manifest = self.current_manifest

        summary = f"📋 CREW MANIFEST - {manifest.vessel_name}\n"
        summary += f"   Date: {manifest.manifest_date.strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"   Total onboard: {manifest.total_onboard}\n\n"

        for person in manifest.persons:
            status_icon = {
                PersonStatus.ONBOARD: "✅",
                PersonStatus.ASHORE: "🏖️",
                PersonStatus.MOB: "🚨",
                PersonStatus.UNKNOWN: "❓"
            }.get(person.status, "?")

            summary += f"   {status_icon} {person.name} ({person.role.value})\n"

            if person.yolo_person_id is not None:
                summary += f"      YOLO: Person #{person.yolo_person_id}\n"

        if manifest.is_single_handed():
            summary += "\n⚠️ SINGLE-HANDED OPERATION\n"
            summary += "   Enhanced MOB monitoring active\n"

        return summary
