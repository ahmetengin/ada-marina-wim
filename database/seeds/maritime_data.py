"""
Maritime Data Seeds
Initial data for Coast Guard contacts and maritime terminology
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.coast_guard_info import CoastGuardContact, MaritimeTerminology
from app.models.maritime_weather import MaritimeWeatherForecast, MaritimeCurrentsForecast

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_coast_guard_contacts(db: Session):
    """Seed Coast Guard regional contacts"""
    logger.info("Seeding Coast Guard contacts...")

    contacts_data = [
        {
            "region_name": "Marmara",
            "command_type": "Bölge",
            "emergency_number": "158",
            "vhf_channel": "16",
            "phone_number": "+90 212 xxx xxxx",
            "website": "https://www.sg.gov.tr",
            "coverage_area": "Marmara Denizi, İstanbul Boğazı, Çanakkale Boğazı",
            "city": "İstanbul",
            "is_active": True,
            "is_24_7": True,
            "notes": "West Istanbul Marina's primary Coast Guard command"
        },
        {
            "region_name": "Ege",
            "command_type": "Bölge",
            "emergency_number": "158",
            "vhf_channel": "16",
            "phone_number": "+90 232 xxx xxxx",
            "website": "https://www.sg.gov.tr",
            "coverage_area": "Ege Denizi kıyıları",
            "city": "İzmir",
            "is_active": True,
            "is_24_7": True,
            "notes": "Aegean Sea Regional Command"
        },
        {
            "region_name": "Akdeniz",
            "command_type": "Bölge",
            "emergency_number": "158",
            "vhf_channel": "16",
            "phone_number": "+90 324 xxx xxxx",
            "website": "https://www.sg.gov.tr",
            "coverage_area": "Akdeniz kıyıları",
            "city": "Mersin",
            "is_active": True,
            "is_24_7": True,
            "notes": "Mediterranean Regional Command"
        },
        {
            "region_name": "Karadeniz",
            "command_type": "Bölge",
            "emergency_number": "158",
            "vhf_channel": "16",
            "phone_number": "+90 462 xxx xxxx",
            "website": "https://www.sg.gov.tr",
            "coverage_area": "Karadeniz kıyıları",
            "city": "Trabzon",
            "is_active": True,
            "is_24_7": True,
            "notes": "Black Sea Regional Command"
        }
    ]

    for contact_data in contacts_data:
        # Check if exists
        existing = db.query(CoastGuardContact).filter(
            CoastGuardContact.region_name == contact_data["region_name"]
        ).first()

        if not existing:
            contact = CoastGuardContact(**contact_data)
            db.add(contact)
            logger.info(f"Added Coast Guard contact: {contact_data['region_name']}")

    db.commit()
    logger.info("Coast Guard contacts seeded successfully")


def seed_maritime_terminology(db: Session):
    """Seed maritime terminology (Denizci Dili)"""
    logger.info("Seeding maritime terminology...")

    terms_data = [
        # VHF Communication Terms
        {
            "term_turkish": "Mayday",
            "term_english": "Mayday",
            "term_greek": "Mayday",
            "definition_turkish": "Acil yardım çağrısı. Can ve mal güvenliği için tehlike anında kullanılır.",
            "definition_english": "International distress signal. Used when life or vessel is in grave and imminent danger.",
            "category": "VHF Communication",
            "subcategory": "Emergency",
            "is_vhf_command": True,
            "vhf_usage_notes": "VHF Channel 16'da 3 kez tekrarlanır: 'Mayday, Mayday, Mayday'",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Pan-Pan",
            "term_english": "Pan-Pan",
            "term_greek": "Pan-Pan",
            "definition_turkish": "Aciliyet mesajı. Mayday kadar kritik olmayan ancak önemli durumlarda kullanılır.",
            "definition_english": "Urgency signal. Used for urgent situations that are not immediately life-threatening.",
            "category": "VHF Communication",
            "subcategory": "Urgency",
            "is_vhf_command": True,
            "vhf_usage_notes": "3 kez tekrarlanır: 'Pan-Pan, Pan-Pan, Pan-Pan'",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Sécurité",
            "term_english": "Sécurité",
            "term_greek": "Sécurité",
            "definition_turkish": "Güvenlik mesajı. Deniz trafiği ve seyrüsefer güvenliği ile ilgili önemli bilgiler için.",
            "definition_english": "Safety message. Used for important navigational or meteorological warnings.",
            "category": "VHF Communication",
            "subcategory": "Safety",
            "is_vhf_command": True,
            "vhf_usage_notes": "3 kez tekrarlanır: 'Sécurité, Sécurité, Sécurité'",
            "source": "sg.gov.tr"
        },
        # Wind Directions (Turkish Maritime)
        {
            "term_turkish": "Poyraz",
            "term_english": "North-East Wind",
            "term_greek": "Βοριαδης (Vorias)",
            "definition_turkish": "Kuzeydoğu rüzgarı. Karadeniz ve Marmara'da sık görülür.",
            "definition_english": "North-east wind. Common in Black Sea and Marmara.",
            "category": "Navigation",
            "subcategory": "Wind Directions",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Lodos",
            "term_english": "South-West Wind",
            "term_greek": "Λίβας (Livas)",
            "definition_turkish": "Güneybatı rüzgarı. Ege ve Marmara'da yaygın, genellikle kuvvetli eser.",
            "definition_english": "South-west wind. Common in Aegean and Marmara, usually strong.",
            "category": "Navigation",
            "subcategory": "Wind Directions",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Karayel",
            "term_english": "North-West Wind",
            "term_greek": "Μαΐστρος (Maestros)",
            "definition_turkish": "Kuzeybatı rüzgarı.",
            "definition_english": "North-west wind.",
            "category": "Navigation",
            "subcategory": "Wind Directions",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Keşişleme",
            "term_english": "South-East Wind",
            "term_greek": "Σιρόκος (Sirokos)",
            "definition_turkish": "Güneydoğu rüzgarı.",
            "definition_english": "South-east wind.",
            "category": "Navigation",
            "subcategory": "Wind Directions",
            "source": "sg.gov.tr"
        },
        # Navigation Terms
        {
            "term_turkish": "İskele",
            "term_english": "Port Side",
            "term_greek": "Αριστερά (Aristera)",
            "definition_turkish": "Geminin sol tarafı. Kırmızı ışık ile işaretlenir.",
            "definition_english": "Left side of the vessel. Marked with red light.",
            "category": "Navigation",
            "subcategory": "Vessel Parts",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Sancak",
            "term_english": "Starboard",
            "term_greek": "Δεξιά (Dexia)",
            "definition_turkish": "Geminin sağ tarafı. Yeşil ışık ile işaretlenir.",
            "definition_english": "Right side of the vessel. Marked with green light.",
            "category": "Navigation",
            "subcategory": "Vessel Parts",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Pruva",
            "term_english": "Bow",
            "term_greek": "Πλώρη (Plori)",
            "definition_turkish": "Geminin ön kısmı.",
            "definition_english": "Front part of the vessel.",
            "category": "Navigation",
            "subcategory": "Vessel Parts",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Kıç",
            "term_english": "Stern",
            "term_greek": "Πρύμνη (Prymni)",
            "definition_turkish": "Geminin arka kısmı.",
            "definition_english": "Rear part of the vessel.",
            "category": "Navigation",
            "subcategory": "Vessel Parts",
            "source": "sg.gov.tr"
        },
        # Safety Equipment
        {
            "term_turkish": "Can Simidi",
            "term_english": "Life Ring / Life Buoy",
            "term_greek": "Σωσίβιο (Sosivio)",
            "definition_turkish": "Denize düşen kişilerin kurtarılması için kullanılan yüzer araç.",
            "definition_english": "Flotation device used to rescue persons who have fallen into water.",
            "category": "Safety Equipment",
            "subcategory": "Rescue",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Can Yeleği",
            "term_english": "Life Jacket",
            "term_greek": "Σωσίβιο γιλέκο (Sosivio gileko)",
            "definition_turkish": "Kişisel yüzme ve kurtarma ekipmanı.",
            "definition_english": "Personal flotation device.",
            "category": "Safety Equipment",
            "subcategory": "Personal",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Fişek",
            "term_english": "Flare",
            "term_greek": "Φωτοβολίδα (Fotovolida)",
            "definition_turkish": "Acil durumlarda konum bildirmek için kullanılan işaret fişeği.",
            "definition_english": "Signaling device used in emergencies to indicate position.",
            "category": "Safety Equipment",
            "subcategory": "Signals",
            "source": "sg.gov.tr"
        },
        # Weather & Sea Conditions
        {
            "term_turkish": "Dalga",
            "term_english": "Wave",
            "term_greek": "Κύμα (Kyma)",
            "definition_turkish": "Denizde rüzgar veya diğer faktörler nedeniyle oluşan su hareketi.",
            "definition_english": "Water movement caused by wind or other factors at sea.",
            "category": "Weather",
            "subcategory": "Sea State",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Akıntı",
            "term_english": "Current",
            "term_greek": "Ρεύμα (Revma)",
            "definition_turkish": "Deniz suyunun belirli bir yönde hareketi.",
            "definition_english": "Movement of sea water in a particular direction.",
            "category": "Weather",
            "subcategory": "Sea State",
            "source": "sg.gov.tr"
        },
        {
            "term_turkish": "Sis",
            "term_english": "Fog",
            "term_greek": "Ομίχλη (Omichli)",
            "definition_turkish": "Görüş mesafesini azaltan yoğun buhar.",
            "definition_english": "Dense vapor that reduces visibility.",
            "category": "Weather",
            "subcategory": "Conditions",
            "source": "sg.gov.tr"
        }
    ]

    for term_data in terms_data:
        # Check if exists
        existing = db.query(MaritimeTerminology).filter(
            MaritimeTerminology.term_turkish == term_data["term_turkish"]
        ).first()

        if not existing:
            term = MaritimeTerminology(**term_data)
            db.add(term)
            logger.info(f"Added maritime term: {term_data['term_turkish']}")

    db.commit()
    logger.info("Maritime terminology seeded successfully")


def main():
    """Main seeding function"""
    logger.info("Starting maritime data seeding...")

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    try:
        # Seed data
        seed_coast_guard_contacts(db)
        seed_maritime_terminology(db)

        logger.info("✅ Maritime data seeding completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error seeding maritime data: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
