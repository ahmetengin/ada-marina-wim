"""
Berths API endpoints
Manages berth/slip inventory, availability, and allocation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.berth import Berth, BerthStatus, BerthSection
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic schemas
class BerthBase(BaseModel):
    berth_number: str
    section: BerthSection
    length_meters: float
    width_meters: float
    depth_meters: float
    has_electricity: bool = True
    has_water: bool = True
    electricity_voltage: int = 220
    has_wifi: bool = True
    daily_rate_eur: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class BerthCreate(BerthBase):
    """Schema for creating a new berth"""
    pass


class BerthUpdate(BaseModel):
    """Schema for updating berth details"""
    status: Optional[BerthStatus] = None
    daily_rate_eur: Optional[float] = None
    has_electricity: Optional[bool] = None
    has_water: Optional[bool] = None
    has_wifi: Optional[bool] = None
    notes: Optional[str] = None


class BerthResponse(BerthBase):
    """Schema for berth response"""
    id: int
    status: BerthStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BerthAvailabilityQuery(BaseModel):
    """Query parameters for checking berth availability"""
    check_in: datetime
    check_out: datetime
    vessel_length: float
    vessel_width: float
    vessel_draft: float
    section: Optional[BerthSection] = None


class BerthAvailabilityResponse(BaseModel):
    """Available berth information"""
    berth_id: int
    berth_number: str
    section: BerthSection
    length_meters: float
    width_meters: float
    daily_rate_eur: float
    total_cost_eur: float
    is_optimal_fit: bool


@router.get("/", response_model=List[BerthResponse])
async def list_berths(
    section: Optional[BerthSection] = None,
    status: Optional[BerthStatus] = None,
    min_length: Optional[float] = None,
    max_length: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all berths with optional filtering

    Parameters:
    - section: Filter by berth section (A-F)
    - status: Filter by berth status
    - min_length: Minimum berth length in meters
    - max_length: Maximum berth length in meters
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(Berth)

    if section:
        query = query.filter(Berth.section == section)
    if status:
        query = query.filter(Berth.status == status)
    if min_length:
        query = query.filter(Berth.length_meters >= min_length)
    if max_length:
        query = query.filter(Berth.length_meters <= max_length)

    berths = query.offset(skip).limit(limit).all()
    return berths


@router.get("/{berth_id}", response_model=BerthResponse)
async def get_berth(berth_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific berth

    Parameters:
    - berth_id: Unique identifier of the berth
    """
    berth = db.query(Berth).filter(Berth.id == berth_id).first()
    if not berth:
        raise HTTPException(status_code=404, detail=f"Berth {berth_id} not found")
    return berth


@router.get("/number/{berth_number}", response_model=BerthResponse)
async def get_berth_by_number(berth_number: str, db: Session = Depends(get_db)):
    """
    Get berth by berth number (e.g., "A-01", "B-12")

    Parameters:
    - berth_number: Berth identification number
    """
    berth = db.query(Berth).filter(Berth.berth_number == berth_number).first()
    if not berth:
        raise HTTPException(status_code=404, detail=f"Berth {berth_number} not found")
    return berth


@router.post("/", response_model=BerthResponse, status_code=201)
async def create_berth(berth: BerthCreate, db: Session = Depends(get_db)):
    """
    Create a new berth in the marina

    Requires administrative privileges
    """
    # Check if berth number already exists
    existing = db.query(Berth).filter(Berth.berth_number == berth.berth_number).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Berth {berth.berth_number} already exists"
        )

    db_berth = Berth(**berth.dict())
    db.add(db_berth)
    db.commit()
    db.refresh(db_berth)
    return db_berth


@router.put("/{berth_id}", response_model=BerthResponse)
async def update_berth(
    berth_id: int,
    berth_update: BerthUpdate,
    db: Session = Depends(get_db)
):
    """
    Update berth information

    Allows updating status, pricing, services, and notes
    """
    berth = db.query(Berth).filter(Berth.id == berth_id).first()
    if not berth:
        raise HTTPException(status_code=404, detail=f"Berth {berth_id} not found")

    # Update only provided fields
    update_data = berth_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(berth, field, value)

    db.commit()
    db.refresh(berth)
    return berth


@router.delete("/{berth_id}", status_code=204)
async def delete_berth(berth_id: int, db: Session = Depends(get_db)):
    """
    Delete a berth (administrative operation)

    Only allowed if berth has no active assignments
    """
    berth = db.query(Berth).filter(Berth.id == berth_id).first()
    if not berth:
        raise HTTPException(status_code=404, detail=f"Berth {berth_id} not found")

    # Check for active assignments
    active_assignments = db.query(BerthAssignment).filter(
        and_(
            BerthAssignment.berth_id == berth_id,
            BerthAssignment.status == AssignmentStatus.ACTIVE
        )
    ).first()

    if active_assignments:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete berth with active assignments"
        )

    db.delete(berth)
    db.commit()
    return None


@router.post("/availability", response_model=List[BerthAvailabilityResponse])
async def check_availability(
    query: BerthAvailabilityQuery,
    db: Session = Depends(get_db)
):
    """
    Check berth availability for given dates and vessel dimensions

    Returns list of available berths sorted by suitability.
    Factors considered:
    - Vessel dimensions vs berth size
    - Current availability
    - Price optimization
    - Optimal fit (not too large, not too small)
    """
    # Calculate number of days
    days = (query.check_out - query.check_in).days
    if days < 1:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    # Find berths that can accommodate the vessel
    suitable_berths = db.query(Berth).filter(
        and_(
            Berth.length_meters >= query.vessel_length,
            Berth.width_meters >= query.vessel_width,
            Berth.depth_meters >= query.vessel_draft,
            Berth.status.in_([BerthStatus.AVAILABLE, BerthStatus.RESERVED])
        )
    )

    # Filter by section if specified
    if query.section:
        suitable_berths = suitable_berths.filter(Berth.section == query.section)

    suitable_berths = suitable_berths.all()

    # Check for conflicting assignments
    available_berths = []
    for berth in suitable_berths:
        # Check if berth has overlapping assignments
        conflicts = db.query(BerthAssignment).filter(
            and_(
                BerthAssignment.berth_id == berth.id,
                BerthAssignment.status == AssignmentStatus.ACTIVE,
                or_(
                    and_(
                        BerthAssignment.check_in <= query.check_in,
                        BerthAssignment.expected_check_out >= query.check_in
                    ),
                    and_(
                        BerthAssignment.check_in <= query.check_out,
                        BerthAssignment.expected_check_out >= query.check_out
                    ),
                    and_(
                        BerthAssignment.check_in >= query.check_in,
                        BerthAssignment.expected_check_out <= query.check_out
                    )
                )
            )
        ).first()

        if not conflicts:
            # Calculate if this is an optimal fit
            # Optimal: vessel uses 70-95% of berth length
            usage_percent = (query.vessel_length / berth.length_meters) * 100
            is_optimal = 70 <= usage_percent <= 95

            total_cost = berth.daily_rate_eur * days

            available_berths.append(
                BerthAvailabilityResponse(
                    berth_id=berth.id,
                    berth_number=berth.berth_number,
                    section=berth.section,
                    length_meters=berth.length_meters,
                    width_meters=berth.width_meters,
                    daily_rate_eur=berth.daily_rate_eur,
                    total_cost_eur=total_cost,
                    is_optimal_fit=is_optimal
                )
            )

    # Sort by optimal fit first, then by price
    available_berths.sort(key=lambda x: (not x.is_optimal_fit, x.total_cost_eur))

    return available_berths


@router.get("/statistics/occupancy")
async def get_occupancy_statistics(db: Session = Depends(get_db)):
    """
    Get overall berth occupancy statistics

    Returns current occupancy rates by section and overall
    """
    total_berths = db.query(Berth).count()
    occupied = db.query(Berth).filter(Berth.status == BerthStatus.OCCUPIED).count()
    available = db.query(Berth).filter(Berth.status == BerthStatus.AVAILABLE).count()
    reserved = db.query(Berth).filter(Berth.status == BerthStatus.RESERVED).count()
    maintenance = db.query(Berth).filter(Berth.status == BerthStatus.MAINTENANCE).count()

    # Occupancy by section
    sections = {}
    for section in BerthSection:
        section_total = db.query(Berth).filter(Berth.section == section).count()
        section_occupied = db.query(Berth).filter(
            and_(Berth.section == section, Berth.status == BerthStatus.OCCUPIED)
        ).count()

        sections[section.value] = {
            "total": section_total,
            "occupied": section_occupied,
            "occupancy_rate": round(section_occupied / section_total * 100, 2) if section_total > 0 else 0
        }

    return {
        "total_berths": total_berths,
        "occupied": occupied,
        "available": available,
        "reserved": reserved,
        "maintenance": maintenance,
        "overall_occupancy_rate": round(occupied / total_berths * 100, 2) if total_berths > 0 else 0,
        "sections": sections
    }
