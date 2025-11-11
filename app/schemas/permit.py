"""
Pydantic schemas for Permit model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class PermitType(str, Enum):
    """Type of permit"""
    HOT_WORK = "hot_work"
    CRANE_OPERATION = "crane_operation"
    DIVING = "diving"
    PAINTING = "painting"
    ENGINE_WORK = "engine_work"
    SPECIAL_EVENT = "special_event"


class PermitStatus(str, Enum):
    """Status of permit"""
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class PermitBase(BaseModel):
    """Base schema with common permit fields"""
    # Permit Details
    permit_number: str = Field(..., min_length=1, max_length=50, description="Unique permit number")
    permit_type: PermitType = Field(..., description="Type of permit")

    # Requestor
    vessel_id: int = Field(..., gt=0, description="Vessel ID (permit requestor)")
    customer_id: int = Field(..., gt=0, description="Customer ID (permit requestor)")

    # Work Description
    work_type: str = Field(..., min_length=1, max_length=200, description="Type of work")
    work_description: str = Field(..., min_length=1, description="Detailed work description")
    work_location: Optional[str] = Field(default=None, max_length=200, description="Work location (berth number or area)")

    # Fire Prevention (for hot work)
    fire_prevention_measures: Optional[str] = Field(default=None, description="Fire prevention measures")
    fire_watch_assigned: Optional[str] = Field(default=None, max_length=200, description="Fire watch personnel assigned")
    extinguishers_positioned: bool = Field(default=False, description="Fire extinguishers positioned")
    surrounding_notified: bool = Field(default=False, description="Surrounding vessels notified")

    # Timing
    start_time: datetime = Field(..., description="Work start time")
    end_time: datetime = Field(..., description="Work end time")
    actual_completion: Optional[datetime] = Field(default=None, description="Actual completion time")

    # Status
    status: PermitStatus = Field(default=PermitStatus.REQUESTED, description="Permit status")

    # Approval
    approved_by: Optional[str] = Field(default=None, max_length=200, description="Approver name")
    approved_at: Optional[datetime] = Field(default=None, description="Approval timestamp")

    # Safety
    safety_briefing_completed: bool = Field(default=False, description="Safety briefing completed")
    insurance_verified: bool = Field(default=False, description="Insurance verified")

    # Notes
    notes: Optional[str] = Field(default=None, description="Additional notes")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('actual_completion')
    def validate_actual_completion(cls, v, values):
        if v is not None:
            if 'start_time' in values and v < values['start_time']:
                raise ValueError('Actual completion must be after or at start time')
        return v

    @validator('approved_at')
    def validate_approved_at(cls, v, values):
        if v is not None:
            if 'start_time' in values and v > values['start_time']:
                raise ValueError('Approval must be before work start time')
        return v


class PermitCreate(PermitBase):
    """Schema for creating a new permit (POST request)"""
    pass


class PermitUpdate(BaseModel):
    """Schema for updating a permit (PUT/PATCH request)"""
    permit_number: Optional[str] = Field(default=None, max_length=50)
    permit_type: Optional[PermitType] = None
    vessel_id: Optional[int] = Field(default=None, gt=0)
    customer_id: Optional[int] = Field(default=None, gt=0)
    work_type: Optional[str] = Field(default=None, max_length=200)
    work_description: Optional[str] = None
    work_location: Optional[str] = Field(default=None, max_length=200)
    fire_prevention_measures: Optional[str] = None
    fire_watch_assigned: Optional[str] = Field(default=None, max_length=200)
    extinguishers_positioned: Optional[bool] = None
    surrounding_notified: Optional[bool] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    status: Optional[PermitStatus] = None
    approved_by: Optional[str] = Field(default=None, max_length=200)
    approved_at: Optional[datetime] = None
    safety_briefing_completed: Optional[bool] = None
    insurance_verified: Optional[bool] = None
    notes: Optional[str] = None

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and values['start_time'] and v and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('actual_completion')
    def validate_actual_completion(cls, v, values):
        if v is not None:
            if 'start_time' in values and values['start_time'] and v < values['start_time']:
                raise ValueError('Actual completion must be after or at start time')
        return v

    @validator('approved_at')
    def validate_approved_at(cls, v, values):
        if v is not None:
            if 'start_time' in values and values['start_time'] and v > values['start_time']:
                raise ValueError('Approval must be before work start time')
        return v


class PermitResponse(PermitBase):
    """Schema for permit responses from database (GET request)"""
    id: int = Field(..., description="Permit ID")
    requested_at: datetime = Field(..., description="Request timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
