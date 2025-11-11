"""
Vessels API endpoints
Manages boats and yachts registered in the marina
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.vessel import Vessel, VesselType
from app.models.customer import Customer
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic schemas
class VesselBase(BaseModel):
    customer_id: int
    name: str = Field(..., min_length=1, max_length=200)
    registration_number: str = Field(..., min_length=1, max_length=100)
    flag_country: str = "Turkey"
    vessel_type: VesselType
    length_meters: float = Field(..., gt=0)
    width_meters: float = Field(..., gt=0)
    draft_meters: float = Field(..., gt=0)
    weight_tons: Optional[float] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_built: Optional[int] = None
    insurance_company: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[datetime] = None
    engine_type: Optional[str] = None
    fuel_capacity_liters: Optional[float] = None
    water_capacity_liters: Optional[float] = None
    notes: Optional[str] = None


class VesselCreate(VesselBase):
    """Schema for creating a new vessel"""
    pass


class VesselUpdate(BaseModel):
    """Schema for updating vessel details"""
    name: Optional[str] = None
    registration_number: Optional[str] = None
    flag_country: Optional[str] = None
    vessel_type: Optional[VesselType] = None
    insurance_company: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[datetime] = None
    engine_type: Optional[str] = None
    fuel_capacity_liters: Optional[float] = None
    water_capacity_liters: Optional[float] = None
    notes: Optional[str] = None


class VesselResponse(VesselBase):
    """Schema for vessel response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VesselWithOwner(VesselResponse):
    """Vessel response with owner information"""
    owner_name: str
    owner_email: str
    owner_phone: str


@router.get("/", response_model=List[VesselResponse])
async def list_vessels(
    search: Optional[str] = None,
    vessel_type: Optional[VesselType] = None,
    flag_country: Optional[str] = None,
    customer_id: Optional[int] = None,
    min_length: Optional[float] = None,
    max_length: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all vessels with optional filtering

    Parameters:
    - search: Search by vessel name or registration number
    - vessel_type: Filter by vessel type
    - flag_country: Filter by flag country
    - customer_id: Filter by owner customer ID
    - min_length: Minimum vessel length in meters
    - max_length: Maximum vessel length in meters
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(Vessel)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Vessel.name.ilike(search_pattern),
                Vessel.registration_number.ilike(search_pattern)
            )
        )

    if vessel_type:
        query = query.filter(Vessel.vessel_type == vessel_type)

    if flag_country:
        query = query.filter(Vessel.flag_country == flag_country)

    if customer_id:
        query = query.filter(Vessel.customer_id == customer_id)

    if min_length:
        query = query.filter(Vessel.length_meters >= min_length)

    if max_length:
        query = query.filter(Vessel.length_meters <= max_length)

    vessels = query.offset(skip).limit(limit).all()
    return vessels


@router.get("/{vessel_id}", response_model=VesselResponse)
async def get_vessel(vessel_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific vessel

    Parameters:
    - vessel_id: Unique identifier of the vessel
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
    return vessel


@router.get("/registration/{registration_number}", response_model=VesselResponse)
async def get_vessel_by_registration(registration_number: str, db: Session = Depends(get_db)):
    """
    Get vessel by registration number

    Parameters:
    - registration_number: Vessel registration or IMO number
    """
    vessel = db.query(Vessel).filter(
        Vessel.registration_number == registration_number
    ).first()
    if not vessel:
        raise HTTPException(
            status_code=404,
            detail=f"Vessel with registration {registration_number} not found"
        )
    return vessel


@router.post("/", response_model=VesselResponse, status_code=201)
async def create_vessel(vessel: VesselCreate, db: Session = Depends(get_db)):
    """
    Register a new vessel in the marina

    Validates owner exists and registration number is unique
    """
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.id == vessel.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {vessel.customer_id} not found"
        )

    # Check for duplicate registration number
    existing = db.query(Vessel).filter(
        Vessel.registration_number == vessel.registration_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Vessel with registration {vessel.registration_number} already exists"
        )

    db_vessel = Vessel(**vessel.dict())
    db.add(db_vessel)
    db.commit()
    db.refresh(db_vessel)
    return db_vessel


@router.put("/{vessel_id}", response_model=VesselResponse)
async def update_vessel(
    vessel_id: int,
    vessel_update: VesselUpdate,
    db: Session = Depends(get_db)
):
    """
    Update vessel information

    Allows updating vessel details and insurance information
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    # Check for registration number conflicts
    if vessel_update.registration_number and vessel_update.registration_number != vessel.registration_number:
        existing = db.query(Vessel).filter(
            and_(
                Vessel.registration_number == vessel_update.registration_number,
                Vessel.id != vessel_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Registration {vessel_update.registration_number} is already in use"
            )

    # Update only provided fields
    update_data = vessel_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vessel, field, value)

    db.commit()
    db.refresh(vessel)
    return vessel


@router.delete("/{vessel_id}", status_code=204)
async def delete_vessel(vessel_id: int, db: Session = Depends(get_db)):
    """
    Delete a vessel from the marina registry

    Only allowed if vessel has no active assignments
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    # Check for active assignments
    from app.models.berth_assignment import BerthAssignment, AssignmentStatus
    active_assignments = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.vessel_id == vessel_id,
            BerthAssignment.status == AssignmentStatus.ACTIVE
        )
    ).first()

    if active_assignments:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete vessel with active berth assignments"
        )

    db.delete(vessel)
    db.commit()
    return None


@router.get("/{vessel_id}/owner")
async def get_vessel_owner(vessel_id: int, db: Session = Depends(get_db)):
    """
    Get owner information for a vessel

    Returns customer details of vessel owner
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    customer = db.query(Customer).filter(Customer.id == vessel.customer_id).first()

    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel.name,
        "owner": customer
    }


@router.get("/{vessel_id}/assignments")
async def get_vessel_assignments(
    vessel_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all berth assignments for a vessel

    Parameters:
    - active_only: If true, only return active assignments
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    from app.models.berth_assignment import BerthAssignment, AssignmentStatus

    query = db.query(BerthAssignment).filter(BerthAssignment.vessel_id == vessel_id)

    if active_only:
        query = query.filter(BerthAssignment.status == AssignmentStatus.ACTIVE)

    assignments = query.order_by(BerthAssignment.check_in.desc()).all()

    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel.name,
        "total_assignments": len(assignments),
        "assignments": assignments
    }


@router.get("/{vessel_id}/insurance/status")
async def check_insurance_status(vessel_id: int, db: Session = Depends(get_db)):
    """
    Check vessel insurance compliance status (Article E.2.1)

    Returns insurance validity and expiration information
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    has_insurance = bool(vessel.insurance_company and vessel.insurance_policy_number)
    is_expired = False
    days_until_expiry = None

    if has_insurance and vessel.insurance_expiry_date:
        today = datetime.now()
        is_expired = vessel.insurance_expiry_date < today
        if not is_expired:
            days_until_expiry = (vessel.insurance_expiry_date - today).days

    compliance_status = "compliant" if (has_insurance and not is_expired) else "non_compliant"

    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel.name,
        "has_insurance": has_insurance,
        "insurance_company": vessel.insurance_company,
        "insurance_policy_number": vessel.insurance_policy_number,
        "insurance_expiry_date": vessel.insurance_expiry_date,
        "is_expired": is_expired,
        "days_until_expiry": days_until_expiry,
        "compliance_status": compliance_status,
        "regulation_article": "E.2.1"
    }


@router.get("/{vessel_id}/violations")
async def get_vessel_violations(
    vessel_id: int,
    include_resolved: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all violations associated with a vessel

    Parameters:
    - include_resolved: If true, include resolved violations
    """
    vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    if not vessel:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")

    from app.models.violation import Violation, ViolationStatus

    query = db.query(Violation).filter(Violation.vessel_id == vessel_id)

    if not include_resolved:
        query = query.filter(Violation.status != ViolationStatus.RESOLVED)

    violations = query.order_by(Violation.detected_at.desc()).all()

    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel.name,
        "total_violations": len(violations),
        "violations": violations
    }


@router.get("/statistics/summary")
async def get_vessel_statistics(db: Session = Depends(get_db)):
    """
    Get overall vessel statistics

    Returns counts by type, flag country, and size distribution
    """
    total_vessels = db.query(Vessel).count()

    # Vessels by type
    vessels_by_type = {}
    for vtype in VesselType:
        count = db.query(Vessel).filter(Vessel.vessel_type == vtype).count()
        vessels_by_type[vtype.value] = count

    # Top flag countries
    top_flags = db.query(
        Vessel.flag_country,
        func.count(Vessel.id).label('count')
    ).group_by(Vessel.flag_country).order_by(func.count(Vessel.id).desc()).limit(10).all()

    # Size distribution
    size_ranges = {
        "small_10_15m": db.query(Vessel).filter(
            and_(Vessel.length_meters >= 10, Vessel.length_meters < 15)
        ).count(),
        "medium_15_25m": db.query(Vessel).filter(
            and_(Vessel.length_meters >= 15, Vessel.length_meters < 25)
        ).count(),
        "large_25_40m": db.query(Vessel).filter(
            and_(Vessel.length_meters >= 25, Vessel.length_meters < 40)
        ).count(),
        "superyacht_40m_plus": db.query(Vessel).filter(Vessel.length_meters >= 40).count()
    }

    # Insurance compliance
    vessels_with_insurance = db.query(Vessel).filter(
        and_(
            Vessel.insurance_company.isnot(None),
            Vessel.insurance_policy_number.isnot(None)
        )
    ).count()

    return {
        "total_vessels": total_vessels,
        "vessels_by_type": vessels_by_type,
        "top_flag_countries": [{"country": f[0], "count": f[1]} for f in top_flags],
        "size_distribution": size_ranges,
        "insurance_compliance": {
            "with_insurance": vessels_with_insurance,
            "without_insurance": total_vessels - vessels_with_insurance,
            "compliance_rate": round(vessels_with_insurance / total_vessels * 100, 2) if total_vessels > 0 else 0
        }
    }
