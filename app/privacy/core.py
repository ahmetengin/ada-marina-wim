"""
ADA.SEA Privacy Core
The foundational privacy-first architecture for maritime data protection

"Kaptan ne derse o olur. Nokta." - Captain's word is final.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DataClassification(Enum):
    """Data classification levels per ADA.SEA privacy policy"""

    # LEVEL 0: Never share without explicit command
    PRIVATE = "private"

    # LEVEL 1: Share only essential data with captain approval
    RESTRICTED = "restricted"

    # LEVEL 2: Can share with captain consent (one-time or standing)
    CONDITIONAL = "conditional"

    # LEVEL 3: Anonymous/aggregated only
    ANONYMOUS = "anonymous"


class PrivacyException(Exception):
    """Base exception for privacy violations"""
    pass


class UnauthorizedDataShareException(PrivacyException):
    """Raised when attempting to share data without captain authorization"""
    pass


class InsufficientPermissionException(PrivacyException):
    """Raised when permission scope is insufficient"""
    pass


@dataclass
class DataTransferRequest:
    """Request to transfer data to external destination"""
    destination: str
    data_type: str
    data_payload: Dict[str, Any]
    purpose: str
    classification: DataClassification
    size_bytes: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.size_bytes is None:
            self.size_bytes = len(str(self.data_payload).encode('utf-8'))


class AdaSeaPrivacyCore:
    """
    Privacy-first core for ADA.SEA

    Key Principles:
    1. Zero Trust by Default - No automatic sharing
    2. Explicit Consent - Captain approval required
    3. Minimal Data - Only send what's necessary
    4. Audit Trail - Complete transparency
    5. Captain Control - Override everything
    6. Edge Computing - Data stays on-device
    7. Zero-Knowledge Cloud - Optional, encrypted, unreadable
    """

    def __init__(
        self,
        consent_manager,
        audit_logger,
        encryption_service,
        captain_auth_required: bool = True,
        cloud_sync_enabled: bool = False,
        edge_only_mode: bool = True
    ):
        """
        Initialize privacy core

        Args:
            consent_manager: Manages captain consent
            audit_logger: Logs all data transfers
            encryption_service: Handles encryption
            captain_auth_required: Require captain auth (default: True)
            cloud_sync_enabled: Allow cloud sync (default: False)
            edge_only_mode: Keep all data on-device (default: True)
        """
        self.consent_manager = consent_manager
        self.audit_logger = audit_logger
        self.encryption_service = encryption_service

        # Privacy settings - SECURE BY DEFAULT
        self.captain_auth_required = captain_auth_required
        self.cloud_sync_enabled = cloud_sync_enabled
        self.edge_only_mode = edge_only_mode

        # Data classification rules
        self.data_policy = self._initialize_data_policy()

        logger.info("AdaSeaPrivacyCore initialized with edge-first, zero-trust architecture")
        logger.info(f"Captain auth required: {captain_auth_required}")
        logger.info(f"Cloud sync: {cloud_sync_enabled}")
        logger.info(f"Edge-only mode: {edge_only_mode}")

    def _initialize_data_policy(self) -> Dict[DataClassification, List[str]]:
        """
        Initialize data classification policy
        Defines what data falls into which privacy level
        """
        return {
            DataClassification.PRIVATE: [
                'gps_history',
                'communication_logs',
                'financial_data',
                'crew_personal_info',
                'sensor_raw_data',
                'security_cameras',
                'passwords',
                'api_keys',
                'vessel_identity',
            ],
            DataClassification.RESTRICTED: [
                'current_position',
                'vessel_specifications',
                'arrival_time',
                'contact_info',
                'berth_number',
            ],
            DataClassification.CONDITIONAL: [
                'weather_preferences',
                'route_planning_style',
                'fuel_consumption_stats',
                'maintenance_schedule',
            ],
            DataClassification.ANONYMOUS: [
                'popular_routes',
                'anchorage_ratings',
                'weather_reports',
            ]
        }

    def classify_data(self, data_type: str) -> DataClassification:
        """
        Classify data type into privacy level

        Args:
            data_type: Type of data to classify

        Returns:
            DataClassification level
        """
        for classification, data_types in self.data_policy.items():
            if data_type in data_types:
                return classification

        # Default to PRIVATE if unknown (fail-safe)
        logger.warning(f"Unknown data type '{data_type}' - classifying as PRIVATE")
        return DataClassification.PRIVATE

    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate cryptographic hash of data for audit trail

        Args:
            data: Data to hash

        Returns:
            SHA-256 hex digest
        """
        data_str = str(sorted(data.items()))
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    async def share_data(
        self,
        destination: str,
        data: Dict[str, Any],
        data_type: str,
        purpose: str,
        captain_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Share data with external destination

        CRITICAL: NO automatic sharing - captain authorization required

        Args:
            destination: Where data is being sent
            data: Data payload to send
            data_type: Type of data being shared
            purpose: Why this data is being shared
            captain_id: Optional captain identifier

        Returns:
            Dict with success status and details

        Raises:
            UnauthorizedDataShareException: If captain auth missing
            InsufficientPermissionException: If permission scope insufficient
        """
        logger.info(f"Data share request: {destination} - {data_type} for {purpose}")

        # 1. Classify the data
        classification = self.classify_data(data_type)

        # 2. Create transfer request
        transfer_request = DataTransferRequest(
            destination=destination,
            data_type=data_type,
            data_payload=data,
            purpose=purpose,
            classification=classification
        )

        # 3. Check if captain authorization required
        if self.captain_auth_required:
            logger.info("Captain authorization required - requesting permission")

            # Request captain permission
            permission = await self.consent_manager.request_permission(
                destination=destination,
                data_type=data_type,
                data_size=transfer_request.size_bytes,
                purpose=purpose,
                classification=classification,
                captain_id=captain_id
            )

            if not permission.granted:
                logger.warning(f"Captain denied data transfer to {destination}")

                # Log denial
                await self.audit_logger.log_denial(
                    destination=destination,
                    data_type=data_type,
                    reason=permission.denial_reason,
                    captain_id=captain_id
                )

                return {
                    'success': False,
                    'reason': 'Captain denied permission',
                    'details': permission.denial_reason
                }
        else:
            logger.warning("Operating without captain authorization - NOT RECOMMENDED")
            permission = None

        # 4. Filter data by permission scope (only send approved fields)
        if permission:
            filtered_data = self._filter_data_by_permission(data, permission)
        else:
            filtered_data = data

        # 5. Calculate data hash for audit trail
        data_hash = self.calculate_data_hash(filtered_data)

        # 6. Log the transfer BEFORE sending
        transfer_log = await self.audit_logger.log_transfer(
            timestamp=datetime.utcnow(),
            destination=destination,
            data_type=data_type,
            data_hash=data_hash,
            captain_id=captain_id,
            permission_id=permission.permission_id if permission else None,
            purpose=purpose,
            data_summary=self._summarize_data(filtered_data)
        )

        # 7. Execute secure transfer
        try:
            result = await self._secure_transfer(destination, filtered_data)

            # 8. Update audit log with result
            await self.audit_logger.update_transfer_result(
                transfer_log.transfer_id,
                success=True,
                result=result
            )

            logger.info(f"Data transfer successful: {destination}")

            return {
                'success': True,
                'transfer_id': transfer_log.transfer_id,
                'destination': destination,
                'data_hash': data_hash,
                'timestamp': transfer_request.timestamp.isoformat()
            }

        except Exception as e:
            logger.error(f"Data transfer failed: {destination} - {str(e)}")

            # Update audit log with failure
            await self.audit_logger.update_transfer_result(
                transfer_log.transfer_id,
                success=False,
                error=str(e)
            )

            return {
                'success': False,
                'reason': 'Transfer failed',
                'error': str(e)
            }

    def _filter_data_by_permission(
        self,
        data: Dict[str, Any],
        permission
    ) -> Dict[str, Any]:
        """
        Filter data payload to only include fields approved by captain

        Args:
            data: Full data payload
            permission: Captain's permission with allowed fields

        Returns:
            Filtered data with only approved fields
        """
        if not permission.field_restrictions:
            # No restrictions - send all
            return data

        # Filter to only allowed fields
        filtered = {
            key: value
            for key, value in data.items()
            if key in permission.allowed_fields
        }

        logger.info(f"Filtered data from {len(data)} to {len(filtered)} fields")

        return filtered

    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """
        Create human-readable summary of data for audit log

        Args:
            data: Data to summarize

        Returns:
            Summary string
        """
        keys = list(data.keys())
        return f"{len(keys)} fields: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}"

    async def _secure_transfer(
        self,
        destination: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute secure data transfer with encryption

        Args:
            destination: Destination endpoint
            data: Data to send

        Returns:
            Transfer result
        """
        # TODO: Implement actual secure transfer with mTLS
        # For now, simulate transfer
        logger.info(f"Executing secure transfer to {destination}")

        # Encrypt data
        encrypted_data = await self.encryption_service.encrypt(data)

        # In production, this would use mTLS to send to destination
        # await http_client.post(destination, data=encrypted_data)

        return {
            'status': 'transferred',
            'bytes_sent': len(str(encrypted_data))
        }

    async def request_captain_permission(
        self,
        destination: str,
        data_type: str,
        purpose: str,
        captain_id: Optional[str] = None
    ) -> bool:
        """
        Request captain permission for data sharing

        This would typically trigger a voice prompt or UI notification

        Args:
            destination: Where data will be sent
            data_type: Type of data
            purpose: Why it's needed
            captain_id: Captain identifier

        Returns:
            True if granted, False if denied
        """
        permission = await self.consent_manager.request_permission(
            destination=destination,
            data_type=data_type,
            purpose=purpose,
            captain_id=captain_id
        )

        return permission.granted

    def check_edge_only_mode(self) -> bool:
        """
        Check if system is in edge-only mode (no cloud)

        Returns:
            True if edge-only, False if cloud allowed
        """
        return self.edge_only_mode

    def enable_cloud_sync(self, captain_confirmed: bool = False):
        """
        Enable cloud sync - requires captain confirmation

        Args:
            captain_confirmed: Captain explicitly approved

        Raises:
            PrivacyException: If captain didn't confirm
        """
        if not captain_confirmed:
            raise PrivacyException(
                "Cloud sync requires explicit captain confirmation"
            )

        self.cloud_sync_enabled = True
        self.edge_only_mode = False

        logger.warning("Cloud sync ENABLED - data may leave device")

        # Log this critical privacy change
        asyncio.create_task(
            self.audit_logger.log_privacy_setting_change(
                setting='cloud_sync',
                old_value=False,
                new_value=True,
                captain_confirmed=True
            )
        )

    def disable_cloud_sync(self):
        """Disable cloud sync - return to edge-only mode"""
        self.cloud_sync_enabled = False
        self.edge_only_mode = True

        logger.info("Cloud sync DISABLED - returning to edge-only mode")

        # Log this privacy change
        asyncio.create_task(
            self.audit_logger.log_privacy_setting_change(
                setting='cloud_sync',
                old_value=True,
                new_value=False,
                captain_confirmed=True
            )
        )
