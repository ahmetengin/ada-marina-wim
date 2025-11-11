"""
Compliance Service
Central service for WIM regulation compliance checking and enforcement

This service integrates with the VERIFY agent and provides
programmatic access to compliance checking functionality.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session

from app.services.wim_regulations import (
    get_regulation,
    get_regulations_by_category,
    get_critical_regulations,
    search_regulations,
    RegulationCategory,
    RegulationArticle
)
from app.models.vessel import Vessel
from app.models.customer import Customer
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.violation import Violation, ViolationSeverity, ViolationStatus
from app.models.permit import Permit, PermitType, PermitStatus

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    Compliance Service for WIM regulations

    Provides methods to check compliance and create violations
    """

    def __init__(self, db: Session):
        self.db = db

    def check_vessel_compliance(
        self,
        vessel_id: int,
        check_articles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive compliance check for a vessel

        Args:
            vessel_id: ID of vessel to check
            check_articles: Specific articles to check (None = check all)

        Returns:
            Compliance report
        """
        vessel = self.db.query(Vessel).filter(Vessel.id == vessel_id).first()
        if not vessel:
            raise ValueError(f"Vessel {vessel_id} not found")

        results = {
            "vessel_id": vessel_id,
            "vessel_name": vessel.name,
            "checked_at": datetime.now(),
            "checks_performed": [],
            "violations_found": [],
            "warnings": [],
            "compliance_score": 100.0
        }

        # Check insurance (E.2.1)
        if not check_articles or "E.2.1" in check_articles:
            insurance_check = self._check_insurance(vessel)
            results["checks_performed"].append(insurance_check)

            if not insurance_check["compliant"]:
                results["violations_found"].append(insurance_check)
                results["compliance_score"] -= 10

        # Check for active violations
        active_violations = self.db.query(Violation).filter(
            Violation.vessel_id == vessel_id,
            Violation.status != ViolationStatus.RESOLVED
        ).all()

        for violation in active_violations:
            regulation = get_regulation(violation.article_violated)
            penalty = 0

            if violation.severity == ViolationSeverity.CRITICAL:
                penalty = 25
            elif violation.severity == ViolationSeverity.MAJOR:
                penalty = 10
            elif violation.severity == ViolationSeverity.MINOR:
                penalty = 5
            elif violation.severity == ViolationSeverity.WARNING:
                penalty = 2

            results["compliance_score"] -= penalty
            results["violations_found"].append({
                "article": violation.article_violated,
                "description": violation.description,
                "severity": violation.severity.value,
                "regulation_title": regulation.title if regulation else "Unknown"
            })

        results["compliance_score"] = max(0, results["compliance_score"])

        # Determine overall status
        if results["compliance_score"] >= 95:
            results["status"] = "EXCELLENT"
        elif results["compliance_score"] >= 85:
            results["status"] = "GOOD"
        elif results["compliance_score"] >= 70:
            results["status"] = "FAIR"
        elif results["compliance_score"] >= 50:
            results["status"] = "POOR"
        else:
            results["status"] = "CRITICAL"

        return results

    def _check_insurance(self, vessel: Vessel) -> Dict[str, Any]:
        """Check insurance compliance (Article E.2.1)"""
        regulation = get_regulation("E.2.1")

        result = {
            "article": "E.2.1",
            "regulation": regulation.title if regulation else "Insurance Requirements",
            "compliant": True,
            "issues": []
        }

        if not vessel.insurance_company:
            result["compliant"] = False
            result["issues"].append("No insurance company on file")

        if not vessel.insurance_policy_number:
            result["compliant"] = False
            result["issues"].append("No insurance policy number on file")

        if vessel.insurance_expiry_date:
            if vessel.insurance_expiry_date < datetime.now():
                result["compliant"] = False
                result["issues"].append(f"Insurance expired on {vessel.insurance_expiry_date.date()}")
            elif vessel.insurance_expiry_date < datetime.now() + timedelta(days=30):
                result["issues"].append(f"Insurance expires soon ({vessel.insurance_expiry_date.date()})")

        return result

    def check_hot_work_compliance(self, permit_id: int) -> Dict[str, Any]:
        """
        Check hot work permit compliance (Article E.5.5)

        Args:
            permit_id: ID of hot work permit

        Returns:
            Compliance check result
        """
        permit = self.db.query(Permit).filter(Permit.id == permit_id).first()
        if not permit:
            raise ValueError(f"Permit {permit_id} not found")

        if permit.permit_type != PermitType.HOT_WORK:
            raise ValueError(f"Permit {permit_id} is not a hot work permit")

        regulation = get_regulation("E.5.5")

        result = {
            "permit_id": permit_id,
            "permit_number": permit.permit_number,
            "article": "E.5.5",
            "regulation": regulation.title if regulation else "Hot Work Permits",
            "compliant": True,
            "issues": []
        }

        # Check required safety measures
        if not permit.fire_prevention_measures:
            result["compliant"] = False
            result["issues"].append("Fire prevention measures not documented")

        if not permit.fire_watch_assigned:
            result["compliant"] = False
            result["issues"].append("Fire watch not assigned")

        if not permit.extinguishers_positioned:
            result["compliant"] = False
            result["issues"].append("Fire extinguishers not positioned")

        if not permit.surrounding_notified:
            result["compliant"] = False
            result["issues"].append("Surrounding vessels not notified")

        if not permit.safety_briefing_completed:
            result["issues"].append("Safety briefing not completed")
            result["compliant"] = False

        # Check permit status
        if permit.status == PermitStatus.EXPIRED:
            result["compliant"] = False
            result["issues"].append("Permit has expired")

        if permit.status == PermitStatus.REVOKED:
            result["compliant"] = False
            result["issues"].append("Permit has been revoked")

        return result

    def create_violation(
        self,
        vessel_id: int,
        article_number: str,
        description: str,
        detected_by: str = "SYSTEM",
        evidence: Optional[str] = None
    ) -> Violation:
        """
        Create a new violation record

        Args:
            vessel_id: ID of vessel
            article_number: Regulation article violated
            description: Description of violation
            detected_by: Who/what detected the violation
            evidence: Optional evidence description

        Returns:
            Created Violation object
        """
        vessel = self.db.query(Vessel).filter(Vessel.id == vessel_id).first()
        if not vessel:
            raise ValueError(f"Vessel {vessel_id} not found")

        regulation = get_regulation(article_number)
        if not regulation:
            logger.warning(f"Unknown regulation article: {article_number}")
            # Create violation anyway but with default severity
            severity = ViolationSeverity.MINOR
            fine_amount = 100.0
        else:
            # Map regulation severity to violation severity
            severity_map = {
                "critical": ViolationSeverity.CRITICAL,
                "major": ViolationSeverity.MAJOR,
                "minor": ViolationSeverity.MINOR,
                "warning": ViolationSeverity.WARNING
            }
            severity = severity_map.get(regulation.severity, ViolationSeverity.MINOR)
            fine_amount = regulation.fine_amount_eur

        violation = Violation(
            vessel_id=vessel_id,
            customer_id=vessel.customer_id,
            article_violated=article_number,
            description=description,
            severity=severity,
            fine_amount_eur=fine_amount,
            detected_by=detected_by,
            evidence_description=evidence
        )

        self.db.add(violation)
        self.db.commit()
        self.db.refresh(violation)

        logger.info(
            f"Violation created: {article_number} for vessel {vessel.name} "
            f"(Severity: {severity.value})"
        )

        return violation

    def check_berth_assignment_compliance(self, assignment_id: int) -> Dict[str, Any]:
        """
        Check compliance for a berth assignment

        Args:
            assignment_id: ID of berth assignment

        Returns:
            Compliance check result
        """
        assignment = self.db.query(BerthAssignment).filter(
            BerthAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        from app.models.berth import Berth

        berth = self.db.query(Berth).filter(Berth.id == assignment.berth_id).first()
        vessel = self.db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()

        result = {
            "assignment_id": assignment_id,
            "compliant": True,
            "issues": []
        }

        if not vessel or not berth:
            result["compliant"] = False
            result["issues"].append("Invalid assignment data")
            return result

        # Check vessel fits in berth (Article B.3)
        if vessel.length_meters > berth.length_meters:
            result["compliant"] = False
            result["issues"].append({
                "article": "B.3",
                "issue": f"Vessel length ({vessel.length_meters}m) exceeds berth capacity ({berth.length_meters}m)"
            })

        if vessel.width_meters > berth.width_meters:
            result["compliant"] = False
            result["issues"].append({
                "article": "B.3",
                "issue": f"Vessel width ({vessel.width_meters}m) exceeds berth width ({berth.width_meters}m)"
            })

        if vessel.draft_meters > berth.depth_meters:
            result["compliant"] = False
            result["issues"].append({
                "article": "B.3",
                "issue": f"Vessel draft ({vessel.draft_meters}m) exceeds berth depth ({berth.depth_meters}m)"
            })

        # Check for overstay (Article E.4.2)
        if assignment.status == AssignmentStatus.ACTIVE:
            if assignment.expected_check_out < datetime.now():
                hours_overdue = (datetime.now() - assignment.expected_check_out).total_seconds() / 3600
                result["issues"].append({
                    "article": "E.4.2",
                    "issue": f"Vessel overstay: {hours_overdue:.1f} hours past expected departure"
                })

        # Check vessel insurance
        insurance_check = self._check_insurance(vessel)
        if not insurance_check["compliant"]:
            result["compliant"] = False
            result["issues"].append({
                "article": "E.2.1",
                "issue": "Insurance compliance issues",
                "details": insurance_check["issues"]
            })

        return result

    def get_compliance_statistics(self) -> Dict[str, Any]:
        """
        Get overall marina compliance statistics

        Returns:
            Statistics dictionary
        """
        total_vessels = self.db.query(Vessel).count()

        # Count violations by severity
        critical_violations = self.db.query(Violation).filter(
            Violation.severity == ViolationSeverity.CRITICAL,
            Violation.status != ViolationStatus.RESOLVED
        ).count()

        major_violations = self.db.query(Violation).filter(
            Violation.severity == ViolationSeverity.MAJOR,
            Violation.status != ViolationStatus.RESOLVED
        ).count()

        minor_violations = self.db.query(Violation).filter(
            Violation.severity == ViolationSeverity.MINOR,
            Violation.status != ViolationStatus.RESOLVED
        ).count()

        # Vessels with violations
        vessels_with_violations = self.db.query(Violation.vessel_id).filter(
            Violation.status != ViolationStatus.RESOLVED
        ).distinct().count()

        # Overall compliance rate
        compliance_rate = (total_vessels - vessels_with_violations) / total_vessels * 100 if total_vessels > 0 else 100

        # Insurance compliance
        vessels_with_insurance = self.db.query(Vessel).filter(
            Vessel.insurance_company.isnot(None),
            Vessel.insurance_policy_number.isnot(None)
        ).count()

        insurance_compliance = vessels_with_insurance / total_vessels * 100 if total_vessels > 0 else 0

        return {
            "total_vessels": total_vessels,
            "overall_compliance_rate": round(compliance_rate, 2),
            "vessels_compliant": total_vessels - vessels_with_violations,
            "vessels_non_compliant": vessels_with_violations,
            "active_violations": {
                "critical": critical_violations,
                "major": major_violations,
                "minor": minor_violations,
                "total": critical_violations + major_violations + minor_violations
            },
            "insurance_compliance_rate": round(insurance_compliance, 2),
            "timestamp": datetime.now().isoformat()
        }

    def get_regulation_info(self, article_number: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific regulation

        Args:
            article_number: Article number to lookup

        Returns:
            Regulation information or None
        """
        regulation = get_regulation(article_number)
        if not regulation:
            return None

        return {
            "article_number": regulation.article_number,
            "category": regulation.category.value,
            "title": regulation.title,
            "description": regulation.description,
            "severity": regulation.severity,
            "fine_amount_eur": regulation.fine_amount_eur,
            "enforcement_action": regulation.enforcement_action
        }

    def search_regulations_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search regulations by keyword

        Args:
            keyword: Search term

        Returns:
            List of matching regulations
        """
        regulations = search_regulations(keyword)

        return [
            {
                "article_number": reg.article_number,
                "title": reg.title,
                "description": reg.description,
                "severity": reg.severity
            }
            for reg in regulations
        ]

    def get_critical_regulations_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all critical regulations

        Returns:
            List of critical regulations
        """
        regulations = get_critical_regulations()

        return [
            {
                "article_number": reg.article_number,
                "title": reg.title,
                "description": reg.description,
                "fine_amount_eur": reg.fine_amount_eur,
                "enforcement_action": reg.enforcement_action
            }
            for reg in regulations
        ]


def create_compliance_service(db: Session) -> ComplianceService:
    """
    Factory function to create ComplianceService

    Args:
        db: Database session

    Returns:
        ComplianceService instance
    """
    return ComplianceService(db)
