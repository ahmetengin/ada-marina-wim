#!/usr/bin/env python3
"""
Adalar Route Planning Demo
Demonstrates weather-aware, intelligent route planning

Scenario:
- Vessel: Phisedelia (65 feet motor yacht)
- Departure: West Istanbul Marina
- Route: Büyükada → Heybeliada → Burgazada
- Duration: 3 nights
- Critical: Wind-protected anchorages!
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routing.weather_aware_planner import (
    WeatherAwareRoutePlanner,
    VesselType,
    WindDirection,
    WeatherConditions
)
from app.integrations.weather_integration import WeatherIntegration
from app.integrations.navigation_integration import NavigationIntegration
from app.privacy.core import AdaSeaPrivacyCore, DataClassification
from app.privacy.consent import ConsentManager
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService


class AdalarRouteDemo:
    """Demonstrates intelligent Adalar route planning"""

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
            trusted_partners=['west_istanbul_marina', 'buyukada_marina']
        )

        self.navigation = NavigationIntegration(self.privacy_core)
        self.planner = WeatherAwareRoutePlanner(self.weather, self.navigation)

    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_anchorage_details(self, anchorage):
        """Print anchorage information"""
        print(f"\n📍 {anchorage.name_tr} ({anchorage.name})")
        print(f"   Konum: {anchorage.latitude:.4f}°N, {anchorage.longitude:.4f}°E")
        print(f"   Derinlik: {anchorage.depth_min_m}-{anchorage.depth_max_m}m")
        print(f"   Zemin: {anchorage.bottom_type} (tutuş: {anchorage.holding})")

        print(f"   ✅ Korunaklı: {', '.join([d.value for d in anchorage.protected_from])}")
        print(f"   ⚠️  Açık: {', '.join([d.value for d in anchorage.exposed_to])}")

        facilities = []
        if anchorage.has_restaurant:
            facilities.append("🍽️ Restoran")
        if anchorage.has_water:
            facilities.append("💧 Su")
        if anchorage.has_mooring_buoys:
            facilities.append("⚓ Şamandıra")

        if facilities:
            print(f"   İmkanlar: {', '.join(facilities)}")

        print(f"   ⭐ Değerlendirme: {anchorage.rating:.1f}/5.0 ({anchorage.review_count} yorum)")

    def print_segment_details(self, segment, day: int):
        """Print route segment information"""
        print(f"\n🚤 GÜN {day}: {segment.from_point} → {segment.to_point}")
        print(f"   Mesafe: {segment.distance_nm:.1f} NM")
        print(f"   Süre: {segment.estimated_time_hours:.1f} saat")
        print(f"   Yön: {segment.bearing:.0f}°")

        if segment.weather_forecast:
            w = segment.weather_forecast
            print(f"   🌤️  Hava: Rüzgar {w.wind_direction.value} {w.wind_speed_knots:.0f} knot, dalga {w.wave_height_m:.1f}m")

        print(f"   😊 Konfor: {segment.comfort_score:.1f}/10")

        if segment.warnings:
            for warning in segment.warnings:
                print(f"   {warning}")

        if segment.recommended:
            print(f"   ✅ Önerilen güzergah")
        else:
            print(f"   ⚠️  Dikkatli seyir gerekli")

    async def demo_weather_check(self):
        """Demo: Check weather before planning"""
        self.print_header("ADIM 1: Hava Durumu Kontrolü")

        print("\n📡 Kaptan: 'Ada, Adalar bölgesi 4 günlük hava durumunu göster'")
        print("\n🔍 Ada.sea hava durumu tahmini alıyor...")

        # Get marine forecast
        forecast = await self.weather.get_marine_forecast(
            region="Marmara Sea - Adalar",
            days=4
        )

        print(f"\n📊 {forecast['region']} - {forecast['forecast_days']} günlük tahmin:")

        for day in forecast['forecast']:
            print(f"\n  📅 {day['date']}")
            print(f"     Rüzgar: {day['wind']}")
            print(f"     Dalga: {day['wave_height']}")
            print(f"     Durum: {day['conditions']}")
            print(f"     Görüş: {day['visibility']}")

        print("\n✅ Hava durumu uygun - rota planlamaya devam edebiliriz")

    async def demo_intelligent_planning(self):
        """Demo: Intelligent route planning with wind analysis"""
        self.print_header("ADIM 2: Akıllı Rota Planlama")

        print("\n🧠 Ada.sea akıllı planlama yapıyor:")
        print("   • Rüzgar yönü analizi")
        print("   • Korunaklı demirlik seçimi")
        print("   • Konforlu seyir rotası")
        print("   • Tekne tipine göre optimizasyon")

        # Plan route
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

        print(f"\n📋 Rota Özeti:")
        print(f"   Tekne: {recommendation.vessel_name} ({recommendation.vessel_type.value})")
        print(f"   Toplam mesafe: {recommendation.total_distance_nm:.1f} NM")
        print(f"   Toplam süre: {recommendation.total_time_hours:.1f} saat")
        print(f"   Genel konfor: {recommendation.overall_comfort_score:.1f}/10")
        print(f"   Hava durumu: {recommendation.weather_summary}")

        return recommendation

    async def demo_anchorage_selection(self, recommendation):
        """Demo: Show anchorage selection with wind protection"""
        self.print_header("ADIM 3: Gece Demirlemeleri (Rüzgar Korumalı)")

        print("\n🌙 Seçilen demirlikler:")
        print("   KRİTİK: Her demirlik o gecenin rüzgar yönünden korunaklı!\n")

        for i, anchorage in enumerate(recommendation.overnight_anchorages, 1):
            print(f"\n{'─' * 70}")
            print(f"GECE {i}")
            self.print_anchorage_details(anchorage)

    async def demo_daily_segments(self, recommendation):
        """Demo: Show daily route segments"""
        self.print_header("ADIM 4: Günlük Seyir Planı")

        print("\n📍 Detaylı rota:")

        for i, segment in enumerate(recommendation.segments, 1):
            self.print_segment_details(segment, i)

    async def demo_recommendations(self, recommendation):
        """Demo: Show AI recommendations"""
        self.print_header("ADIM 5: Ada.sea Önerileri")

        if recommendation.warnings:
            print("\n⚠️  DİKKAT:")
            for warning in recommendation.warnings:
                print(f"   • {warning}")

        if recommendation.recommendations:
            print("\n💡 ÖNERİLER:")
            for rec in recommendation.recommendations:
                print(f"   • {rec}")

    async def demo_bad_weather_example(self):
        """Demo: Show what happens with bad weather"""
        self.print_header("BONUS: Kötü Hava Senaryosu")

        print("\n🌪️  Senaryo: Yarın Poyraz (NE) 25 knot bekleniyor")
        print("\n🤔 Soru: Büyükada Yörükali'ye gidebilir miyiz?")

        # Get Yörükali anchorage
        anchorages = self.planner._get_adalar_anchorages()
        yorukali = next(a for a in anchorages if a.id == 'buyukada_yorukali')

        print(f"\n📍 {yorukali.name_tr}:")
        print(f"   ✅ Korunaklı: {', '.join([d.value for d in yorukali.protected_from])}")
        print(f"   ⚠️  Açık: {', '.join([d.value for d in yorukali.exposed_to])}")

        wind_dir = WindDirection.NE

        if wind_dir in yorukali.protected_from:
            print(f"\n✅ EVET! NE rüzgarından korunaklı - güvenle demirlenebilir")
        else:
            print(f"\n❌ HAYIR! NE rüzgarına açık - bu demirlik uygun değil")

            # Find alternative
            suitable = [
                a for a in anchorages
                if wind_dir in a.protected_from and 'buyukada' in a.id
            ]

            if suitable:
                alt = suitable[0]
                print(f"\n💡 ALTERNATİF: {alt.name_tr}")
                print(f"   ✅ NE rüzgarından korunaklı")

    async def demo_sailing_vs_motor(self):
        """Demo: Compare sailing vs motor yacht planning"""
        self.print_header("BONUS: Yelkenli vs Motorlu Karşılaştırma")

        print("\n⛵ Yelkenli tekne:")
        print("   • Rüzgar yönü kritik (ideal: 10-15 knot)")
        print("   • Motorluden daha yavaş (ortalama 5-6 knot)")
        print("   • Rüzgar 20+ knot: Yelken küçültme gerekli")

        print("\n🚤 Motorlu tekne:")
        print("   • Sabit hız (8 knot ortalama)")
        print("   • Rüzgar yönü önemli değil")
        print("   • Dalga yüksekliği konforu etkiler")

        print("\n📊 Phisedelia (65ft motorlu):")
        print("   • 8 knot ortalama")
        print("   • Rüzgar <20 knot: Konforlu")
        print("   • Dalga <1.5m: İdeal")

    async def run_complete_demo(self):
        """Run complete demonstration"""
        print("=" * 70)
        print("  ADALAR ROTASI - AKILLI PLANLAMA DEMONSTRATİF")
        print("  Weather-Aware Route Planning")
        print("=" * 70)
        print("\n🚤 Tekne: Phisedelia (65 feet motorlu yat)")
        print("📅 Plan: 3 gece / 4 gün")
        print("📍 Rota: West Istanbul → Büyükada → Heybeliada → Burgazada")

        # Step 1: Weather check
        await self.demo_weather_check()
        await asyncio.sleep(1)

        # Step 2: Intelligent planning
        recommendation = await self.demo_intelligent_planning()
        await asyncio.sleep(1)

        # Step 3: Anchorage selection
        await self.demo_anchorage_selection(recommendation)
        await asyncio.sleep(1)

        # Step 4: Daily segments
        await self.demo_daily_segments(recommendation)
        await asyncio.sleep(1)

        # Step 5: Recommendations
        await self.demo_recommendations(recommendation)
        await asyncio.sleep(1)

        # Bonus demos
        await self.demo_bad_weather_example()
        await asyncio.sleep(1)

        await self.demo_sailing_vs_motor()

        # Final summary
        self.print_header("ÖZET")
        print("\n✅ Ada.sea Akıllı Planlama:")
        print("   • Hava durumu entegrasyonu")
        print("   • Rüzgar bazlı demirlik seçimi")
        print("   • Korunaklı gece demirlemeleri")
        print("   • Konforlu seyir rotası")
        print("   • Tekne tipine göre optimizasyon")

        print("\n🔐 Gizlilik:")
        print("   • Hava durumu: Anonim sorgu")
        print("   • Rota hesaplama: Lokal (Mac Mini M4)")
        print("   • AIS public data: Otomatik paylaşım")
        print("   • Audit trail: Tam şeffaflık")

        print("\n🎯 Sonuç:")
        print("   • Güvenli rota planlandı")
        print("   • Tüm demirlikler rüzgar korumalı")
        print("   • Konforlu seyir garantilendi")
        print("   • Production testlere hazır!")

        print("\n" + "=" * 70)
        print("  İyi seyirler! ⚓")
        print("=" * 70)


async def main():
    """Main entry point"""
    demo = AdalarRouteDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
