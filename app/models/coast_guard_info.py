"""
Coast Guard Information and Maritime Terminology
Sahil Güvenlik Komutanlığı bilgileri ve denizci dili
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class CoastGuardContact(Base):
    """
    Coast Guard Contact Information
    Sahil Güvenlik iletişim bilgileri ve bölge komutanlıkları
    """
    __tablename__ = "coast_guard_contacts"

    id = Column(Integer, primary_key=True, index=True)

    # Regional command
    region_name = Column(String(100), nullable=False, index=True)  # e.g., "Marmara", "Ege", "Akdeniz"
    command_type = Column(String(50), nullable=False)  # "Bölge", "Grup", "İstasyon"

    # Contact details
    emergency_number = Column(String(20), default="158")  # Main Coast Guard emergency
    vhf_channel = Column(String(20), nullable=True)       # VHF channel for region
    phone_number = Column(String(50), nullable=True)
    fax_number = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(50), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)

    # Jurisdiction area
    coverage_area = Column(Text, nullable=True)  # Description of coverage area

    # Additional info
    website = Column(String(200), default="https://www.sg.gov.tr")
    notes = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_24_7 = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CoastGuard {self.region_name} - {self.command_type}>"


class MaritimeTerminology(Base):
    """
    Maritime Terminology Dictionary (Denizci Dili)
    Terms from Sahil Güvenlik and international maritime standards
    """
    __tablename__ = "maritime_terminology"

    id = Column(Integer, primary_key=True, index=True)

    # Term details
    term_turkish = Column(String(200), nullable=False, index=True)
    term_english = Column(String(200), nullable=True, index=True)
    term_greek = Column(String(200), nullable=True)

    # Definition
    definition_turkish = Column(Text, nullable=False)
    definition_english = Column(Text, nullable=True)

    # Category
    category = Column(String(100), nullable=True, index=True)  # e.g., "Navigation", "Equipment", "Signals"
    subcategory = Column(String(100), nullable=True)

    # Usage context
    usage_context = Column(Text, nullable=True)
    example_sentence = Column(Text, nullable=True)

    # Related terms
    related_terms = Column(JSON, nullable=True)  # Array of related term IDs
    synonyms = Column(JSON, nullable=True)

    # Source
    source = Column(String(100), default="sg.gov.tr")
    reference_url = Column(String(300), nullable=True)

    # For VHF communication
    is_vhf_command = Column(Boolean, default=False)
    vhf_usage_notes = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MaritimeTerm {self.term_turkish}>"


class CoastGuardIncident(Base):
    """
    Coast Guard Incident Reports
    Marina to Coast Guard communication log
    """
    __tablename__ = "coast_guard_incidents"

    id = Column(Integer, primary_key=True, index=True)

    # Incident details
    incident_type = Column(String(100), nullable=False, index=True)
    # Types: "emergency", "suspicious_activity", "pollution", "accident", "routine_report"

    incident_time = Column(DateTime(timezone=True), nullable=False)
    reported_time = Column(DateTime(timezone=True), server_default=func.now())

    # Location
    location_description = Column(Text, nullable=False)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    berth_number = Column(String(20), nullable=True)  # If in marina

    # Vessel involved
    vessel_name = Column(String(200), nullable=True)
    vessel_registration = Column(String(100), nullable=True)

    # Description
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical

    # Coast Guard response
    coast_guard_notified = Column(Boolean, default=False)
    notification_method = Column(String(50), nullable=True)  # "VHF", "Phone", "158", "Email"
    coast_guard_reference = Column(String(100), nullable=True)  # Their incident number
    response_time_minutes = Column(Integer, nullable=True)

    # Status
    status = Column(String(50), default="reported")  # reported, investigating, resolved, closed
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Reporter
    reported_by = Column(String(200), nullable=True)
    reporter_contact = Column(String(100), nullable=True)

    # Additional data
    attachments = Column(JSON, nullable=True)  # Photo URLs, documents
    metadata_json = Column(JSON, nullable=True)

    # Compliance tracking
    wim_regulation_article = Column(String(50), nullable=True)  # Related WIM article

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<CoastGuardIncident {self.incident_type} @ {self.incident_time}>"
