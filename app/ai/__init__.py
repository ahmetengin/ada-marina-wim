"""
AI Module - Intelligent Maritime Systems

"Ada.sea herşeyi biliyor olmalı - her şeye ve her an hazır!"

Components:
- intelligent_assistant.py: AI-powered maritime assistant
- mob_detection.py: YOLO-based MOB detection (future)
- single_handed_mob.py: Autonomous emergency response for single-handed MOB
"""

from app.ai.intelligent_assistant import (
    IntelligentMaritimeAssistant,
    AssistantQuery,
    AssistantResponse
)

from app.ai.mob_detection import (
    MOBDetectionSystem,
    MOBProcedureAssistant,
    DetectionStatus,
    AlertPriority,
    MOBAlert
)

from app.ai.single_handed_mob import (
    SingleHandedMOBEmergency,
    CrewManifestSystem,
    VesselManifest,
    Person,
    PersonRole,
    PersonStatus
)

__all__ = [
    # Intelligent Assistant
    'IntelligentMaritimeAssistant',
    'AssistantQuery',
    'AssistantResponse',

    # MOB Detection
    'MOBDetectionSystem',
    'MOBProcedureAssistant',
    'DetectionStatus',
    'AlertPriority',
    'MOBAlert',

    # Single-Handed MOB
    'SingleHandedMOBEmergency',
    'CrewManifestSystem',
    'VesselManifest',
    'Person',
    'PersonRole',
    'PersonStatus',
]
