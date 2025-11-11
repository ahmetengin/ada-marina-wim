"""
Pydantic schemas for Vessel model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class VesselType(str, Enum):
    """Type of vessel"""
    SAILBOAT = "sailboat"
    MOTORBOAT = "motorboat"
    CATAMARAN = "catamaran"
    YACHT = "yacht"
    SUPERYACHT = "superyacht"


class VesselBase(BaseModel):
    """Base schema with common vessel fields"""
    # Owner
    customer_id: int = Field(..., gt=0, description="Customer ID (vessel owner)")

    # Vessel Identification
    name: str = Field(..., min_length=1, max_length=200, description="Vessel name")
    registration_number: str = Field(..., min_length=1, max_length=100, description="Registration/IMO number")
    flag_country: str = Field(default="Turkey", max_length=100, description="Flag country")

    # Vessel Specifications
    vessel_type: VesselType = Field(..., description="Type of vessel")
    length_meters: float = Field(..., gt=0, description="Vessel length in meters")
    width_meters: float = Field(..., gt=0, description="Vessel width (beam) in meters")
    draft_meters: float = Field(..., gt=0, description="Vessel draft (keel depth) in meters")
    weight_tons: Optional[float] = Field(default=None, gt=0, description="Vessel weight in tons")

    # Build Information
    manufacturer: Optional[str] = Field(default=None, max_length=200, description="Manufacturer/builder")
    model: Optional[str] = Field(default=None, max_length=200, description="Vessel model")
    year_built: Optional[int] = Field(default=None, description="Year vessel was built")

    # Insurance (Article E.2.1 compliance)
    insurance_company: Optional[str] = Field(default=None, max_length=200, description="Insurance company")
    insurance_policy_number: Optional[str] = Field(default=None, max_length=100, description="Insurance policy number")
    insurance_expiry_date: Optional[datetime] = Field(default=None, description="Insurance expiry date")

    # Technical Specifications
    engine_type: Optional[str] = Field(default=None, max_length=100, description="Engine type (diesel, petrol, electric, etc.)")
    fuel_capacity_liters: Optional[float] = Field(default=None, gt=0, description="Fuel tank capacity in liters")
    water_capacity_liters: Optional[float] = Field(default=None, gt=0, description="Water tank capacity in liters")

    # Notes
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")

    @validator('year_built')
    def validate_year_built(cls, v):
        if v is not None and (v < 1900 or v > datetime.now().year):
            raise ValueError(f'Year built must be between 1900 and {datetime.now().year}')
        return v


class VesselCreate(VesselBase):
    """Schema for creating a new vessel (POST request)"""
    pass


class VesselUpdate(BaseModel):
    """Schema for updating a vessel (PUT/PATCH request)"""
    customer_id: Optional[int] = Field(default=None, gt=0)
    name: Optional[str] = Field(default=None, max_length=200)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    flag_country: Optional[str] = Field(default=None, max_length=100)
    vessel_type: Optional[VesselType] = None
    length_meters: Optional[float] = Field(default=None, gt=0)
    width_meters: Optional[float] = Field(default=None, gt=0)
    draft_meters: Optional[float] = Field(default=None, gt=0)
    weight_tons: Optional[float] = Field(default=None, gt=0)
    manufacturer: Optional[str] = Field(default=None, max_length=200)
    model: Optional[str] = Field(default=None, max_length=200)
    year_built: Optional[int] = None
    insurance_company: Optional[str] = Field(default=None, max_length=200)
    insurance_policy_number: Optional[str] = Field(default=None, max_length=100)
    insurance_expiry_date: Optional[datetime] = None
    engine_type: Optional[str] = Field(default=None, max_length=100)
    fuel_capacity_liters: Optional[float] = Field(default=None, gt=0)
    water_capacity_liters: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = Field(default=None, max_length=1000)

    @validator('year_built')
    def validate_year_built(cls, v):
        if v is not None and (v < 1900 or v > datetime.now().year):
            raise ValueError(f'Year built must be between 1900 and {datetime.now().year}')
        return v


class VesselResponse(VesselBase):
    """Schema for vessel responses from database (GET request)"""
    id: int = Field(..., description="Vessel ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
