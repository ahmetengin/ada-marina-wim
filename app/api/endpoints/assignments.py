"""
Berth Assignments API endpoints
Manages vessel-to-berth assignments, check-ins, and check-outs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.berth import Berth, BerthStatus
from app.models.vessel import Vessel
from app.models.customer import Customer
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic schemas
class AssignmentBase(BaseModel):
    berth_id: int
    vessel_id: int
    customer_id: int
    check_in: datetime
    expected_check_out: datetime
    electricity_requested: Optional[int] = None
    water_requested: bool = True
    wifi_requested: bool = True
    notes: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    """Schema for creating a new berth assignment"""
    vhf_log_id: Optional[int] = None


class AssignmentUpdate(BaseModel):
    """Schema for updating assignment details"""
    expected_check_out: Optional[datetime] = None
    electricity_requested: Optional[int] = None
    water_requested: Optional[bool] = None
    wifi_requested: Optional[bool] = None
    notes: Optional[str] = None


class AssignmentResponse(AssignmentBase):
    """Schema for assignment response"""
    id: int
    status: AssignmentStatus
    actual_check_out: Optional[datetime] = None
    daily_rate_eur: float
    total_days: int
    total_amount_eur: float
    invoice_id: Optional[int] = None
    was_seal_predicted: bool
    seal_confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    """Request to check in a vessel"""
    berth_id: int
    vessel_id: int
    customer_id: int
    expected_check_out: datetime
    electricity_requested: Optional[int] = None
    water_requested: bool = True
    wifi_requested: bool = True
    vhf_log_id: Optional[int] = None
    notes: Optional[str] = None


class CheckOutRequest(BaseModel):
    """Request to check out a vessel"""
    create_invoice: bool = True
    notes: Optional[str] = None


@router.get("/", response_model=List[AssignmentResponse])
async def list_assignments(
    status: Optional[AssignmentStatus] = None,
    berth_id: Optional[int] = None,
    vessel_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    check_in_from: Optional[datetime] = None,
    check_in_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all berth assignments with optional filtering

    Parameters:
    - status: Filter by assignment status
    - berth_id: Filter by berth
    - vessel_id: Filter by vessel
    - customer_id: Filter by customer
    - check_in_from: Filter assignments checking in after this date
    - check_in_to: Filter assignments checking in before this date
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(BerthAssignment)

    if status:
        query = query.filter(BerthAssignment.status == status)
    if berth_id:
        query = query.filter(BerthAssignment.berth_id == berth_id)
    if vessel_id:
        query = query.filter(BerthAssignment.vessel_id == vessel_id)
    if customer_id:
        query = query.filter(BerthAssignment.customer_id == customer_id)
    if check_in_from:
        query = query.filter(BerthAssignment.check_in >= check_in_from)
    if check_in_to:
        query = query.filter(BerthAssignment.check_in <= check_in_to)

    assignments = query.order_by(BerthAssignment.check_in.desc()).offset(skip).limit(limit).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific assignment

    Parameters:
    - assignment_id: Unique identifier of the assignment
    """
    assignment = db.query(BerthAssignment).filter(BerthAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")
    return assignment


@router.post("/", response_model=AssignmentResponse, status_code=201)
async def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    """
    Create a new berth assignment

    Validates:
    - Berth exists and is available
    - Vessel exists
    - Customer exists
    - No conflicting assignments for the berth
    - Vessel dimensions fit the berth
    """
    # Validate berth exists
    berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
    if not berth:
        raise HTTPException(status_code=404, detail=f"Berth {assignment.berth_id} not found")

    # Validate vessel exists
    vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {assignment.vessel_id} not found")

    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == assignment.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {assignment.customer_id} not found")

    # Validate vessel fits in berth
    if vessel.length_meters > berth.length_meters:
        raise HTTPException(
            status_code=400,
            detail=f"Vessel length ({vessel.length_meters}m) exceeds berth capacity ({berth.length_meters}m)"
        )
    if vessel.width_meters > berth.width_meters:
        raise HTTPException(
            status_code=400,
            detail=f"Vessel width ({vessel.width_meters}m) exceeds berth width ({berth.width_meters}m)"
        )
    if vessel.draft_meters > berth.depth_meters:
        raise HTTPException(
            status_code=400,
            detail=f"Vessel draft ({vessel.draft_meters}m) exceeds berth depth ({berth.depth_meters}m)"
        )

    # Check for conflicting assignments
    conflicts = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.berth_id == assignment.berth_id,
            BerthAssignment.status == AssignmentStatus.ACTIVE,
            or_(
                and_(
                    BerthAssignment.check_in <= assignment.check_in,
                    BerthAssignment.expected_check_out >= assignment.check_in
                ),
                and_(
                    BerthAssignment.check_in <= assignment.expected_check_out,
                    BerthAssignment.expected_check_out >= assignment.expected_check_out
                ),
                and_(
                    BerthAssignment.check_in >= assignment.check_in,
                    BerthAssignment.expected_check_out <= assignment.expected_check_out
                )
            )
        )
    ).first()

    if conflicts:
        raise HTTPException(
            status_code=400,
            detail=f"Berth {berth.berth_number} has conflicting assignment for this period"
        )

    # Calculate billing
    total_days = (assignment.expected_check_out - assignment.check_in).days
    if total_days < 1:
        total_days = 1  # Minimum 1 day

    total_amount = berth.daily_rate_eur * total_days

    # Create assignment
    db_assignment = BerthAssignment(
        **assignment.dict(),
        daily_rate_eur=berth.daily_rate_eur,
        total_days=total_days,
        total_amount_eur=total_amount,
        status=AssignmentStatus.ACTIVE
    )
    db.add(db_assignment)

    # Update berth status
    berth.status = BerthStatus.OCCUPIED
    db.commit()
    db.refresh(db_assignment)

    return db_assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update assignment details

    Allows updating expected checkout and service requests
    """
    assignment = db.query(BerthAssignment).filter(BerthAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if assignment.status != AssignmentStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update assignment with status {assignment.status}"
        )

    # Update only provided fields
    update_data = assignment_update.dict(exclude_unset=True)

    # If expected_check_out is being updated, recalculate billing
    if 'expected_check_out' in update_data:
        new_check_out = update_data['expected_check_out']
        total_days = (new_check_out - assignment.check_in).days
        if total_days < 1:
            total_days = 1
        assignment.total_days = total_days
        assignment.total_amount_eur = assignment.daily_rate_eur * total_days

    for field, value in update_data.items():
        setattr(assignment, field, value)

    db.commit()
    db.refresh(assignment)
    return assignment


@router.post("/check-in", response_model=AssignmentResponse, status_code=201)
async def check_in(check_in_req: CheckInRequest, db: Session = Depends(get_db)):
    """
    Check in a vessel to a berth

    This is a convenience endpoint that creates an assignment with check_in = now
    """
    assignment = AssignmentCreate(
        berth_id=check_in_req.berth_id,
        vessel_id=check_in_req.vessel_id,
        customer_id=check_in_req.customer_id,
        check_in=datetime.now(),
        expected_check_out=check_in_req.expected_check_out,
        electricity_requested=check_in_req.electricity_requested,
        water_requested=check_in_req.water_requested,
        wifi_requested=check_in_req.wifi_requested,
        vhf_log_id=check_in_req.vhf_log_id,
        notes=check_in_req.notes
    )

    return await create_assignment(assignment, db)


@router.post("/{assignment_id}/check-out", response_model=AssignmentResponse)
async def check_out(
    assignment_id: int,
    check_out_req: CheckOutRequest,
    db: Session = Depends(get_db)
):
    """
    Check out a vessel from its berth

    Marks assignment as completed and frees up the berth
    Optionally creates an invoice for payment
    """
    assignment = db.query(BerthAssignment).filter(BerthAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if assignment.status != AssignmentStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot check out assignment with status {assignment.status}"
        )

    # Update assignment
    assignment.actual_check_out = datetime.now()
    assignment.status = AssignmentStatus.COMPLETED

    # Recalculate billing based on actual checkout
    actual_days = (assignment.actual_check_out - assignment.check_in).days
    if actual_days < 1:
        actual_days = 1
    assignment.total_days = actual_days
    assignment.total_amount_eur = assignment.daily_rate_eur * actual_days

    if check_out_req.notes:
        assignment.notes = (assignment.notes or "") + "\n" + check_out_req.notes

    # Update berth status
    berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
    if berth:
        berth.status = BerthStatus.AVAILABLE

    # TODO: Create invoice if requested
    if check_out_req.create_invoice:
        # This would integrate with Parasut API
        # For now, just log it
        pass

    db.commit()
    db.refresh(assignment)

    return assignment


@router.delete("/{assignment_id}", status_code=204)
async def cancel_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """
    Cancel a berth assignment

    Marks assignment as cancelled and frees up the berth
    Only allowed for active assignments
    """
    assignment = db.query(BerthAssignment).filter(BerthAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail=f"Assignment {assignment_id} not found")

    if assignment.status != AssignmentStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel assignment with status {assignment.status}"
        )

    assignment.status = AssignmentStatus.CANCELLED

    # Update berth status
    berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
    if berth:
        berth.status = BerthStatus.AVAILABLE

    db.commit()
    return None


@router.get("/active/current")
async def get_current_assignments(db: Session = Depends(get_db)):
    """
    Get all currently active assignments

    Returns list of vessels currently checked in
    """
    active = db.query(BerthAssignment).filter(
        BerthAssignment.status == AssignmentStatus.ACTIVE
    ).all()

    # Enrich with berth and vessel details
    enriched = []
    for assignment in active:
        berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
        vessel = db.query(Vessel).filter(Vessel.id == assignment.vessel_id).first()
        customer = db.query(Customer).filter(Customer.id == assignment.customer_id).first()

        enriched.append({
            "assignment_id": assignment.id,
            "berth_number": berth.berth_number if berth else None,
            "vessel_name": vessel.name if vessel else None,
            "customer_name": customer.name if customer else None,
            "check_in": assignment.check_in,
            "expected_check_out": assignment.expected_check_out,
            "days_remaining": (assignment.expected_check_out - datetime.now()).days
        })

    return {
        "total_active": len(enriched),
        "assignments": enriched
    }


@router.get("/statistics/summary")
async def get_assignment_statistics(db: Session = Depends(get_db)):
    """
    Get assignment statistics

    Returns counts and revenue information
    """
    total_assignments = db.query(BerthAssignment).count()
    active_assignments = db.query(BerthAssignment).filter(
        BerthAssignment.status == AssignmentStatus.ACTIVE
    ).count()
    completed_assignments = db.query(BerthAssignment).filter(
        BerthAssignment.status == AssignmentStatus.COMPLETED
    ).count()
    cancelled_assignments = db.query(BerthAssignment).filter(
        BerthAssignment.status == AssignmentStatus.CANCELLED
    ).count()

    # Revenue from completed assignments
    total_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        BerthAssignment.status == AssignmentStatus.COMPLETED
    ).scalar() or 0

    # Expected revenue from active assignments
    expected_revenue = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
        BerthAssignment.status == AssignmentStatus.ACTIVE
    ).scalar() or 0

    # SEAL predictions
    seal_predicted = db.query(BerthAssignment).filter(
        BerthAssignment.was_seal_predicted == True
    ).count()

    return {
        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "completed_assignments": completed_assignments,
        "cancelled_assignments": cancelled_assignments,
        "total_revenue_eur": round(total_revenue, 2),
        "expected_revenue_eur": round(expected_revenue, 2),
        "seal_predictions": {
            "total_predicted": seal_predicted,
            "prediction_rate": round(seal_predicted / total_assignments * 100, 2) if total_assignments > 0 else 0
        }
    }
