"""
Maritime Knowledge Base Module

"Ada.sea herşeyi biliyor olmalı!"

Complete maritime knowledge covering:
- Emergency procedures (MOB, fire, flooding, medical)
- Navigation rules (COLREGS)
- Weather phenomena (Poyraz, Lodos, Meltem)
- VHF radio protocols (Mayday, Pan-Pan, Securite)
- Safety equipment
- Medical emergencies
- Knots and lines
"""

from app.knowledge.maritime_knowledge_base import (
    MaritimeKnowledgeBase,
    EmergencyProcedure,
    EmergencyType,
    NavigationRule,
    WeatherPhenomenon,
    VHFChannel,
    RadioProtocol
)

__all__ = [
    'MaritimeKnowledgeBase',
    'EmergencyProcedure',
    'EmergencyType',
    'NavigationRule',
    'WeatherPhenomenon',
    'VHFChannel',
    'RadioProtocol',
]
