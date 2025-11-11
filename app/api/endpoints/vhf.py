"""
VHF Communications API endpoints
Manages VHF Channel 72 communications and voice command processing
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.vhf_log import VHFLog, VHFDirection, VHFIntent
from pydantic import BaseModel, Field
import json

router = APIRouter()


# Pydantic schemas
class VHFLogBase(BaseModel):
    channel: int = 72
    frequency: str = "156.625"
    direction: VHFDirection
    vessel_name: Optional[str] = None
    caller_id: Optional[str] = None
    message_text: str
    language_detected: str = "tr"


class VHFLogCreate(VHFLogBase):
    """Schema for creating a new VHF log entry"""
    pass


class VHFProcessRequest(BaseModel):
    """Request to process a VHF message"""
    message_text: str
    vessel_name: Optional[str] = None
    caller_id: Optional[str] = None
    language: str = "tr"


class VHFLogResponse(VHFLogBase):
    """Schema for VHF log response"""
    id: int
    timestamp: datetime
    intent_parsed: Optional[VHFIntent] = None
    confidence_score: Optional[int] = None
    entities_extracted: Optional[str] = None
    response_text: Optional[str] = None
    response_time_seconds: Optional[int] = None
    was_processed: bool
    resulted_in_assignment: bool
    assignment_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VHFResponseModel(BaseModel):
    """AI-generated response to VHF message"""
    intent: VHFIntent
    confidence: float
    response_text: str
    entities: dict
    suggested_action: Optional[str] = None


@router.get("/", response_model=List[VHFLogResponse])
async def list_vhf_logs(
    direction: Optional[VHFDirection] = None,
    vessel_name: Optional[str] = None,
    intent: Optional[VHFIntent] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    language: Optional[str] = None,
    was_processed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List VHF communication logs with optional filtering

    Parameters:
    - direction: Filter by incoming/outgoing
    - vessel_name: Filter by vessel name
    - intent: Filter by parsed intent
    - from_date: Filter logs from this date
    - to_date: Filter logs until this date
    - language: Filter by detected language
    - was_processed: Filter by processing status
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    """
    query = db.query(VHFLog)

    if direction:
        query = query.filter(VHFLog.direction == direction)
    if vessel_name:
        query = query.filter(VHFLog.vessel_name.ilike(f"%{vessel_name}%"))
    if intent:
        query = query.filter(VHFLog.intent_parsed == intent)
    if from_date:
        query = query.filter(VHFLog.timestamp >= from_date)
    if to_date:
        query = query.filter(VHFLog.timestamp <= to_date)
    if language:
        query = query.filter(VHFLog.language_detected == language)
    if was_processed is not None:
        query = query.filter(VHFLog.was_processed == was_processed)

    logs = query.order_by(VHFLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/{log_id}", response_model=VHFLogResponse)
async def get_vhf_log(log_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific VHF log entry

    Parameters:
    - log_id: Unique identifier of the VHF log
    """
    log = db.query(VHFLog).filter(VHFLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail=f"VHF log {log_id} not found")
    return log


@router.post("/", response_model=VHFLogResponse, status_code=201)
async def create_vhf_log(log: VHFLogCreate, db: Session = Depends(get_db)):
    """
    Create a new VHF communication log entry

    Used by the VHF system to log all communications
    """
    db_log = VHFLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.post("/process", response_model=VHFResponseModel)
async def process_vhf_message(
    request: VHFProcessRequest,
    db: Session = Depends(get_db)
):
    """
    Process a VHF voice message using Claude AI (SCOUT Agent)

    This endpoint:
    1. Receives the transcribed VHF message
    2. Uses Claude to understand intent and extract entities
    3. Generates appropriate response
    4. Logs the communication
    5. Takes action if needed (e.g., create reservation)

    Aviation-style radio communication processing
    """
    from app.core.config import settings
    import anthropic

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Construct prompt for intent parsing
    system_prompt = """You are the SCOUT agent for ADA.MARINA West Istanbul Marina.
You process VHF Channel 72 radio communications from vessels.

Your tasks:
1. Understand the vessel's intent (reservation, berth inquiry, service request, arrival/departure, emergency)
2. Extract key entities (vessel name, length, type, dates, services needed)
3. Generate a professional, concise radio response in the same language as the message
4. Suggest system actions if applicable

Respond in JSON format with:
{
  "intent": "reservation_create|berth_inquiry|service_request|arrival_notification|departure_notification|emergency|general_inquiry",
  "confidence": 0.0-1.0,
  "response_text": "Your VHF radio response",
  "entities": {
    "vessel_name": "...",
    "vessel_length": 0.0,
    "vessel_type": "...",
    "check_in_date": "...",
    "check_out_date": "...",
    "special_requests": []
  },
  "suggested_action": "create_assignment|check_availability|send_to_port_control|..."
}"""

    user_message = f"""VHF Message received:
Language: {request.language}
Vessel: {request.vessel_name or 'Unknown'}
Message: {request.message_text}

Process this communication and provide appropriate response."""

    try:
        # Call Claude API
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Parse Claude's response
        response_content = message.content[0].text

        # Try to parse as JSON
        try:
            parsed_response = json.loads(response_content)
        except json.JSONDecodeError:
            # If not valid JSON, create a basic response
            parsed_response = {
                "intent": "general_inquiry",
                "confidence": 0.5,
                "response_text": "Marina West Istanbul, message received. Please standby.",
                "entities": {},
                "suggested_action": None
            }

        # Map string intent to enum
        intent_map = {
            "reservation_create": VHFIntent.RESERVATION,
            "berth_inquiry": VHFIntent.BERTH_INQUIRY,
            "service_request": VHFIntent.SERVICE_REQUEST,
            "arrival_notification": VHFIntent.ARRIVAL_NOTIFICATION,
            "departure_notification": VHFIntent.DEPARTURE_NOTIFICATION,
            "emergency": VHFIntent.EMERGENCY,
            "general_inquiry": VHFIntent.GENERAL_INQUIRY
        }

        intent_enum = intent_map.get(parsed_response.get("intent"), VHFIntent.GENERAL_INQUIRY)

        # Log the VHF communication
        vhf_log = VHFLog(
            direction=VHFDirection.INCOMING,
            vessel_name=request.vessel_name,
            caller_id=request.caller_id,
            message_text=request.message_text,
            language_detected=request.language,
            intent_parsed=intent_enum,
            confidence_score=int(parsed_response.get("confidence", 0.5) * 100),
            entities_extracted=json.dumps(parsed_response.get("entities", {})),
            response_text=parsed_response.get("response_text"),
            was_processed=True
        )
        db.add(vhf_log)
        db.commit()
        db.refresh(vhf_log)

        # Log the outgoing response
        response_log = VHFLog(
            direction=VHFDirection.OUTGOING,
            vessel_name=request.vessel_name,
            message_text=parsed_response.get("response_text"),
            language_detected=request.language,
            was_processed=True
        )
        db.add(response_log)
        db.commit()

        return VHFResponseModel(
            intent=intent_enum,
            confidence=parsed_response.get("confidence", 0.5),
            response_text=parsed_response.get("response_text"),
            entities=parsed_response.get("entities", {}),
            suggested_action=parsed_response.get("suggested_action")
        )

    except Exception as e:
        # Log error
        error_log = VHFLog(
            direction=VHFDirection.INCOMING,
            vessel_name=request.vessel_name,
            message_text=request.message_text,
            language_detected=request.language,
            was_processed=False
        )
        db.add(error_log)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Error processing VHF message: {str(e)}"
        )


@router.get("/statistics/summary")
async def get_vhf_statistics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get VHF communication statistics

    Returns counts by intent, language, and processing status
    """
    query = db.query(VHFLog)

    if from_date:
        query = query.filter(VHFLog.timestamp >= from_date)
    if to_date:
        query = query.filter(VHFLog.timestamp <= to_date)

    total_messages = query.count()
    incoming = query.filter(VHFLog.direction == VHFDirection.INCOMING).count()
    outgoing = query.filter(VHFLog.direction == VHFDirection.OUTGOING).count()
    processed = query.filter(VHFLog.was_processed == True).count()
    resulted_in_assignment = query.filter(VHFLog.resulted_in_assignment == True).count()

    # Messages by intent
    intents = {}
    for intent in VHFIntent:
        count = query.filter(VHFLog.intent_parsed == intent).count()
        intents[intent.value] = count

    # Messages by language
    languages = {}
    lang_stats = db.query(
        VHFLog.language_detected,
        func.count(VHFLog.id).label('count')
    ).group_by(VHFLog.language_detected).all()

    for lang, count in lang_stats:
        languages[lang] = count

    # Average confidence score
    avg_confidence = db.query(func.avg(VHFLog.confidence_score)).filter(
        VHFLog.confidence_score.isnot(None)
    ).scalar() or 0

    # Average response time
    avg_response_time = db.query(func.avg(VHFLog.response_time_seconds)).filter(
        VHFLog.response_time_seconds.isnot(None)
    ).scalar() or 0

    return {
        "total_messages": total_messages,
        "incoming": incoming,
        "outgoing": outgoing,
        "processed": processed,
        "processing_rate": round(processed / total_messages * 100, 2) if total_messages > 0 else 0,
        "resulted_in_assignment": resulted_in_assignment,
        "conversion_rate": round(resulted_in_assignment / incoming * 100, 2) if incoming > 0 else 0,
        "by_intent": intents,
        "by_language": languages,
        "avg_confidence_score": round(avg_confidence, 2),
        "avg_response_time_seconds": round(avg_response_time, 2)
    }


@router.get("/recent/incoming")
async def get_recent_incoming(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent incoming VHF messages

    Useful for monitoring and quick review
    """
    logs = db.query(VHFLog).filter(
        VHFLog.direction == VHFDirection.INCOMING
    ).order_by(VHFLog.timestamp.desc()).limit(limit).all()

    return {
        "count": len(logs),
        "messages": logs
    }


@router.get("/emergency/all")
async def get_emergency_messages(db: Session = Depends(get_db)):
    """
    Get all emergency VHF communications

    Critical for safety monitoring and response
    """
    logs = db.query(VHFLog).filter(
        VHFLog.intent_parsed == VHFIntent.EMERGENCY
    ).order_by(VHFLog.timestamp.desc()).all()

    return {
        "total_emergencies": len(logs),
        "messages": logs
    }
