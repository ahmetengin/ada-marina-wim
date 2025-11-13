#!/usr/bin/env python3
"""
Single-Handed MOB Emergency Demo

Critical scenario demonstration:
"Senaryo: teknede sadece bir kişi var... yolo var, hava kötü,
MOB oldu. Tek kişi ise sadece bütün yetenekleri ile kurtarmak
için elinden geleni yapmalı."

Demonstrates:
1. Single-handed operation (captain alone)
2. YOLO detects MOB
3. System realizes vessel is now UNMANNED
4. Autonomous emergency response:
   - Automatic Mayday via VHF DSC
   - Autopilot Williamson Turn
   - Circle MOB position
   - Continuous alerts to Coast Guard
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai.single_handed_mob import (
    SingleHandedMOBEmergency,
    CrewManifestSystem,
    Person,
    PersonRole,
    PersonStatus,
    VesselManifest
)
from app.ai.mob_detection import MOBDetectionSystem
from app.knowledge.maritime_knowledge_base import MaritimeKnowledgeBase


class SingleHandedMOBDemo:
    """Demonstrates single-handed MOB autonomous response"""

    def __init__(self):
        # Initialize systems
        self.vessel_name = "Phisedelia"
        self.mmsi = "271002123"

        # Maritime knowledge base
        self.knowledge_base = MaritimeKnowledgeBase()

        # MOB detection system
        self.mob_detection = MOBDetectionSystem(vessel_name=self.vessel_name)

        # Single-handed MOB emergency system
        self.single_handed_mob = SingleHandedMOBEmergency(
            vessel_name=self.vessel_name,
            mmsi=self.mmsi,
            mob_detection_system=self.mob_detection,
            knowledge_base=self.knowledge_base
        )

        # Crew manifest system
        self.manifest_system = CrewManifestSystem(vessel_name=self.vessel_name)

    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    async def demo_scenario_1_normal_operation(self):
        """Scenario 1: Normal operation with multiple crew"""
        self.print_header("SENARYO 1: Normal Operasyon - Çoklu Mürettebat")

        print("\n📋 Mürettebat listesi oluşturuluyor...")

        # Create manifest with captain + crew
        persons = [
            Person(
                person_id="captain_boss",
                name="Boss (Kaptan)",
                role=PersonRole.CAPTAIN,
                status=PersonStatus.ONBOARD,
                yolo_person_id=1
            ),
            Person(
                person_id="crew_ahmet",
                name="Ahmet (Mürettebat)",
                role=PersonRole.CREW,
                status=PersonStatus.ONBOARD,
                yolo_person_id=2
            ),
            Person(
                person_id="guest_marina",
                name="Marina (Misafir)",
                role=PersonRole.GUEST,
                status=PersonStatus.ONBOARD,
                yolo_person_id=3
            )
        ]

        manifest = self.manifest_system.create_manifest(persons)
        self.single_handed_mob.update_manifest(manifest)

        print(f"\n{self.manifest_system.get_manifest_summary()}")

        print("\n✅ Normal operasyon - 3 kişi teknede")
        print("   MOB durumunda mürettebat kurtarma yapabilir")

    async def demo_scenario_2_crew_goes_ashore(self):
        """Scenario 2: Crew goes ashore - now single-handed"""
        self.print_header("SENARYO 2: Mürettebat Karaya Çıkıyor")

        print("\n🏖️  Büyükada'ya vardık - Ahmet ve Marina karaya çıkıyor...")

        self.manifest_system.person_goes_ashore("crew_ahmet")
        self.manifest_system.person_goes_ashore("guest_marina")

        print(f"\n{self.manifest_system.get_manifest_summary()}")

        print("\n⚠️  Dikkat: Artık tek kişi kaldı (single-handed operation)")
        print("   Ada.sea gelişmiş MOB izleme moduna geçti")

    async def demo_scenario_3_single_handed_mob_emergency(self):
        """Scenario 3: CRITICAL - Single-handed MOB"""
        self.print_header("SENARYO 3: KRİTİK - Tek Kişi MOB Acil Durumu")

        print("\n🌊 Durum:")
        print("   • Teknede sadece kaptan var (tek başına)")
        print("   • Hava kötü - rüzgar 25 knot")
        print("   • Güvertede çalışıyor...")
        print("   • 🚨 KAPTAN DENİZE DÜŞTÜ!")

        await asyncio.sleep(2)

        print("\n📹 YOLO Kamera Sistemi:")
        print("   • Person #1 tracked (Kaptan)")
        print("   • Position: Near stern")
        print("   • Confidence: 0.95")
        print("   • ⚠️ SUDDEN DISAPPEARANCE DETECTED!")
        print("   • 🚨 MOB ALERT!")

        await asyncio.sleep(1)

        # Current vessel state
        current_gps = (40.8515, 29.1202)  # Near Büyükada
        current_heading = 45.0  # NE
        current_speed = 5.5  # 5.5 knots

        print("\n📊 Tekne durumu:")
        print(f"   GPS: {current_gps[0]:.6f}°N, {current_gps[1]:.6f}°E")
        print(f"   Heading: {current_heading:.0f}°")
        print(f"   Speed: {current_speed:.1f} knots")

        await asyncio.sleep(1)

        # Trigger MOB detection
        print("\n🤖 Ada.sea analiz yapıyor...")
        print("   • Manifest: 1 kişi teknede")
        print("   • YOLO: Person #1 kayıp (MOB)")
        print("   • Sonuç: 1 kişi - 1 MOB = 0 kişi teknede")
        print("   • 🚨 TEKNE İNSANSIZ!")

        await asyncio.sleep(1)

        # Process MOB with autonomous response
        await self.single_handed_mob.process_mob_detection(
            yolo_person_id=1,  # Captain's YOLO ID
            current_gps=current_gps,
            current_heading=current_heading,
            current_speed=current_speed
        )

    async def demo_scenario_4_coast_guard_rescue(self):
        """Scenario 4: Coast Guard arrives and rescues"""
        self.print_header("SENARYO 4: Sahil Güvenlik Kurtarma")

        print("\n⏱️  Acil durum başladığından beri 25 dakika geçti...")
        print("\n🚁 Sahil Güvenlik helikopteri yaklaşıyor")
        print("   📻 VHF 16: 'Phisedelia, burada Sahil Güvenlik'")

        await asyncio.sleep(2)

        print("\n🏥 Kurtarma operasyonu:")
        print("   • Helikopter MOB pozisyonuna indi")
        print("   • Kaptanı sudan çıkardılar")
        print("   • Sağlık durumu: İyi, hafif hipotermik")
        print("   • Helikopter tekneye indi")
        print("   • Kaptan tekneye döndü")

        await asyncio.sleep(1)

        # Manual all-clear
        self.single_handed_mob.manual_all_clear(
            recovered_by="Sahil Güvenlik Helikopteri",
            recovery_notes="Kaptan sudan kurtarıldı, hafif hipotermi, tekneye döndü"
        )

        print("\n✅ Acil durum bitti")
        print("   📻 VHF DSC: ALL-CLEAR gönderildi")
        print("   🧭 Autopilot: Normal moda döndü")

        # Captain back onboard
        self.manifest_system.person_returns_onboard("captain_boss")

        print(f"\n{self.manifest_system.get_manifest_summary()}")

    async def demo_scenario_5_what_if_multi_crew(self):
        """Scenario 5: What if there was crew onboard?"""
        self.print_header("SENARYO 5: Peki Ya Mürettebat Olsaydı?")

        print("\n🤔 Alternatif senaryo: Ahmet teknede olsaydı...")

        # Create new manifest with crew
        persons = [
            Person(
                person_id="captain_boss",
                name="Boss (Kaptan)",
                role=PersonRole.CAPTAIN,
                status=PersonStatus.ONBOARD,
                yolo_person_id=1
            ),
            Person(
                person_id="crew_ahmet",
                name="Ahmet (Mürettebat)",
                role=PersonRole.CREW,
                status=PersonStatus.ONBOARD,
                yolo_person_id=2
            )
        ]

        manifest = self.manifest_system.create_manifest(persons)
        self.single_handed_mob.update_manifest(manifest)

        print("\n📋 Yeni manifest:")
        print("   • Kaptan: Boss")
        print("   • Mürettebat: Ahmet")
        print("   • Toplam: 2 kişi")

        print("\n🚨 Kaptan MOB durumunda:")

        # Simulate MOB with crew onboard
        current_gps = (40.8515, 29.1202)
        captain = persons[0]
        captain.status = PersonStatus.MOB

        print("\n📋 STANDART MOB PROSEDÜRÜ (Mürettebat var):")
        print("   1. 'DENİZE ADAM DÜŞTÜ!' diye BAĞIR")
        print("   2. Can simidi FIRLAT")
        print("   3. GPS MOB tuşuna BAS")
        print("   4. Motor - çalıştır")
        print("   5. Williamson Turn yap")
        print("   6. Kaptanı kurtar")

        print("\n⚠️  Fark:")
        print("   • Mürettebat var: Manuel kurtarma")
        print("   • Mürettebat yok: OTOMATİK autonomous response")
        print("   • Ada.sea her durumda yardım eder!")

    async def run_complete_demo(self):
        """Run all scenarios"""
        print("=" * 70)
        print("  TEK KİŞİ MOB ACİL DURUM DEMONSTRATİF")
        print("  Single-Handed MOB Emergency Demo")
        print("=" * 70)
        print("\n🤖 'Tek kişi ise sadece bütün yetenekleri ile kurtarmak için")
        print("    elinden geleni yapmalı' - Ada.sea autonomous response")

        await self.demo_scenario_1_normal_operation()
        await asyncio.sleep(2)

        await self.demo_scenario_2_crew_goes_ashore()
        await asyncio.sleep(2)

        await self.demo_scenario_3_single_handed_mob_emergency()
        await asyncio.sleep(3)

        await self.demo_scenario_4_coast_guard_rescue()
        await asyncio.sleep(2)

        await self.demo_scenario_5_what_if_multi_crew()

        self.print_header("ÖZET")

        print("\n🤖 Ada.sea Single-Handed MOB Sistemi:")
        print("   • YOLO ile kişi takibi")
        print("   • Mürettebat manifest yönetimi")
        print("   • Tek kişi operasyon tespiti")
        print("   • MOB algılandığında: Tekne insansız mı kontrol eder")

        print("\n🚨 Autonomous Emergency Response:")
        print("   1. GPS MOB pozisyon işareti")
        print("   2. Otomatik Mayday (VHF DSC)")
        print("   3. Autopilot - Williamson Turn")
        print("   4. MOB pozisyonuna dönüş")
        print("   5. 50m yarıçapında daire çiz (2 knot)")
        print("   6. Sahil Güvenlik'e sürekli alert")
        print("   7. Kurtarma ekibi gelene kadar bekle")

        print("\n📡 Mayday İçeriği:")
        print("   • Tekne: İsim, MMSI")
        print("   • Pozisyon: GPS koordinatları")
        print("   • Durum: 'Tek kişi MOB - tekne insansız'")
        print("   • Yardım: 'ACİL YARDIM GEREKLİ'")
        print("   • Autopilot: 'Aktif, MOB çevresinde dönüyor'")

        print("\n🎯 Sistem Özellikleri:")
        print("   ✅ Tek kişi operasyonda gelişmiş izleme")
        print("   ✅ YOLO person tracking entegrasyonu (future)")
        print("   ✅ Autonomous autopilot maneuvers")
        print("   ✅ Otomatik VHF DSC Mayday")
        print("   ✅ Sürekli Coast Guard alerts")
        print("   ✅ AIS SART aktivasyonu")

        print("\n👨‍✈️  Çoklu Mürettebat vs Tek Kişi:")
        print("   • Mürettebat var: Standart MOB prosedürü")
        print("   • Tek kişi + MOB: AUTONOMOUS RESPONSE")
        print("   • Ada.sea durumu analiz eder ve uygun aksiyonu alır")

        print("\n🔮 Gelecek Özellikler:")
        print("   • YOLO v8/v9 real-time person detection")
        print("   • Deck camera integration (4 cameras)")
        print("   • Crew face recognition")
        print("   • Apple Neural Engine (Mac Mini M4)")
        print("   • Thermal camera (gece görüşü)")
        print("   • Autopilot interface (actual hardware)")
        print("   • VHF DSC interface (actual radio)")

        print("\n" + "=" * 70)
        print("  'Denizde tek başınayken bile Ada.sea yanınızda' 🤖")
        print("=" * 70)


async def main():
    """Main entry point"""
    demo = SingleHandedMOBDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
