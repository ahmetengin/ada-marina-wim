"""
Pydantic schemas for Berth Assignment model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class AssignmentStatus(str, Enum):
    """Status of berth assignment"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentBase(BaseModel):
    """Base schema with common assignment fields"""
    # References
    berth_id: int = Field(..., gt=0, description="Berth ID")
    vessel_id: int = Field(..., gt=0, description="Vessel ID")
    customer_id: int = Field(..., gt=0, description="Customer ID")

    # Timing
    check_in: datetime = Field(..., description="Check-in timestamp")
    expected_check_out: datetime = Field(..., description="Expected check-out timestamp")
    actual_check_out: Optional[datetime] = Field(default=None, description="Actual check-out timestamp")

    # Status
    status: AssignmentStatus = Field(default=AssignmentStatus.ACTIVE, description="Assignment status")

    # Services requested
    electricity_requested: Optional[int] = Field(default=None, description="Electricity voltage requested (220V or 380V)")
    water_requested: bool = Field(default=True, description="Water service requested")
    wifi_requested: bool = Field(default=True, description="WiFi service requested")

    # Billing
    daily_rate_eur: float = Field(..., ge=0, description="Daily rate in EUR")
    total_days: int = Field(..., gt=0, description="Total number of days")
    total_amount_eur: float = Field(..., ge=0, description="Total amount in EUR")
    invoice_id: Optional[int] = Field(default=None, gt=0, description="Associated invoice ID")

    # VHF Communication
    vhf_log_id: Optional[int] = Field(default=None, gt=0, description="Associated VHF log ID")

    # SEAL Learning
    was_seal_predicted: bool = Field(default=False, description="Was this assignment SEAL-predicted")
    seal_confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="SEAL confidence score (0-1)")

    # Notes
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")

    @validator('check_in', 'expected_check_out', 'actual_check_out')
    def validate_dates(cls, v):
        if v is not None and v < datetime.now(v.tzinfo if hasattr(v, 'tzinfo') else None):
            # Allow past dates for completed assignments
            pass
        return v

    @validator('expected_check_out')
    def validate_checkout_after_checkin(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('Expected check-out must be after check-in')
        return v

    @validator('electricity_requested')
    def validate_electricity(cls, v):
        if v is not None and v not in [220, 380]:
            raise ValueError('Electricity voltage must be 220V or 380V')
        return v


class AssignmentCreate(AssignmentBase):
    """Schema for creating a new assignment (POST request)"""
    pass


class AssignmentUpdate(BaseModel):
    """Schema for updating an assignment (PUT/PATCH request)"""
    berth_id: Optional[int] = Field(default=None, gt=0)
    vessel_id: Optional[int] = Field(default=None, gt=0)
    customer_id: Optional[int] = Field(default=None, gt=0)
    check_in: Optional[datetime] = None
    expected_check_out: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status: Optional[AssignmentStatus] = None
    electricity_requested: Optional[int] = None
    water_requested: Optional[bool] = None
    wifi_requested: Optional[bool] = None
    daily_rate_eur: Optional[float] = Field(default=None, ge=0)
    total_days: Optional[int] = Field(default=None, gt=0)
    total_amount_eur: Optional[float] = Field(default=None, ge=0)
    invoice_id: Optional[int] = Field(default=None, gt=0)
    vhf_log_id: Optional[int] = Field(default=None, gt=0)
    was_seal_predicted: Optional[bool] = None
    seal_confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    notes: Optional[str] = Field(default=None, max_length=1000)

    @validator('expected_check_out')
    def validate_checkout_after_checkin(cls, v, values):
        if 'check_in' in values and values['check_in'] and v and v <= values['check_in']:
            raise ValueError('Expected check-out must be after check-in')
        return v

    @validator('electricity_requested')
    def validate_electricity(cls, v):
        if v is not None and v not in [220, 380]:
            raise ValueError('Electricity voltage must be 220V or 380V')
        return v


class AssignmentResponse(AssignmentBase):
    """Schema for assignment responses from database (GET request)"""
    id: int = Field(..., description="Assignment ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
