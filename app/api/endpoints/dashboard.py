"""
Dashboard API endpoints
Provides real-time statistics and monitoring for marina operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.models.berth import Berth, BerthStatus, BerthSection
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.customer import Customer
from app.models.vessel import Vessel, VesselType
from app.models.violation import Violation, ViolationSeverity, ViolationStatus
from app.models.permit import Permit, PermitType, PermitStatus
from app.models.vhf_log import VHFLog, VHFDirection, VHFIntent
from pydantic import BaseModel

router = APIRouter()


# Pydantic schemas
class DashboardOverview(BaseModel):
    """Overall marina status"""
    timestamp: datetime
    total_berths: int
    occupied_berths: int
    available_berths: int
    occupancy_rate: float
    total_vessels: int
    total_customers: int
    active_assignments: int
    active_permits: int
    active_violations: int
    vhf_messages_today: int


class OccupancyBySection(BaseModel):
    """Berth occupancy by section"""
    section: str
    total: int
    occupied: int
    available: int
    reserved: int
    maintenance: int
    occupancy_rate: float


class RevenueMetrics(BaseModel):
    """Financial metrics"""
    today_revenue: float
    week_revenue: float
    month_revenue: float
    year_revenue: float
    expected_revenue: float
    currency: str = "EUR"


class SafetyMetrics(BaseModel):
    """Safety and compliance metrics"""
    active_hot_work_permits: int
    critical_violations: int
    pending_violations: int
    compliance_rate: float
    insurance_compliance_rate: float


class OperationalMetrics(BaseModel):
    """Operational statistics"""
    check_ins_today: int
    check_outs_today: int
    expected_arrivals: int
    expected_departures: int
    vhf_messages_today: int
    vhf_response_rate: float
    seal_prediction_rate: float


@router.get("/overview", response_model=DashboardOverview)
async def get_overview(db: Session = Depends(get_db)):
    """
    Get overall marina dashboard overview

    Returns key metrics at a glance
    """
    total_berths = db.query(Berth).count()
    occupied_berths = db.query(Berth).filter(Berth.status == BerthStatus.OCCUPIED).count()
    available_berths = db.query(Berth).filter(Berth.status == BerthStatus.AVAILABLE).count()

    total_vessels = db.query(Vessel).count()
    total_customers = db.query(Customer).filter(Customer.is_active == True).count()

    active_assignments = db.query(BerthAssignment).filter(
        BerthAssignment.status == AssignmentStatus.ACTIVE
    ).count()

    active_permits = db.query(Permit).filter(
        Permit.status == PermitStatus.ACTIVE
    ).count()

    active_violations = db.query(Violation).filter(
        Violation.status.in_([ViolationStatus.REPORTED, ViolationStatus.UNDER_REVIEW])
    ).count()

    # VHF messages today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    vhf_today = db.query(VHFLog).filter(VHFLog.timestamp >= today_start).count()

    return DashboardOverview(
        timestamp=datetime.now(),
        total_berths=total_berths,
        occupied_berths=occupied_berths,
        available_berths=available_berths,
        occupancy_rate=round(occupied_berths / total_berths * 100, 2) if total_berths > 0 else 0,
        total_vessels=total_vessels,
        total_customers=total_customers,
        active_assignments=active_assignments,
        active_permits=active_permits,
        active_violations=active_violations,
        vhf_messages_today=vhf_today
    )


@router.get("/occupancy", response_model=List[OccupancyBySection])
async def get_occupancy_by_section(db: Session = Depends(get_db)):
    """
    Get berth occupancy breakdown by section (A-F)

    Shows detailed capacity utilization
    """
    sections = []

    for section in BerthSection:
        total = db.query(Berth).filter(Berth.section == section).count()
        occupied = db.query(Berth).filter(
            and_(Berth.section == section, Berth.status == BerthStatus.OCCUPIED)
        ).count()
        available = db.query(Berth).filter(
            and_(Berth.section == section, Berth.status == BerthStatus.AVAILABLE)
        ).count()
        reserved = db.query(Berth).filter(
            and_(Berth.section == section, Berth.status == BerthStatus.RESERVED)
        ).count()
        maintenance = db.query(Berth).filter(
            and_(Berth.section == section, Berth.status == BerthStatus.MAINTENANCE)
        ).count()

        sections.append(OccupancyBySection(
            section=section.value,
            total=total,
            occupied=occupied,
            available=available,
            reserved=reserved,
            maintenance=maintenance,
            occupancy_rate=round(occupied / total * 100, 2) if total > 0 else 0
        ))

    return sections


@router.get("/revenue", response_model=RevenueMetrics)
async def get_revenue_metrics(db: Session = Depends(get_db)):
    """
    Get revenue metrics

    Shows earned and expected revenue over different periods
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)

    # Revenue from completed assignments
    today_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        and_(
            BerthAssignment.status == AssignmentStatus.COMPLETED,
            BerthAssignment.actual_check_out >= today_start
        )
    ).scalar() or 0

    week_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        and_(
            BerthAssignment.status == AssignmentStatus.COMPLETED,
            BerthAssignment.actual_check_out >= week_start
        )
    ).scalar() or 0

    month_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        and_(
            BerthAssignment.status == AssignmentStatus.COMPLETED,
            BerthAssignment.actual_check_out >= month_start
        )
    ).scalar() or 0

    year_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        and_(
            BerthAssignment.status == AssignmentStatus.COMPLETED,
            BerthAssignment.actual_check_out >= year_start
        )
    ).scalar() or 0

    # Expected revenue from active assignments
    expected_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        BerthAssignment.status == AssignmentStatus.ACTIVE
    ).scalar() or 0

    return RevenueMetrics(
        today_revenue=round(today_revenue, 2),
        week_revenue=round(week_revenue, 2),
        month_revenue=round(month_revenue, 2),
        year_revenue=round(year_revenue, 2),
        expected_revenue=round(expected_revenue, 2)
    )


@router.get("/safety", response_model=SafetyMetrics)
async def get_safety_metrics(db: Session = Depends(get_db)):
    """
    Get safety and compliance metrics

    Critical for monitoring WIM regulation compliance
    """
    # Active hot work permits
    active_hot_work = db.query(Permit).filter(
        and_(
            Permit.permit_type == PermitType.HOT_WORK,
            Permit.status == PermitStatus.ACTIVE
        )
    ).count()

    # Critical violations
    critical_violations = db.query(Violation).filter(
        and_(
            Violation.severity == ViolationSeverity.CRITICAL,
            Violation.status != ViolationStatus.RESOLVED
        )
    ).count()

    # Pending violations
    pending_violations = db.query(Violation).filter(
        Violation.status.in_([ViolationStatus.REPORTED, ViolationStatus.UNDER_REVIEW])
    ).count()

    # Overall compliance rate (based on violations)
    total_vessels = db.query(Vessel).count()
    vessels_with_violations = db.query(Violation.vessel_id).filter(
        Violation.status != ViolationStatus.RESOLVED
    ).distinct().count()

    compliance_rate = 100.0
    if total_vessels > 0:
        compliance_rate = ((total_vessels - vessels_with_violations) / total_vessels) * 100

    # Insurance compliance
    vessels_with_insurance = db.query(Vessel).filter(
        and_(
            Vessel.insurance_company.isnot(None),
            Vessel.insurance_policy_number.isnot(None),
            or_(
                Vessel.insurance_expiry_date.is_(None),
                Vessel.insurance_expiry_date >= datetime.now()
            )
        )
    ).count()

    insurance_compliance_rate = 0.0
    if total_vessels > 0:
        insurance_compliance_rate = (vessels_with_insurance / total_vessels) * 100

    return SafetyMetrics(
        active_hot_work_permits=active_hot_work,
        critical_violations=critical_violations,
        pending_violations=pending_violations,
        compliance_rate=round(compliance_rate, 2),
        insurance_compliance_rate=round(insurance_compliance_rate, 2)
    )


@router.get("/operations", response_model=OperationalMetrics)
async def get_operational_metrics(db: Session = Depends(get_db)):
    """
    Get operational metrics

    Shows daily operations and AI agent performance
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    # Check-ins today
    check_ins_today = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.check_in >= today_start,
            BerthAssignment.check_in < tomorrow_start
        )
    ).count()

    # Check-outs today
    check_outs_today = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.actual_check_out >= today_start,
            BerthAssignment.actual_check_out < tomorrow_start
        )
    ).count()

    # Expected arrivals (assignments scheduled for today)
    expected_arrivals = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.check_in >= today_start,
            BerthAssignment.check_in < tomorrow_start,
            BerthAssignment.status == AssignmentStatus.ACTIVE
        )
    ).count()

    # Expected departures (assignments ending today)
    expected_departures = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.expected_check_out >= today_start,
            BerthAssignment.expected_check_out < tomorrow_start,
            BerthAssignment.status == AssignmentStatus.ACTIVE
        )
    ).count()

    # VHF messages today
    vhf_today = db.query(VHFLog).filter(VHFLog.timestamp >= today_start).count()

    # VHF response rate
    vhf_processed = db.query(VHFLog).filter(
        and_(
            VHFLog.timestamp >= today_start,
            VHFLog.was_processed == True
        )
    ).count()

    vhf_response_rate = 0.0
    if vhf_today > 0:
        vhf_response_rate = (vhf_processed / vhf_today) * 100

    # SEAL prediction rate
    total_assignments = db.query(BerthAssignment).count()
    seal_predicted = db.query(BerthAssignment).filter(
        BerthAssignment.was_seal_predicted == True
    ).count()

    seal_prediction_rate = 0.0
    if total_assignments > 0:
        seal_prediction_rate = (seal_predicted / total_assignments) * 100

    return OperationalMetrics(
        check_ins_today=check_ins_today,
        check_outs_today=check_outs_today,
        expected_arrivals=expected_arrivals,
        expected_departures=expected_departures,
        vhf_messages_today=vhf_today,
        vhf_response_rate=round(vhf_response_rate, 2),
        seal_prediction_rate=round(seal_prediction_rate, 2)
    )


@router.get("/timeline/today")
async def get_today_timeline(db: Session = Depends(get_db)):
    """
    Get timeline of events for today

    Shows chronological view of all activities
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    timeline = []

    # Check-ins
    check_ins = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.check_in >= today_start,
            BerthAssignment.check_in < tomorrow_start
        )
    ).order_by(BerthAssignment.check_in).all()

    for assignment in check_ins:
        vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
        berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()

        timeline.append({
            "time": assignment.check_in,
            "type": "check_in",
            "description": f"{vessel.name if vessel else 'Vessel'} checked in to {berth.berth_number if berth else 'berth'}",
            "entity_id": assignment.id
        })

    # Check-outs
    check_outs = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.actual_check_out >= today_start,
            BerthAssignment.actual_check_out < tomorrow_start
        )
    ).order_by(BerthAssignment.actual_check_out).all()

    for assignment in check_outs:
        vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
        berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()

        timeline.append({
            "time": assignment.actual_check_out,
            "type": "check_out",
            "description": f"{vessel.name if vessel else 'Vessel'} checked out from {berth.berth_number if berth else 'berth'}",
            "entity_id": assignment.id
        })

    # Violations
    violations = db.query(Violation).filter(
        Violation.detected_at >= today_start
    ).order_by(Violation.detected_at).all()

    for violation in violations:
        vessel = db.query(Vessel).filter(Vessel.id == violation.vessel_id).first()

        timeline.append({
            "time": violation.detected_at,
            "type": "violation",
            "description": f"Violation of Article {violation.article_violated} detected for {vessel.name if vessel else 'vessel'}",
            "severity": violation.severity.value,
            "entity_id": violation.id
        })

    # Permits
    permits = db.query(Permit).filter(
        Permit.requested_at >= today_start
    ).order_by(Permit.requested_at).all()

    for permit in permits:
        vessel = db.query(Vessel).filter(Vessel.id == permit.vessel_id).first()

        timeline.append({
            "time": permit.requested_at,
            "type": "permit_request",
            "description": f"{permit.permit_type.value} permit requested for {vessel.name if vessel else 'vessel'}",
            "entity_id": permit.id
        })

    # VHF messages
    vhf_messages = db.query(VHFLog).filter(
        and_(
            VHFLog.timestamp >= today_start,
            VHFLog.direction == VHFDirection.INCOMING
        )
    ).order_by(VHFLog.timestamp).all()

    for vhf in vhf_messages:
        timeline.append({
            "time": vhf.timestamp,
            "type": "vhf_message",
            "description": f"VHF message from {vhf.vessel_name or 'unknown vessel'}: {vhf.intent_parsed.value if vhf.intent_parsed else 'general'}",
            "entity_id": vhf.id
        })

    # Sort timeline by time
    timeline.sort(key=lambda x: x["time"])

    return {
        "date": today_start.date(),
        "total_events": len(timeline),
        "events": timeline
    }


@router.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """
    Get current alerts and warnings

    Critical for real-time monitoring and decision making
    """
    alerts = []

    # Critical violations
    critical_violations = db.query(Violation).filter(
        and_(
            Violation.severity == ViolationSeverity.CRITICAL,
            Violation.status != ViolationStatus.RESOLVED
        )
    ).all()

    for violation in critical_violations:
        vessel = db.query(Vessel).filter(Vessel.id == violation.vessel_id).first()
        alerts.append({
            "level": "critical",
            "type": "violation",
            "message": f"Critical violation: {vessel.name if vessel else 'Vessel'} - Article {violation.article_violated}",
            "entity_id": violation.id,
            "timestamp": violation.detected_at
        })

    # Active hot work
    active_hot_work = db.query(Permit).filter(
        and_(
            Permit.permit_type == PermitType.HOT_WORK,
            Permit.status == PermitStatus.ACTIVE
        )
    ).all()

    for permit in active_hot_work:
        vessel = db.query(Vessel).filter(Vessel.id == permit.vessel_id).first()
        alerts.append({
            "level": "warning",
            "type": "hot_work",
            "message": f"Hot work in progress: {vessel.name if vessel else 'Vessel'} at {permit.work_location}",
            "entity_id": permit.id,
            "timestamp": permit.start_time
        })

    # Expiring insurance
    vessels_expiring = db.query(Vessel).filter(
        and_(
            Vessel.insurance_expiry_date.isnot(None),
            Vessel.insurance_expiry_date <= datetime.now() + timedelta(days=30),
            Vessel.insurance_expiry_date >= datetime.now()
        )
    ).all()

    for vessel in vessels_expiring:
        days_until = (vessel.insurance_expiry_date - datetime.now()).days
        alerts.append({
            "level": "info",
            "type": "insurance_expiring",
            "message": f"Insurance expiring in {days_until} days: {vessel.name}",
            "entity_id": vessel.id,
            "timestamp": datetime.now()
        })

    # Sort by timestamp (most recent first)
    alerts.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }


@router.get("/statistics/trending")
async def get_trending_statistics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get trending statistics over time

    Shows patterns and trends for decision making
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Daily occupancy trend
    daily_occupancy = []
    current_date = start_date.date()

    while current_date <= end_date.date():
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())

        # Count active assignments for this day
        active = db.query(BerthAssignment).filter(
            and_(
                BerthAssignment.check_in <= day_end,
                or_(
                    BerthAssignment.actual_check_out >= day_start,
                    and_(
                        BerthAssignment.actual_check_out.is_(None),
                        BerthAssignment.expected_check_out >= day_start
                    )
                )
            )
        ).count()

        total_berths = db.query(Berth).count()

        daily_occupancy.append({
            "date": current_date.isoformat(),
            "occupied": active,
            "occupancy_rate": round(active / total_berths * 100, 2) if total_berths > 0 else 0
        })

        current_date += timedelta(days=1)

    # Revenue trend (weekly)
    weekly_revenue = []
    current_week = start_date

    while current_week <= end_date:
        week_end = current_week + timedelta(days=7)

        revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
            and_(
                BerthAssignment.status == AssignmentStatus.COMPLETED,
                BerthAssignment.actual_check_out >= current_week,
                BerthAssignment.actual_check_out < week_end
            )
        ).scalar() or 0

        weekly_revenue.append({
            "week_start": current_week.date().isoformat(),
            "revenue": round(revenue, 2)
        })

        current_week = week_end

    return {
        "period_days": days,
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "daily_occupancy": daily_occupancy,
        "weekly_revenue": weekly_revenue
    }
