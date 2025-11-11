"""
Violations API endpoints
Manages WIM regulation violations and compliance tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.violation import Violation, ViolationSeverity, ViolationStatus
from app.models.vessel import Vessel
from app.models.customer import Customer
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic schemas
class ViolationBase(BaseModel):
    vessel_id: int
    customer_id: int
    article_violated: str = Field(..., description="WIM regulation article (e.g., E.1.10)")
    description: str
    severity: ViolationSeverity
    fine_amount_eur: Optional[float] = None
    detected_by: Optional[str] = "MANUAL"
    evidence_description: Optional[str] = None
    evidence_files: Optional[str] = None


class ViolationCreate(ViolationBase):
    """Schema for creating a new violation"""
    pass


class ViolationUpdate(BaseModel):
    """Schema for updating violation details"""
    status: Optional[ViolationStatus] = None
    fine_amount_eur: Optional[float] = None
    fine_paid: Optional[bool] = None
    resolution_notes: Optional[str] = None
    evidence_description: Optional[str] = None
    evidence_files: Optional[str] = None


class ViolationResponse(ViolationBase):
    """Schema for violation response"""
    id: int
    status: ViolationStatus
    fine_paid: bool
    fine_paid_at: Optional[datetime] = None
    detected_at: datetime
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ViolationWithDetails(ViolationResponse):
    """Violation with vessel and customer details"""
    vessel_name: str
    customer_name: str
    regulation_title: Optional[str] = None


class ComplianceCheckRequest(BaseModel):
    """Request to check compliance for a vessel"""
    vessel_id: int
    check_articles: Optional[List[str]] = None


class ComplianceCheckResponse(BaseModel):
    """Compliance check result"""
    vessel_id: int
    vessel_name: str
    overall_compliance: str
    total_violations: int
    active_violations: int
    resolved_violations: int
    articles_violated: List[str]
    compliance_score: float
    recommendations: List[str]


@router.get("/", response_model=List[ViolationResponse])
async def list_violations(
    vessel_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    article: Optional[str] = None,
    severity: Optional[ViolationSeverity] = None,
    status: Optional[ViolationStatus] = None,
    fine_paid: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all violations with optional filtering

    Parameters:
    - vessel_id: Filter by vessel
    - customer_id: Filter by customer
    - article: Filter by regulation article
    - severity: Filter by violation severity
    - status: Filter by violation status
    - fine_paid: Filter by fine payment status
    - from_date: Filter violations from this date
    - to_date: Filter violations until this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(Violation)

    if vessel_id:
        query = query.filter(Violation.vessel_id == vessel_id)
    if customer_id:
        query = query.filter(Violation.customer_id == customer_id)
    if article:
        query = query.filter(Violation.article_violated == article)
    if severity:
        query = query.filter(Violation.severity == severity)
    if status:
        query = query.filter(Violation.status == status)
    if fine_paid is not None:
        query = query.filter(Violation.fine_paid == fine_paid)
    if from_date:
        query = query.filter(Violation.detected_at >= from_date)
    if to_date:
        query = query.filter(Violation.detected_at <= to_date)

    violations = query.order_by(Violation.detected_at.desc()).offset(skip).limit(limit).all()
    return violations


@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific violation

    Parameters:
    - violation_id: Unique identifier of the violation
    """
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")
    return violation


@router.post("/", response_model=ViolationResponse, status_code=201)
async def create_violation(violation: ViolationCreate, db: Session = Depends(get_db)):
    """
    Report a new violation

    Can be created manually or by the VERIFY agent
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == violation.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {violation.vessel_id} not found")

    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == violation.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {violation.customer_id} not found")

    db_violation = Violation(**violation.dict())
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation


@router.put("/{violation_id}", response_model=ViolationResponse)
async def update_violation(
    violation_id: int,
    violation_update: ViolationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update violation details

    Used for status changes, fine payment, and resolution
    """
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

    # Update only provided fields
    update_data = violation_update.dict(exclude_unset=True)

    # If fine is being marked as paid, set timestamp
    if 'fine_paid' in update_data and update_data['fine_paid'] and not violation.fine_paid:
        violation.fine_paid_at = datetime.now()

    # If status is being changed to resolved, set timestamp
    if 'status' in update_data and update_data['status'] == ViolationStatus.RESOLVED:
        if not violation.resolved_at:
            violation.resolved_at = datetime.now()

    for field, value in update_data.items():
        setattr(violation, field, value)

    db.commit()
    db.refresh(violation)
    return violation


@router.delete("/{violation_id}", status_code=204)
async def delete_violation(violation_id: int, db: Session = Depends(get_db)):
    """
    Delete a violation record

    Only allowed for violations in REPORTED status
    """
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

    if violation.status != ViolationStatus.REPORTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete violation with status {violation.status}"
        )

    db.delete(violation)
    db.commit()
    return None


@router.post("/{violation_id}/resolve")
async def resolve_violation(
    violation_id: int,
    resolution_notes: str,
    db: Session = Depends(get_db)
):
    """
    Mark a violation as resolved

    Requires resolution notes explaining how the issue was addressed
    """
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

    if violation.status == ViolationStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Violation already resolved")

    violation.status = ViolationStatus.RESOLVED
    violation.resolution_notes = resolution_notes
    violation.resolved_at = datetime.now()

    db.commit()
    db.refresh(violation)

    return {
        "violation_id": violation_id,
        "status": "resolved",
        "resolved_at": violation.resolved_at,
        "message": "Violation resolved successfully"
    }


@router.post("/{violation_id}/appeal")
async def appeal_violation(
    violation_id: int,
    appeal_reason: str,
    db: Session = Depends(get_db)
):
    """
    Appeal a violation

    Customer can appeal if they believe the violation was incorrect
    """
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        raise HTTPException(status_code=404, detail=f"Violation {violation_id} not found")

    if violation.status == ViolationStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Cannot appeal resolved violation")

    violation.status = ViolationStatus.APPEALED
    violation.resolution_notes = f"APPEAL: {appeal_reason}"

    db.commit()
    db.refresh(violation)

    return {
        "violation_id": violation_id,
        "status": "appealed",
        "message": "Violation appeal registered. Will be reviewed by marina management."
    }


@router.post("/compliance/check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: ComplianceCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check compliance status for a vessel

    Analyzes violations and provides compliance score and recommendations
    """
    vessel = db.query(Vessel).filter(Vessel.id == request.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {request.vessel_id} not found")

    # Get all violations for this vessel
    query = db.query(Violation).filter(Violation.vessel_id == request.vessel_id)

    if request.check_articles:
        query = query.filter(Violation.article_violated.in_(request.check_articles))

    all_violations = query.all()
    active_violations = [v for v in all_violations if v.status != ViolationStatus.RESOLVED]
    resolved_violations = [v for v in all_violations if v.status == ViolationStatus.RESOLVED]

    # Get unique articles violated
    articles_violated = list(set([v.article_violated for v in all_violations]))

    # Calculate compliance score (100 - penalties)
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

    # Determine overall compliance status
    if compliance_score >= 95:
        overall_compliance = "EXCELLENT"
    elif compliance_score >= 85:
        overall_compliance = "GOOD"
    elif compliance_score >= 70:
        overall_compliance = "FAIR"
    elif compliance_score >= 50:
        overall_compliance = "POOR"
    else:
        overall_compliance = "CRITICAL"

    # Generate recommendations
    recommendations = []
    if active_violations:
        for violation in active_violations:
            if violation.severity == ViolationSeverity.CRITICAL:
                recommendations.append(
                    f"URGENT: Address critical violation of Article {violation.article_violated}"
                )
            elif not violation.fine_paid and violation.fine_amount_eur:
                recommendations.append(
                    f"Pay outstanding fine for Article {violation.article_violated}: €{violation.fine_amount_eur}"
                )

    # Check insurance compliance (Article E.2.1)
    if not vessel.insurance_company or not vessel.insurance_policy_number:
        recommendations.append("Update vessel insurance information (Article E.2.1)")

    if vessel.insurance_expiry_date and vessel.insurance_expiry_date < datetime.now():
        recommendations.append("Renew expired insurance policy (Article E.2.1)")

    return ComplianceCheckResponse(
        vessel_id=vessel.id,
        vessel_name=vessel.name,
        overall_compliance=overall_compliance,
        total_violations=len(all_violations),
        active_violations=len(active_violations),
        resolved_violations=len(resolved_violations),
        articles_violated=articles_violated,
        compliance_score=round(compliance_score, 2),
        recommendations=recommendations
    )


@router.get("/statistics/summary")
async def get_violation_statistics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get violation statistics

    Returns counts by severity, status, and article
    """
    query = db.query(Violation)

    if from_date:
        query = query.filter(Violation.detected_at >= from_date)
    if to_date:
        query = query.filter(Violation.detected_at <= to_date)

    total_violations = query.count()

    # By severity
    by_severity = {}
    for severity in ViolationSeverity:
        count = query.filter(Violation.severity == severity).count()
        by_severity[severity.value] = count

    # By status
    by_status = {}
    for status in ViolationStatus:
        count = query.filter(Violation.status == status).count()
        by_status[status.value] = count

    # Top violated articles
    top_articles = db.query(
        Violation.article_violated,
        func.count(Violation.id).label('count')
    ).group_by(Violation.article_violated).order_by(func.count(Violation.id).desc()).limit(10).all()

    # Detection sources
    detection_sources = db.query(
        Violation.detected_by,
        func.count(Violation.id).label('count')
    ).group_by(Violation.detected_by).all()

    # Financial
    total_fines = db.query(func.sum(Violation.fine_amount_eur)).scalar() or 0
    paid_fines = db.query(func.sum(Violation.fine_amount_eur)).filter(
        Violation.fine_paid == True
    ).scalar() or 0
    unpaid_fines = total_fines - paid_fines

    return {
        "total_violations": total_violations,
        "by_severity": by_severity,
        "by_status": by_status,
        "top_violated_articles": [
            {"article": a[0], "count": a[1]} for a in top_articles
        ],
        "detection_sources": [
            {"source": s[0] or "UNKNOWN", "count": s[1]} for s in detection_sources
        ],
        "financial": {
            "total_fines_eur": round(total_fines, 2),
            "paid_fines_eur": round(paid_fines, 2),
            "unpaid_fines_eur": round(unpaid_fines, 2),
            "collection_rate": round(paid_fines / total_fines * 100, 2) if total_fines > 0 else 0
        }
    }


@router.get("/critical/active")
async def get_critical_violations(db: Session = Depends(get_db)):
    """
    Get all active critical violations

    These require immediate attention
    """
    violations = db.query(Violation).filter(
        and_(
            Violation.severity == ViolationSeverity.CRITICAL,
            Violation.status != ViolationStatus.RESOLVED
        )
    ).order_by(Violation.detected_at.desc()).all()

    # Enrich with vessel details
    enriched = []
    for violation in violations:
        vessel = db.query(Vessel).filter(Vessel.id == violation.vessel_id).first()
        customer = db.query(Customer).filter(Customer.id == violation.customer_id).first()

        enriched.append({
            "violation_id": violation.id,
            "article": violation.article_violated,
            "description": violation.description,
            "vessel_name": vessel.name if vessel else "Unknown",
            "customer_name": customer.name if customer else "Unknown",
            "detected_at": violation.detected_at,
            "days_open": (datetime.now() - violation.detected_at).days
        })

    return {
        "total_critical": len(enriched),
        "violations": enriched
    }
