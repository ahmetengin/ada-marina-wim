"""
SCOUT Agent - VHF Monitoring and Voice Command Processing
Part of the Big-5 Agents architecture for ADA.MARINA

Responsibilities:
- Monitor VHF Channel 72 (156.625 MHz)
- Process voice commands in TR/EN/EL languages
- Extract intent and entities from communications
- Generate appropriate responses
- Route requests to PLAN agent for berth allocation
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json

import anthropic
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.vhf_log import VHFLog, VHFDirection, VHFIntent
from app.models.vessel import Vessel
from app.models.customer import Customer

logger = logging.getLogger(__name__)


class ScoutAgent:
    """
    SCOUT Agent - Aviation-style VHF communication processing

    Uses Claude AI to understand and respond to VHF radio communications
    in multiple languages (Turkish, English, Greek).
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.channel = settings.VHF_CHANNEL
        self.frequency = settings.VHF_FREQUENCY
        self.supported_languages = settings.VHF_SUPPORTED_LANGUAGES.split(",")
        self.is_running = False

        logger.info(f"SCOUT Agent initialized - Channel {self.channel} ({self.frequency} MHz)")

    async def start(self):
        """Start the SCOUT agent background service"""
        self.is_running = True
        logger.info("SCOUT Agent started - Monitoring VHF Channel 72")

        # In production, this would connect to actual VHF radio hardware
        # For now, it runs as a background service ready to process messages
        while self.is_running:
            try:
                # Simulate monitoring cycle
                await asyncio.sleep(1)

                # Check for unprocessed VHF messages
                await self._process_pending_messages()

            except Exception as e:
                logger.error(f"Error in SCOUT agent main loop: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the SCOUT agent"""
        self.is_running = False
        logger.info("SCOUT Agent stopped")

    async def _process_pending_messages(self):
        """Process any pending VHF messages"""
        db = SessionLocal()
        try:
            # Get unprocessed incoming messages
            pending = db.query(VHFLog).filter(
                VHFLog.direction == VHFDirection.INCOMING,
                VHFLog.was_processed == False
            ).limit(10).all()

            for vhf_log in pending:
                await self._process_message(db, vhf_log)

        except Exception as e:
            logger.error(f"Error processing pending messages: {e}")
        finally:
            db.close()

    async def _process_message(self, db: Session, vhf_log: VHFLog):
        """
        Process a single VHF message using Claude AI

        Args:
            db: Database session
            vhf_log: VHF log entry to process
        """
        try:
            start_time = datetime.now()

            # Construct system prompt for Claude
            system_prompt = self._build_system_prompt()

            # Construct user message
            user_message = f"""VHF Message received on Channel {vhf_log.channel}:
Language: {vhf_log.language_detected}
Vessel: {vhf_log.vessel_name or 'Unknown'}
Caller ID: {vhf_log.caller_id or 'Unknown'}
Message: {vhf_log.message_text}

Process this communication and provide:
1. Intent classification
2. Extracted entities
3. Appropriate VHF radio response
4. Suggested system action"""

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Parse response
            response_content = message.content[0].text

            # Try to parse as JSON
            try:
                parsed = json.loads(response_content)
            except json.JSONDecodeError:
                # If not JSON, create basic structure
                parsed = {
                    "intent": "general_inquiry",
                    "confidence": 0.5,
                    "response_text": "Marina West Istanbul, roger. Please standby.",
                    "entities": {},
                    "suggested_action": None
                }

            # Map intent to enum
            intent = self._map_intent(parsed.get("intent", "general_inquiry"))

            # Update VHF log
            vhf_log.intent_parsed = intent
            vhf_log.confidence_score = int(parsed.get("confidence", 0.5) * 100)
            vhf_log.entities_extracted = json.dumps(parsed.get("entities", {}))
            vhf_log.response_text = parsed.get("response_text")
            vhf_log.was_processed = True

            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            vhf_log.response_time_seconds = int(response_time)

            db.commit()

            # Log the outgoing response
            response_log = VHFLog(
                channel=vhf_log.channel,
                frequency=vhf_log.frequency,
                direction=VHFDirection.OUTGOING,
                vessel_name=vhf_log.vessel_name,
                message_text=parsed.get("response_text"),
                language_detected=vhf_log.language_detected,
                was_processed=True
            )
            db.add(response_log)
            db.commit()

            # Handle suggested actions
            suggested_action = parsed.get("suggested_action")
            if suggested_action:
                await self._handle_action(db, vhf_log, parsed)

            logger.info(
                f"Processed VHF message {vhf_log.id}: "
                f"Intent={intent.value}, Confidence={vhf_log.confidence_score}%"
            )

        except Exception as e:
            logger.error(f"Error processing VHF message {vhf_log.id}: {e}")
            vhf_log.was_processed = False
            db.commit()

    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude"""
        return f"""You are the SCOUT agent for ADA.MARINA West Istanbul Marina.

Your role is to process VHF Channel {self.channel} radio communications from vessels.

RESPONSIBILITIES:
1. Understand vessel intent from VHF messages
2. Extract key information (vessel details, dates, services needed)
3. Generate professional aviation-style radio responses
4. Suggest appropriate system actions

SUPPORTED LANGUAGES: {', '.join(self.supported_languages)}

INTENT CATEGORIES:
- reservation_create: Vessel wants to make a berth reservation
- berth_inquiry: Asking about berth availability
- service_request: Requesting marina services (fuel, water, etc.)
- arrival_notification: Vessel approaching marina
- departure_notification: Vessel departing
- emergency: Emergency situation requiring immediate attention
- general_inquiry: General questions about marina

RESPONSE FORMAT (JSON):
{{
  "intent": "intent_category",
  "confidence": 0.0-1.0,
  "response_text": "Professional VHF radio response in same language",
  "entities": {{
    "vessel_name": "extracted vessel name",
    "vessel_length": 0.0,
    "vessel_type": "sailboat|motorboat|yacht|...",
    "check_in_date": "YYYY-MM-DD",
    "check_out_date": "YYYY-MM-DD",
    "special_requests": ["list", "of", "requests"]
  }},
  "suggested_action": "create_assignment|check_availability|alert_port_control|..."
}}

RADIO RESPONSE STYLE:
- Professional and concise
- Aviation-standard terminology
- Clear and unambiguous
- Same language as the incoming message
- Include marina callsign "West Istanbul Marina"

Example responses:
- English: "West Istanbul Marina, roger. Berth available for 45-foot yacht. Proceed to waypoint ALPHA for berth assignment."
- Turkish: "Batı İstanbul Marina, alındı. 45 fit yat için iskele mevcut. İskele ataması için ALFA noktasına gidin."
- Greek: "West Istanbul Marina, κατανοητό. Διαθέσιμη θέση για γιοτ 45 ποδών. Προχωρήστε στο σημείο ALPHA."
"""

    def _map_intent(self, intent_str: str) -> VHFIntent:
        """Map string intent to VHFIntent enum"""
        intent_map = {
            "reservation_create": VHFIntent.RESERVATION,
            "berth_inquiry": VHFIntent.BERTH_INQUIRY,
            "service_request": VHFIntent.SERVICE_REQUEST,
            "arrival_notification": VHFIntent.ARRIVAL_NOTIFICATION,
            "departure_notification": VHFIntent.DEPARTURE_NOTIFICATION,
            "emergency": VHFIntent.EMERGENCY,
            "general_inquiry": VHFIntent.GENERAL_INQUIRY
        }
        return intent_map.get(intent_str, VHFIntent.GENERAL_INQUIRY)

    async def _handle_action(self, db: Session, vhf_log: VHFLog, parsed: Dict[str, Any]):
        """
        Handle suggested actions from Claude

        Args:
            db: Database session
            vhf_log: VHF log entry
            parsed: Parsed response from Claude
        """
        action = parsed.get("suggested_action")
        entities = parsed.get("entities", {})

        if action == "create_assignment":
            # Route to PLAN agent for berth allocation
            logger.info(f"Routing to PLAN agent: Create assignment for {vhf_log.vessel_name}")
            # This would trigger the PLAN agent
            # For now, just log it

        elif action == "check_availability":
            logger.info(f"Checking availability for {vhf_log.vessel_name}")
            # Query available berths based on vessel dimensions

        elif action == "alert_port_control":
            logger.warning(f"Alert: Port control notification for {vhf_log.vessel_name}")
            # Send alert to port control

        elif action == "emergency_response":
            logger.critical(f"EMERGENCY: {vhf_log.vessel_name} - {vhf_log.message_text}")
            # Trigger emergency protocols

    async def process_incoming_message(
        self,
        message_text: str,
        vessel_name: Optional[str] = None,
        caller_id: Optional[str] = None,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Process an incoming VHF message (API endpoint)

        Args:
            message_text: The VHF message content
            vessel_name: Name of the vessel (if known)
            caller_id: Caller identification
            language: Detected language code

        Returns:
            Processed response with intent and suggested response
        """
        db = SessionLocal()
        try:
            # Create VHF log entry
            vhf_log = VHFLog(
                channel=self.channel,
                frequency=self.frequency,
                direction=VHFDirection.INCOMING,
                vessel_name=vessel_name,
                caller_id=caller_id,
                message_text=message_text,
                language_detected=language,
                was_processed=False
            )
            db.add(vhf_log)
            db.commit()
            db.refresh(vhf_log)

            # Process the message
            await self._process_message(db, vhf_log)

            # Return the processed result
            return {
                "vhf_log_id": vhf_log.id,
                "intent": vhf_log.intent_parsed.value if vhf_log.intent_parsed else None,
                "confidence": vhf_log.confidence_score,
                "response": vhf_log.response_text,
                "entities": json.loads(vhf_log.entities_extracted) if vhf_log.entities_extracted else {}
            }

        except Exception as e:
            logger.error(f"Error processing incoming VHF message: {e}")
            raise
        finally:
            db.close()


# Global SCOUT agent instance
scout_agent = ScoutAgent()


async def start_scout_agent():
    """Start the SCOUT agent background service"""
    await scout_agent.start()


async def stop_scout_agent():
    """Stop the SCOUT agent background service"""
    await scout_agent.stop()
