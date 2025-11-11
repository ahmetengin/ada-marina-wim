"""
Customer model - Yacht owners and marina customers
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """
    Customer (Müşteri) - Yacht owner or boat captain

    Represents individuals or companies that use the marina.
    Includes both Turkish and international customers.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Personal/Company Information
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=False)

    # Turkish ID or Passport
    tc_kimlik = Column(String(11), unique=True, nullable=True)  # Turkish ID (11 digits)
    passport_number = Column(String(50), unique=True, nullable=True)

    # Address
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Turkey")

    # Company (if applicable)
    is_company = Column(Boolean, default=False)
    company_name = Column(String(200), nullable=True)
    tax_number = Column(String(50), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)

    # Preferences (for SEAL learning)
    preferred_language = Column(String(2), default="tr")  # tr, en, el
    preferred_berth_section = Column(String(1), nullable=True)  # A-F

    # Account Status
    is_active = Column(Boolean, default=True)
    is_vip = Column(Boolean, default=False)

    # Parasut Customer ID (for invoicing)
    parasut_customer_id = Column(String(100), nullable=True)

    # Metadata
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Customer {self.name} - {self.email}>"
