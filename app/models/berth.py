"""
Berth model - Marina berth/slip management
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BerthSection(str, enum.Enum):
    """Berth sections based on vessel size"""
    A = "A"  # 10-15m
    B = "B"  # 12-18m
    C = "C"  # 15-25m
    D = "D"  # 20-35m
    E = "E"  # 30-50m (super yachts)
    F = "F"  # Dry storage


class BerthStatus(str, enum.Enum):
    """Berth occupancy status"""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class Berth(Base):
    """
    Berth (İskele Yeri) - Individual boat slip

    Represents physical berths in the marina, organized by sections.
    Total: 600 berths across 6 sections (A-F).
    """
    __tablename__ = "berths"

    id = Column(Integer, primary_key=True, index=True)
    berth_number = Column(String(10), unique=True, nullable=False, index=True)  # e.g., "A-01", "B-12"
    section = Column(SQLEnum(BerthSection), nullable=False, index=True)

    # Berth specifications
    length_meters = Column(Float, nullable=False)  # Max vessel length
    width_meters = Column(Float, nullable=False)   # Berth width
    depth_meters = Column(Float, nullable=False)   # Water depth

    # Services available
    has_electricity = Column(Boolean, default=True)
    has_water = Column(Boolean, default=True)
    electricity_voltage = Column(Integer, default=220)  # 220V or 380V
    has_wifi = Column(Boolean, default=True)

    # Status
    status = Column(SQLEnum(BerthStatus), default=BerthStatus.AVAILABLE, index=True)

    # Pricing (EUR per night)
    daily_rate_eur = Column(Float, nullable=False)

    # Location coordinates within marina
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Metadata
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Berth {self.berth_number} - {self.status}>"
