"""
Permit model - Hot work and special permits
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PermitType(str, enum.Enum):
    """Type of permit"""
    HOT_WORK = "hot_work"  # Article E.5.5 (welding, grinding, etc.)
    CRANE_OPERATION = "crane_operation"
    DIVING = "diving"
    PAINTING = "painting"
    ENGINE_WORK = "engine_work"
    SPECIAL_EVENT = "special_event"


class PermitStatus(str, enum.Enum):
    """Status of permit"""
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Permit(Base):
    """
    Permit (İzin) - Work permits for marina operations

    Tracks permits required by WIM regulations.
    Hot work permits (Article E.5.5) require special approval.
    """
    __tablename__ = "permits"

    id = Column(Integer, primary_key=True, index=True)

    # Permit Details
    permit_number = Column(String(50), unique=True, nullable=False, index=True)
    permit_type = Column(SQLEnum(PermitType), nullable=False, index=True)

    # Requestor
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Work Description
    work_type = Column(String(200), nullable=False)
    work_description = Column(Text, nullable=False)
    work_location = Column(String(200), nullable=True)  # Berth number or area

    # Fire Prevention (for hot work - Article E.5.5)
    fire_prevention_measures = Column(Text, nullable=True)
    fire_watch_assigned = Column(String(200), nullable=True)
    extinguishers_positioned = Column(Integer, default=False)
    surrounding_notified = Column(Integer, default=False)

    # Timing
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    actual_completion = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(SQLEnum(PermitStatus), default=PermitStatus.REQUESTED, index=True)

    # Approval
    approved_by = Column(String(200), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Safety
    safety_briefing_completed = Column(Integer, default=False)
    insurance_verified = Column(Integer, default=False)

    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vessel = relationship("Vessel", backref="permits")
    customer = relationship("Customer", backref="permits")

    def __repr__(self):
        return f"<Permit {self.permit_number} - {self.permit_type}>"
