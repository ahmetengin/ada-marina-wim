"""
Customers API endpoints
Manages yacht owners and marina customers
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.customer import Customer
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


# Pydantic schemas
class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=50)
    tc_kimlik: Optional[str] = Field(None, min_length=11, max_length=11)
    passport_number: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Turkey"
    is_company: bool = False
    company_name: Optional[str] = None
    tax_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    preferred_language: str = "tr"
    preferred_berth_section: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating customer details"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    company_name: Optional[str] = None
    tax_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_berth_section: Optional[str] = None
    is_active: Optional[bool] = None
    is_vip: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    id: int
    is_active: bool
    is_vip: bool
    parasut_customer_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    search: Optional[str] = None,
    country: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_vip: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all customers with optional filtering

    Parameters:
    - search: Search by name, email, or phone
    - country: Filter by country
    - is_active: Filter by active status
    - is_vip: Filter by VIP status
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(Customer)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                Customer.phone.ilike(search_pattern)
            )
        )

    if country:
        query = query.filter(Customer.country == country)

    if is_active is not None:
        query = query.filter(Customer.is_active == is_active)

    if is_vip is not None:
        query = query.filter(Customer.is_vip == is_vip)

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific customer

    Parameters:
    - customer_id: Unique identifier of the customer
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@router.get("/email/{email}", response_model=CustomerResponse)
async def get_customer_by_email(email: str, db: Session = Depends(get_db)):
    """
    Get customer by email address

    Parameters:
    - email: Customer email address
    """
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with email {email} not found")
    return customer


@router.get("/tc/{tc_kimlik}", response_model=CustomerResponse)
async def get_customer_by_tc(tc_kimlik: str, db: Session = Depends(get_db)):
    """
    Get customer by Turkish ID (TC Kimlik)

    Parameters:
    - tc_kimlik: Turkish national identification number (11 digits)
    """
    if len(tc_kimlik) != 11:
        raise HTTPException(status_code=400, detail="TC Kimlik must be 11 digits")

    customer = db.query(Customer).filter(Customer.tc_kimlik == tc_kimlik).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with TC {tc_kimlik} not found")
    return customer


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer

    Validates that email, TC kimlik, and passport are unique
    """
    # Check for duplicate email
    existing_email = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail=f"Customer with email {customer.email} already exists"
        )

    # Check for duplicate TC kimlik
    if customer.tc_kimlik:
        existing_tc = db.query(Customer).filter(Customer.tc_kimlik == customer.tc_kimlik).first()
        if existing_tc:
            raise HTTPException(
                status_code=400,
                detail=f"Customer with TC kimlik {customer.tc_kimlik} already exists"
            )

    # Check for duplicate passport
    if customer.passport_number:
        existing_passport = db.query(Customer).filter(
            Customer.passport_number == customer.passport_number
        ).first()
        if existing_passport:
            raise HTTPException(
                status_code=400,
                detail=f"Customer with passport {customer.passport_number} already exists"
            )

    # Validate that either TC kimlik or passport is provided
    if not customer.tc_kimlik and not customer.passport_number:
        raise HTTPException(
            status_code=400,
            detail="Either TC kimlik or passport number must be provided"
        )

    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer information

    Allows updating all customer fields except ID-related fields
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    # Check for email conflicts if email is being updated
    if customer_update.email and customer_update.email != customer.email:
        existing_email = db.query(Customer).filter(
            and_(
                Customer.email == customer_update.email,
                Customer.id != customer_id
            )
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail=f"Email {customer_update.email} is already in use"
            )

    # Update only provided fields
    update_data = customer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """
    Delete a customer (soft delete by setting is_active=False)

    For hard delete, use force=true query parameter (requires admin)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    # Soft delete by default
    customer.is_active = False
    db.commit()
    return None


@router.post("/{customer_id}/vip")
async def set_vip_status(
    customer_id: int,
    is_vip: bool,
    db: Session = Depends(get_db)
):
    """
    Set or remove VIP status for a customer

    VIP customers may receive priority berth allocation and special services
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    customer.is_vip = is_vip
    db.commit()

    return {
        "customer_id": customer_id,
        "name": customer.name,
        "is_vip": is_vip,
        "message": f"VIP status {'enabled' if is_vip else 'disabled'} for {customer.name}"
    }


@router.get("/{customer_id}/vessels")
async def get_customer_vessels(customer_id: int, db: Session = Depends(get_db)):
    """
    Get all vessels owned by a customer

    Returns list of vessels registered to this customer
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    from app.models.vessel import Vessel
    vessels = db.query(Vessel).filter(Vessel.customer_id == customer_id).all()

    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "total_vessels": len(vessels),
        "vessels": vessels
    }


@router.get("/{customer_id}/assignments")
async def get_customer_assignments(
    customer_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all berth assignments for a customer

    Parameters:
    - active_only: If true, only return active assignments
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    from app.models.berth_assignment import BerthAssignment, AssignmentStatus

    query = db.query(BerthAssignment).filter(BerthAssignment.customer_id == customer_id)

    if active_only:
        query = query.filter(BerthAssignment.status == AssignmentStatus.ACTIVE)

    assignments = query.order_by(BerthAssignment.check_in.desc()).all()

    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "total_assignments": len(assignments),
        "assignments": assignments
    }


@router.get("/statistics/summary")
async def get_customer_statistics(db: Session = Depends(get_db)):
    """
    Get overall customer statistics

    Returns counts by country, VIP status, and activity
    """
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.is_active == True).count()
    vip_customers = db.query(Customer).filter(Customer.is_vip == True).count()
    company_customers = db.query(Customer).filter(Customer.is_company == True).count()

    # Top countries
    from sqlalchemy import func
    top_countries = db.query(
        Customer.country,
        func.count(Customer.id).label('count')
    ).group_by(Customer.country).order_by(func.count(Customer.id).desc()).limit(10).all()

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "inactive_customers": total_customers - active_customers,
        "vip_customers": vip_customers,
        "company_customers": company_customers,
        "individual_customers": total_customers - company_customers,
        "top_countries": [{"country": c[0], "count": c[1]} for c in top_countries]
    }
