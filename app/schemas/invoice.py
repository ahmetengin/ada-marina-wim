"""
Pydantic schemas for Invoice model
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice payment status"""
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceBase(BaseModel):
    """Base schema with common invoice fields"""
    # Customer
    customer_id: int = Field(..., gt=0, description="Customer ID")

    # Invoice Details
    invoice_number: str = Field(..., min_length=1, max_length=100, description="Unique invoice number")
    invoice_date: datetime = Field(..., description="Invoice issue date")
    due_date: datetime = Field(..., description="Payment due date")

    # Amounts (in EUR)
    subtotal_eur: float = Field(..., ge=0, description="Subtotal amount in EUR")
    tax_amount_eur: float = Field(default=0.0, ge=0, description="Tax/VAT amount in EUR")
    total_amount_eur: float = Field(..., ge=0, description="Total amount in EUR")

    # Status
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Invoice status")

    # Payment
    payment_method: Optional[str] = Field(default=None, max_length=50, description="Payment method (cash, card, bank_transfer)")
    paid_at: Optional[datetime] = Field(default=None, description="Payment timestamp")

    # Parasut Integration
    parasut_invoice_id: Optional[str] = Field(default=None, max_length=100, description="Parasut e-invoice ID")
    parasut_url: Optional[str] = Field(default=None, max_length=500, description="Parasut invoice URL")

    # Line Items
    line_items: Optional[str] = Field(default=None, description="Line items as JSON string")

    # Notes
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date must be on or after invoice date')
        return v

    @validator('total_amount_eur')
    def validate_total(cls, v, values):
        if 'subtotal_eur' in values and 'tax_amount_eur' in values:
            expected_total = values['subtotal_eur'] + values['tax_amount_eur']
            # Allow small floating point differences
            if abs(v - expected_total) > 0.01:
                raise ValueError(f'Total amount ({v}) must equal subtotal ({values["subtotal_eur"]}) + tax ({values["tax_amount_eur"]})')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v is not None and v not in ['cash', 'card', 'bank_transfer']:
            raise ValueError('Payment method must be cash, card, or bank_transfer')
        return v


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice (POST request)"""
    pass


class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses from database (GET request)"""
    id: int = Field(..., description="Invoice ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        orm_mode = True
