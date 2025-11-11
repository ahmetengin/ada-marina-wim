"""
Permits API endpoints
Manages hot work permits and special operation permits
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.permit import Permit, PermitType, PermitStatus
from app.models.vessel import Vessel
from app.models.customer import Customer
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic schemas
class PermitBase(BaseModel):
    permit_type: PermitType
    vessel_id: int
    customer_id: int
    work_type: str
    work_description: str
    work_location: Optional[str] = None
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None


class HotWorkPermitCreate(PermitBase):
    """Schema for creating hot work permit (Article E.5.5)"""
    fire_prevention_measures: str
    fire_watch_assigned: str
    extinguishers_positioned: bool = True
    surrounding_notified: bool = True


class PermitCreate(PermitBase):
    """Schema for creating a general permit"""
    fire_prevention_measures: Optional[str] = None
    fire_watch_assigned: Optional[str] = None
    extinguishers_positioned: bool = False
    surrounding_notified: bool = False


class PermitUpdate(BaseModel):
    """Schema for updating permit details"""
    status: Optional[PermitStatus] = None
    work_description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    notes: Optional[str] = None


class PermitResponse(BaseModel):
    """Schema for permit response"""
    id: int
    permit_number: str
    permit_type: PermitType
    vessel_id: int
    customer_id: int
    work_type: str
    work_description: str
    work_location: Optional[str]
    fire_prevention_measures: Optional[str]
    fire_watch_assigned: Optional[str]
    extinguishers_positioned: bool
    surrounding_notified: bool
    requested_at: datetime
    start_time: datetime
    end_time: datetime
    actual_completion: Optional[datetime]
    status: PermitStatus
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    safety_briefing_completed: bool
    insurance_verified: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PermitApprovalRequest(BaseModel):
    """Request to approve a permit"""
    approved_by: str
    safety_briefing_completed: bool = True
    insurance_verified: bool = True
    notes: Optional[str] = None


@router.get("/", response_model=List[PermitResponse])
async def list_permits(
    permit_type: Optional[PermitType] = None,
    status: Optional[PermitStatus] = None,
    vessel_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all permits with optional filtering

    Parameters:
    - permit_type: Filter by permit type
    - status: Filter by permit status
    - vessel_id: Filter by vessel
    - customer_id: Filter by customer
    - from_date: Filter permits from this date
    - to_date: Filter permits until this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(Permit)

    if permit_type:
        query = query.filter(Permit.permit_type == permit_type)
    if status:
        query = query.filter(Permit.status == status)
    if vessel_id:
        query = query.filter(Permit.vessel_id == vessel_id)
    if customer_id:
        query = query.filter(Permit.customer_id == customer_id)
    if from_date:
        query = query.filter(Permit.start_time >= from_date)
    if to_date:
        query = query.filter(Permit.end_time <= to_date)

    permits = query.order_by(Permit.requested_at.desc()).offset(skip).limit(limit).all()
    return permits


@router.get("/{permit_id}", response_model=PermitResponse)
async def get_permit(permit_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific permit

    Parameters:
    - permit_id: Unique identifier of the permit
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")
    return permit


@router.get("/number/{permit_number}", response_model=PermitResponse)
async def get_permit_by_number(permit_number: str, db: Session = Depends(get_db)):
    """
    Get permit by permit number

    Parameters:
    - permit_number: Permit identification number
    """
    permit = db.query(Permit).filter(Permit.permit_number == permit_number).first()
    if not permit:
        raise HTTPException(
            status_code=404,
            detail=f"Permit {permit_number} not found"
        )
    return permit


@router.post("/", response_model=PermitResponse, status_code=201)
async def create_permit(permit: PermitCreate, db: Session = Depends(get_db)):
    """
    Request a new permit

    For hot work permits (Article E.5.5), additional safety measures are required
    """
    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == permit.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {permit.vessel_id} not found")

    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == permit.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {permit.customer_id} not found")

    # Validate hot work requirements (Article E.5.5)
    if permit.permit_type == PermitType.HOT_WORK:
        if not permit.fire_prevention_measures:
            raise HTTPException(
                status_code=400,
                detail="Hot work permits require fire prevention measures (Article E.5.5)"
            )
        if not permit.fire_watch_assigned:
            raise HTTPException(
                status_code=400,
                detail="Hot work permits require assigned fire watch (Article E.5.5)"
            )
        if not permit.extinguishers_positioned:
            raise HTTPException(
                status_code=400,
                detail="Fire extinguishers must be positioned before hot work (Article E.5.5)"
            )
        if not permit.surrounding_notified:
            raise HTTPException(
                status_code=400,
                detail="Surrounding vessels must be notified before hot work (Article E.5.5)"
            )

    # Generate permit number
    # Format: PERMIT-TYPE-YYYYMMDD-XXXX
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    type_code = permit.permit_type.value[:3].upper()

    # Count permits of this type today
    count = db.query(Permit).filter(
        and_(
            Permit.permit_type == permit.permit_type,
            func.date(Permit.requested_at) == today.date()
        )
    ).count()

    permit_number = f"{type_code}-{date_str}-{count + 1:04d}"

    db_permit = Permit(
        **permit.dict(),
        permit_number=permit_number,
        status=PermitStatus.REQUESTED
    )
    db.add(db_permit)
    db.commit()
    db.refresh(db_permit)
    return db_permit


@router.post("/hot-work", response_model=PermitResponse, status_code=201)
async def create_hot_work_permit(
    permit: HotWorkPermitCreate,
    db: Session = Depends(get_db)
):
    """
    Request a hot work permit (Article E.5.5)

    Hot work includes welding, grinding, cutting, and any work that produces
    sparks, flames, or heat. Special safety requirements apply.
    """
    # Override permit type to ensure it's hot work
    permit.permit_type = PermitType.HOT_WORK
    return await create_permit(permit, db)


@router.put("/{permit_id}", response_model=PermitResponse)
async def update_permit(
    permit_id: int,
    permit_update: PermitUpdate,
    db: Session = Depends(get_db)
):
    """
    Update permit details

    Allows updating work description, timing, and status
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    # Update only provided fields
    update_data = permit_update.dict(exclude_unset=True)

    # If marking as completed, set actual_completion if not provided
    if 'status' in update_data and update_data['status'] == PermitStatus.COMPLETED:
        if not permit.actual_completion and 'actual_completion' not in update_data:
            permit.actual_completion = datetime.now()

    for field, value in update_data.items():
        setattr(permit, field, value)

    db.commit()
    db.refresh(permit)
    return permit


@router.post("/{permit_id}/approve", response_model=PermitResponse)
async def approve_permit(
    permit_id: int,
    approval: PermitApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve a permit

    Requires safety briefing completion and insurance verification
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    if permit.status != PermitStatus.REQUESTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve permit with status {permit.status}"
        )

    permit.status = PermitStatus.APPROVED
    permit.approved_by = approval.approved_by
    permit.approved_at = datetime.now()
    permit.safety_briefing_completed = approval.safety_briefing_completed
    permit.insurance_verified = approval.insurance_verified

    if approval.notes:
        permit.notes = (permit.notes or "") + "\n" + approval.notes

    db.commit()
    db.refresh(permit)

    return permit


@router.post("/{permit_id}/activate")
async def activate_permit(permit_id: int, db: Session = Depends(get_db)):
    """
    Activate an approved permit

    Marks the permit as active, allowing work to begin
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    if permit.status != PermitStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot activate permit with status {permit.status}. Must be APPROVED first."
        )

    # Check if current time is within permitted work window
    now = datetime.now()
    if now < permit.start_time:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot activate permit before start time: {permit.start_time}"
        )

    if now > permit.end_time:
        raise HTTPException(
            status_code=400,
            detail=f"Permit has expired. End time was: {permit.end_time}"
        )

    permit.status = PermitStatus.ACTIVE
    db.commit()

    return {
        "permit_id": permit_id,
        "permit_number": permit.permit_number,
        "status": "active",
        "message": "Permit activated. Work may begin.",
        "valid_until": permit.end_time
    }


@router.post("/{permit_id}/complete")
async def complete_permit(
    permit_id: int,
    completion_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Mark permit as completed

    Called when work is finished
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    if permit.status not in [PermitStatus.ACTIVE, PermitStatus.APPROVED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete permit with status {permit.status}"
        )

    permit.status = PermitStatus.COMPLETED
    permit.actual_completion = datetime.now()

    if completion_notes:
        permit.notes = (permit.notes or "") + f"\nCompleted: {completion_notes}"

    db.commit()

    return {
        "permit_id": permit_id,
        "permit_number": permit.permit_number,
        "status": "completed",
        "completed_at": permit.actual_completion
    }


@router.post("/{permit_id}/revoke")
async def revoke_permit(
    permit_id: int,
    revocation_reason: str,
    db: Session = Depends(get_db)
):
    """
    Revoke a permit

    Used for safety violations or policy breaches
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    if permit.status == PermitStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot revoke completed permit")

    permit.status = PermitStatus.REVOKED
    permit.notes = (permit.notes or "") + f"\nREVOKED: {revocation_reason}"

    db.commit()

    return {
        "permit_id": permit_id,
        "permit_number": permit.permit_number,
        "status": "revoked",
        "reason": revocation_reason,
        "message": "Permit revoked. Work must stop immediately."
    }


@router.delete("/{permit_id}", status_code=204)
async def delete_permit(permit_id: int, db: Session = Depends(get_db)):
    """
    Delete a permit

    Only allowed for REQUESTED status permits
    """
    permit = db.query(Permit).filter(Permit.id == permit_id).first()
    if not permit:
        raise HTTPException(status_code=404, detail=f"Permit {permit_id} not found")

    if permit.status != PermitStatus.REQUESTED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete permit with status {permit.status}"
        )

    db.delete(permit)
    db.commit()
    return None


@router.get("/active/current")
async def get_active_permits(db: Session = Depends(get_db)):
    """
    Get all currently active permits

    Critical for safety monitoring
    """
    active = db.query(Permit).filter(
        Permit.status == PermitStatus.ACTIVE
    ).order_by(Permit.start_time).all()

    # Enrich with vessel details
    enriched = []
    for permit in active:
        vessel = db.query(Vessel).filter(Vessel.id == permit.vessel_id).first()

        enriched.append({
            "permit_id": permit.id,
            "permit_number": permit.permit_number,
            "permit_type": permit.permit_type,
            "vessel_name": vessel.name if vessel else "Unknown",
            "work_type": permit.work_type,
            "work_location": permit.work_location,
            "start_time": permit.start_time,
            "end_time": permit.end_time,
            "time_remaining_minutes": int((permit.end_time - datetime.now()).total_seconds() / 60)
        })

    return {
        "total_active": len(enriched),
        "permits": enriched
    }


@router.get("/hot-work/active")
async def get_active_hot_work(db: Session = Depends(get_db)):
    """
    Get all active hot work permits

    Critical safety monitoring for fire prevention (Article E.5.5)
    """
    active_hot_work = db.query(Permit).filter(
        and_(
            Permit.permit_type == PermitType.HOT_WORK,
            Permit.status == PermitStatus.ACTIVE
        )
    ).order_by(Permit.start_time).all()

    enriched = []
    for permit in active_hot_work:
        vessel = db.query(Vessel).filter(Vessel.id == permit.vessel_id).first()

        enriched.append({
            "permit_id": permit.id,
            "permit_number": permit.permit_number,
            "vessel_name": vessel.name if vessel else "Unknown",
            "work_type": permit.work_type,
            "work_location": permit.work_location,
            "fire_watch": permit.fire_watch_assigned,
            "start_time": permit.start_time,
            "end_time": permit.end_time,
            "time_remaining_minutes": int((permit.end_time - datetime.now()).total_seconds() / 60)
        })

    return {
        "total_active_hot_work": len(enriched),
        "permits": enriched,
        "safety_note": "Article E.5.5: Fire watch required for all hot work operations"
    }


@router.get("/statistics/summary")
async def get_permit_statistics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get permit statistics

    Returns counts by type, status, and approval metrics
    """
    query = db.query(Permit)

    if from_date:
        query = query.filter(Permit.requested_at >= from_date)
    if to_date:
        query = query.filter(Permit.requested_at <= to_date)

    total_permits = query.count()

    # By type
    by_type = {}
    for ptype in PermitType:
        count = query.filter(Permit.permit_type == ptype).count()
        by_type[ptype.value] = count

    # By status
    by_status = {}
    for status in PermitStatus:
        count = query.filter(Permit.status == status).count()
        by_status[status.value] = count

    # Approval metrics
    approved_permits = query.filter(
        Permit.status.in_([PermitStatus.APPROVED, PermitStatus.ACTIVE, PermitStatus.COMPLETED])
    ).count()

    # Average approval time
    approved_with_times = db.query(Permit).filter(
        and_(
            Permit.approved_at.isnot(None),
            Permit.requested_at.isnot(None)
        )
    ).all()

    avg_approval_hours = 0
    if approved_with_times:
        total_seconds = sum([
            (p.approved_at - p.requested_at).total_seconds()
            for p in approved_with_times
        ])
        avg_approval_hours = total_seconds / len(approved_with_times) / 3600

    return {
        "total_permits": total_permits,
        "by_type": by_type,
        "by_status": by_status,
        "approval_metrics": {
            "total_approved": approved_permits,
            "approval_rate": round(approved_permits / total_permits * 100, 2) if total_permits > 0 else 0,
            "avg_approval_time_hours": round(avg_approval_hours, 2)
        },
        "hot_work_compliance": {
            "total_hot_work": by_type.get("hot_work", 0),
            "regulation": "Article E.5.5 - Fire Prevention"
        }
    }
