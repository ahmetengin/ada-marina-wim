"""
Privacy-Safe Marina Integration
Connects with ADA.MARINA while respecting captain's privacy
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MarinaIntegration:
    """
    Privacy-safe integration with marina systems (ADA.MARINA)

    Key Principles:
    - Explicit captain approval required
    - Minimal data transfer
    - No automatic sync
    - Complete audit trail
    """

    def __init__(self, privacy_core, marina_api_endpoint: str):
        """
        Initialize marina integration

        Args:
            privacy_core: AdaSeaPrivacyCore instance
            marina_api_endpoint: Marina API endpoint
        """
        self.privacy_core = privacy_core
        self.marina_api_endpoint = marina_api_endpoint
        self.trusted_destination = True  # Ada ecosystem

        logger.info(f"MarinaIntegration initialized: {marina_api_endpoint}")

    async def request_berth_assignment(
        self,
        marina_id: str,
        vessel_specs: Dict[str, Any],
        arrival_time: datetime,
        captain_id: str
    ) -> Dict[str, Any]:
        """
        Request berth assignment from marina

        CRITICAL: Requires captain approval

        Args:
            marina_id: Marina identifier
            vessel_specs: Vessel specifications
            arrival_time: Expected arrival time
            captain_id: Captain identifier

        Returns:
            Assignment result
        """
        logger.info(f"Berth assignment request for marina {marina_id}")

        # 1. Prepare minimal data (ONLY what's needed)
        minimal_data = {
            'vessel_length': vessel_specs.get('length'),
            'vessel_beam': vessel_specs.get('beam'),
            'vessel_draft': vessel_specs.get('draft'),
            'arrival_time': arrival_time.isoformat()
            # NO: GPS coordinates, owner info, financial data
        }

        # 2. Request captain permission via privacy core
        result = await self.privacy_core.share_data(
            destination=f"Marina: {marina_id}",
            data=minimal_data,
            data_type='vessel_specifications',
            purpose='berth_assignment',
            captain_id=captain_id
        )

        if not result['success']:
            return {
                'success': False,
                'reason': 'Captain denied permission',
                'details': result.get('details')
            }

        # 3. If approved, execute API call
        # In production, this would be actual HTTP request
        berth_assignment = await self._call_marina_api(
            marina_id=marina_id,
            endpoint='berth-assignments',
            data=minimal_data
        )

        return {
            'success': True,
            'marina_id': marina_id,
            'berth_number': berth_assignment.get('berth_number'),
            'confirmation_code': berth_assignment.get('confirmation'),
            'data_shared': list(minimal_data.keys()),
            'transfer_id': result.get('transfer_id')
        }

    async def check_in(
        self,
        marina_id: str,
        berth_number: str,
        vessel_name: str,
        current_position: Optional[Dict[str, float]],
        captain_id: str
    ) -> Dict[str, Any]:
        """
        Check in to marina

        Args:
            marina_id: Marina identifier
            berth_number: Assigned berth
            vessel_name: Vessel name
            current_position: Current GPS (optional, requires consent)
            captain_id: Captain identifier

        Returns:
            Check-in confirmation
        """
        logger.info(f"Check-in to marina {marina_id}, berth {berth_number}")

        # Base data (always needed)
        check_in_data = {
            'vessel_name': vessel_name,
            'berth_number': berth_number,
            'check_in_time': datetime.utcnow().isoformat()
        }

        # Add position ONLY if captain approves
        if current_position:
            position_data = {
                **check_in_data,
                'current_position': current_position
            }

            result = await self.privacy_core.share_data(
                destination=f"Marina: {marina_id}",
                data=position_data,
                data_type='check_in_with_position',
                purpose='marina_arrival_notification',
                captain_id=captain_id
            )
        else:
            # No position - just basic check-in
            result = await self.privacy_core.share_data(
                destination=f"Marina: {marina_id}",
                data=check_in_data,
                data_type='check_in_basic',
                purpose='marina_arrival_notification',
                captain_id=captain_id
            )

        if not result['success']:
            return {
                'success': False,
                'reason': 'Captain denied check-in data sharing'
            }

        # Execute check-in
        confirmation = await self._call_marina_api(
            marina_id=marina_id,
            endpoint='check-in',
            data=check_in_data if not current_position else position_data
        )

        return {
            'success': True,
            'marina_id': marina_id,
            'berth_number': berth_number,
            'confirmation': confirmation,
            'welcome_message': confirmation.get('message'),
            'transfer_id': result.get('transfer_id')
        }

    async def get_marina_services(
        self,
        marina_id: str,
        anonymous: bool = True
    ) -> Dict[str, Any]:
        """
        Get available marina services

        Args:
            marina_id: Marina identifier
            anonymous: Fetch anonymously (no vessel identification)

        Returns:
            Available services
        """
        logger.info(f"Fetching services for marina {marina_id} (anonymous: {anonymous})")

        # Anonymous requests don't require captain approval
        if anonymous:
            services = await self._call_marina_api(
                marina_id=marina_id,
                endpoint='services',
                data=None,
                anonymous=True
            )

            return {
                'success': True,
                'marina_id': marina_id,
                'services': services,
                'anonymous': True
            }

        # Non-anonymous might get personalized pricing
        # Would require captain approval
        return {
            'success': False,
            'reason': 'Personalized services require captain approval'
        }

    async def _call_marina_api(
        self,
        marina_id: str,
        endpoint: str,
        data: Optional[Dict[str, Any]],
        anonymous: bool = False
    ) -> Dict[str, Any]:
        """
        Call marina API endpoint

        In production, this would use mTLS and certificate pinning

        Args:
            marina_id: Marina identifier
            endpoint: API endpoint
            data: Request data
            anonymous: Anonymous request

        Returns:
            API response
        """
        # TODO: Implement actual HTTPS request with mTLS
        # For now, simulate response

        logger.info(f"API call to marina {marina_id}/{endpoint}")

        if endpoint == 'berth-assignments':
            return {
                'berth_number': 'C-42',
                'confirmation': 'BERTH-WIM-2025-001',
                'status': 'confirmed'
            }
        elif endpoint == 'check-in':
            return {
                'status': 'checked_in',
                'message': 'Welcome to West Istanbul Marina!',
                'confirmation': 'CHECKIN-WIM-2025-001'
            }
        elif endpoint == 'services':
            return [
                {'service': 'Water', 'available': True},
                {'service': 'Electricity', 'available': True},
                {'service': 'WiFi', 'available': True},
                {'service': 'Fuel', 'available': True}
            ]

        return {'status': 'success'}

    async def privacy_safe_reservation(
        self,
        marina_id: str,
        vessel_length: float,
        arrival_date: datetime,
        duration_nights: int,
        captain_id: str,
        include_contact: bool = False
    ) -> Dict[str, Any]:
        """
        Make privacy-safe reservation

        Example for Yalikavak Marina demo scenario

        Args:
            marina_id: Marina identifier
            vessel_length: Vessel length in feet
            arrival_date: Arrival date
            duration_nights: Stay duration
            captain_id: Captain identifier
            include_contact: Include contact info (requires extra consent)

        Returns:
            Reservation confirmation
        """
        logger.info(f"Privacy-safe reservation for {marina_id}")

        # Minimal reservation data
        reservation_data = {
            'vessel_length': vessel_length,
            'arrival_date': arrival_date.isoformat(),
            'duration_nights': duration_nights
        }

        # Add contact if requested (requires separate consent)
        if include_contact:
            # This would trigger separate captain approval
            pass

        # Request captain approval
        result = await self.privacy_core.share_data(
            destination=f"Marina: {marina_id}",
            data=reservation_data,
            data_type='reservation_request',
            purpose='berth_reservation',
            captain_id=captain_id
        )

        if not result['success']:
            return {
                'success': False,
                'reason': 'Captain denied reservation data sharing'
            }

        # Execute reservation
        confirmation = await self._call_marina_api(
            marina_id=marina_id,
            endpoint='reservations',
            data=reservation_data
        )

        return {
            'success': True,
            'marina_id': marina_id,
            'reservation_id': confirmation.get('reservation_id', 'RES-2025-001'),
            'status': 'pending_confirmation',
            'data_shared': list(reservation_data.keys()),
            'NOT_shared': [
                'gps_history',
                'financial_data',
                'crew_information',
                'previous_marinas'
            ],
            'transfer_id': result.get('transfer_id')
        }
