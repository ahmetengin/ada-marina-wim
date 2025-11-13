"""
Maritime Knowledge Base
Complete maritime knowledge system for Ada.sea

"Ada.sea herşeyi biliyor olmalı - her şeye hazır!"
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Emergency types"""
    MOB = "man_overboard"  # Denize adam düştü!
    FIRE = "fire"  # Yangın
    FLOODING = "flooding"  # Su alma
    MEDICAL = "medical"  # Tıbbi acil durum
    ENGINE_FAILURE = "engine_failure"  # Motor arızası
    GROUNDING = "grounding"  # Karaya oturma
    COLLISION = "collision"  # Çarpışma
    ABANDONING_SHIP = "abandoning_ship"  # Tekneyi terk


class VHFChannel(Enum):
    """VHF radio channels"""
    DISTRESS = 16  # Acil durum
    WORKING = 67  # Çalışma kanalı
    MARINA = 73  # Marina koordinasyonu
    SHIP_TO_SHIP = 72  # Gemi-gemi


@dataclass
class EmergencyProcedure:
    """Emergency procedure"""
    emergency_type: EmergencyType
    name_en: str
    name_tr: str
    priority: int  # 1=CRITICAL, 2=HIGH, 3=MEDIUM
    immediate_actions: List[str]
    immediate_actions_tr: List[str]
    detailed_steps: List[str]
    detailed_steps_tr: List[str]
    vhf_channels: List[VHFChannel]
    emergency_contacts: List[str]
    equipment_needed: List[str]


@dataclass
class NavigationRule:
    """Navigation rule (COLREGS)"""
    rule_number: int
    title: str
    title_tr: str
    description: str
    description_tr: str
    applies_to: str  # "all vessels", "sailing", "power", etc.


@dataclass
class WeatherPhenomenon:
    """Weather phenomenon knowledge"""
    name: str
    name_tr: str
    description: str
    description_tr: str
    warning_signs: List[str]
    warning_signs_tr: List[str]
    recommended_actions: List[str]
    recommended_actions_tr: List[str]
    danger_level: int  # 1-5


class MaritimeKnowledgeBase:
    """
    Complete maritime knowledge system

    Ada.sea's brain - knows everything about:
    - Emergency procedures (MOB, fire, flooding, medical)
    - Navigation rules (COLREGS)
    - Weather phenomena (storms, fog, etc.)
    - Radio protocols (VHF, DSC)
    - Safety equipment
    - Knots and lines
    - Anchoring techniques
    - Medical emergencies
    """

    def __init__(self):
        """Initialize knowledge base"""
        self.emergency_procedures = self._load_emergency_procedures()
        self.navigation_rules = self._load_navigation_rules()
        self.weather_knowledge = self._load_weather_knowledge()
        self.radio_protocols = self._load_radio_protocols()
        self.safety_equipment = self._load_safety_equipment()
        self.knots_and_lines = self._load_knots_and_lines()
        self.medical_guide = self._load_medical_guide()

        logger.info("MaritimeKnowledgeBase initialized - Ada.sea knows everything!")

    def _load_emergency_procedures(self) -> Dict[EmergencyType, EmergencyProcedure]:
        """Load emergency procedures"""
        return {
            EmergencyType.MOB: EmergencyProcedure(
                emergency_type=EmergencyType.MOB,
                name_en="Man Overboard",
                name_tr="Denize Adam Düştü",
                priority=1,  # CRITICAL
                immediate_actions=[
                    "1. SHOUT 'MAN OVERBOARD!' immediately",
                    "2. THROW life ring/buoy to person",
                    "3. ASSIGN crew to keep eyes on person",
                    "4. PRESS MOB button on GPS/chartplotter",
                    "5. ENGINE - engage immediately",
                    "6. TURN vessel towards person (Williamson Turn)",
                    "7. RADIO - Mayday relay if alone"
                ],
                immediate_actions_tr=[
                    "1. 'DENİZE ADAM DÜŞTÜ!' diye BAĞIR",
                    "2. Can simidi FIRLAT",
                    "3. Birini gözcü ATAYIN (gözünü ayırmasın)",
                    "4. GPS'te MOB tuşuna BAS",
                    "5. MOTOR'u çalıştır",
                    "6. Tekneyi kişiye DÖNDÜR (Williamson Turn)",
                    "7. VHF Mayday (eğer yalnızsan)"
                ],
                detailed_steps=[
                    "WILLIAMSON TURN MANEUVER:",
                    "1. Put helm hard over to side person fell",
                    "2. After 60° turn, shift helm hard to opposite side",
                    "3. When heading 180° from original, straighten",
                    "4. Return on reciprocal course to MOB position",
                    "",
                    "RECOVERY:",
                    "1. Approach MOB from downwind",
                    "2. Engine neutral as approaching",
                    "3. Throw line with life ring",
                    "4. Use ladder/boarding platform",
                    "5. If unconscious, lift horizontal (spinal injury)",
                    "",
                    "RADIO:",
                    "VHF Channel 16: 'MAYDAY MAYDAY MAYDAY'",
                    "This is [vessel name]",
                    "Position: [lat/lon]",
                    "Man overboard, require assistance",
                    "",
                    "AFTER RECOVERY:",
                    "1. Check for hypothermia",
                    "2. Warm slowly (blankets, warm drinks)",
                    "3. Check for injuries",
                    "4. Call for medical advice"
                ],
                detailed_steps_tr=[
                    "WİLLİAMSON TURN MANEVRASı:",
                    "1. Dümen kişinin düştüğü tarafa TAMAMEN çevir",
                    "2. 60° döndükten sonra, dümeni KARŞI tarafa çevir",
                    "3. Orijinal rotadan 180° döndüğünde düzelt",
                    "4. MOB pozisyonuna ters rotada dön",
                    "",
                    "KURTARMA:",
                    "1. Kişiye rüzgar altından yaklaş",
                    "2. Yaklaşırken motoru nötre al",
                    "3. Can simidi ile halat at",
                    "4. Merdiven/platform kullan",
                    "5. Bilinçsizse yatay kaldır (omurga yaralanması)",
                    "",
                    "RADYO:",
                    "VHF Kanal 16: 'MAYDAY MAYDAY MAYDAY'",
                    "Burası [tekne adı]",
                    "Pozisyon: [lat/lon]",
                    "Denize adam düştü, yardım gerekiyor",
                    "",
                    "KURTARMADAN SONRA:",
                    "1. Hipotermi kontrol et",
                    "2. Yavaş ısın (battaniye, ılık içecek)",
                    "3. Yaralanma kontrol et",
                    "4. Tıbbi yardım çağır"
                ],
                vhf_channels=[VHFChannel.DISTRESS],
                emergency_contacts=["Coast Guard: 158", "Emergency: 112"],
                equipment_needed=[
                    "Life ring with line",
                    "Throwing rope",
                    "Boarding ladder",
                    "First aid kit",
                    "Blankets",
                    "GPS with MOB button"
                ]
            ),

            EmergencyType.FIRE: EmergencyProcedure(
                emergency_type=EmergencyType.FIRE,
                name_en="Fire Onboard",
                name_tr="Teknede Yangın",
                priority=1,  # CRITICAL
                immediate_actions=[
                    "1. SHOUT 'FIRE!' - alert all crew",
                    "2. SHUT fuel valve immediately",
                    "3. SHUT OFF electrical power",
                    "4. GRAB fire extinguisher",
                    "5. FIGHT fire (if small and safe)",
                    "6. PUT ON life jackets",
                    "7. RADIO Mayday if fire uncontrolled"
                ],
                immediate_actions_tr=[
                    "1. 'YANGIN!' diye BAĞIR - mürettebatı uyar",
                    "2. Yakıt valfini KAPAT",
                    "3. Elektriği KES",
                    "4. Yangın söndürücüyü AL",
                    "5. Ateşle SAVAŞ (küçük ve güvenliyse)",
                    "6. Can yeleklerini GİYİN",
                    "7. VHF Mayday (kontrol dışıysa)"
                ],
                detailed_steps=[
                    "FIRE TRIANGLE - Remove one:",
                    "- FUEL: Shut fuel valve, remove flammables",
                    "- OXYGEN: Close hatches, use CO2 extinguisher",
                    "- HEAT: Use water (not on electrical/fuel!)",
                    "",
                    "EXTINGUISHER TYPES:",
                    "- ABC Dry powder: General purpose",
                    "- CO2: Electrical fires",
                    "- Foam: Fuel fires",
                    "- Water: Wood/fabric (NOT electrical!)",
                    "",
                    "FIGHTING FIRE:",
                    "1. Attack from upwind",
                    "2. Aim at base of flames",
                    "3. Sweep side to side",
                    "4. Keep low (smoke rises)",
                    "5. Have escape route",
                    "",
                    "IF FIRE OUT OF CONTROL:",
                    "1. Mayday on VHF 16",
                    "2. Put on life jackets",
                    "3. Prepare life raft",
                    "4. Close hatches (starve fire)",
                    "5. Ready to abandon ship"
                ],
                detailed_steps_tr=[
                    "YANGIN ÜÇGENİ - Birini kaldır:",
                    "- YAKIT: Yakıt valfini kapat, yanıcıları uzaklaştır",
                    "- OKSİJEN: Ambar kapılarını kapat, CO2 kullan",
                    "- ISI: Su kullan (elektrik/yakıtta DEĞİL!)",
                    "",
                    "SÖNDÜRÜCÜ TİPLERİ:",
                    "- ABC Kuru kimyevi: Genel amaçlı",
                    "- CO2: Elektrik yangınları",
                    "- Köpük: Yakıt yangınları",
                    "- Su: Ahşap/kumaş (ELEKTRİK DEĞİL!)",
                    "",
                    "YANGINLA SAVAŞ:",
                    "1. Rüzgar üstünden saldır",
                    "2. Alevlerin tabanına nişan al",
                    "3. Sağa sola süpür",
                    "4. Alçakta kal (duman yükselir)",
                    "5. Kaçış yolunu aç tut",
                    "",
                    "YANGIN KONTROL DIŞIYSA:",
                    "1. VHF 16 Mayday",
                    "2. Can yeleklerini giyin",
                    "3. Can salını hazırla",
                    "4. Ambar kapaklarını kapat (yangını boğ)",
                    "5. Tekneyi terk etmeye hazır ol"
                ],
                vhf_channels=[VHFChannel.DISTRESS],
                emergency_contacts=["Coast Guard: 158", "Fire: 110"],
                equipment_needed=[
                    "Fire extinguishers (ABC, CO2)",
                    "Fire blanket",
                    "Life jackets",
                    "Life raft",
                    "VHF radio"
                ]
            ),

            EmergencyType.MEDICAL: EmergencyProcedure(
                emergency_type=EmergencyType.MEDICAL,
                name_en="Medical Emergency",
                name_tr="Tıbbi Acil Durum",
                priority=2,  # HIGH
                immediate_actions=[
                    "1. ASSESS - Check ABC (Airway, Breathing, Circulation)",
                    "2. CALL for help - VHF medical advice",
                    "3. STOP bleeding if present",
                    "4. TREAT shock - lie down, elevate legs",
                    "5. MONITOR vitals",
                    "6. DOCUMENT everything",
                    "7. RADIO Coast Guard if severe"
                ],
                immediate_actions_tr=[
                    "1. DEĞERLENDİR - ABC (Hava yolu, Solunum, Dolaşım)",
                    "2. YARDIM çağır - VHF tıbbi danışma",
                    "3. Kanama varsa DURDUR",
                    "4. Şoku TEDAVI ET - yatır, bacakları kaldır",
                    "5. Yaşamsal belirtileri TAKİP ET",
                    "6. Her şeyi BELGELE",
                    "7. Ciddiyse Sahil Güvenlik ÇAĞIR"
                ],
                detailed_steps=[
                    "PRIMARY SURVEY - ABC:",
                    "A - Airway: Clear? Open?",
                    "B - Breathing: Rate, depth?",
                    "C - Circulation: Pulse, bleeding?",
                    "",
                    "COMMON EMERGENCIES:",
                    "- Heart attack: Aspirin, rest, oxygen",
                    "- Stroke: FAST test, immediate evacuation",
                    "- Broken bones: Immobilize, ice",
                    "- Burns: Cool water, cover",
                    "- Hypothermia: Warm slowly",
                    "- Seasickness: Ginger, acupressure",
                    "",
                    "RADIO MEDICAL ADVICE:",
                    "VHF 16: Request medical advice",
                    "Describe: Age, symptoms, vitals",
                    "Follow doctor's instructions",
                    "",
                    "EVACUATION:",
                    "Coast Guard helicopter if severe",
                    "Nearest port if stable",
                    "Document all treatment"
                ],
                detailed_steps_tr=[
                    "BİRİNCİL DEĞERLENDİRME - ABC:",
                    "A - Airway: Hava yolu açık mı?",
                    "B - Breathing: Solunum var mı?",
                    "C - Circulation: Nabız, kanama?",
                    "",
                    "YAYGN ACİL DURUMLAR:",
                    "- Kalp krizi: Aspirin, istirahat, oksijen",
                    "- İnme: FAST testi, acil tahliye",
                    "- Kırık: Sabitle, buz",
                    "- Yanık: Soğuk su, ört",
                    "- Hipotermi: Yavaş ısıt",
                    "- Deniz tutması: Zencefil, akupresur",
                    "",
                    "TIBBİ DANIŞMA:",
                    "VHF 16: Tıbbi danışma iste",
                    "Anlat: Yaş, semptomlar, vital",
                    "Doktor talimatlarını uygula",
                    "",
                    "TAHLİYE:",
                    "Sahil Güvenlik helikopteri (ciddi)",
                    "En yakın liman (stabil)",
                    "Tüm müdahaleyi belgele"
                ],
                vhf_channels=[VHFChannel.DISTRESS],
                emergency_contacts=["Coast Guard: 158", "Ambulance: 112"],
                equipment_needed=[
                    "First aid kit (comprehensive)",
                    "Oxygen tank",
                    "Defibrillator (AED)",
                    "Medications",
                    "Splints",
                    "Blankets"
                ]
            ),

            EmergencyType.ENGINE_FAILURE: EmergencyProcedure(
                emergency_type=EmergencyType.ENGINE_FAILURE,
                name_en="Engine Failure",
                name_tr="Motor Arızası",
                priority=2,  # HIGH
                immediate_actions=[
                    "1. DROP anchor if near shore/traffic",
                    "2. HOIST sails if sailing vessel",
                    "3. CHECK fuel, oil, cooling",
                    "4. RADIO position to Coast Guard",
                    "5. SHOW signals (day: cone, night: red over red)",
                    "6. PREPARE tow if needed"
                ],
                immediate_actions_tr=[
                    "1. Kıyıdaysan/trafikteysen DEMİR AT",
                    "2. Yelkenli ise yelkenleri AÇ",
                    "3. Yakıt, yağ, soğutma KONTROL ET",
                    "4. Pozisyonu Sahil Güvenlik'e BİLDİR",
                    "5. Sinyalleri GÖSTer (gündüz: koni, gece: kırmızı/kırmızı)",
                    "6. Gerekirse çekme HAZIRLA"
                ],
                detailed_steps=[
                    "QUICK CHECKS:",
                    "1. Fuel: Check tank, prime pump",
                    "2. Oil: Check level, pressure",
                    "3. Cooling: Check temp, hoses",
                    "4. Electrical: Check battery, connections",
                    "5. Air: Check filter, intake",
                    "",
                    "COMMON PROBLEMS:",
                    "- Out of fuel: Switch tank, prime",
                    "- Overheating: Stop, let cool, check coolant",
                    "- Won't start: Check battery, starter",
                    "- Running rough: Check fuel filter",
                    "- No power: Check prop for line/debris",
                    "",
                    "IF UNABLE TO FIX:",
                    "1. Anchor in safe location",
                    "2. Radio for tow assistance",
                    "3. Show 'not under command' signals",
                    "4. Monitor radio and weather"
                ],
                detailed_steps_tr=[
                    "HIZLI KONTROLLER:",
                    "1. Yakıt: Tank kontrol, pompa prime et",
                    "2. Yağ: Seviye, basınç kontrol",
                    "3. Soğutma: Sıcaklık, hortumlar kontrol",
                    "4. Elektrik: Batarya, bağlantılar kontrol",
                    "5. Hava: Filtre, giriş kontrol",
                    "",
                    "YAYGN SORUNLAR:",
                    "- Yakıt bitti: Tank değiştir, prime et",
                    "- Aşırı ısınma: Dur, soğut, soğutma suyu kontrol",
                    "- Çalışmıyor: Batarya, marş kontrol",
                    "- Titrek: Yakıt filtresi kontrol",
                    "- Güç yok: Pervanede halat/pislik kontrol",
                    "",
                    "TAMİR EDEMİYORSAN:",
                    "1. Güvenli yere demir at",
                    "2. Çekme yardımı çağır",
                    "3. 'Komuta edilmiyor' sinyali göster",
                    "4. Radyo ve havayı izle"
                ],
                vhf_channels=[VHFChannel.DISTRESS, VHFChannel.WORKING],
                emergency_contacts=["Coast Guard: 158", "Tow service"],
                equipment_needed=[
                    "Tools",
                    "Spare parts",
                    "Fuel filters",
                    "Tow line",
                    "Anchor",
                    "Signal flags/lights"
                ]
            ),
        }

    def _load_navigation_rules(self) -> List[NavigationRule]:
        """Load COLREGS navigation rules"""
        return [
            NavigationRule(
                rule_number=5,
                title="Look-out",
                title_tr="Gözcü Bulundurma",
                description="Every vessel shall at all times maintain a proper look-out by sight and hearing.",
                description_tr="Her tekne her zaman görme ve işitme ile düzgün gözcü bulundurmalıdır.",
                applies_to="all vessels"
            ),
            NavigationRule(
                rule_number=7,
                title="Risk of Collision",
                title_tr="Çarpışma Riski",
                description="Every vessel shall use all available means to determine if risk of collision exists.",
                description_tr="Her tekne çarpışma riskini belirlemek için tüm araçları kullanmalıdır.",
                applies_to="all vessels"
            ),
            NavigationRule(
                rule_number=8,
                title="Action to Avoid Collision",
                title_tr="Çarpışmadan Kaçınma Hareketi",
                description="Any action to avoid collision shall be positive, made in ample time and with due regard to good seamanship.",
                description_tr="Çarpışmadan kaçınma hareketi pozitif, zamanında ve denizcilik kurallarına uygun olmalıdır.",
                applies_to="all vessels"
            ),
            NavigationRule(
                rule_number=13,
                title="Overtaking",
                title_tr="Sollama",
                description="Any vessel overtaking another shall keep out of the way of the vessel being overtaken.",
                description_tr="Sollayan tekne sollananın yolundan çekilmekle yükümlüdür.",
                applies_to="all vessels"
            ),
            NavigationRule(
                rule_number=15,
                title="Crossing Situation",
                title_tr="Kesişme Durumu",
                description="When two power-driven vessels are crossing, the vessel which has the other on her starboard side shall keep out of the way.",
                description_tr="İki motorlu tekne kesiştiğinde, diğerini sancak (sağ) tarafında gören yol vermekle yükümlüdür.",
                applies_to="power vessels"
            ),
            NavigationRule(
                rule_number=18,
                title="Responsibilities Between Vessels",
                title_tr="Tekneler Arası Sorumluluklar",
                description="Power gives way to sail. Sail gives way to fishing. Fishing gives way to restricted maneuverability. All give way to not under command.",
                description_tr="Motorlu yelkenliye yol verir. Yelkenli balıkçıya yol verir. Balıkçı manevra kısıtlısına yol verir. Herkes komuta edilemeyene yol verir.",
                applies_to="all vessels"
            ),
        ]

    def _load_weather_knowledge(self) -> List[WeatherPhenomenon]:
        """Load weather phenomena knowledge"""
        return [
            WeatherPhenomenon(
                name="Poyraz (Northeasterly)",
                name_tr="Poyraz",
                description="Cold, dry northeasterly wind in Turkey. Can be strong and gusty.",
                description_tr="Türkiye'de soğuk, kuru kuzeydoğu rüzgarı. Kuvvetli ve sert olabilir.",
                warning_signs=[
                    "Rapid temperature drop",
                    "Clear skies",
                    "Increased wave height",
                    "Barometer rising"
                ],
                warning_signs_tr=[
                    "Ani sıcaklık düşüşü",
                    "Açık gökyüzü",
                    "Dalga yüksekliği artışı",
                    "Barometre yükseliyor"
                ],
                recommended_actions=[
                    "Seek shelter from north/northeast",
                    "Double anchor if at anchor",
                    "Check all lines and fenders",
                    "Monitor weather closely"
                ],
                recommended_actions_tr=[
                    "Kuzey/kuzeydoğudan korunaklı yer ara",
                    "Demirdeysen çift demir kullan",
                    "Tüm halatları ve fenderleri kontrol et",
                    "Havayı yakından izle"
                ],
                danger_level=4
            ),
            WeatherPhenomenon(
                name="Lodos (Southwesterly)",
                name_tr="Lodos",
                description="Warm, humid southwesterly wind. Often precedes storms.",
                description_tr="Sıcak, nemli güneybatı rüzgarı. Genelde fırtına öncesidir.",
                warning_signs=[
                    "Sudden wind shift to SW",
                    "Increasing humidity",
                    "Dark clouds approaching",
                    "Barometer falling"
                ],
                warning_signs_tr=[
                    "Ani güneybatıya rüzgar değişimi",
                    "Artan nem",
                    "Kara bulutlar yaklaşıyor",
                    "Barometre düşüyor"
                ],
                recommended_actions=[
                    "Return to port if possible",
                    "Seek shelter from southwest",
                    "Prepare for storm",
                    "Secure all loose items"
                ],
                recommended_actions_tr=[
                    "Mümkünse limana dön",
                    "Güneybatıdan korunaklı yer ara",
                    "Fırtınaya hazırlan",
                    "Gevşek eşyaları sabitle"
                ],
                danger_level=5
            ),
        ]

    def _load_radio_protocols(self) -> Dict[str, Any]:
        """Load VHF radio protocols"""
        return {
            "mayday": {
                "when": "Life-threatening emergency",
                "when_tr": "Yaşamı tehdit eden acil durum",
                "channel": 16,
                "format": [
                    "MAYDAY MAYDAY MAYDAY",
                    "This is [vessel name] [vessel name] [vessel name]",
                    "MAYDAY [vessel name]",
                    "Position: [latitude longitude]",
                    "Nature of distress: [fire/sinking/collision/etc]",
                    "Number of persons onboard: [number]",
                    "Description of vessel: [length, color, type]",
                    "OVER"
                ],
                "format_tr": [
                    "MAYDAY MAYDAY MAYDAY",
                    "Burası [tekne adı] [tekne adı] [tekne adı]",
                    "MAYDAY [tekne adı]",
                    "Pozisyon: [enlem boylam]",
                    "Acil durum: [yangın/batıyor/çarpışma/vs]",
                    "Kişi sayısı: [sayı]",
                    "Tekne: [uzunluk, renk, tip]",
                    "TAMAM"
                ]
            },
            "pan_pan": {
                "when": "Urgent but not life-threatening",
                "when_tr": "Acil ama yaşamsal tehdit yok",
                "channel": 16,
                "format": [
                    "PAN PAN PAN PAN PAN PAN",
                    "All stations, all stations, all stations",
                    "This is [vessel name]",
                    "[urgent message]",
                    "OVER"
                ]
            },
            "securite": {
                "when": "Safety message (weather warning, navigational hazard)",
                "when_tr": "Güvenlik mesajı (hava uyarısı, seyir tehlikesi)",
                "channel": 16,
                "format": [
                    "SECURITE SECURITE SECURITE",
                    "All stations, all stations, all stations",
                    "This is [vessel name]",
                    "[safety message]",
                    "OVER"
                ]
            }
        }

    def _load_safety_equipment(self) -> Dict[str, Any]:
        """Load safety equipment knowledge"""
        return {
            "life_jackets": {
                "type": "Personal flotation device",
                "type_tr": "Kişisel can kurtarma aracı",
                "requirement": "One per person minimum",
                "requirement_tr": "Kişi başı en az bir adet",
                "inspection": "Check annually: straps, buckles, flotation",
                "inspection_tr": "Yıllık kontrol: kayışlar, tokalar, yüzdürme"
            },
            "fire_extinguishers": {
                "types": {
                    "ABC": "General purpose (dry powder)",
                    "CO2": "Electrical fires",
                    "Foam": "Fuel fires"
                },
                "requirement": "Minimum 2, checked annually",
                "requirement_tr": "En az 2 adet, yıllık kontrol",
                "expiry": "Check pressure gauge monthly"
            },
            "flares": {
                "types": {
                    "red_hand": "Distress signal (day/night)",
                    "orange_smoke": "Distress signal (day)",
                    "white": "Warning of your presence (not distress)"
                },
                "requirement": "Set of 6 minimum",
                "expiry": "4 years - check expiry dates"
            },
            "epirb": {
                "type": "Emergency Position Indicating Radio Beacon",
                "type_tr": "Acil Durum Pozisyon Bildirici",
                "function": "Satellite distress alert with GPS position",
                "battery": "Replace every 5-10 years"
            }
        }

    def _load_knots_and_lines(self) -> Dict[str, Any]:
        """Load knots and lines knowledge"""
        return {
            "bowline": {
                "name_tr": "Şerifli düğüm",
                "use": "Creates fixed loop, won't slip",
                "use_tr": "Sabit halka oluşturur, kaymaz",
                "strength": "High",
                "applications": ["Attaching mooring lines", "Rescue loops"]
            },
            "clove_hitch": {
                "name_tr": "Çift bağ",
                "use": "Quick attachment to post/rail",
                "use_tr": "Direk/korkuluğa hızlı bağlama",
                "strength": "Medium",
                "applications": ["Temporary fender attachment", "Dock lines"]
            },
            "figure_eight": {
                "name_tr": "Sekiz düğümü",
                "use": "Stopper knot (prevents line running through)",
                "use_tr": "Durdurma düğümü (halatın kaçmasını önler)",
                "strength": "Very high",
                "applications": ["Sheet ends", "Halyard ends"]
            },
            "anchor_bend": {
                "name_tr": "Demir bağı",
                "use": "Secure anchor line to anchor",
                "use_tr": "Demir halatını demire güvenli bağlama",
                "strength": "Very high",
                "applications": ["Anchor attachment"]
            }
        }

    def _load_medical_guide(self) -> Dict[str, Any]:
        """Load medical emergency guide"""
        return {
            "cpr": {
                "name": "Cardiopulmonary Resuscitation",
                "name_tr": "Kalp-Akciğer Canlandırması (KAC)",
                "rate": "100-120 compressions per minute",
                "rate_tr": "Dakikada 100-120 baskı",
                "depth": "5-6 cm chest compression",
                "ratio": "30 compressions : 2 breaths"
            },
            "choking": {
                "name_tr": "Boğulma",
                "conscious": "Heimlich maneuver (abdominal thrusts)",
                "conscious_tr": "Heimlich manevrası (karın baskısı)",
                "unconscious": "Begin CPR",
                "unconscious_tr": "KAC başlat"
            },
            "hypothermia": {
                "name_tr": "Hipotermi",
                "mild": "Shivering, confusion - warm gradually",
                "mild_tr": "Titreme, kafa karışıklığı - yavaş ısıt",
                "severe": "No shivering, unconscious - evacuate immediately",
                "severe_tr": "Titreme yok, bilinçsiz - acil tahliye",
                "treatment": "Remove wet clothes, warm blankets, warm drinks (if conscious)",
                "treatment_tr": "Islak kıyafetleri çıkar, battaniye, ılık içecek (bilinçliyse)"
            }
        }

    def get_emergency_procedure(self, emergency_type: EmergencyType) -> Optional[EmergencyProcedure]:
        """Get emergency procedure"""
        return self.emergency_procedures.get(emergency_type)

    def search_knowledge(self, query: str, language: str = "tr") -> List[Dict[str, Any]]:
        """
        Search knowledge base

        Args:
            query: Search query
            language: "tr" or "en"

        Returns:
            List of relevant results
        """
        results = []
        query_lower = query.lower()

        # Search emergency procedures
        for emergency_type, procedure in self.emergency_procedures.items():
            if language == "tr":
                if query_lower in procedure.name_tr.lower():
                    results.append({
                        'type': 'emergency',
                        'name': procedure.name_tr,
                        'procedure': procedure
                    })
            else:
                if query_lower in procedure.name_en.lower():
                    results.append({
                        'type': 'emergency',
                        'name': procedure.name_en,
                        'procedure': procedure
                    })

        # Search weather phenomena
        for phenomenon in self.weather_knowledge:
            if language == "tr":
                if query_lower in phenomenon.name_tr.lower():
                    results.append({
                        'type': 'weather',
                        'name': phenomenon.name_tr,
                        'phenomenon': phenomenon
                    })
            else:
                if query_lower in phenomenon.name.lower():
                    results.append({
                        'type': 'weather',
                        'name': phenomenon.name,
                        'phenomenon': phenomenon
                    })

        return results

    def get_mob_procedure_quick(self) -> str:
        """Get MOB quick reference (for voice/display)"""
        mob = self.emergency_procedures[EmergencyType.MOB]

        quick_ref = "🚨 DENİZE ADAM DÜŞTÜ!\n\n"
        quick_ref += "HEMEN:\n"
        for action in mob.immediate_actions_tr:
            quick_ref += f"{action}\n"

        return quick_ref
