#!/usr/bin/env python3
"""
ADA.SEA Smart Privacy Demo
Demonstrates AIS-aware privacy system

Key Concepts:
1. PUBLIC_AIS data (already broadcast) - no approval needed
2. Trusted partners (contracted marinas) - simplified approval
3. Private data (financial, crew) - strict approval required
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.privacy.core import AdaSeaPrivacyCore, DataClassification
from app.privacy.consent import ConsentManager, ConsentMethod
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService
from app.integrations.marina_integration import MarinaIntegration


class SmartPrivacyDemo:
    """Demonstrates smart privacy with AIS awareness"""

    def __init__(self):
        # Initialize privacy system with trusted partners
        self.encryption_service = EncryptionService()
        self.consent_manager = ConsentManager()
        self.audit_logger = AuditLogger()

        # Initialize with West Istanbul Marina as trusted partner
        self.privacy_core = AdaSeaPrivacyCore(
            consent_manager=self.consent_manager,
            audit_logger=self.audit_logger,
            encryption_service=self.encryption_service,
            trusted_partners=[
                'west_istanbul_marina',
                'buyukada_marina',
                'yalikavak_marina'
            ]
        )

        self.marina_integration = MarinaIntegration(
            privacy_core=self.privacy_core,
            marina_api_endpoint="https://api.west-istanbul-marina.com"
        )

    def print_section(self, title: str):
        """Print section header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    async def demo_1_ais_public_data(self):
        """
        Demo 1: Sharing AIS public data
        No approval needed - already broadcast on AIS
        """
        self.print_section("DEMO 1: AIS Public Data (No Approval Needed)")

        print("\n📡 Scenario: Marina wants vessel position")
        print("   This is already broadcast on AIS (Marine Traffic shows it)")

        # Share current position (already AIS public)
        result = await self.privacy_core.share_data(
            destination="Marina: west_istanbul_marina",
            data={
                'current_position': {'latitude': 40.9567, 'longitude': 29.1183},
                'vessel_name': 'Phisedelia',
                'vessel_specifications': {'length': 65, 'beam': 18, 'draft': 2.4}
            },
            data_type='current_position',  # PUBLIC_AIS
            purpose='marina_check_in',
            captain_id='boss@ada.sea'
        )

        print(f"\n✅ Result: {result['success']}")
        print(f"   Reason: AIS data already public - no captain approval needed")
        print(f"   Audit: Transfer logged for transparency")
        print(f"   Transfer ID: {result.get('transfer_id', 'N/A')}")

    async def demo_2_trusted_marina(self):
        """
        Demo 2: Trusted partner (contracted marina)
        Simplified approval for non-sensitive data
        """
        self.print_section("DEMO 2: Trusted Marina (Simplified Approval)")

        print("\n🤝 Scenario: Check-in to West Istanbul Marina")
        print("   Marina is contracted partner - you already have business relationship")
        print("   Sharing: Berth number + arrival time (non-sensitive)")

        result = await self.privacy_core.share_data(
            destination="Marina: west_istanbul_marina",
            data={
                'berth_number': 'C-42',
                'arrival_time': '2025-11-13T10:00:00Z',
                'vessel_name': 'Phisedelia'  # AIS public
            },
            data_type='berth_number',  # RESTRICTED
            purpose='check_in_confirmation',
            captain_id='boss@ada.sea'
        )

        print(f"\n✅ Result: {result['success']}")
        print(f"   Reason: Trusted partner + non-sensitive data")
        print(f"   Note: Still audited for complete transparency")

    async def demo_3_private_data_requires_approval(self):
        """
        Demo 3: Private financial data
        STRICT approval required - NOT on AIS, NOT public
        """
        self.print_section("DEMO 3: Private Financial Data (Strict Approval)")

        print("\n🔒 Scenario: Marina requests payment information")
        print("   This is PRIVATE data - NOT on AIS")
        print("   Requires explicit captain approval via voice/biometric")

        # Grant permission first (simulate captain approval)
        permission = self.consent_manager.grant_permission(
            request_id='financial_001',
            captain_id='boss@ada.sea',
            method=ConsentMethod.VOICE,
            confirmation_text="Evet, ödeme bilgisini paylaş"
        )

        print(f"\n🎤 Captain: 'Evet, ödeme bilgisini paylaş'")
        print(f"   Permission granted: {permission.granted}")

        result = await self.privacy_core.share_data(
            destination="Marina: west_istanbul_marina",
            data={
                'payment_method': 'credit_card',
                'last_4_digits': '****',
                'invoice_email': 'billing@example.com'
            },
            data_type='financial_data',  # PRIVATE
            purpose='marina_payment',
            captain_id='boss@ada.sea'
        )

        print(f"\n✅ Result: {result['success']}")
        print(f"   Reason: Captain explicitly approved via voice")
        print(f"   Audit: Full trail of approval + transfer")

    async def demo_4_comparison(self):
        """Show comparison between data types"""
        self.print_section("COMPARISON: Privacy Levels")

        print("\n📊 Data Classification Summary:")
        print("\n1. PUBLIC_AIS (No Approval Needed)")
        print("   ✅ Vessel name, MMSI")
        print("   ✅ Current GPS position")
        print("   ✅ Vessel dimensions (length/beam/draft)")
        print("   ✅ Speed, heading, course")
        print("   → Already broadcast on AIS 24/7")
        print("   → No additional privacy risk")

        print("\n2. RESTRICTED (Trusted Partner: Simplified)")
        print("   ⚠️  Berth assignments")
        print("   ⚠️  Arrival/departure times")
        print("   ⚠️  Contact information")
        print("   → Contracted marina already knows you")
        print("   → Business relationship exists")

        print("\n3. PRIVATE (Always Strict Approval)")
        print("   🔒 Financial data (payment info)")
        print("   🔒 Crew personal information")
        print("   🔒 GPS history (not current position)")
        print("   🔒 Insurance information")
        print("   🔒 Medical information")
        print("   → NEVER on AIS")
        print("   → Requires explicit captain approval ALWAYS")

    async def demo_5_adalar_route(self):
        """Demo for Adalar route planning"""
        self.print_section("DEMO 5: Adalar Route - Smart Privacy")

        print("\n🚤 Scenario: Planning 3-day Adalar route")
        print("   Starting: West Istanbul Marina")
        print("   Route: Büyükada → Heybeliada → Burgazada")

        # 1. Weather request (anonymous)
        print("\n1️⃣ Weather Forecast Request")
        print("   Data: Region only (Marmara - Adalar)")
        print("   Classification: ANONYMOUS")
        print("   Approval: Not needed (no vessel identification)")
        print("   ✅ No privacy concerns")

        # 2. Marina check-out (AIS public + trusted partner)
        print("\n2️⃣ West Istanbul Marina Check-out")
        result = await self.privacy_core.share_data(
            destination="Marina: west_istanbul_marina",
            data={
                'vessel_name': 'Phisedelia',  # AIS public
                'departure_time': '2025-11-13T09:00:00Z',
                'destination': 'Büyükada'  # AIS destination field
            },
            data_type='vessel_name',  # PUBLIC_AIS
            purpose='check_out',
            captain_id='boss@ada.sea'
        )
        print(f"   Classification: PUBLIC_AIS")
        print(f"   Approval: Not needed (AIS data)")
        print(f"   Result: ✅ {result['success']}")

        # 3. Büyükada Marina info request (anonymous)
        print("\n3️⃣ Büyükada Marina Info Request")
        print("   Data: None (just querying services)")
        print("   Classification: ANONYMOUS")
        print("   Approval: Not needed")
        print("   ✅ Just reading public information")

        print("\n🎯 Summary: Smart Privacy for Adalar Route")
        print("   • Weather: Anonymous ✅")
        print("   • Check-out: AIS public data ✅")
        print("   • Marina info: Public query ✅")
        print("   • No captain approvals needed!")
        print("   • All transactions audited for transparency")

    async def run_all_demos(self):
        """Run all demos"""
        print("=" * 60)
        print("  ADA.SEA SMART PRIVACY DEMONSTRATION")
        print("  AIS-Aware Privacy Architecture")
        print("=" * 60)
        print("\n🔒 'Kaptan ne derse o olur. Nokta.'")
        print("   But we're smart about what needs approval!\n")

        await self.demo_1_ais_public_data()
        await asyncio.sleep(1)

        await self.demo_2_trusted_marina()
        await asyncio.sleep(1)

        await self.demo_3_private_data_requires_approval()
        await asyncio.sleep(1)

        await self.demo_4_comparison()
        await asyncio.sleep(1)

        await self.demo_5_adalar_route()

        print("\n" + "=" * 60)
        print("  DEMO COMPLETE")
        print("=" * 60)
        print("\n✅ Smart Privacy = Better UX + Strong Security")
        print("   • AIS public data: No friction")
        print("   • Trusted partners: Simplified")
        print("   • Private data: Protected")
        print("\n🎯 Ready for production testing!")


async def main():
    """Main entry point"""
    demo = SmartPrivacyDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())
