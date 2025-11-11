"""
Berth Assignment model - Links vessels to berths
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class AssignmentStatus(str, enum.Enum):
    """Status of berth assignment"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BerthAssignment(Base):
    """
    Berth Assignment (İskele Ataması) - Assignment of vessel to berth

    Tracks which vessel is assigned to which berth and for how long.
    Includes check-in/check-out times and billing information.
    """
    __tablename__ = "berth_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # References
    berth_id = Column(Integer, ForeignKey("berths.id"), nullable=False, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Timing
    check_in = Column(DateTime(timezone=True), nullable=False)
    expected_check_out = Column(DateTime(timezone=True), nullable=False)
    actual_check_out = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ACTIVE, index=True)

    # Services requested
    electricity_requested = Column(Integer, nullable=True)  # 220V or 380V
    water_requested = Column(Integer, default=True)
    wifi_requested = Column(Integer, default=True)

    # Billing
    daily_rate_eur = Column(Float, nullable=False)
    total_days = Column(Integer, nullable=False)
    total_amount_eur = Column(Float, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # VHF Communication
    vhf_log_id = Column(Integer, ForeignKey("vhf_logs.id"), nullable=True)

    # SEAL Learning
    # This tracks if this was a SEAL-predicted assignment
    was_seal_predicted = Column(Integer, default=False)
    seal_confidence_score = Column(Float, nullable=True)

    # Metadata
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    berth = relationship("Berth", backref="assignments")
    vessel = relationship("Vessel", backref="assignments")
    customer = relationship("Customer", backref="assignments")

    def __repr__(self):
        return f"<BerthAssignment Vessel:{self.vessel_id} → Berth:{self.berth_id}>"
