"""
Invoice model - Parasut e-invoices
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Invoice payment status"""
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    """
    Invoice (Fatura) - Parasut e-invoice integration

    Represents invoices for marina services.
    Integrated with Parasut Turkish e-invoice system.
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Invoice Details
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Amounts (in EUR)
    subtotal_eur = Column(Float, nullable=False)
    tax_amount_eur = Column(Float, nullable=False, default=0.0)  # KDV/VAT
    total_amount_eur = Column(Float, nullable=False)

    # Status
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, index=True)

    # Payment
    payment_method = Column(String(50), nullable=True)  # cash, card, bank_transfer
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Parasut Integration
    parasut_invoice_id = Column(String(100), nullable=True, unique=True)
    parasut_url = Column(String(500), nullable=True)

    # Line Items (JSON)
    line_items = Column(Text, nullable=True)  # JSON array of invoice items

    # Metadata
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", backref="invoices")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.total_amount_eur} EUR>"
