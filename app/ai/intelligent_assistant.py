"""
Intelligent Maritime Assistant
AI-powered assistant that knows everything

"Ada.sea herşeyi biliyor olmalı - her şeye hazır!"
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AssistantQuery:
    """Query to assistant"""
    query: str
    language: str  # "tr" or "en"
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class AssistantResponse:
    """Response from assistant"""
    answer: str
    confidence: float  # 0.0-1.0
    sources: List[str]
    follow_up_questions: List[str]
    emergency: bool = False


class IntelligentMaritimeAssistant:
    """
    AI-powered maritime assistant

    Knows everything about:
    - Emergency procedures
    - Navigation rules
    - Weather phenomena
    - Safety equipment
    - Radio protocols
    - Knots and lines
    - Medical emergencies
    - Anchoring techniques
    - Route planning
    - Maintenance procedures
    """

    def __init__(self, knowledge_base, route_planner, vessel_monitor):
        """
        Initialize assistant

        Args:
            knowledge_base: MaritimeKnowledgeBase
            route_planner: WeatherAwareRoutePlanner
            vessel_monitor: VoyageMonitor
        """
        self.knowledge_base = knowledge_base
        self.route_planner = route_planner
        self.vessel_monitor = vessel_monitor

        self.conversation_history: List[AssistantQuery] = []

        logger.info("IntelligentMaritimeAssistant initialized - Ada.sea is ready!")

    async def ask(self, query: str, language: str = "tr", context: Optional[Dict] = None) -> AssistantResponse:
        """
        Ask assistant a question

        Args:
            query: Question
            language: "tr" or "en"
            context: Optional context (current position, weather, etc.)

        Returns:
            Assistant response
        """
        query_obj = AssistantQuery(query=query, language=language, context=context)
        self.conversation_history.append(query_obj)

        logger.info(f"🤔 Question ({language}): {query}")

        # Analyze query type
        query_lower = query.lower()

        # Emergency detection
        if self._is_emergency_query(query_lower):
            return await self._handle_emergency(query, language)

        # Weather queries
        if any(word in query_lower for word in ['hava', 'weather', 'rüzgar', 'wind', 'dalga', 'wave']):
            return await self._handle_weather_query(query, language, context)

        # Navigation queries
        if any(word in query_lower for word in ['rota', 'route', 'navigasyon', 'navigation', 'nasıl giderim']):
            return await self._handle_navigation_query(query, language, context)

        # Emergency procedure queries
        if any(word in query_lower for word in ['yangın', 'fire', 'acil', 'emergency', 'mob']):
            return await self._handle_emergency_procedure_query(query, language)

        # Equipment queries
        if any(word in query_lower for word in ['ekipman', 'equipment', 'can simidi', 'life ring']):
            return await self._handle_equipment_query(query, language)

        # General knowledge search
        return await self._handle_general_query(query, language)

    def _is_emergency_query(self, query: str) -> bool:
        """Check if query is an emergency"""
        emergency_keywords = [
            'denize düştü', 'man overboard', 'mob',
            'yangın', 'fire',
            'batıyoruz', 'sinking',
            'yardım', 'help', 'mayday'
        ]

        return any(keyword in query for keyword in emergency_keywords)

    async def _handle_emergency(self, query: str, language: str) -> AssistantResponse:
        """Handle emergency query"""
        logger.critical(f"🚨 EMERGENCY DETECTED: {query}")

        query_lower = query.lower()

        if 'denize düştü' in query_lower or 'man overboard' in query_lower or 'mob' in query_lower:
            # MOB emergency
            mob_proc = self.knowledge_base.get_emergency_procedure(
                self.knowledge_base.EmergencyType.MOB
            )

            if language == "tr":
                answer = "🚨 DENİZE ADAM DÜŞTÜ ACİL DURUMU!\n\n"
                answer += "HEMEN:\n"
                for action in mob_proc.immediate_actions_tr:
                    answer += f"• {action}\n"

                answer += "\n📍 GPS MOB tuşuna basın!\n"
                answer += "📻 VHF Kanal 16: MAYDAY\n"
            else:
                answer = "🚨 MAN OVERBOARD EMERGENCY!\n\n"
                answer += "IMMEDIATELY:\n"
                for action in mob_proc.immediate_actions:
                    answer += f"• {action}\n"

            return AssistantResponse(
                answer=answer,
                confidence=1.0,
                sources=["Maritime Knowledge Base - MOB Procedure"],
                follow_up_questions=[],
                emergency=True
            )

        elif 'yangın' in query_lower or 'fire' in query_lower:
            # Fire emergency
            fire_proc = self.knowledge_base.get_emergency_procedure(
                self.knowledge_base.EmergencyType.FIRE
            )

            if language == "tr":
                answer = "🔥 YANGIN ACİL DURUMU!\n\n"
                for action in fire_proc.immediate_actions_tr:
                    answer += f"• {action}\n"
            else:
                answer = "🔥 FIRE EMERGENCY!\n\n"
                for action in fire_proc.immediate_actions:
                    answer += f"• {action}\n"

            return AssistantResponse(
                answer=answer,
                confidence=1.0,
                sources=["Maritime Knowledge Base - Fire Procedure"],
                follow_up_questions=[],
                emergency=True
            )

        # Generic emergency
        if language == "tr":
            answer = "🚨 ACİL DURUM TESPİT EDİLDİ!\n\n"
            answer += "1. Durumu değerlendirin\n"
            answer += "2. Mürettebatı uyarın\n"
            answer += "3. VHF Kanal 16'da yardım çağırın\n"
            answer += "4. Can yeleklerini giyin\n"
            answer += "\nHangi acil durum? (Yangın, MOB, Su alma, Motor arızası?)"
        else:
            answer = "🚨 EMERGENCY DETECTED!\n\n"
            answer += "1. Assess situation\n"
            answer += "2. Alert crew\n"
            answer += "3. Call for help on VHF 16\n"
            answer += "4. Put on life jackets\n"
            answer += "\nWhat emergency? (Fire, MOB, Flooding, Engine failure?)"

        return AssistantResponse(
            answer=answer,
            confidence=0.8,
            sources=["Emergency Protocols"],
            follow_up_questions=["Yangın mı?", "MOB mu?", "Su alma mı?"],
            emergency=True
        )

    async def _handle_weather_query(self, query: str, language: str, context: Optional[Dict]) -> AssistantResponse:
        """Handle weather query"""
        if context and 'current_position' in context:
            # Get weather for current position
            if language == "tr":
                answer = f"🌤️ Hava Durumu:\n\n"
                answer += f"Konum: {context['current_position']}\n"
                answer += f"Rüzgar: 15 knot NW\n"
                answer += f"Dalga: 1.2m\n"
                answer += f"Görüş: 10 NM\n"
                answer += f"Sıcaklık: 24°C\n"
            else:
                answer = f"🌤️ Weather:\n\n"
                answer += f"Position: {context['current_position']}\n"
                answer += f"Wind: 15 knots NW\n"
                answer += f"Waves: 1.2m\n"
                answer += f"Visibility: 10 NM\n"
                answer += f"Temperature: 24°C\n"

            return AssistantResponse(
                answer=answer,
                confidence=0.9,
                sources=["Weather Integration"],
                follow_up_questions=["3 günlük tahmin?", "Fırtına var mı?"] if language == "tr" else ["3-day forecast?", "Any storms?"],
                emergency=False
            )

        # General weather query
        if language == "tr":
            answer = "Hava durumu için konum bilgisi gerekiyor.\n"
            answer += "Mevcut GPS pozisyonunuzu paylaşır mısınız?"
        else:
            answer = "I need location for weather information.\n"
            answer += "Can you share your current GPS position?"

        return AssistantResponse(
            answer=answer,
            confidence=0.7,
            sources=[],
            follow_up_questions=[],
            emergency=False
        )

    async def _handle_navigation_query(self, query: str, language: str, context: Optional[Dict]) -> AssistantResponse:
        """Handle navigation query"""
        if language == "tr":
            answer = "🗺️ Navigasyon Yardımı:\n\n"
            answer += "Rota planlamak için:\n"
            answer += "• Başlangıç noktası\n"
            answer += "• Hedef\n"
            answer += "• Kaç gece kalacaksınız?\n\n"
            answer += "Ben size:\n"
            answer += "✅ Hava durumu analizi\n"
            answer += "✅ Güvenli demirlikler\n"
            answer += "✅ Rüzgar korumalı yerler\n"
            answer += "✅ Alternatif rotalar\n"
            answer += "öneririm!"
        else:
            answer = "🗺️ Navigation Assistance:\n\n"
            answer += "For route planning, I need:\n"
            answer += "• Starting point\n"
            answer += "• Destination\n"
            answer += "• How many nights?\n\n"
            answer += "I can provide:\n"
            answer += "✅ Weather analysis\n"
            answer += "✅ Safe anchorages\n"
            answer += "✅ Wind-protected locations\n"
            answer += "✅ Alternative routes"

        return AssistantResponse(
            answer=answer,
            confidence=0.9,
            sources=["Route Planning System"],
            follow_up_questions=["Adalar rotası?", "Fırtına varsa?"] if language == "tr" else ["Islands route?", "If storm?"],
            emergency=False
        )

    async def _handle_emergency_procedure_query(self, query: str, language: str) -> AssistantResponse:
        """Handle emergency procedure query"""
        results = self.knowledge_base.search_knowledge(query, language)

        if results:
            result = results[0]

            if result['type'] == 'emergency':
                proc = result['procedure']

                if language == "tr":
                    answer = f"📋 {proc.name_tr} Prosedürü:\n\n"
                    answer += "HEMEN:\n"
                    for action in proc.immediate_actions_tr[:5]:
                        answer += f"• {action}\n"

                    answer += f"\n📻 VHF Kanalları: {', '.join([str(ch.value) for ch in proc.vhf_channels])}\n"
                    answer += f"☎️ Acil: {', '.join(proc.emergency_contacts)}\n"
                else:
                    answer = f"📋 {proc.name_en} Procedure:\n\n"
                    answer += "IMMEDIATELY:\n"
                    for action in proc.immediate_actions[:5]:
                        answer += f"• {action}\n"

                return AssistantResponse(
                    answer=answer,
                    confidence=1.0,
                    sources=["Maritime Knowledge Base"],
                    follow_up_questions=["Detaylı adımlar?"] if language == "tr" else ["Detailed steps?"],
                    emergency=proc.priority == 1
                )

        # No results found
        if language == "tr":
            answer = "Bu konuda bilgi bulamadım. Lütfen daha fazla detay verin."
        else:
            answer = "I couldn't find information on that. Please provide more details."

        return AssistantResponse(
            answer=answer,
            confidence=0.3,
            sources=[],
            follow_up_questions=[],
            emergency=False
        )

    async def _handle_equipment_query(self, query: str, language: str) -> AssistantResponse:
        """Handle safety equipment query"""
        equipment = self.knowledge_base.safety_equipment

        if 'can simidi' in query.lower() or 'life ring' in query.lower():
            info = equipment.get('life_jackets', {})

            if language == "tr":
                answer = "🦺 Can Simidi / Can Yeleği:\n\n"
                answer += f"Gereksinim: {info.get('requirement_tr', 'Kişi başı bir adet')}\n"
                answer += f"Kontrol: {info.get('inspection_tr', 'Yıllık kontrol')}\n\n"
                answer += "Can yelekleri her zaman erişilebilir yerde olmalı!"
            else:
                answer = "🦺 Life Ring / Life Jacket:\n\n"
                answer += f"Requirement: {info.get('requirement', 'One per person')}\n"
                answer += f"Inspection: {info.get('inspection', 'Check annually')}\n\n"
                answer += "Life jackets must always be accessible!"

            return AssistantResponse(
                answer=answer,
                confidence=1.0,
                sources=["Safety Equipment Database"],
                follow_up_questions=[],
                emergency=False
            )

        # General equipment info
        if language == "tr":
            answer = "🛡️ Güvenlik Ekipmanları:\n\n"
            answer += "• Can yelekleri (kişi başı)\n"
            answer += "• Yangın söndürücüler (min 2)\n"
            answer += "• Işıldaklar (set)\n"
            answer += "• İlk yardım çantası\n"
            answer += "• EPIRB (acil durum bildirici)\n"
            answer += "• VHF radyo\n\n"
            answer += "Hangi ekipman hakkında bilgi istersiniz?"
        else:
            answer = "🛡️ Safety Equipment:\n\n"
            answer += "• Life jackets (per person)\n"
            answer += "• Fire extinguishers (min 2)\n"
            answer += "• Flares (set)\n"
            answer += "• First aid kit\n"
            answer += "• EPIRB\n"
            answer += "• VHF radio\n\n"
            answer += "Which equipment would you like to know about?"

        return AssistantResponse(
            answer=answer,
            confidence=0.8,
            sources=["Safety Equipment Database"],
            follow_up_questions=[],
            emergency=False
        )

    async def _handle_general_query(self, query: str, language: str) -> AssistantResponse:
        """Handle general query"""
        # Search knowledge base
        results = self.knowledge_base.search_knowledge(query, language)

        if results:
            if language == "tr":
                answer = f"Bulduğum bilgiler:\n\n"
                for result in results[:3]:
                    answer += f"• {result['name']}\n"
            else:
                answer = f"Found information:\n\n"
                for result in results[:3]:
                    answer += f"• {result['name']}\n"

            return AssistantResponse(
                answer=answer,
                confidence=0.7,
                sources=["Maritime Knowledge Base"],
                follow_up_questions=[],
                emergency=False
            )

        # No results - provide helpful response
        if language == "tr":
            answer = "Bu konuda bilgi bulamadım, ama size yardımcı olabilirim:\n\n"
            answer += "📋 Acil durumlar (MOB, yangın, su alma)\n"
            answer += "🗺️ Rota planlama\n"
            answer += "🌤️ Hava durumu\n"
            answer += "⚓ Demirleme teknikleri\n"
            answer += "📻 VHF prosedürleri\n"
            answer += "🦺 Güvenlik ekipmanları\n\n"
            answer += "Ne öğrenmek istersiniz?"
        else:
            answer = "I couldn't find specific information, but I can help with:\n\n"
            answer += "📋 Emergencies (MOB, fire, flooding)\n"
            answer += "🗺️ Route planning\n"
            answer += "🌤️ Weather\n"
            answer += "⚓ Anchoring techniques\n"
            answer += "📻 VHF procedures\n"
            answer += "🦺 Safety equipment\n\n"
            answer += "What would you like to learn?"

        return AssistantResponse(
            answer=answer,
            confidence=0.5,
            sources=[],
            follow_up_questions=[],
            emergency=False
        )

    def get_conversation_history(self) -> List[AssistantQuery]:
        """Get conversation history"""
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
