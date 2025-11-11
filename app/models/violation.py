"""
Violation model - WIM regulation violations
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ViolationSeverity(str, enum.Enum):
    """Severity level of violation"""
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ViolationStatus(str, enum.Enum):
    """Status of violation handling"""
    REPORTED = "reported"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    APPEALED = "appealed"


class Violation(Base):
    """
    Violation (İhlal) - WIM regulation violations

    Tracks violations of the 176-article WIM Operating Regulation.
    Each violation references specific article(s) violated.
    """
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)

    # Violator
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    # Violation Details
    article_violated = Column(String(20), nullable=False, index=True)  # e.g., "E.1.10", "E.5.5"
    description = Column(Text, nullable=False)

    # Severity & Status
    severity = Column(SQLEnum(ViolationSeverity), nullable=False, index=True)
    status = Column(SQLEnum(ViolationStatus), default=ViolationStatus.REPORTED)

    # Financial
    fine_amount_eur = Column(Float, nullable=True)
    fine_paid = Column(Integer, default=False)
    fine_paid_at = Column(DateTime(timezone=True), nullable=True)

    # Detection
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    detected_by = Column(String(100), nullable=True)  # "VERIFY_AGENT", "MANUAL", "SENSOR"

    # Evidence
    evidence_description = Column(Text, nullable=True)
    evidence_files = Column(Text, nullable=True)  # JSON array of file paths

    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vessel = relationship("Vessel", backref="violations")
    customer = relationship("Customer", backref="violations")

    def __repr__(self):
        return f"<Violation {self.article_violated} - {self.severity}>"
