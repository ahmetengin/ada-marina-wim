"""
Coast Guard Service
Sahil Güvenlik Komutanlığı bilgileri ve entegrasyonu
https://www.sg.gov.tr
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.coast_guard_info import (
    CoastGuardContact,
    MaritimeTerminology,
    CoastGuardIncident
)
from app.schemas.coast_guard import (
    CoastGuardContactCreate,
    MaritimeTerminologyCreate,
    CoastGuardIncidentCreate
)

logger = logging.getLogger(__name__)


class CoastGuardService:
    """
    Turkish Coast Guard (Sahil Güvenlik) Service

    Provides:
    - Emergency contact information
    - Maritime terminology (Denizci Dili)
    - Incident reporting and tracking
    - Regional command contacts
    - VHF communication support
    """

    # Emergency contacts
    EMERGENCY_NUMBER = "158"
    INTERNATIONAL_VHF = "16"
    MARINA_VHF = "72"

    # Regional commands for Turkish coasts
    REGIONAL_COMMANDS = {
        "karadeniz": {
            "name": "Karadeniz Bölge Komutanlığı",
            "name_en": "Black Sea Regional Command",
            "region": "Karadeniz",
            "coverage": "Black Sea coast",
        },
        "marmara": {
            "name": "Marmara Bölge Komutanlığı",
            "name_en": "Marmara Regional Command",
            "region": "Marmara",
            "coverage": "Sea of Marmara, Istanbul Strait",
        },
        "ege": {
            "name": "Ege Deniz Bölge Komutanlığı",
            "name_en": "Aegean Sea Regional Command",
            "region": "Ege",
            "coverage": "Aegean Sea coast",
        },
        "akdeniz": {
            "name": "Akdeniz Bölge Komutanlığı",
            "name_en": "Mediterranean Regional Command",
            "region": "Akdeniz",
            "coverage": "Mediterranean coast",
        }
    }

    def __init__(self):
        pass

    def initialize_regional_contacts(self, db: Session) -> List[CoastGuardContact]:
        """
        Initialize regional Coast Guard contacts in database

        Creates entries for all regional commands if they don't exist.

        Args:
            db: Database session

        Returns:
            List of created/updated contacts
        """
        contacts = []

        for key, info in self.REGIONAL_COMMANDS.items():
            # Check if exists
            existing = db.query(CoastGuardContact).filter(
                CoastGuardContact.region_name == info["region"]
            ).first()

            if not existing:
                contact = CoastGuardContact(
                    region_name=info["region"],
                    command_type="Bölge",
                    emergency_number=self.EMERGENCY_NUMBER,
                    vhf_channel=self.INTERNATIONAL_VHF,
                    website="https://www.sg.gov.tr",
                    coverage_area=info["coverage"],
                    is_active=True,
                    is_24_7=True,
                    notes=info["name_en"]
                )
                db.add(contact)
                contacts.append(contact)
                logger.info(f"Created Coast Guard contact for {info['region']}")

        if contacts:
            db.commit()
            for contact in contacts:
                db.refresh(contact)

        return contacts

    def get_regional_contact(
        self,
        db: Session,
        region: str = "Marmara"
    ) -> Optional[CoastGuardContact]:
        """
        Get Coast Guard contact for specific region

        Args:
            db: Database session
            region: Region name (Marmara, Ege, etc.)

        Returns:
            CoastGuardContact or None
        """
        return db.query(CoastGuardContact).filter(
            CoastGuardContact.region_name == region,
            CoastGuardContact.is_active == True
        ).first()

    def get_all_contacts(self, db: Session) -> List[CoastGuardContact]:
        """Get all active Coast Guard contacts"""
        return db.query(CoastGuardContact).filter(
            CoastGuardContact.is_active == True
        ).order_by(CoastGuardContact.region_name).all()

    def add_maritime_term(
        self,
        db: Session,
        term_data: MaritimeTerminologyCreate
    ) -> MaritimeTerminology:
        """
        Add maritime terminology to database

        Args:
            db: Database session
            term_data: Maritime term data

        Returns:
            Created MaritimeTerminology
        """
        term = MaritimeTerminology(**term_data.model_dump())
        db.add(term)
        db.commit()
        db.refresh(term)

        logger.info(f"Added maritime term: {term.term_turkish}")
        return term

    def search_maritime_terms(
        self,
        db: Session,
        search_query: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[MaritimeTerminology]:
        """
        Search maritime terminology

        Args:
            db: Database session
            search_query: Search text (Turkish or English)
            category: Filter by category
            limit: Max results

        Returns:
            List of matching terms
        """
        query = db.query(MaritimeTerminology)

        # Search in Turkish and English terms and definitions
        search_filter = (
            MaritimeTerminology.term_turkish.ilike(f"%{search_query}%") |
            MaritimeTerminology.term_english.ilike(f"%{search_query}%") |
            MaritimeTerminology.definition_turkish.ilike(f"%{search_query}%")
        )
        query = query.filter(search_filter)

        if category:
            query = query.filter(MaritimeTerminology.category == category)

        return query.limit(limit).all()

    def get_vhf_commands(self, db: Session) -> List[MaritimeTerminology]:
        """
        Get all VHF radio command terms

        Returns terms commonly used in VHF marine radio communication

        Args:
            db: Database session

        Returns:
            List of VHF command terms
        """
        return db.query(MaritimeTerminology).filter(
            MaritimeTerminology.is_vhf_command == True
        ).order_by(MaritimeTerminology.term_turkish).all()

    def report_incident(
        self,
        db: Session,
        incident_data: CoastGuardIncidentCreate
    ) -> CoastGuardIncident:
        """
        Report incident to Coast Guard

        Creates incident record and marks it for Coast Guard notification

        Args:
            db: Database session
            incident_data: Incident details

        Returns:
            Created CoastGuardIncident
        """
        incident = CoastGuardIncident(**incident_data.model_dump())
        incident.reported_time = datetime.utcnow()

        db.add(incident)
        db.commit()
        db.refresh(incident)

        logger.info(f"Created Coast Guard incident report: {incident.incident_type}")

        # In production, this would trigger actual notification
        # via VHF, phone, or electronic system
        if incident.coast_guard_notified:
            logger.warning(f"Coast Guard notification required for incident {incident.id}")

        return incident

    def update_incident_status(
        self,
        db: Session,
        incident_id: int,
        status: str,
        resolution: Optional[str] = None,
        coast_guard_reference: Optional[str] = None
    ) -> CoastGuardIncident:
        """
        Update incident status

        Args:
            db: Database session
            incident_id: Incident ID
            status: New status
            resolution: Resolution details
            coast_guard_reference: Coast Guard reference number

        Returns:
            Updated incident
        """
        incident = db.query(CoastGuardIncident).filter(
            CoastGuardIncident.id == incident_id
        ).first()

        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        incident.status = status
        if resolution:
            incident.resolution = resolution
        if coast_guard_reference:
            incident.coast_guard_reference = coast_guard_reference

        if status == "resolved" or status == "closed":
            incident.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(incident)

        logger.info(f"Updated incident {incident_id} status to {status}")
        return incident

    def get_open_incidents(self, db: Session) -> List[CoastGuardIncident]:
        """Get all open (not resolved/closed) incidents"""
        return db.query(CoastGuardIncident).filter(
            CoastGuardIncident.status.in_(["reported", "investigating"])
        ).order_by(CoastGuardIncident.incident_time.desc()).all()

    def get_incident_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get incident statistics

        Returns:
            Dictionary with statistics
        """
        total = db.query(func.count(CoastGuardIncident.id)).scalar()

        by_type = db.query(
            CoastGuardIncident.incident_type,
            func.count(CoastGuardIncident.id)
        ).group_by(CoastGuardIncident.incident_type).all()

        by_severity = db.query(
            CoastGuardIncident.severity,
            func.count(CoastGuardIncident.id)
        ).group_by(CoastGuardIncident.severity).all()

        open_count = db.query(func.count(CoastGuardIncident.id)).filter(
            CoastGuardIncident.status.in_(["reported", "investigating"])
        ).scalar()

        resolved_count = db.query(func.count(CoastGuardIncident.id)).filter(
            CoastGuardIncident.status.in_(["resolved", "closed"])
        ).scalar()

        # Average response time (only for notified incidents)
        avg_response = db.query(
            func.avg(CoastGuardIncident.response_time_minutes)
        ).filter(
            CoastGuardIncident.coast_guard_notified == True,
            CoastGuardIncident.response_time_minutes.isnot(None)
        ).scalar()

        return {
            "total_incidents": total or 0,
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "open_incidents": open_count or 0,
            "resolved_incidents": resolved_count or 0,
            "average_response_time_minutes": float(avg_response) if avg_response else None
        }

    def get_emergency_info(self) -> Dict[str, Any]:
        """
        Get emergency contact information

        Returns:
            Dictionary with emergency procedures and contacts
        """
        return {
            "emergency_number": self.EMERGENCY_NUMBER,
            "international_vhf": self.INTERNATIONAL_VHF,
            "marina_vhf": self.MARINA_VHF,
            "website": "https://www.sg.gov.tr",
            "procedures": [
                "1. Durumu değerlendirin (Assess the situation)",
                "2. 158'i arayın veya VHF Channel 16'yı kullanın",
                "3. Lokasyonunuzu net bir şekilde bildirin",
                "4. Olay türünü ve ciddiyetini açıklayın",
                "5. Yaralı veya kayıp varsa bildirin",
                "6. Marina operasyon merkezini bilgilendirin",
                "7. Sahil Güvenlik talimatlarını bekleyin ve uygulayın"
            ],
            "what_to_report": [
                "Deniz kazaları",
                "Şüpheli aktiviteler",
                "Petrol ve kimyasal sızıntılar",
                "Kayıp tekneler veya kişiler",
                "Denizde sıkıntıdaki tekneler",
                "Güvenlik tehditleri"
            ],
            "information_to_provide": [
                "Lokasyon (koordinatlar veya landmark)",
                "Tekne adı ve kayıt numarası",
                "Olay türü ve zamanı",
                "Yaralı sayısı",
                "Hava durumu ve deniz durumu",
                "İletişim bilgileri"
            ]
        }
