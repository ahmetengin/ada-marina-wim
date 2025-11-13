"""
Coast Guard Information Schemas
Sahil Güvenlik Komutanlığı bilgileri
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class CommandTypeEnum(str, Enum):
    """Coast Guard command types"""
    BOLGE = "Bölge"  # Regional Command
    GRUP = "Grup"    # Group Command
    ISTASYON = "İstasyon"  # Station


class IncidentTypeEnum(str, Enum):
    """Incident types"""
    EMERGENCY = "emergency"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLLUTION = "pollution"
    ACCIDENT = "accident"
    ROUTINE_REPORT = "routine_report"
    MEDICAL = "medical"
    FIRE = "fire"
    SEARCH_RESCUE = "search_rescue"


class IncidentSeverityEnum(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatusEnum(str, Enum):
    """Incident status"""
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CoastGuardContactBase(BaseModel):
    """Base Coast Guard contact schema"""
    region_name: str = Field(..., description="Region name (Marmara, Ege, etc.)")
    command_type: str = Field(..., description="Command type")
    emergency_number: str = "158"
    vhf_channel: Optional[str] = None
    phone_number: Optional[str] = None
    fax_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    coverage_area: Optional[str] = None
    website: str = "https://www.sg.gov.tr"
    notes: Optional[str] = None
    is_active: bool = True
    is_24_7: bool = True


class CoastGuardContactCreate(CoastGuardContactBase):
    """Schema for creating Coast Guard contact"""
    pass


class CoastGuardContactResponse(CoastGuardContactBase):
    """Schema for Coast Guard contact response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaritimeTerminologyBase(BaseModel):
    """Base maritime terminology schema"""
    term_turkish: str = Field(..., description="Turkish term")
    term_english: Optional[str] = Field(None, description="English term")
    term_greek: Optional[str] = Field(None, description="Greek term")
    definition_turkish: str = Field(..., description="Turkish definition")
    definition_english: Optional[str] = None
    category: Optional[str] = Field(None, description="Category (Navigation, Equipment, etc.)")
    subcategory: Optional[str] = None
    usage_context: Optional[str] = None
    example_sentence: Optional[str] = None
    related_terms: Optional[List[int]] = None
    synonyms: Optional[List[str]] = None
    source: str = "sg.gov.tr"
    reference_url: Optional[str] = None
    is_vhf_command: bool = False
    vhf_usage_notes: Optional[str] = None


class MaritimeTerminologyCreate(MaritimeTerminologyBase):
    """Schema for creating maritime term"""
    pass


class MaritimeTerminologyResponse(MaritimeTerminologyBase):
    """Schema for maritime term response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CoastGuardIncidentBase(BaseModel):
    """Base Coast Guard incident schema"""
    incident_type: str = Field(..., description="Type of incident")
    incident_time: datetime = Field(..., description="When incident occurred")
    location_description: str = Field(..., description="Where incident occurred")
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    berth_number: Optional[str] = None
    vessel_name: Optional[str] = None
    vessel_registration: Optional[str] = None
    description: str = Field(..., description="Detailed description")
    severity: str = "medium"
    coast_guard_notified: bool = False
    notification_method: Optional[str] = None
    coast_guard_reference: Optional[str] = None
    response_time_minutes: Optional[int] = None
    status: str = "reported"
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    reported_by: Optional[str] = None
    reporter_contact: Optional[str] = None
    attachments: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    wim_regulation_article: Optional[str] = None


class CoastGuardIncidentCreate(CoastGuardIncidentBase):
    """Schema for creating Coast Guard incident"""
    pass


class CoastGuardIncidentResponse(CoastGuardIncidentBase):
    """Schema for incident response"""
    id: int
    reported_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str
    number: str
    description: str
    is_primary: bool = False


class CoastGuardEmergencyInfo(BaseModel):
    """Emergency contact and procedure information"""
    emergency_number: str = "158"
    vhf_channel: str = "Channel 16 (International), Channel 72 (Marina)"

    contacts: List[EmergencyContact] = [
        EmergencyContact(
            name="Sahil Güvenlik Komutanlığı",
            number="158",
            description="24/7 Coast Guard Emergency Line",
            is_primary=True
        ),
        EmergencyContact(
            name="İtfaiye (Fire)",
            number="110",
            description="Fire emergency"
        ),
        EmergencyContact(
            name="Ambulans (Ambulance)",
            number="112",
            description="Medical emergency"
        ),
        EmergencyContact(
            name="Polis (Police)",
            number="155",
            description="Police emergency"
        )
    ]

    procedures: List[str] = [
        "1. Durumu değerlendirin (Assess the situation)",
        "2. 158'i arayın veya VHF Channel 16'yı kullanın",
        "3. Lokasyonunuzu bildirin (marina adı, iskele numarası)",
        "4. Olay türünü açıklayın",
        "5. Yaralı varsa bildirin",
        "6. Marina güvenliğini bilgilendirin",
        "7. Talimatları bekleyin"
    ]


class MaritimeTermDictionary(BaseModel):
    """Maritime terminology dictionary response"""
    total_terms: int
    categories: List[str]
    terms: List[MaritimeTerminologyResponse]


class IncidentStatistics(BaseModel):
    """Coast Guard incident statistics"""
    total_incidents: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    average_response_time_minutes: Optional[float] = None
    resolved_incidents: int
    pending_incidents: int
