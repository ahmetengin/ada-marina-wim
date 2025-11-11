"""
Pydantic schemas for SEAL Learning model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class SEALLearningBase(BaseModel):
    """Base schema with common SEAL learning fields"""
    # Pattern Identification
    customer_id: int = Field(..., gt=0, description="Customer ID")
    vessel_id: Optional[int] = Field(default=None, gt=0, description="Vessel ID (optional, pattern may apply to all vessels)")

    # Pattern Type
    pattern_type: str = Field(..., min_length=1, max_length=100, description="Type of pattern (berth_preference, service_preference, etc.)")

    # Pattern Details
    pattern_description: str = Field(..., min_length=1, description="Human-readable pattern description")

    # Statistical Confidence
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    occurrence_count: int = Field(default=1, ge=1, description="Number of times pattern was observed")
    last_observed_at: datetime = Field(..., description="Last observation timestamp")

    # Learned Parameters
    learned_parameters: Optional[str] = Field(default=None, description="Learned parameters as JSON string")

    # Reward Signal
    reward_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Reward score (0.0 to 1.0)")

    # Application Status
    is_active: bool = Field(default=True, description="Whether pattern is active")
    auto_apply: bool = Field(default=False, description="Whether to auto-suggest when confidence is high")

    # Performance Tracking
    times_applied: int = Field(default=0, ge=0, description="Number of times pattern was applied")
    times_accepted: int = Field(default=0, ge=0, description="Number of times application was accepted")
    times_rejected: int = Field(default=0, ge=0, description="Number of times application was rejected")

    @validator('pattern_type')
    def validate_pattern_type(cls, v):
        valid_types = [
            'berth_preference',
            'service_preference',
            'timing_preference',
            'duration_pattern',
            'electricity_preference',
            'language_preference'
        ]
        if v not in valid_types:
            raise ValueError(f'Pattern type must be one of: {", ".join(valid_types)}')
        return v

    @validator('occurrence_count', 'times_applied', 'times_accepted', 'times_rejected')
    def validate_counts(cls, v):
        if v < 0:
            raise ValueError('Count values must be non-negative')
        return v

    @validator('times_applied')
    def validate_times_applied(cls, v, values):
        if 'times_accepted' in values and 'times_rejected' in values:
            total = values['times_accepted'] + values['times_rejected']
            if v < total:
                raise ValueError('Times applied must be >= times_accepted + times_rejected')
        return v


class SEALLearningCreate(SEALLearningBase):
    """Schema for creating a new SEAL learning entry (POST request)"""
    pass


class SEALLearningResponse(SEALLearningBase):
    """Schema for SEAL learning responses from database (GET request)"""
    id: int = Field(..., description="SEAL Learning ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
