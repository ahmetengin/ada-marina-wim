#!/usr/bin/env python3
"""
Voyage Cancellation & Captain Override Demo

Demonstrates:
1. System recommends cancellation for dangerous weather
2. Alternative routes suggested
3. Captain override mechanism (force majeure)

"3. gün fırtına varsa, seferi iptal et. Ama kaptan yine de gidebilir."
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routing.weather_aware_planner import (
    WeatherAwareRoutePlanner,
    VesselType,
    WindDirection
)
from app.integrations.weather_integration import WeatherIntegration
from app.integrations.navigation_integration import NavigationIntegration
from app.privacy.core import AdaSeaPrivacyCore
from app.privacy.consent import ConsentManager
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService


class VoyageCancellationDemo:
    """Demonstrates voyage cancellation and captain override"""

    def __init__(self):
        # Initialize systems
        self.weather = WeatherIntegration()
        self.encryption = EncryptionService()
        self.consent_manager = ConsentManager()
        self.audit_logger = AuditLogger()

        self.privacy_core = AdaSeaPrivacyCore(
            consent_manager=self.consent_manager,
            audit_logger=self.audit_logger,
            encryption_service=self.encryption,
            trusted_partners=['west_istanbul_marina']
        )

        self.navigation = NavigationIntegration(self.privacy_core)
        self.planner = WeatherAwareRoutePlanner(self.weather, self.navigation)

    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    async def demo_scenario_1_safe_weather(self):
        """Scenario 1: Good weather - voyage approved"""
        self.print_header("SENARYO 1: İyi Hava - Sefer Onaylı")

        print("\n📅 Plan: 3 gece Adalar rotası")
        print("🌤️  Hava durumu: Orta rüzgar, güvenli koşullar")

        departure = {
            'name': 'West Istanbul Marina',
            'latitude': 40.9567,
            'longitude': 29.1183,
            'region': 'Marmara Sea - Adalar'
        }

        waypoints = [
            {'name': 'Büyükada', 'latitude': 40.8515, 'longitude': 29.1202},
            {'name': 'Heybeliada', 'latitude': 40.8702, 'longitude': 29.0947},
            {'name': 'Burgazada', 'latitude': 40.8795, 'longitude': 29.0695},
        ]

        recommendation = await self.planner.plan_multi_day_route(
            vessel_name='Phisedelia',
            vessel_type=VesselType.MOTOR,
            vessel_length=65,
            departure=departure,
            waypoints=waypoints,
            nights=3,
            departure_date=datetime.now() + timedelta(days=1)
        )

        print(f"\n📊 Sonuç:")
        print(f"   Güvenli mi: {'✅ EVET' if recommendation.voyage_safe else '❌ HAYIR'}")
        print(f"   İptal önerisi: {'🔴 EVET' if recommendation.cancellation_recommended else '✅ Hayır'}")
        print(f"   Hava özeti: {recommendation.weather_summary}")

        if recommendation.voyage_safe:
            print(f"\n✅ Sefer GÜVENLİ - İyi seyirler!")
        else:
            print(f"\n⚠️ DİKKAT: {recommendation.cancellation_reason}")

    async def demo_scenario_2_dangerous_weather(self):
        """Scenario 2: Dangerous weather - cancellation recommended"""
        self.print_header("SENARYO 2: Tehlikeli Hava - İptal Önerisi")

        print("\n📅 Plan: 3 gece Adalar rotası")
        print("🌪️  Hava durumu: 3. gün 32 knot fırtına bekleniyor")

        # Mock dangerous weather by modifying planner temporarily
        original_limits = self.planner.safety_limits.copy()

        # Simulate: 3rd day will have 32 knot wind
        print("\n🔍 Ada.sea hava durumu analiz ediyor...")
        print("   Gün 1: 15 knot - ✅ Güvenli")
        print("   Gün 2: 18 knot - ✅ Güvenli")
        print("   Gün 3: 32 knot - 🔴 TEHLİKELİ!")

        # Simulate dangerous forecast
        self.planner.safety_limits['wind_dangerous'] = 25  # Lower threshold for demo

        departure = {
            'name': 'West Istanbul Marina',
            'latitude': 40.9567,
            'longitude': 29.1183,
            'region': 'Marmara Sea - Adalar'
        }

        waypoints = [
            {'name': 'Büyükada', 'latitude': 40.8515, 'longitude': 29.1202},
            {'name': 'Heybeliada', 'latitude': 40.8702, 'longitude': 29.0947},
            {'name': 'Burgazada', 'latitude': 40.8795, 'longitude': 29.0695},
        ]

        recommendation = await self.planner.plan_multi_day_route(
            vessel_name='Phisedelia',
            vessel_type=VesselType.MOTOR,
            vessel_length=65,
            departure=departure,
            waypoints=waypoints,
            nights=3,
            departure_date=datetime.now() + timedelta(days=1)
        )

        # Restore limits
        self.planner.safety_limits = original_limits

        print(f"\n📊 Ada.sea Değerlendirmesi:")
        print(f"   Güvenli mi: {'✅ EVET' if recommendation.voyage_safe else '❌ HAYIR'}")
        print(f"   İptal önerisi: {'🔴 EVET' if recommendation.cancellation_recommended else '✅ Hayır'}")

        if recommendation.cancellation_recommended:
            print(f"\n🔴 ADA.SEA ÖNERİSİ:")
            print(f"   {recommendation.cancellation_reason}")
            print(f"\n💡 Kaptan override gerekli: {'EVET' if recommendation.captain_override_required else 'Hayır'}")

        # Show alternatives
        if recommendation.alternative_routes:
            print(f"\n🗺️  ALTERNATİF ROTALAR: {len(recommendation.alternative_routes)} seçenek")

            for i, alt in enumerate(recommendation.alternative_routes, 1):
                print(f"\n   Alternatif {i}:")
                print(f"   • Kalkış: {alt.departure_date if hasattr(alt, 'departure_date') else 'N/A'}")
                print(f"   • Mesafe: {alt.total_distance_nm:.1f} NM")
                print(f"   • Güvenli: {'✅' if alt.voyage_safe else '❌'}")
                print(f"   • Hava: {alt.weather_summary}")

    async def demo_scenario_3_captain_override(self):
        """Scenario 3: Captain override - force majeure"""
        self.print_header("SENARYO 3: Kaptan Override - Force Majeure")

        print("\n🚨 Durum: Acil durum - hasta var, Büyükada'ya gitmemiz şart")
        print("⚠️  Ada.sea: Fırtına nedeniyle seferi iptal etmenizi öneriyoruz")
        print("👨‍✈️  Kaptan: Acil durum, gitmem gerekiyor")

        # Create a cancelled recommendation (mock)
        from app.routing.weather_aware_planner import RouteRecommendation

        dangerous_recommendation = RouteRecommendation(
            vessel_name='Phisedelia',
            vessel_type=VesselType.MOTOR,
            departure='West Istanbul Marina',
            destination='Büyükada',
            segments=[],
            overnight_anchorages=[],
            total_distance_nm=18.0,
            total_time_hours=2.5,
            overall_comfort_score=3.0,
            weather_summary="3 günlük tahmin: Ortalama rüzgar 28 knot (max 32)",
            recommendations=[],
            warnings=["🔴 Kuvvetli fırtına bekleniyor"],
            voyage_safe=False,
            cancellation_recommended=True,
            cancellation_reason="⚠️ TEHLİKELİ: 32 knot rüzgar bekleniyor (Gün 3). Seferi ertelemenizi ÖNERİYORUM.",
            captain_override_required=True,
            captain_override_reason="dangerous_weather"
        )

        print(f"\n🔴 Ada.sea Uyarısı:")
        print(f"   {dangerous_recommendation.cancellation_reason}")

        print(f"\n👨‍✈️  Kaptan override başlatıyor...")

        # Captain override
        override_result = self.planner.captain_override(
            recommendation=dangerous_recommendation,
            captain_id='boss@ada.sea',
            override_reason='Acil tıbbi durum - hasta taşınması gerekiyor',
            force_majeure=True
        )

        print(f"\n✅ Override kabul edildi:")
        print(f"   {override_result['message_tr']}")

        print(f"\n📋 Güvenlik Tavsiyeleri:")
        for rec in override_result['recommendations']:
            print(f"   {rec}")

        print(f"\n📝 Override Log:")
        log = override_result['override_log']
        print(f"   Kaptan: {log['captain_id']}")
        print(f"   Sebep: {log['override_reason']}")
        print(f"   Force Majeure: {'✅ Evet' if log['force_majeure'] else 'Hayır'}")
        print(f"   Riskler kabul edildi: {'✅ Evet' if log['acknowledged_risks'] else 'Hayır'}")

        print(f"\n⚠️  Kaptan sorumluluğu üstlendi - sefer başlıyor")

    async def demo_scenario_4_alternative_routes(self):
        """Scenario 4: Alternative routes calculation"""
        self.print_header("SENARYO 4: Alternatif Rota Hesaplama")

        print("\n📅 Ana Plan: 3 gece, tüm adalar")
        print("⚠️  Problem: 3. gün tehlikeli")
        print("🗺️  Ada.sea alternatif rotalar üretiyor...")

        print(f"\n💡 Alternatif 1: 24 saat erteleme")
        print(f"   • Kalkış: Yarın değil, öbür gün")
        print(f"   • Durum: Fırtına geçtikten sonra")
        print(f"   • Avantaj: Aynı rota, daha güvenli")

        print(f"\n💡 Alternatif 2: 48 saat erteleme")
        print(f"   • Kalkış: 2 gün sonra")
        print(f"   • Durum: Hava tamamen düzelmiş")
        print(f"   • Avantaj: En güvenli seçenek")

        print(f"\n💡 Alternatif 3: Kısa rota")
        print(f"   • Plan: Sadece Büyükada + Heybeliada (2 gece)")
        print(f"   • Durum: Burgazada'yı atlıyoruz")
        print(f"   • Avantaj: Fırtınadan önce dönüyoruz")

        print(f"\n📊 Kaptan seçeneklerden birini seçebilir:")
        print(f"   1️⃣ 24 saat bekle")
        print(f"   2️⃣ 48 saat bekle")
        print(f"   3️⃣ Kısa rotayı seç")
        print(f"   4️⃣ Override ile yine de git (force majeure)")

    async def run_complete_demo(self):
        """Run all scenarios"""
        print("=" * 70)
        print("  SEFER İPTALİ & KAPTAN OVERRIDE DEMONSTRATİF")
        print("  Voyage Cancellation & Captain Override Demo")
        print("=" * 70)
        print("\n💡 'Kaptan ne derse o olur' - AMA Ada.sea önce uyarır!")

        await self.demo_scenario_1_safe_weather()
        await asyncio.sleep(2)

        await self.demo_scenario_2_dangerous_weather()
        await asyncio.sleep(2)

        await self.demo_scenario_3_captain_override()
        await asyncio.sleep(2)

        await self.demo_scenario_4_alternative_routes()

        self.print_header("ÖZET")

        print("\n✅ Ada.sea Güvenlik Sistemi:")
        print("   • Tehlikeli hava durumunu tespit eder")
        print("   • Sefer iptali önerir (30+ knot)")
        print("   • Alternatif rotalar üretir")
        print("   • Kaptan override'a izin verir (force majeure)")
        print("   • Tüm kararları loglar (audit trail)")

        print("\n🎯 Güvenlik Seviyeleri:")
        print("   • 0-15 knot: ✅ Rahat seyir")
        print("   • 15-20 knot: ✅ Konforlu")
        print("   • 20-25 knot: ⚠️  Dikkatli seyir")
        print("   • 25-30 knot: ⚠️  Tehlikeli - iptal önerilir")
        print("   • 30-35 knot: 🔴 Çok tehlikeli - KESİNLİKLE İPTAL")
        print("   • 35+ knot: 🔴 KRİTİK - ASLA GİTMEYİN")

        print("\n👨‍✈️  Kaptan Yetkileri:")
        print("   ✅ Ada.sea'in önerisini dinleyebilir")
        print("   ✅ Override ile yine de gidebilir")
        print("   ✅ Force majeure nedeni belirtebilir")
        print("   ✅ Sorumluluk üstlenir, audit trail kaydedilir")

        print("\n🗺️  Alternatif Rota Seçenekleri:")
        print("   1. Erteleme (24-48 saat)")
        print("   2. Kısa rota (bazı waypoint'leri atla)")
        print("   3. Farklı demirlikler (daha korunaklı)")

        print("\n" + "=" * 70)
        print("  'Deniz şaka değil - ama kaptan karar verir' 🔒")
        print("=" * 70)


async def main():
    """Main entry point"""
    demo = VoyageCancellationDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
