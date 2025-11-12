#!/usr/bin/env python3
"""
ADA.SEA Production Demo Script
Comprehensive demonstration of privacy-first architecture

Run this for production testing and investor demos
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.privacy.core import AdaSeaPrivacyCore, DataClassification
from app.privacy.consent import ConsentManager, ConsentMethod, ConsentDuration
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService, ZeroKnowledgeBackup
from app.privacy.captain_control import CaptainControlInterface
from app.privacy.compliance import KVKKCompliance, GDPRCompliance
from app.integrations.marina_integration import MarinaIntegration
from app.integrations.weather_integration import WeatherIntegration
from app.integrations.navigation_integration import NavigationIntegration


class ProductionDemo:
    """Production demonstration scenarios"""

    def __init__(self):
        """Initialize demo with privacy system"""
        print("🔒 ADA.SEA Production Demo - Privacy-First Architecture")
        print("=" * 60)
        print()

        # Initialize privacy components
        self.encryption_service = EncryptionService()
        self.audit_logger = AuditLogger()
        self.consent_manager = ConsentManager(voice_enabled=True)
        self.backup_system = ZeroKnowledgeBackup(self.encryption_service)

        self.privacy_core = AdaSeaPrivacyCore(
            consent_manager=self.consent_manager,
            audit_logger=self.audit_logger,
            encryption_service=self.encryption_service,
            captain_auth_required=True,
            cloud_sync_enabled=False,
            edge_only_mode=True
        )

        self.captain_control = CaptainControlInterface(
            privacy_core=self.privacy_core,
            consent_manager=self.consent_manager,
            audit_logger=self.audit_logger,
            backup_system=self.backup_system,
            default_language="tr"
        )

        # Initialize integrations
        self.marina_integration = MarinaIntegration(
            privacy_core=self.privacy_core,
            marina_api_endpoint="https://api.west-istanbul-marina.com"
        )
        self.weather_integration = WeatherIntegration()
        self.navigation_integration = NavigationIntegration(self.privacy_core)

        # Compliance
        self.kvkk_compliance = KVKKCompliance(self.audit_logger, self.consent_manager)
        self.gdpr_compliance = GDPRCompliance(self.audit_logger, self.consent_manager)

        print("✓ Privacy system initialized")
        print(f"✓ Edge-only mode: {self.privacy_core.edge_only_mode}")
        print(f"✓ Cloud sync: {self.privacy_core.cloud_sync_enabled}")
        print()

    async def demo_scenario_1_marina_checkin(self):
        """
        Scenario 1: West Istanbul Marina Check-in
        Demonstrates: Explicit consent, minimal data, audit trail
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 1: West Istanbul Marina Check-in")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"
        vessel_name = "Phisedelia"

        print("🎤 Captain: 'Ada, West Istanbul Marina'ya check-in yap'")
        print()

        # 1. Captain control processes voice command
        print("📱 Ada.sea:")
        print("   Marina'ya şu bilgileri göndermem gerekiyor:")
        print("   • Tekne: Phisedelia")
        print("   • Uzunluk: 65 feet")
        print("   • Berth: C-42")
        print()
        print("   Onaylıyor musunuz?")
        print()

        # 2. Simulate captain approval
        print("🎤 Captain: 'Evet paylaş'")
        print()

        # Grant permission
        permission = self.consent_manager.grant_permission(
            request_id='checkin_request_001',
            captain_id=captain_id,
            method=ConsentMethod.VOICE,
            duration=ConsentDuration.ONE_TIME,
            confirmation_text="Evet paylaş"
        )

        # 3. Execute check-in
        result = await self.marina_integration.check_in(
            marina_id='west_istanbul_marina',
            berth_number='C-42',
            vessel_name=vessel_name,
            current_position=None,  # Not sharing position
            captain_id=captain_id
        )

        if result['success']:
            print("✅ Ada.sea: 'Check-in tamamlandı.'")
            print(f"   Confirmation: {result['confirmation']}")
            print()

        # 4. Show audit trail
        print("📊 Audit Trail:")
        summary = self.audit_logger.get_audit_summary(captain_id, days=1)
        print(f"   • Total transfers: {summary['total_transfers']}")
        print(f"   • Successful: {summary['successful_transfers']}")
        print()

        print("🔐 Data Shared:")
        print("   ✓ Vessel name: Phisedelia")
        print("   ✓ Berth number: C-42")
        print()
        print("🚫 Data NOT Shared:")
        print("   ✗ GPS history")
        print("   ✗ Crew information")
        print("   ✗ Financial data")
        print()

    async def demo_scenario_2_yalikavak_reservation(self):
        """
        Scenario 2: Yalikavak Marina Reservation
        Demonstrates: Privacy-safe reservation, data minimization
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 2: Yalikavak Marina Reservation")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"

        print("🎤 Captain: 'Kanal 72, Yalikavak Marina'da berth reserve et'")
        print()

        # 1. Request reservation
        arrival_date = datetime.utcnow() + timedelta(days=1)

        print("📱 Ada.sea:")
        print("   Yalikavak Marina'ya rezervasyon için şu bilgileri")
        print("   göndermem gerekiyor:")
        print("   • Tekne uzunluğu: 65 feet")
        print("   • Varış tarihi: Yarın saat 14:00")
        print("   • Süre: 2 gece")
        print()
        print("   Onaylıyor musunuz?")
        print()

        print("🎤 Captain: 'Evet, paylaş'")
        print()

        # Grant permission
        permission = self.consent_manager.grant_permission(
            request_id='yalikavak_reservation_001',
            captain_id=captain_id,
            method=ConsentMethod.VOICE,
            duration=ConsentDuration.ONE_TIME
        )

        # 2. Execute reservation
        result = await self.marina_integration.privacy_safe_reservation(
            marina_id='yalikavak_marina',
            vessel_length=65,
            arrival_date=arrival_date,
            duration_nights=2,
            captain_id=captain_id,
            include_contact=False
        )

        if result['success']:
            print("✅ Ada.sea: 'Rezervasyon talebi gönderildi.'")
            print(f"   Reservation ID: {result['reservation_id']}")
            print()

        print("📊 Privacy Report:")
        print(f"   Data shared: {', '.join(result['data_shared'])}")
        print(f"   NOT shared: {', '.join(result['NOT_shared'])}")
        print()

    async def demo_scenario_3_privacy_status(self):
        """
        Scenario 3: Privacy Status Check
        Demonstrates: Captain control interface, transparency
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 3: Privacy Status Check")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"

        print("🎤 Captain: 'Ada, gizlilik durumunu göster'")
        print()

        # Get privacy status
        status = await self.captain_control.show_privacy_status(
            captain_id=captain_id,
            language="tr"
        )

        print(status['message'])
        print()

    async def demo_scenario_4_anonymous_weather(self):
        """
        Scenario 4: Anonymous Weather Request
        Demonstrates: Privacy-safe external services
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 4: Anonymous Weather Request")
        print("="*60)
        print()

        print("🎤 Captain: 'Ada, hava durumu bilgisi al'")
        print()

        # Get weather (anonymous)
        weather = await self.weather_integration.get_current_weather(
            latitude=40.9833,
            longitude=28.9784,
            anonymous=True
        )

        print("📱 Ada.sea:")
        print(f"   📍 Location: {weather['location']['latitude']}, {weather['location']['longitude']}")
        print(f"      (Accuracy: {weather['location']['accuracy']})")
        print()
        print("   🌤️  Weather:")
        print(f"      Temperature: {weather['weather']['temperature_c']}°C")
        print(f"      Conditions: {weather['weather']['conditions']}")
        print(f"      Wind: {weather['weather']['wind_speed_knots']} knots {weather['weather']['wind_direction']}")
        print()
        print(f"   🔐 Privacy: {weather['privacy_note']}")
        print(f"   🔒 Anonymous: {weather['anonymous']}")
        print()

    async def demo_scenario_5_kvkk_compliance(self):
        """
        Scenario 5: KVKK Compliance (Data Access Request)
        Demonstrates: Data subject rights, compliance
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 5: KVKK Compliance - Access Request")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"

        print("🎤 Captain: 'Ada, tüm kişisel verilerimi göster' (KVKK Article 11)")
        print()

        # KVKK access request
        access_data = await self.kvkk_compliance.handle_access_request(captain_id)

        print("📱 Ada.sea: KVKK Veri Erişim Raporu")
        print()
        print(f"   Captain ID: {access_data['captain_id']}")
        print(f"   Request Type: {access_data['request_type']}")
        print(f"   Processed: {access_data['processed_at']}")
        print()
        print("   Data Holdings:")
        print(f"   • Transfer logs: {len(access_data['data']['transfer_logs'])} records")
        print(f"   • Consent history: {len(access_data['data']['consent_history'])} records")
        print(f"   • Active permissions: {access_data['data']['active_permissions']}")
        print()
        print("   Data Controller:")
        print(f"   • Name: {access_data['data_controller']['name']}")
        print(f"   • Contact: {access_data['data_controller']['contact']}")
        print(f"   • DPO: {access_data['data_controller']['dpo']}")
        print()

    async def demo_scenario_6_revoke_all(self):
        """
        Scenario 6: Revoke All Permissions
        Demonstrates: Captain control, immediate effect
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 6: Revoke All Permissions")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"

        print("🎤 Captain: 'Ada, tüm paylaşımları iptal et'")
        print()

        # Revoke all permissions
        result = await self.captain_control.revoke_all_permissions(
            captain_id=captain_id,
            language="tr"
        )

        print(f"📱 Ada.sea: {result['message']}")
        print()

    async def demo_scenario_7_audit_export(self):
        """
        Scenario 7: Export Audit Trail
        Demonstrates: Data portability, compliance
        """
        print("\n" + "="*60)
        print("📍 SCENARIO 7: Export Audit Trail (Data Portability)")
        print("="*60)
        print()

        captain_id = "boss@ada.sea"

        print("🎤 Captain: 'Ada, veri paylaşım geçmişini dışa aktar'")
        print()

        # Export audit trail
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()

        export = await self.audit_logger.export_audit_trail(
            captain_id=captain_id,
            start_date=start_date,
            end_date=end_date,
            format="json"
        )

        print("📱 Ada.sea: Audit trail exported")
        print()
        print(f"   Format: JSON")
        print(f"   Period: {start_date.date()} to {end_date.date()}")
        print(f"   Size: {len(export)} bytes")
        print()
        print("   ✓ Ready for download")
        print("   ✓ KVKK Article 11 compliant (data portability)")
        print()

    async def run_all_scenarios(self):
        """Run all demo scenarios"""
        print("\n")
        print("🚀 ADA.SEA PRODUCTION DEMO")
        print("Privacy-First Maritime Platform")
        print()
        print("Demo Vessel: Phisedelia (65 feet)")
        print("Captain: boss@ada.sea")
        print("Location: West Istanbul Marina → Yalikavak Marina")
        print()

        input("Press ENTER to start demo...")

        try:
            await self.demo_scenario_1_marina_checkin()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_2_yalikavak_reservation()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_3_privacy_status()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_4_anonymous_weather()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_5_kvkk_compliance()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_6_revoke_all()
            input("\nPress ENTER for next scenario...")

            await self.demo_scenario_7_audit_export()

            # Summary
            print("\n" + "="*60)
            print("✅ DEMO COMPLETE")
            print("="*60)
            print()
            print("Key Takeaways:")
            print()
            print("1. ✓ Zero-Trust Architecture")
            print("   Every data transfer requires captain approval")
            print()
            print("2. ✓ Data Minimization")
            print("   Only essential data shared, nothing more")
            print()
            print("3. ✓ Complete Audit Trail")
            print("   Full transparency and accountability")
            print()
            print("4. ✓ Captain Control")
            print("   Voice commands in Turkish for privacy management")
            print()
            print("5. ✓ KVKK/GDPR Compliant")
            print("   Data subject rights fully implemented")
            print()
            print("6. ✓ Edge-First Computing")
            print("   Data stays on device (Mac Mini M4)")
            print()
            print("7. ✓ Zero-Knowledge Backup")
            print("   Optional encrypted backup (client-side only)")
            print()
            print('"Kaptan ne derse o olur. Nokta."')
            print()

        except Exception as e:
            print(f"\n❌ Error during demo: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point"""
    demo = ProductionDemo()
    await demo.run_all_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
