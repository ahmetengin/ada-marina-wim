"""
Pydantic schemas for Customer model
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base schema with common customer fields"""
    # Personal/Company Information
    name: str = Field(..., min_length=1, max_length=200, description="Customer name or company name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., min_length=1, max_length=50, description="Phone number")

    # Turkish ID or Passport
    tc_kimlik: Optional[str] = Field(default=None, max_length=11, description="Turkish ID (11 digits)")
    passport_number: Optional[str] = Field(default=None, max_length=50, description="Passport number")

    # Address
    address: Optional[str] = Field(default=None, max_length=500, description="Street address")
    city: Optional[str] = Field(default=None, max_length=100, description="City")
    country: str = Field(default="Turkey", max_length=100, description="Country")

    # Company (if applicable)
    is_company: bool = Field(default=False, description="Is this a company customer")
    company_name: Optional[str] = Field(default=None, max_length=200, description="Company name")
    tax_number: Optional[str] = Field(default=None, max_length=50, description="Tax number")

    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(default=None, max_length=200, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=50, description="Emergency contact phone")

    # Preferences
    preferred_language: str = Field(default="tr", max_length=2, description="Preferred language (tr, en, el)")
    preferred_berth_section: Optional[str] = Field(default=None, max_length=1, description="Preferred berth section (A-F)")

    # Account Status
    is_active: bool = Field(default=True, description="Is customer account active")
    is_vip: bool = Field(default=False, description="Is VIP customer")

    # Parasut Customer ID
    parasut_customer_id: Optional[str] = Field(default=None, max_length=100, description="Parasut customer ID")

    # Notes
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")

    @validator('tc_kimlik')
    def validate_tc_kimlik(cls, v):
        if v is not None and (not v.isdigit() or len(v) != 11):
            raise ValueError('Turkish ID must be 11 digits')
        return v

    @validator('preferred_language')
    def validate_language(cls, v):
        if v not in ['tr', 'en', 'el']:
            raise ValueError('Language must be tr, en, or el')
        return v

    @validator('preferred_berth_section')
    def validate_berth_section(cls, v):
        if v is not None and v not in ['A', 'B', 'C', 'D', 'E', 'F']:
            raise ValueError('Berth section must be A-F')
        return v


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer (POST request)"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer (PUT/PATCH request)"""
    name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    tc_kimlik: Optional[str] = Field(default=None, max_length=11)
    passport_number: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    is_company: Optional[bool] = None
    company_name: Optional[str] = Field(default=None, max_length=200)
    tax_number: Optional[str] = Field(default=None, max_length=50)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=50)
    preferred_language: Optional[str] = Field(default=None, max_length=2)
    preferred_berth_section: Optional[str] = Field(default=None, max_length=1)
    is_active: Optional[bool] = None
    is_vip: Optional[bool] = None
    parasut_customer_id: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)

    @validator('tc_kimlik')
    def validate_tc_kimlik(cls, v):
        if v is not None and (not v.isdigit() or len(v) != 11):
            raise ValueError('Turkish ID must be 11 digits')
        return v

    @validator('preferred_language')
    def validate_language(cls, v):
        if v is not None and v not in ['tr', 'en', 'el']:
            raise ValueError('Language must be tr, en, or el')
        return v

    @validator('preferred_berth_section')
    def validate_berth_section(cls, v):
        if v is not None and v not in ['A', 'B', 'C', 'D', 'E', 'F']:
            raise ValueError('Berth section must be A-F')
        return v


class CustomerResponse(CustomerBase):
    """Schema for customer responses from database (GET request)"""
    id: int = Field(..., description="Customer ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
