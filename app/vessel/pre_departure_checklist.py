"""
Pre-Departure Checklist
Complete vessel systems check before departure

"Deniz şaka değil" - Full check required!
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Check item status"""
    NOT_CHECKED = "not_checked"
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"


class SystemCategory(Enum):
    """Vessel system categories"""
    ENGINE = "engine"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    NAVIGATION = "navigation"
    SAFETY = "safety"
    ANCHORING = "anchoring"
    PROVISIONS = "provisions"


@dataclass
class CheckItem:
    """Single checklist item"""
    id: str
    category: SystemCategory
    item: str
    item_tr: str  # Turkish
    critical: bool
    status: CheckStatus = CheckStatus.NOT_CHECKED
    notes: Optional[str] = None
    checked_at: Optional[datetime] = None
    checked_by: Optional[str] = None


@dataclass
class ResourceLevel:
    """Resource level tracking (fuel, water, etc.)"""
    resource_type: str
    current_level: float
    capacity: float
    unit: str
    last_filled: Optional[datetime]
    consumption_rate: Optional[float] = None  # Per hour/day


@dataclass
class MaintenanceRecord:
    """Maintenance and service record"""
    id: str
    date: datetime
    system: SystemCategory
    description: str
    performed_by: str
    next_service_date: Optional[datetime] = None
    next_service_hours: Optional[float] = None


class PreDepartureChecklist:
    """
    Complete pre-departure checklist system

    Ensures vessel is ready for safe passage:
    - Engine and mechanical systems
    - Electrical systems
    - Safety equipment
    - Fuel and water levels
    - Navigation equipment
    - Anchoring equipment
    """

    def __init__(self, vessel_name: str):
        """
        Initialize checklist for vessel

        Args:
            vessel_name: Vessel name
        """
        self.vessel_name = vessel_name
        self.checklist = self._initialize_checklist()
        self.resources = {}
        self.maintenance_log = []

        logger.info(f"PreDepartureChecklist initialized for {vessel_name}")

    def _initialize_checklist(self) -> List[CheckItem]:
        """
        Initialize complete checklist

        Returns:
            List of check items
        """
        return [
            # ENGINE & MECHANICAL
            CheckItem(
                id="engine_oil_level",
                category=SystemCategory.ENGINE,
                item="Engine oil level",
                item_tr="Motor yağı seviyesi",
                critical=True
            ),
            CheckItem(
                id="engine_coolant",
                category=SystemCategory.ENGINE,
                item="Coolant level",
                item_tr="Soğutma suyu seviyesi",
                critical=True
            ),
            CheckItem(
                id="engine_belts",
                category=SystemCategory.ENGINE,
                item="Belt tension and condition",
                item_tr="Kayış gerginliği ve durumu",
                critical=True
            ),
            CheckItem(
                id="fuel_filters",
                category=SystemCategory.ENGINE,
                item="Fuel filters clean",
                item_tr="Yakıt filtreleri temiz",
                critical=True
            ),
            CheckItem(
                id="bilge_pump",
                category=SystemCategory.ENGINE,
                item="Bilge pump operational",
                item_tr="Sintine pompası çalışıyor",
                critical=True
            ),
            CheckItem(
                id="engine_start_test",
                category=SystemCategory.ENGINE,
                item="Engine starts and runs smoothly",
                item_tr="Motor sorunsuz çalışıyor",
                critical=True
            ),

            # ELECTRICAL
            CheckItem(
                id="battery_voltage",
                category=SystemCategory.ELECTRICAL,
                item="Battery voltage (>12.4V)",
                item_tr="Batarya voltajı (>12.4V)",
                critical=True
            ),
            CheckItem(
                id="battery_connections",
                category=SystemCategory.ELECTRICAL,
                item="Battery connections tight and clean",
                item_tr="Batarya bağlantıları sıkı ve temiz",
                critical=True
            ),
            CheckItem(
                id="navigation_lights",
                category=SystemCategory.ELECTRICAL,
                item="All navigation lights working",
                item_tr="Seyir lambaları çalışıyor",
                critical=True
            ),
            CheckItem(
                id="anchor_light",
                category=SystemCategory.ELECTRICAL,
                item="Anchor light working",
                item_tr="Demir ışığı çalışıyor",
                critical=True
            ),

            # PLUMBING & RESOURCES
            CheckItem(
                id="fuel_level",
                category=SystemCategory.PLUMBING,
                item="Fuel tank full or adequate",
                item_tr="Yakıt deposu dolu veya yeterli",
                critical=True
            ),
            CheckItem(
                id="water_level",
                category=SystemCategory.PLUMBING,
                item="Fresh water tank full",
                item_tr="Tatlı su deposu dolu",
                critical=True
            ),
            CheckItem(
                id="water_pump",
                category=SystemCategory.PLUMBING,
                item="Water pump operational",
                item_tr="Su pompası çalışıyor",
                critical=False
            ),
            CheckItem(
                id="holding_tank",
                category=SystemCategory.PLUMBING,
                item="Holding tank empty or adequate capacity",
                item_tr="Pis su tankı boş veya yeterli kapasite",
                critical=False
            ),

            # NAVIGATION
            CheckItem(
                id="gps_operational",
                category=SystemCategory.NAVIGATION,
                item="GPS/Chartplotter working",
                item_tr="GPS/Chartplotter çalışıyor",
                critical=True
            ),
            CheckItem(
                id="depth_sounder",
                category=SystemCategory.NAVIGATION,
                item="Depth sounder working",
                item_tr="Derinlik sensörü çalışıyor",
                critical=True
            ),
            CheckItem(
                id="vhf_radio",
                category=SystemCategory.NAVIGATION,
                item="VHF radio working (test on ch 16)",
                item_tr="VHF radyo çalışıyor (kanal 16 test)",
                critical=True
            ),
            CheckItem(
                id="ais_transponder",
                category=SystemCategory.NAVIGATION,
                item="AIS transponder transmitting",
                item_tr="AIS transponder yayın yapıyor",
                critical=False
            ),
            CheckItem(
                id="compass",
                category=SystemCategory.NAVIGATION,
                item="Compass operational",
                item_tr="Pusula çalışıyor",
                critical=True
            ),

            # SAFETY EQUIPMENT
            CheckItem(
                id="life_jackets",
                category=SystemCategory.SAFETY,
                item="Life jackets for all crew",
                item_tr="Tüm mürettebat için can yeleği",
                critical=True
            ),
            CheckItem(
                id="life_rings",
                category=SystemCategory.SAFETY,
                item="Life rings accessible",
                item_tr="Can simitleri erişilebilir",
                critical=True
            ),
            CheckItem(
                id="fire_extinguishers",
                category=SystemCategory.SAFETY,
                item="Fire extinguishers (check date)",
                item_tr="Yangın söndürücüler (tarih kontrol)",
                critical=True
            ),
            CheckItem(
                id="flares",
                category=SystemCategory.SAFETY,
                item="Flares within expiry date",
                item_tr="Işıldaklar son kullanma tarihinde",
                critical=True
            ),
            CheckItem(
                id="first_aid_kit",
                category=SystemCategory.SAFETY,
                item="First aid kit stocked",
                item_tr="İlk yardım çantası dolu",
                critical=True
            ),
            CheckItem(
                id="epirb",
                category=SystemCategory.SAFETY,
                item="EPIRB/PLB battery good",
                item_tr="EPIRB/PLB batarya iyi",
                critical=False
            ),

            # ANCHORING EQUIPMENT
            CheckItem(
                id="main_anchor",
                category=SystemCategory.ANCHORING,
                item="Main anchor + 40m+ chain",
                item_tr="Ana demir + 40m+ zincir",
                critical=True
            ),
            CheckItem(
                id="anchor_windlass",
                category=SystemCategory.ANCHORING,
                item="Anchor windlass operational",
                item_tr="Demir vinci çalışıyor",
                critical=True
            ),
            CheckItem(
                id="spare_anchor",
                category=SystemCategory.ANCHORING,
                item="Spare/stern anchor ready",
                item_tr="Yedek/kıç demiri hazır",
                critical=False
            ),
            CheckItem(
                id="anchor_rode",
                category=SystemCategory.ANCHORING,
                item="Anchor rode/chain inspected",
                item_tr="Demir zinciri kontrol edildi",
                critical=True
            ),
            CheckItem(
                id="fenders_lines",
                category=SystemCategory.ANCHORING,
                item="Fenders and mooring lines ready",
                item_tr="Fender ve palamar hazır",
                critical=False
            ),

            # PROVISIONS
            CheckItem(
                id="food_provisions",
                category=SystemCategory.PROVISIONS,
                item="Food for voyage duration + 1 day",
                item_tr="Sefer süresi + 1 gün yiyecek",
                critical=False
            ),
            CheckItem(
                id="drinking_water",
                category=SystemCategory.PROVISIONS,
                item="Bottled drinking water",
                item_tr="Şişe içme suyu",
                critical=True
            ),
            CheckItem(
                id="garbage_bags",
                category=SystemCategory.PROVISIONS,
                item="Garbage bags (no throwing overboard!)",
                item_tr="Çöp poşetleri (denize atmayın!)",
                critical=False
            ),
        ]

    def check_item(
        self,
        item_id: str,
        status: CheckStatus,
        notes: Optional[str] = None,
        checked_by: Optional[str] = None
    ) -> bool:
        """
        Check an item on the list

        Args:
            item_id: Item identifier
            status: Check result
            notes: Optional notes
            checked_by: Who performed the check

        Returns:
            True if item found and updated
        """
        for item in self.checklist:
            if item.id == item_id:
                item.status = status
                item.notes = notes
                item.checked_at = datetime.utcnow()
                item.checked_by = checked_by

                if status == CheckStatus.CRITICAL or status == CheckStatus.FAILED:
                    logger.warning(f"⚠️ CRITICAL: {item.item_tr} - {notes}")
                elif status == CheckStatus.WARNING:
                    logger.warning(f"⚠️ Warning: {item.item_tr} - {notes}")
                else:
                    logger.info(f"✅ {item.item_tr} - OK")

                return True

        return False

    def get_checklist_status(self) -> Dict[str, Any]:
        """
        Get overall checklist status

        Returns:
            Status summary
        """
        total = len(self.checklist)
        checked = sum(1 for item in self.checklist if item.status != CheckStatus.NOT_CHECKED)
        ok = sum(1 for item in self.checklist if item.status == CheckStatus.OK)
        warnings = sum(1 for item in self.checklist if item.status == CheckStatus.WARNING)
        critical = sum(1 for item in self.checklist if item.status in [CheckStatus.CRITICAL, CheckStatus.FAILED])

        # Check if critical items are all OK
        critical_items = [item for item in self.checklist if item.critical]
        critical_ok = all(item.status == CheckStatus.OK for item in critical_items)

        ready_for_departure = (checked == total) and (critical == 0) and critical_ok

        return {
            'vessel': self.vessel_name,
            'total_items': total,
            'checked': checked,
            'ok': ok,
            'warnings': warnings,
            'critical_issues': critical,
            'ready_for_departure': ready_for_departure,
            'completion_percentage': (checked / total * 100) if total > 0 else 0
        }

    def get_critical_issues(self) -> List[CheckItem]:
        """
        Get list of critical issues

        Returns:
            List of critical/failed items
        """
        return [
            item for item in self.checklist
            if item.status in [CheckStatus.CRITICAL, CheckStatus.FAILED]
        ]

    def get_by_category(self, category: SystemCategory) -> List[CheckItem]:
        """
        Get items by category

        Args:
            category: System category

        Returns:
            List of items in category
        """
        return [item for item in self.checklist if item.category == category]

    def update_resource_level(
        self,
        resource_type: str,
        current_level: float,
        capacity: float,
        unit: str,
        last_filled: Optional[datetime] = None
    ):
        """
        Update resource level (fuel, water, etc.)

        Args:
            resource_type: Type of resource
            current_level: Current level
            capacity: Total capacity
            unit: Unit (liters, gallons, etc.)
            last_filled: When last filled
        """
        self.resources[resource_type] = ResourceLevel(
            resource_type=resource_type,
            current_level=current_level,
            capacity=capacity,
            unit=unit,
            last_filled=last_filled or datetime.utcnow()
        )

        percentage = (current_level / capacity * 100) if capacity > 0 else 0

        if percentage < 25:
            logger.warning(f"⚠️ Low {resource_type}: {percentage:.0f}% ({current_level} {unit})")
        else:
            logger.info(f"✅ {resource_type}: {percentage:.0f}% ({current_level} {unit})")

    def get_resource_status(self) -> Dict[str, ResourceLevel]:
        """Get all resource levels"""
        return self.resources

    def add_maintenance_record(
        self,
        system: SystemCategory,
        description: str,
        performed_by: str,
        next_service_date: Optional[datetime] = None,
        next_service_hours: Optional[float] = None
    ):
        """
        Add maintenance record

        Args:
            system: System category
            description: What was done
            performed_by: Who performed it
            next_service_date: When next service due
            next_service_hours: Engine hours until next service
        """
        record = MaintenanceRecord(
            id=f"maint_{len(self.maintenance_log) + 1}",
            date=datetime.utcnow(),
            system=system,
            description=description,
            performed_by=performed_by,
            next_service_date=next_service_date,
            next_service_hours=next_service_hours
        )

        self.maintenance_log.append(record)
        logger.info(f"📝 Maintenance logged: {description}")

    def get_upcoming_maintenance(self, days_ahead: int = 30) -> List[MaintenanceRecord]:
        """
        Get upcoming maintenance items

        Args:
            days_ahead: Look ahead this many days

        Returns:
            List of upcoming maintenance
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)

        upcoming = [
            record for record in self.maintenance_log
            if record.next_service_date and record.next_service_date <= cutoff_date
        ]

        return upcoming

    def print_checklist(self, category: Optional[SystemCategory] = None):
        """
        Print checklist (for CLI use)

        Args:
            category: Optional category filter
        """
        if category:
            items = self.get_by_category(category)
            print(f"\n{'=' * 60}")
            print(f"  {category.value.upper()} CHECKLIST")
            print(f"{'=' * 60}")
        else:
            items = self.checklist
            print(f"\n{'=' * 60}")
            print(f"  PRE-DEPARTURE CHECKLIST: {self.vessel_name}")
            print(f"{'=' * 60}")

        for item in items:
            status_icon = {
                CheckStatus.NOT_CHECKED: "⬜",
                CheckStatus.OK: "✅",
                CheckStatus.WARNING: "⚠️",
                CheckStatus.CRITICAL: "🔴",
                CheckStatus.FAILED: "❌"
            }.get(item.status, "❓")

            critical_marker = " [CRITICAL]" if item.critical else ""
            print(f"{status_icon} {item.item_tr}{critical_marker}")
            if item.notes:
                print(f"   Note: {item.notes}")

        if not category:
            print(f"\n{'=' * 60}")
            status = self.get_checklist_status()
            print(f"  STATUS: {status['checked']}/{status['total_items']} checked")
            print(f"  Completion: {status['completion_percentage']:.0f}%")

            if status['critical_issues'] > 0:
                print(f"  🔴 CRITICAL ISSUES: {status['critical_issues']}")
                print(f"  ❌ NOT READY FOR DEPARTURE")
            elif status['warnings'] > 0:
                print(f"  ⚠️  WARNINGS: {status['warnings']}")
                print(f"  ⚠️  Proceed with caution")
            elif status['ready_for_departure']:
                print(f"  ✅ READY FOR DEPARTURE")
            else:
                print(f"  ⏳ Checklist incomplete")
            print(f"{'=' * 60}\n")
