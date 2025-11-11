"""
Vessel model - Boats and yachts
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class VesselType(str, enum.Enum):
    """Type of vessel"""
    SAILBOAT = "sailboat"
    MOTORBOAT = "motorboat"
    CATAMARAN = "catamaran"
    YACHT = "yacht"
    SUPERYACHT = "superyacht"


class Vessel(Base):
    """
    Vessel (Tekne/Yat) - Boats and yachts registered in the marina

    Represents vessels that use the marina.
    Each vessel belongs to a customer.
    """
    __tablename__ = "vessels"

    id = Column(Integer, primary_key=True, index=True)

    # Owner
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Vessel Identification
    name = Column(String(200), nullable=False, index=True)
    registration_number = Column(String(100), unique=True, nullable=False)  # TC number or IMO
    flag_country = Column(String(100), nullable=False, default="Turkey")

    # Vessel Specifications
    vessel_type = Column(SQLEnum(VesselType), nullable=False)
    length_meters = Column(Float, nullable=False)
    width_meters = Column(Float, nullable=False)
    draft_meters = Column(Float, nullable=False)  # Draft/keel depth
    weight_tons = Column(Float, nullable=True)

    # Build Information
    manufacturer = Column(String(200), nullable=True)
    model = Column(String(200), nullable=True)
    year_built = Column(Integer, nullable=True)

    # Insurance (Article E.2.1 compliance)
    insurance_company = Column(String(200), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_expiry_date = Column(DateTime(timezone=True), nullable=True)

    # Technical Specifications
    engine_type = Column(String(100), nullable=True)
    fuel_capacity_liters = Column(Float, nullable=True)
    water_capacity_liters = Column(Float, nullable=True)

    # Metadata
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("Customer", backref="vessels")

    def __repr__(self):
        return f"<Vessel {self.name} - {self.registration_number}>"
