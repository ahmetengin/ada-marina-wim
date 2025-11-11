"""
Pydantic schemas for Violation model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ViolationSeverity(str, Enum):
    """Severity level of violation"""
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ViolationStatus(str, Enum):
    """Status of violation handling"""
    REPORTED = "reported"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    APPEALED = "appealed"


class ViolationBase(BaseModel):
    """Base schema with common violation fields"""
    # Violator
    vessel_id: int = Field(..., gt=0, description="Vessel ID (violator)")
    customer_id: int = Field(..., gt=0, description="Customer ID (violator)")

    # Violation Details
    article_violated: str = Field(..., min_length=1, max_length=20, description="WIM article violated (e.g., E.1.10)")
    description: str = Field(..., min_length=1, description="Violation description")

    # Severity & Status
    severity: ViolationSeverity = Field(..., description="Violation severity level")
    status: ViolationStatus = Field(default=ViolationStatus.REPORTED, description="Violation status")

    # Financial
    fine_amount_eur: Optional[float] = Field(default=None, ge=0, description="Fine amount in EUR")
    fine_paid: bool = Field(default=False, description="Whether fine was paid")
    fine_paid_at: Optional[datetime] = Field(default=None, description="Fine payment timestamp")

    # Detection
    detected_at: datetime = Field(..., description="Detection timestamp")
    detected_by: Optional[str] = Field(default=None, max_length=100, description="Detection source (VERIFY_AGENT, MANUAL, SENSOR)")

    # Evidence
    evidence_description: Optional[str] = Field(default=None, description="Evidence description")
    evidence_files: Optional[str] = Field(default=None, description="Evidence file paths as JSON array")

    # Resolution
    resolution_notes: Optional[str] = Field(default=None, description="Resolution notes")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")

    @validator('fine_paid_at')
    def validate_fine_paid_at(cls, v, values):
        if v is not None:
            if 'detected_at' in values and v < values['detected_at']:
                raise ValueError('Fine paid date must be after detection date')
        return v

    @validator('resolved_at')
    def validate_resolved_at(cls, v, values):
        if v is not None:
            if 'detected_at' in values and v < values['detected_at']:
                raise ValueError('Resolved date must be after detection date')
        return v

    @validator('detected_by')
    def validate_detected_by(cls, v):
        if v is not None and v not in ['VERIFY_AGENT', 'MANUAL', 'SENSOR']:
            raise ValueError('Detected by must be VERIFY_AGENT, MANUAL, or SENSOR')
        return v


class ViolationCreate(ViolationBase):
    """Schema for creating a new violation (POST request)"""
    pass


class ViolationUpdate(BaseModel):
    """Schema for updating a violation (PUT/PATCH request)"""
    vessel_id: Optional[int] = Field(default=None, gt=0)
    customer_id: Optional[int] = Field(default=None, gt=0)
    article_violated: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = None
    severity: Optional[ViolationSeverity] = None
    status: Optional[ViolationStatus] = None
    fine_amount_eur: Optional[float] = Field(default=None, ge=0)
    fine_paid: Optional[bool] = None
    fine_paid_at: Optional[datetime] = None
    detected_at: Optional[datetime] = None
    detected_by: Optional[str] = Field(default=None, max_length=100)
    evidence_description: Optional[str] = None
    evidence_files: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None

    @validator('fine_paid_at')
    def validate_fine_paid_at(cls, v, values):
        if v is not None:
            if 'detected_at' in values and values['detected_at'] and v < values['detected_at']:
                raise ValueError('Fine paid date must be after detection date')
        return v

    @validator('resolved_at')
    def validate_resolved_at(cls, v, values):
        if v is not None:
            if 'detected_at' in values and values['detected_at'] and v < values['detected_at']:
                raise ValueError('Resolved date must be after detection date')
        return v

    @validator('detected_by')
    def validate_detected_by(cls, v):
        if v is not None and v not in ['VERIFY_AGENT', 'MANUAL', 'SENSOR']:
            raise ValueError('Detected by must be VERIFY_AGENT, MANUAL, or SENSOR')
        return v


class ViolationResponse(ViolationBase):
    """Schema for violation responses from database (GET request)"""
    id: int = Field(..., description="Violation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
