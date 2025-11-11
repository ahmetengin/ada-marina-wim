"""
Pydantic schemas for Berth model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class BerthSection(str, Enum):
    """Berth sections based on vessel size"""
    A = "A"  # 10-15m
    B = "B"  # 12-18m
    C = "C"  # 15-25m
    D = "D"  # 20-35m
    E = "E"  # 30-50m (super yachts)
    F = "F"  # Dry storage


class BerthStatus(str, Enum):
    """Berth occupancy status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class BerthBase(BaseModel):
    """Base schema with common berth fields"""
    berth_number: str = Field(..., min_length=1, max_length=10, description="Berth identifier (e.g., A-01)")
    section: BerthSection = Field(..., description="Berth section (A-F)")

    # Berth specifications
    length_meters: float = Field(..., gt=0, description="Maximum vessel length in meters")
    width_meters: float = Field(..., gt=0, description="Berth width in meters")
    depth_meters: float = Field(..., gt=0, description="Water depth in meters")

    # Services available
    has_electricity: bool = Field(default=True, description="Electricity availability")
    has_water: bool = Field(default=True, description="Water availability")
    electricity_voltage: int = Field(default=220, description="Electricity voltage (220V or 380V)")
    has_wifi: bool = Field(default=True, description="WiFi availability")

    # Status
    status: BerthStatus = Field(default=BerthStatus.AVAILABLE, description="Current berth status")

    # Pricing
    daily_rate_eur: float = Field(..., ge=0, description="Daily rate in EUR")

    # Location
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")

    # Notes
    notes: Optional[str] = Field(default=None, max_length=500, description="Additional notes")

    @validator('electricity_voltage')
    def validate_voltage(cls, v):
        if v not in [220, 380]:
            raise ValueError('Voltage must be 220V or 380V')
        return v


class BerthCreate(BerthBase):
    """Schema for creating a new berth (POST request)"""
    pass


class BerthUpdate(BaseModel):
    """Schema for updating a berth (PUT/PATCH request)"""
    berth_number: Optional[str] = Field(default=None, max_length=10)
    section: Optional[BerthSection] = None
    length_meters: Optional[float] = Field(default=None, gt=0)
    width_meters: Optional[float] = Field(default=None, gt=0)
    depth_meters: Optional[float] = Field(default=None, gt=0)
    has_electricity: Optional[bool] = None
    has_water: Optional[bool] = None
    electricity_voltage: Optional[int] = None
    has_wifi: Optional[bool] = None
    status: Optional[BerthStatus] = None
    daily_rate_eur: Optional[float] = Field(default=None, ge=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    @validator('electricity_voltage')
    def validate_voltage(cls, v):
        if v is not None and v not in [220, 380]:
            raise ValueError('Voltage must be 220V or 380V')
        return v


class BerthResponse(BerthBase):
    """Schema for berth responses from database (GET request)"""
    id: int = Field(..., description="Berth ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
