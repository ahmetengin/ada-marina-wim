"""
SEAL Learning model - Self-learning patterns
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SEALLearning(Base):
    """
    SEAL Learning (SEAL Öğrenme) - Self-learning patterns

    Tracks learned patterns from customer behavior.
    Used by SHIP agent to improve PLAN agent decisions.

    Example: "Psedelia always prefers Berth B-12"
    """
    __tablename__ = "seal_learning"

    id = Column(Integer, primary_key=True, index=True)

    # Pattern Identification
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=True, index=True)

    # Pattern Type
    pattern_type = Column(String(100), nullable=False, index=True)
    # Types: "berth_preference", "service_preference", "timing_preference", "duration_pattern"

    # Pattern Details
    pattern_description = Column(Text, nullable=False)
    # Example: "Always requests Berth B-12", "Prefers 380V electricity", "Usually stays 3-4 nights"

    # Statistical Confidence
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    occurrence_count = Column(Integer, default=1)  # How many times observed
    last_observed_at = Column(DateTime(timezone=True), nullable=False)

    # Learned Parameters (JSON)
    learned_parameters = Column(Text, nullable=True)
    # Example: {"preferred_berth": "B-12", "confidence": 0.95, "times_requested": 5}

    # Reward Signal (for reinforcement learning)
    reward_score = Column(Float, nullable=True)  # 0.0 to 1.0
    # Based on customer satisfaction, no-shows, complaints, etc.

    # Application Status
    is_active = Column(Integer, default=True)
    auto_apply = Column(Integer, default=False)  # Auto-suggest when confidence > threshold

    # Performance Tracking
    times_applied = Column(Integer, default=0)
    times_accepted = Column(Integer, default=0)
    times_rejected = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", backref="seal_patterns")
    vessel = relationship("Vessel", backref="seal_patterns")

    def __repr__(self):
        return f"<SEALLearning Customer:{self.customer_id} - {self.pattern_type} ({self.confidence_score:.2f})>"
