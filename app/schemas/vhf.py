"""
Pydantic schemas for VHF Log model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class VHFDirection(str, Enum):
    """Direction of VHF communication"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class VHFIntent(str, Enum):
    """Parsed intent from VHF communication"""
    RESERVATION = "reservation_create"
    BERTH_INQUIRY = "berth_inquiry"
    SERVICE_REQUEST = "service_request"
    ARRIVAL_NOTIFICATION = "arrival_notification"
    DEPARTURE_NOTIFICATION = "departure_notification"
    EMERGENCY = "emergency"
    GENERAL_INQUIRY = "general_inquiry"


class VHFLogBase(BaseModel):
    """Base schema with common VHF log fields"""
    # Communication Details
    channel: int = Field(default=72, description="VHF channel number")
    frequency: str = Field(default="156.625", max_length=20, description="VHF frequency")
    direction: VHFDirection = Field(..., description="Communication direction (incoming/outgoing)")

    # Content
    vessel_name: Optional[str] = Field(default=None, max_length=200, description="Name of calling vessel")
    caller_id: Optional[str] = Field(default=None, max_length=100, description="Caller identification")
    message_text: str = Field(..., description="Full message text")
    language_detected: str = Field(default="tr", max_length=2, description="Detected language (tr, en, el)")

    # AI Processing (SCOUT Agent)
    intent_parsed: Optional[VHFIntent] = Field(default=None, description="Parsed intent from message")
    confidence_score: Optional[int] = Field(default=None, ge=0, le=100, description="AI confidence score (0-100)")
    entities_extracted: Optional[str] = Field(default=None, description="Extracted entities as JSON string")

    # Response
    response_text: Optional[str] = Field(default=None, description="System response text")
    response_time_seconds: Optional[int] = Field(default=None, ge=0, description="Response time in seconds")

    # Processing Status
    was_processed: bool = Field(default=False, description="Whether message was processed by AI")
    resulted_in_assignment: bool = Field(default=False, description="Whether processing resulted in a berth assignment")
    assignment_id: Optional[int] = Field(default=None, gt=0, description="Associated assignment ID if created")

    @validator('confidence_score')
    def validate_confidence(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('Confidence score must be between 0 and 100')
        return v

    @validator('language_detected')
    def validate_language(cls, v):
        if v not in ['tr', 'en', 'el']:
            raise ValueError('Language must be tr, en, or el')
        return v

    @validator('channel')
    def validate_channel(cls, v):
        if v < 0 or v > 88:
            raise ValueError('VHF channel must be between 0 and 88')
        return v


class VHFLogCreate(VHFLogBase):
    """Schema for creating a new VHF log (POST request)"""
    pass


class VHFLogResponse(VHFLogBase):
    """Schema for VHF log responses from database (GET request)"""
    id: int = Field(..., description="VHF Log ID")
    timestamp: datetime = Field(..., description="Communication timestamp")
    created_at: datetime = Field(..., description="Log creation timestamp")

    class Config:
        orm_mode = True
