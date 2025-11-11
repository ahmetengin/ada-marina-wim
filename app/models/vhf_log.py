"""
VHF Log model - VHF radio communications
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class VHFDirection(str, enum.Enum):
    """Direction of VHF communication"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class VHFIntent(str, enum.Enum):
    """Parsed intent from VHF communication"""
    RESERVATION = "reservation_create"
    BERTH_INQUIRY = "berth_inquiry"
    SERVICE_REQUEST = "service_request"
    ARRIVAL_NOTIFICATION = "arrival_notification"
    DEPARTURE_NOTIFICATION = "departure_notification"
    EMERGENCY = "emergency"
    GENERAL_INQUIRY = "general_inquiry"


class VHFLog(Base):
    """
    VHF Log (VHF İletişim Kaydı) - VHF Channel 72 communications

    Aviation-style VHF communication logging.
    Captures voice commands and system responses for compliance and audit.
    """
    __tablename__ = "vhf_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Communication Details
    channel = Column(Integer, default=72, nullable=False)
    frequency = Column(String(20), default="156.625", nullable=False)
    direction = Column(SQLEnum(VHFDirection), nullable=False)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Content
    vessel_name = Column(String(200), nullable=True, index=True)
    caller_id = Column(String(100), nullable=True)
    message_text = Column(Text, nullable=False)
    language_detected = Column(String(2), default="tr")  # tr, en, el

    # AI Processing (SCOUT Agent)
    intent_parsed = Column(SQLEnum(VHFIntent), nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    entities_extracted = Column(Text, nullable=True)  # JSON string

    # Response
    response_text = Column(Text, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)

    # Processing Status
    was_processed = Column(Integer, default=False)
    resulted_in_assignment = Column(Integer, default=False)
    assignment_id = Column(Integer, nullable=True)  # Link to berth_assignments.id

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<VHFLog Ch{self.channel} - {self.vessel_name} - {self.intent_parsed}>"
