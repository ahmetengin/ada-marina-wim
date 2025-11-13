"""
Maritime Services API Endpoints
Weather, sea conditions, and Coast Guard integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.services.maritime_service import MaritimeService
from app.services.coast_guard_service import CoastGuardService
from app.schemas.maritime_weather import (
    MaritimeWeatherResponse,
    MaritimeWeatherCreate,
    MaritimeCurrentsResponse,
    MaritimeCurrentsCreate,
    MarinaWeatherDashboard,
    WeatherSummary
)
from app.schemas.coast_guard import (
    CoastGuardContactResponse,
    CoastGuardContactCreate,
    MaritimeTerminologyResponse,
    MaritimeTerminologyCreate,
    CoastGuardIncidentResponse,
    CoastGuardIncidentCreate,
    CoastGuardEmergencyInfo,
    MaritimeTermDictionary,
    IncidentStatistics
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
maritime_service = MaritimeService()
coast_guard_service = CoastGuardService()


# ==================== WEATHER & SEA CONDITIONS ====================

@router.get("/dashboard", response_model=MarinaWeatherDashboard)
async def get_weather_dashboard(
    db: Session = Depends(get_db)
):
    """
    🌊 Get complete maritime weather dashboard

    Provides comprehensive weather and sea conditions from:
    - Piri Reis (Turkish Meteorological Service)
    - Poseidon HCMR (Hellenic Centre for Marine Research)

    Includes:
    - Current conditions
    - 24-hour and 5-day forecasts
    - Safety assessments
    - Departure/arrival recommendations
    """
    try:
        dashboard = maritime_service.get_weather_dashboard(db)
        return dashboard
    except Exception as e:
        logger.error(f"Error fetching weather dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather dashboard: {str(e)}")


@router.get("/weather/summary", response_model=WeatherSummary)
async def get_weather_summary(
    db: Session = Depends(get_db)
):
    """
    ☀️ Get weather summary

    Concise summary of current and forecast weather conditions
    """
    try:
        summary = maritime_service.get_weather_summary(db)
        return summary
    except Exception as e:
        logger.error(f"Error fetching weather summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/piri-reis", response_model=MaritimeWeatherResponse)
async def create_piri_reis_forecast(
    region: str = Query("Marmara", description="Region name"),
    wind_direction: Optional[str] = Query(None, description="Wind direction (e.g., 'NE', 'Poyraz')"),
    wind_speed_knots: Optional[float] = Query(None, ge=0, le=200, description="Wind speed in knots"),
    wave_height_meters: Optional[float] = Query(None, ge=0, le=30, description="Wave height in meters"),
    visibility_km: Optional[float] = Query(None, ge=0, le=100, description="Visibility in km"),
    weather_description: Optional[str] = Query(None, description="Weather description"),
    forecast_hours: int = Query(24, ge=1, le=168, description="Forecast duration in hours"),
    db: Session = Depends(get_db)
):
    """
    📝 Manually create Piri Reis forecast

    Use this to manually enter weather data from https://pirireis.mgm.gov.tr
    when automatic API access is not available.

    Data should be copied from the official Piri Reis website.
    """
    try:
        forecast = maritime_service.piri_reis.create_manual_forecast(
            db=db,
            region=region,
            wind_direction=wind_direction,
            wind_speed_knots=wind_speed_knots,
            wave_height_meters=wave_height_meters,
            visibility_km=visibility_km,
            weather_description=weather_description,
            forecast_hours=forecast_hours
        )
        logger.info(f"Created Piri Reis forecast for {region}")
        return forecast
    except Exception as e:
        logger.error(f"Error creating Piri Reis forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather/poseidon", response_model=MaritimeWeatherResponse)
async def create_poseidon_forecast(
    region: str = Query("North Aegean", description="Region name"),
    latitude: float = Query(40.9867, ge=-90, le=90, description="Latitude"),
    longitude: float = Query(28.7864, ge=-180, le=180, description="Longitude"),
    wind_speed_knots: Optional[float] = Query(None, ge=0, le=200),
    wind_direction: Optional[str] = Query(None),
    wave_height_meters: Optional[float] = Query(None, ge=0, le=30),
    wave_direction: Optional[str] = Query(None),
    wave_period_seconds: Optional[float] = Query(None, ge=0, le=30),
    water_temp_celsius: Optional[float] = Query(None, ge=-5, le=40),
    forecast_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    📝 Manually create Poseidon forecast

    Use this to manually enter data from https://poseidon.hcmr.gr
    when automatic API access is not available.

    Poseidon provides high-resolution forecasts for Aegean and Mediterranean.
    """
    try:
        forecast = maritime_service.poseidon.create_manual_forecast(
            db=db,
            region=region,
            latitude=latitude,
            longitude=longitude,
            wind_speed_knots=wind_speed_knots,
            wind_direction=wind_direction,
            wave_height_meters=wave_height_meters,
            wave_direction=wave_direction,
            wave_period_seconds=wave_period_seconds,
            water_temp_celsius=water_temp_celsius,
            forecast_hours=forecast_hours
        )
        logger.info(f"Created Poseidon forecast for {region}")
        return forecast
    except Exception as e:
        logger.error(f"Error creating Poseidon forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/currents/poseidon", response_model=MaritimeCurrentsResponse)
async def create_poseidon_currents(
    region: str = Query("North Aegean", description="Region name"),
    latitude: float = Query(40.9867, ge=-90, le=90),
    longitude: float = Query(28.7864, ge=-180, le=180),
    current_speed_knots: Optional[float] = Query(None, ge=0, le=20),
    current_direction: Optional[str] = Query(None),
    water_temp_celsius: Optional[float] = Query(None, ge=-5, le=40),
    salinity_psu: Optional[float] = Query(None, ge=0, le=50),
    depth_meters: Optional[float] = Query(None, ge=0),
    forecast_hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    📝 Manually create Poseidon currents forecast

    Sea currents data from Poseidon hydrodynamic model
    """
    try:
        currents = maritime_service.poseidon.create_manual_currents(
            db=db,
            region=region,
            latitude=latitude,
            longitude=longitude,
            current_speed_knots=current_speed_knots,
            current_direction=current_direction,
            water_temp_celsius=water_temp_celsius,
            salinity_psu=salinity_psu,
            depth_meters=depth_meters,
            forecast_hours=forecast_hours
        )
        logger.info(f"Created Poseidon currents for {region}")
        return currents
    except Exception as e:
        logger.error(f"Error creating Poseidon currents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/departure-check")
async def check_departure_safety(
    vessel_length_meters: float = Query(..., ge=5, le=100, description="Vessel length in meters"),
    destination_region: Optional[str] = Query(None, description="Destination region"),
    db: Session = Depends(get_db)
):
    """
    ✅ Check if it's safe for vessel to depart

    Assesses current weather and sea conditions based on vessel size.
    Provides detailed safety analysis and recommendations.

    Considers:
    - Wind speed and gusts
    - Wave height
    - Visibility
    - Sea currents
    - Storm warnings
    """
    try:
        safety_check = maritime_service.check_departure_safety(
            db=db,
            vessel_length_meters=vessel_length_meters,
            destination_region=destination_region
        )
        return safety_check
    except Exception as e:
        logger.error(f"Error checking departure safety: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COAST GUARD ====================

@router.get("/coast-guard/emergency", response_model=CoastGuardEmergencyInfo)
async def get_emergency_info():
    """
    🚨 Get Coast Guard emergency contact information

    Essential emergency procedures and contact numbers:
    - Coast Guard: 158
    - VHF Channels
    - Emergency procedures
    - What to report and how
    """
    try:
        info = coast_guard_service.get_emergency_info()
        return info
    except Exception as e:
        logger.error(f"Error fetching emergency info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coast-guard/contacts", response_model=List[CoastGuardContactResponse])
async def get_coast_guard_contacts(
    region: Optional[str] = Query(None, description="Filter by region (Marmara, Ege, etc.)"),
    db: Session = Depends(get_db)
):
    """
    📞 Get Coast Guard regional contacts

    List all Coast Guard regional commands and their contact information
    """
    try:
        if region:
            contact = coast_guard_service.get_regional_contact(db, region)
            return [contact] if contact else []
        else:
            contacts = coast_guard_service.get_all_contacts(db)
            return contacts
    except Exception as e:
        logger.error(f"Error fetching Coast Guard contacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coast-guard/contacts", response_model=CoastGuardContactResponse)
async def create_coast_guard_contact(
    contact_data: CoastGuardContactCreate,
    db: Session = Depends(get_db)
):
    """
    📝 Add Coast Guard contact information
    """
    try:
        from app.models.coast_guard_info import CoastGuardContact
        contact = CoastGuardContact(**contact_data.model_dump())
        db.add(contact)
        db.commit()
        db.refresh(contact)
        logger.info(f"Created Coast Guard contact for {contact.region_name}")
        return contact
    except Exception as e:
        logger.error(f"Error creating Coast Guard contact: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coast-guard/initialize")
async def initialize_coast_guard_data(
    db: Session = Depends(get_db)
):
    """
    🚀 Initialize Coast Guard regional contacts

    Sets up default regional command contacts for:
    - Karadeniz (Black Sea)
    - Marmara
    - Ege (Aegean)
    - Akdeniz (Mediterranean)
    """
    try:
        contacts = coast_guard_service.initialize_regional_contacts(db)
        return {
            "message": "Coast Guard contacts initialized",
            "contacts_created": len(contacts),
            "regions": [c.region_name for c in contacts]
        }
    except Exception as e:
        logger.error(f"Error initializing Coast Guard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MARITIME TERMINOLOGY ====================

@router.get("/terminology/search", response_model=List[MaritimeTerminologyResponse])
async def search_maritime_terms(
    query: str = Query(..., min_length=2, description="Search query (Turkish or English)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    db: Session = Depends(get_db)
):
    """
    🔍 Search maritime terminology dictionary

    Search Turkish-English maritime terms from Coast Guard (Denizci Dili)

    Categories include:
    - Navigation (Seyir)
    - Equipment (Donanım)
    - Signals (İşaretler)
    - Commands (Komutlar)
    """
    try:
        terms = coast_guard_service.search_maritime_terms(
            db=db,
            search_query=query,
            category=category,
            limit=limit
        )
        return terms
    except Exception as e:
        logger.error(f"Error searching maritime terms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/terminology/vhf", response_model=List[MaritimeTerminologyResponse])
async def get_vhf_commands(
    db: Session = Depends(get_db)
):
    """
    📻 Get VHF radio command terminology

    Returns maritime terms commonly used in VHF radio communication
    """
    try:
        terms = coast_guard_service.get_vhf_commands(db)
        return terms
    except Exception as e:
        logger.error(f"Error fetching VHF commands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/terminology", response_model=MaritimeTerminologyResponse)
async def add_maritime_term(
    term_data: MaritimeTerminologyCreate,
    db: Session = Depends(get_db)
):
    """
    📝 Add maritime terminology

    Add a new term to the maritime terminology dictionary
    """
    try:
        term = coast_guard_service.add_maritime_term(db, term_data)
        return term
    except Exception as e:
        logger.error(f"Error adding maritime term: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==================== INCIDENTS ====================

@router.post("/incidents", response_model=CoastGuardIncidentResponse)
async def report_incident(
    incident_data: CoastGuardIncidentCreate,
    db: Session = Depends(get_db)
):
    """
    🚨 Report incident to Coast Guard

    Create an incident report for Coast Guard notification

    Incident types:
    - emergency
    - suspicious_activity
    - pollution
    - accident
    - medical
    - fire
    - search_rescue
    """
    try:
        incident = coast_guard_service.report_incident(db, incident_data)
        return incident
    except Exception as e:
        logger.error(f"Error reporting incident: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents", response_model=List[CoastGuardIncidentResponse])
async def get_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    incident_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    📋 Get incident reports

    List Coast Guard incident reports with optional filtering
    """
    try:
        from app.models.coast_guard_info import CoastGuardIncident
        query = db.query(CoastGuardIncident)

        if status:
            query = query.filter(CoastGuardIncident.status == status)
        if incident_type:
            query = query.filter(CoastGuardIncident.incident_type == incident_type)

        incidents = query.order_by(
            CoastGuardIncident.incident_time.desc()
        ).limit(limit).all()

        return incidents
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/open", response_model=List[CoastGuardIncidentResponse])
async def get_open_incidents(
    db: Session = Depends(get_db)
):
    """
    ⚠️ Get open (unresolved) incidents

    Returns all incidents that are still reported or under investigation
    """
    try:
        incidents = coast_guard_service.get_open_incidents(db)
        return incidents
    except Exception as e:
        logger.error(f"Error fetching open incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/incidents/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    status: str = Query(..., description="New status"),
    resolution: Optional[str] = Query(None, description="Resolution details"),
    coast_guard_reference: Optional[str] = Query(None, description="Coast Guard reference number"),
    db: Session = Depends(get_db)
):
    """
    🔄 Update incident status

    Update the status of a Coast Guard incident report
    """
    try:
        incident = coast_guard_service.update_incident_status(
            db=db,
            incident_id=incident_id,
            status=status,
            resolution=resolution,
            coast_guard_reference=coast_guard_reference
        )
        return incident
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating incident status: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents/statistics", response_model=IncidentStatistics)
async def get_incident_statistics(
    db: Session = Depends(get_db)
):
    """
    📊 Get incident statistics

    Statistical overview of all Coast Guard incidents
    """
    try:
        stats = coast_guard_service.get_incident_statistics(db)
        return stats
    except Exception as e:
        logger.error(f"Error fetching incident statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
