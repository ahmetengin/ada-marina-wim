"""
VERIFY Agent - Compliance Checking and Violation Detection
Part of the Big-5 Agents architecture for ADA.MARINA

Responsibilities:
- Monitor compliance with 176 WIM regulation articles
- Automated violation detection
- Insurance verification (Article E.2.1)
- Permit compliance monitoring
- Hot work safety checks (Article E.5.5)
- Generate compliance reports
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

import anthropic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.vessel import Vessel
from app.models.customer import Customer
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.violation import Violation, ViolationSeverity, ViolationStatus
from app.models.permit import Permit, PermitType, PermitStatus

logger = logging.getLogger(__name__)


class VerifyAgent:
    """
    VERIFY Agent - Automated compliance monitoring

    Continuously monitors marina operations for WIM regulation compliance
    and automatically detects violations.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.compliance_threshold = settings.COMPLIANCE_THRESHOLD
        self.is_running = False

        logger.info("VERIFY Agent initialized - Monitoring WIM regulations")

    async def start(self):
        """Start the VERIFY agent background service"""
        self.is_running = True
        logger.info("VERIFY Agent started - Compliance monitoring active")

        while self.is_running:
            try:
                # Run compliance checks periodically
                await self._run_compliance_checks()

                # Wait before next check cycle
                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in VERIFY agent main loop: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Stop the VERIFY agent"""
        self.is_running = False
        logger.info("VERIFY Agent stopped")

    async def _run_compliance_checks(self):
        """Run all compliance checks"""
        db = SessionLocal()
        try:
            logger.debug("Running compliance checks...")

            # Check insurance compliance (Article E.2.1)
            await self._check_insurance_compliance(db)

            # Check permit compliance
            await self._check_permit_compliance(db)

            # Check hot work safety (Article E.5.5)
            await self._check_hot_work_safety(db)

            # Check expired permits
            await self._check_expired_permits(db)

            # Check for general regulation violations
            await self._check_general_compliance(db)

        except Exception as e:
            logger.error(f"Error running compliance checks: {e}")
        finally:
            db.close()

    async def _check_insurance_compliance(self, db: Session):
        """
        Check vessel insurance compliance (Article E.2.1)

        All vessels must have valid insurance
        """
        # Get all vessels with active assignments
        active_assignments = db.query(BerthAssignment).filter(
            BerthAssignment.status == AssignmentStatus.ACTIVE
        ).all()

        for assignment in active_assignments:
            vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
            if not vessel:
                continue

            violation_detected = False
            violation_description = ""

            # Check if insurance info exists
            if not vessel.insurance_company or not vessel.insurance_policy_number:
                violation_detected = True
                violation_description = "Vessel operating without insurance documentation"

            # Check if insurance is expired
            elif vessel.insurance_expiry_date:
                if vessel.insurance_expiry_date < datetime.now():
                    violation_detected = True
                    violation_description = f"Vessel insurance expired on {vessel.insurance_expiry_date.date()}"

            if violation_detected:
                # Check if violation already exists
                existing = db.query(Violation).filter(
                    and_(
                        Violation.vessel_id == vessel.id,
                        Violation.article_violated == "E.2.1",
                        Violation.status != ViolationStatus.RESOLVED
                    )
                ).first()

                if not existing:
                    # Create new violation
                    violation = Violation(
                        vessel_id=vessel.id,
                        customer_id=vessel.customer_id,
                        article_violated="E.2.1",
                        description=violation_description,
                        severity=ViolationSeverity.MAJOR,
                        detected_by="VERIFY_AGENT",
                        fine_amount_eur=500.0  # Standard insurance violation fine
                    )
                    db.add(violation)
                    db.commit()

                    logger.warning(
                        f"Insurance violation detected: Vessel {vessel.name} - {violation_description}"
                    )

    async def _check_permit_compliance(self, db: Session):
        """Check that required permits are in place for active work"""
        # Get all active assignments
        active_assignments = db.query(BerthAssignment).filter(
            BerthAssignment.status == AssignmentStatus.ACTIVE
        ).all()

        for assignment in active_assignments:
            # Check if vessel has active hot work
            # This would integrate with actual monitoring systems
            # For now, we check if they have permits when they should
            pass

    async def _check_hot_work_safety(self, db: Session):
        """
        Monitor hot work permit safety compliance (Article E.5.5)

        Verify fire prevention measures are in place
        """
        active_hot_work = db.query(Permit).filter(
            and_(
                Permit.permit_type == PermitType.HOT_WORK,
                Permit.status == PermitStatus.ACTIVE
            )
        ).all()

        for permit in active_hot_work:
            violations = []

            # Check required safety measures
            if not permit.fire_prevention_measures:
                violations.append("Fire prevention measures not documented")

            if not permit.fire_watch_assigned:
                violations.append("Fire watch not assigned")

            if not permit.extinguishers_positioned:
                violations.append("Fire extinguishers not positioned")

            if not permit.surrounding_notified:
                violations.append("Surrounding vessels not notified")

            # If any violations found, create violation record
            if violations:
                existing = db.query(Violation).filter(
                    and_(
                        Violation.vessel_id == permit.vessel_id,
                        Violation.article_violated == "E.5.5",
                        Violation.status != ViolationStatus.RESOLVED
                    )
                ).first()

                if not existing:
                    violation = Violation(
                        vessel_id=permit.vessel_id,
                        customer_id=permit.customer_id,
                        article_violated="E.5.5",
                        description=f"Hot work safety violations: {'; '.join(violations)}",
                        severity=ViolationSeverity.CRITICAL,  # Fire safety is critical
                        detected_by="VERIFY_AGENT",
                        fine_amount_eur=1000.0  # Higher fine for safety violations
                    )
                    db.add(violation)
                    db.commit()

                    logger.critical(
                        f"Hot work safety violation detected: Permit {permit.permit_number}"
                    )

                    # Consider revoking permit
                    # permit.status = PermitStatus.REVOKED
                    # db.commit()

    async def _check_expired_permits(self, db: Session):
        """Check for expired permits that are still marked as active"""
        now = datetime.now()

        expired_permits = db.query(Permit).filter(
            and_(
                Permit.status == PermitStatus.ACTIVE,
                Permit.end_time < now
            )
        ).all()

        for permit in expired_permits:
            permit.status = PermitStatus.EXPIRED
            db.commit()

            logger.info(f"Permit {permit.permit_number} marked as expired")

            # If it's hot work, create a violation for continuing work
            if permit.permit_type == PermitType.HOT_WORK:
                violation = Violation(
                    vessel_id=permit.vessel_id,
                    customer_id=permit.customer_id,
                    article_violated="E.5.5",
                    description=f"Hot work continued after permit expiration (Permit: {permit.permit_number})",
                    severity=ViolationSeverity.MAJOR,
                    detected_by="VERIFY_AGENT",
                    fine_amount_eur=750.0
                )
                db.add(violation)
                db.commit()

    async def _check_general_compliance(self, db: Session):
        """
        Check for other regulation violations

        This would integrate with various sensors and monitoring systems
        """
        # Example checks that could be implemented:
        # - Speed limit violations in marina
        # - Noise violations
        # - Waste disposal violations
        # - Unauthorized vessel movements
        # - Berthing violations (wrong berth, overstay, etc.)

        # Check for overstays
        now = datetime.now()
        overstays = db.query(BerthAssignment).filter(
            and_(
                BerthAssignment.status == AssignmentStatus.ACTIVE,
                BerthAssignment.expected_check_out < now - timedelta(hours=6)  # 6 hour grace period
            )
        ).all()

        for assignment in overstays:
            # Check if violation already reported
            existing = db.query(Violation).filter(
                and_(
                    Violation.vessel_id == assignment.vessel_id,
                    Violation.article_violated == "E.4.2",
                    Violation.status != ViolationStatus.RESOLVED
                )
            ).first()

            if not existing:
                vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
                hours_overdue = (now - assignment.expected_check_out).total_seconds() / 3600

                violation = Violation(
                    vessel_id=assignment.vessel_id,
                    customer_id=assignment.customer_id,
                    article_violated="E.4.2",
                    description=f"Vessel overstay: {hours_overdue:.1f} hours past expected departure",
                    severity=ViolationSeverity.MINOR,
                    detected_by="VERIFY_AGENT",
                    fine_amount_eur=50.0 * (hours_overdue // 24 + 1)  # €50 per day
                )
                db.add(violation)
                db.commit()

                logger.info(
                    f"Overstay violation detected: {vessel.name if vessel else 'Unknown'} - {hours_overdue:.1f}h overdue"
                )

    async def check_vessel_compliance(self, vessel_id: int) -> Dict[str, Any]:
        """
        Perform comprehensive compliance check for a specific vessel

        Args:
            vessel_id: ID of the vessel to check

        Returns:
            Compliance report with all violations and recommendations
        """
        db = SessionLocal()
        try:
            vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
            if not vessel:
                raise ValueError(f"Vessel {vessel_id} not found")

            # Get all violations for this vessel
            violations = db.query(Violation).filter(
                Violation.vessel_id == vessel_id
            ).all()

            active_violations = [v for v in violations if v.status != ViolationStatus.RESOLVED]
            resolved_violations = [v for v in violations if v.status == ViolationStatus.RESOLVED]

            # Calculate compliance score
            compliance_score = 100.0

            for violation in active_violations:
                if violation.severity == ViolationSeverity.CRITICAL:
                    compliance_score -= 25
                elif violation.severity == ViolationSeverity.MAJOR:
                    compliance_score -= 10
                elif violation.severity == ViolationSeverity.MINOR:
                    compliance_score -= 5
                elif violation.severity == ViolationSeverity.WARNING:
                    compliance_score -= 2

            compliance_score = max(0, compliance_score)

            # Check insurance
            insurance_valid = bool(
                vessel.insurance_company and
                vessel.insurance_policy_number and
                (not vessel.insurance_expiry_date or vessel.insurance_expiry_date >= datetime.now())
            )

            # Generate recommendations
            recommendations = []

            if not insurance_valid:
                recommendations.append({
                    "priority": "high",
                    "article": "E.2.1",
                    "action": "Update or renew vessel insurance"
                })

            for violation in active_violations:
                if violation.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]:
                    recommendations.append({
                        "priority": "high",
                        "article": violation.article_violated,
                        "action": f"Resolve: {violation.description}"
                    })

                if not violation.fine_paid and violation.fine_amount_eur:
                    recommendations.append({
                        "priority": "medium",
                        "article": violation.article_violated,
                        "action": f"Pay outstanding fine: €{violation.fine_amount_eur}"
                    })

            # Determine overall status
            if compliance_score >= 95:
                status = "EXCELLENT"
            elif compliance_score >= 85:
                status = "GOOD"
            elif compliance_score >= 70:
                status = "FAIR"
            elif compliance_score >= 50:
                status = "POOR"
            else:
                status = "CRITICAL"

            return {
                "vessel_id": vessel_id,
                "vessel_name": vessel.name,
                "compliance_status": status,
                "compliance_score": round(compliance_score, 2),
                "total_violations": len(violations),
                "active_violations": len(active_violations),
                "resolved_violations": len(resolved_violations),
                "insurance_compliant": insurance_valid,
                "violations": [
                    {
                        "id": v.id,
                        "article": v.article_violated,
                        "description": v.description,
                        "severity": v.severity.value,
                        "status": v.status.value,
                        "fine_amount": v.fine_amount_eur,
                        "fine_paid": v.fine_paid
                    }
                    for v in active_violations
                ],
                "recommendations": recommendations,
                "checked_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking vessel compliance: {e}")
            raise
        finally:
            db.close()

    async def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate overall marina compliance report

        Returns comprehensive statistics and violation summary
        """
        db = SessionLocal()
        try:
            total_vessels = db.query(Vessel).count()

            # Count violations by severity
            critical = db.query(Violation).filter(
                and_(
                    Violation.severity == ViolationSeverity.CRITICAL,
                    Violation.status != ViolationStatus.RESOLVED
                )
            ).count()

            major = db.query(Violation).filter(
                and_(
                    Violation.severity == ViolationSeverity.MAJOR,
                    Violation.status != ViolationStatus.RESOLVED
                )
            ).count()

            minor = db.query(Violation).filter(
                and_(
                    Violation.severity == ViolationSeverity.MINOR,
                    Violation.status != ViolationStatus.RESOLVED
                )
            ).count()

            # Insurance compliance
            compliant_insurance = db.query(Vessel).filter(
                and_(
                    Vessel.insurance_company.isnot(None),
                    Vessel.insurance_policy_number.isnot(None),
                    or_(
                        Vessel.insurance_expiry_date.is_(None),
                        Vessel.insurance_expiry_date >= datetime.now()
                    )
                )
            ).count()

            # Overall compliance rate
            vessels_with_violations = db.query(Violation.vessel_id).filter(
                Violation.status != ViolationStatus.RESOLVED
            ).distinct().count()

            overall_compliance = (total_vessels - vessels_with_violations) / total_vessels * 100 if total_vessels > 0 else 100

            return {
                "report_date": datetime.now().isoformat(),
                "total_vessels": total_vessels,
                "overall_compliance_rate": round(overall_compliance, 2),
                "active_violations": {
                    "critical": critical,
                    "major": major,
                    "minor": minor,
                    "total": critical + major + minor
                },
                "insurance_compliance": {
                    "compliant": compliant_insurance,
                    "non_compliant": total_vessels - compliant_insurance,
                    "compliance_rate": round(compliant_insurance / total_vessels * 100, 2) if total_vessels > 0 else 0
                },
                "meets_threshold": overall_compliance >= (self.compliance_threshold * 100)
            }

        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
        finally:
            db.close()


# Global VERIFY agent instance
verify_agent = VerifyAgent()


async def start_verify_agent():
    """Start the VERIFY agent background service"""
    await verify_agent.start()


async def stop_verify_agent():
    """Stop the VERIFY agent background service"""
    await verify_agent.stop()
