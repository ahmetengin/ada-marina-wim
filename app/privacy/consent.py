"""
ADA.SEA Consent Management
Explicit captain consent system for data sharing

"Every data transfer requires captain's explicit approval"
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ConsentMethod(Enum):
    """How captain provided consent"""
    VOICE = "voice"
    MANUAL = "manual"
    STANDING = "standing"  # Pre-approved standing permission
    BIOMETRIC = "biometric"


class ConsentDuration(Enum):
    """How long consent is valid"""
    ONE_TIME = "one_time"
    SESSION = "session"  # Until captain logs out
    STANDING = "standing"  # Permanent until revoked
    TEMPORARY = "temporary"  # Expires after set time


@dataclass
class ConsentRequest:
    """Request for captain's consent to share data"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    destination: str = ""
    data_type: str = ""
    data_size: Optional[int] = None
    purpose: str = ""
    classification: Any = None  # DataClassification from core.py
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Turkish voice prompt (default language)
    turkish_prompt: Optional[str] = None

    def get_voice_prompt(self, language: str = "tr") -> str:
        """
        Generate voice prompt for captain

        Args:
            language: Language code (tr, en, el)

        Returns:
            Voice prompt string
        """
        if language == "tr":
            return (
                f"Kaptan, {self.destination} için "
                f"{self.data_type} verisi paylaşılsın mı? "
                f"Amaç: {self.purpose}. "
                f"Cevap: 'Evet paylaş' veya 'Hayır'"
            )
        elif language == "en":
            return (
                f"Captain, share {self.data_type} data "
                f"with {self.destination}? "
                f"Purpose: {self.purpose}. "
                f"Reply: 'Yes, share' or 'No'"
            )
        elif language == "el":
            return (
                f"Καπετάνιε, να μοιραστούν δεδομένα {self.data_type} "
                f"με {self.destination}; "
                f"Σκοπός: {self.purpose}. "
                f"Απάντηση: 'Ναι' ή 'Όχι'"
            )
        else:
            return self.get_voice_prompt("en")


@dataclass
class ConsentPermission:
    """Captain's permission/denial for data sharing"""
    permission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    granted: bool = False
    captain_id: Optional[str] = None
    method: ConsentMethod = ConsentMethod.MANUAL
    duration: ConsentDuration = ConsentDuration.ONE_TIME
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # If granted
    allowed_fields: Optional[List[str]] = None
    field_restrictions: bool = False
    expires_at: Optional[datetime] = None

    # If denied
    denial_reason: Optional[str] = None

    # Voice confirmation
    voice_signature: Optional[str] = None
    confirmation_text: Optional[str] = None


class ConsentManager:
    """
    Manages captain consent for all data sharing operations

    Key Features:
    - Voice confirmation support
    - Standing permissions (pre-approved destinations)
    - Granular field-level control
    - Consent expiration
    - Full audit trail
    """

    def __init__(self, voice_enabled: bool = True, require_biometric: bool = False):
        """
        Initialize consent manager

        Args:
            voice_enabled: Enable voice confirmation
            require_biometric: Require biometric auth
        """
        self.voice_enabled = voice_enabled
        self.require_biometric = require_biometric

        # In-memory storage (in production, use encrypted database)
        self.active_permissions: Dict[str, ConsentPermission] = {}
        self.standing_permissions: Dict[str, ConsentPermission] = {}
        self.consent_history: List[ConsentPermission] = []

        logger.info("ConsentManager initialized")
        logger.info(f"Voice enabled: {voice_enabled}")
        logger.info(f"Biometric required: {require_biometric}")

    async def request_permission(
        self,
        destination: str,
        data_type: str,
        purpose: str,
        data_size: Optional[int] = None,
        classification: Any = None,
        captain_id: Optional[str] = None,
        language: str = "tr"
    ) -> ConsentPermission:
        """
        Request captain's permission to share data

        Args:
            destination: Where data will be sent
            data_type: Type of data to share
            purpose: Why this data is needed
            data_size: Size in bytes
            classification: Data classification level
            captain_id: Captain identifier
            language: Language for voice prompt

        Returns:
            ConsentPermission with granted/denied status
        """
        # 1. Create consent request
        request = ConsentRequest(
            destination=destination,
            data_type=data_type,
            data_size=data_size,
            purpose=purpose,
            classification=classification
        )

        logger.info(f"Requesting permission: {destination} - {data_type}")

        # 2. Check for existing standing permission
        standing_permission = self._check_standing_permission(
            destination, data_type
        )
        if standing_permission:
            logger.info(f"Found standing permission for {destination}")
            return standing_permission

        # 3. Prompt captain for approval
        voice_prompt = request.get_voice_prompt(language)
        logger.info(f"Voice prompt: {voice_prompt}")

        # 4. Get captain's response
        # In production, this would integrate with voice recognition
        # For now, we'll return a permission object that needs to be confirmed
        permission = await self._prompt_captain(
            request=request,
            voice_prompt=voice_prompt,
            captain_id=captain_id
        )

        # 5. Store permission
        if permission.granted:
            self.active_permissions[permission.permission_id] = permission

        # 6. Add to history
        self.consent_history.append(permission)

        return permission

    async def _prompt_captain(
        self,
        request: ConsentRequest,
        voice_prompt: str,
        captain_id: Optional[str]
    ) -> ConsentPermission:
        """
        Prompt captain for approval (voice or UI)

        In production, this would:
        1. Play voice prompt through speakers
        2. Listen for captain's voice response
        3. Verify voice signature
        4. Show UI notification with approve/deny buttons

        Args:
            request: Consent request
            voice_prompt: Voice prompt text
            captain_id: Captain ID

        Returns:
            ConsentPermission
        """
        # TODO: Integrate with voice recognition system
        # TODO: Integrate with UI notification system
        # TODO: Implement biometric verification

        # For now, create a permission that requires external confirmation
        logger.warning("Captain prompt not implemented - creating pending permission")

        permission = ConsentPermission(
            request_id=request.request_id,
            granted=False,  # Requires explicit confirmation
            captain_id=captain_id,
            method=ConsentMethod.VOICE if self.voice_enabled else ConsentMethod.MANUAL,
            duration=ConsentDuration.ONE_TIME,
            denial_reason="Awaiting captain response"
        )

        return permission

    def grant_permission(
        self,
        request_id: str,
        captain_id: str,
        method: ConsentMethod = ConsentMethod.MANUAL,
        duration: ConsentDuration = ConsentDuration.ONE_TIME,
        allowed_fields: Optional[List[str]] = None,
        confirmation_text: Optional[str] = None
    ) -> ConsentPermission:
        """
        Grant permission (called after captain approves)

        Args:
            request_id: ID of the consent request
            captain_id: Captain identifier
            method: How approval was given
            duration: How long permission is valid
            allowed_fields: Specific fields captain approved
            confirmation_text: Captain's confirmation phrase

        Returns:
            Granted ConsentPermission
        """
        permission = ConsentPermission(
            request_id=request_id,
            granted=True,
            captain_id=captain_id,
            method=method,
            duration=duration,
            allowed_fields=allowed_fields,
            field_restrictions=bool(allowed_fields),
            confirmation_text=confirmation_text,
            expires_at=self._calculate_expiration(duration)
        )

        # Store permission
        self.active_permissions[permission.permission_id] = permission

        if duration == ConsentDuration.STANDING:
            self.standing_permissions[permission.permission_id] = permission
            logger.info(f"Added standing permission: {permission.permission_id}")

        logger.info(f"Permission granted: {permission.permission_id}")

        return permission

    def deny_permission(
        self,
        request_id: str,
        captain_id: str,
        reason: str = "Captain denied"
    ) -> ConsentPermission:
        """
        Deny permission (called after captain denies)

        Args:
            request_id: ID of the consent request
            captain_id: Captain identifier
            reason: Why permission was denied

        Returns:
            Denied ConsentPermission
        """
        permission = ConsentPermission(
            request_id=request_id,
            granted=False,
            captain_id=captain_id,
            denial_reason=reason
        )

        # Add to history
        self.consent_history.append(permission)

        logger.info(f"Permission denied: {request_id} - {reason}")

        return permission

    def _check_standing_permission(
        self,
        destination: str,
        data_type: str
    ) -> Optional[ConsentPermission]:
        """
        Check if there's a standing permission for this destination/data type

        Args:
            destination: Destination to check
            data_type: Data type to check

        Returns:
            ConsentPermission if found and valid, None otherwise
        """
        # In production, query database for standing permissions
        # For now, check in-memory storage

        for permission in self.standing_permissions.values():
            # Check if permission is still valid
            if permission.expires_at and permission.expires_at < datetime.utcnow():
                continue

            # TODO: Match against destination and data type
            # This requires storing request details with permission
            return permission

        return None

    def _calculate_expiration(self, duration: ConsentDuration) -> Optional[datetime]:
        """
        Calculate when permission expires

        Args:
            duration: Duration type

        Returns:
            Expiration datetime or None if no expiration
        """
        if duration == ConsentDuration.ONE_TIME:
            return datetime.utcnow() + timedelta(minutes=5)
        elif duration == ConsentDuration.SESSION:
            return datetime.utcnow() + timedelta(hours=24)
        elif duration == ConsentDuration.TEMPORARY:
            return datetime.utcnow() + timedelta(days=7)
        elif duration == ConsentDuration.STANDING:
            return None  # No expiration
        else:
            return datetime.utcnow() + timedelta(hours=1)

    def revoke_permission(self, permission_id: str, captain_id: str) -> bool:
        """
        Revoke a permission

        Args:
            permission_id: Permission to revoke
            captain_id: Captain revoking (must match original captain)

        Returns:
            True if revoked, False if not found or unauthorized
        """
        # Check active permissions
        if permission_id in self.active_permissions:
            permission = self.active_permissions[permission_id]

            if permission.captain_id != captain_id:
                logger.warning(
                    f"Captain {captain_id} attempted to revoke "
                    f"permission owned by {permission.captain_id}"
                )
                return False

            del self.active_permissions[permission_id]
            logger.info(f"Revoked active permission: {permission_id}")

        # Check standing permissions
        if permission_id in self.standing_permissions:
            permission = self.standing_permissions[permission_id]

            if permission.captain_id != captain_id:
                return False

            del self.standing_permissions[permission_id]
            logger.info(f"Revoked standing permission: {permission_id}")

        return True

    def revoke_all_permissions(self, captain_id: str, destination: Optional[str] = None):
        """
        Revoke all permissions for a captain

        Args:
            captain_id: Captain whose permissions to revoke
            destination: Optional - only revoke for specific destination
        """
        # Revoke active permissions
        to_remove = []
        for perm_id, perm in self.active_permissions.items():
            if perm.captain_id == captain_id:
                if destination is None or perm.request_id.startswith(destination):
                    to_remove.append(perm_id)

        for perm_id in to_remove:
            del self.active_permissions[perm_id]

        # Revoke standing permissions
        to_remove = []
        for perm_id, perm in self.standing_permissions.items():
            if perm.captain_id == captain_id:
                if destination is None or perm.request_id.startswith(destination):
                    to_remove.append(perm_id)

        for perm_id in to_remove:
            del self.standing_permissions[perm_id]

        logger.info(
            f"Revoked all permissions for captain {captain_id}"
            f"{f' to {destination}' if destination else ''}"
        )

    def get_consent_history(
        self,
        captain_id: str,
        days: int = 7
    ) -> List[ConsentPermission]:
        """
        Get consent history for captain

        Args:
            captain_id: Captain to get history for
            days: Number of days to look back

        Returns:
            List of consent permissions
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        history = [
            perm for perm in self.consent_history
            if perm.captain_id == captain_id and perm.timestamp >= cutoff
        ]

        return sorted(history, key=lambda p: p.timestamp, reverse=True)

    def get_active_permissions(self, captain_id: str) -> List[ConsentPermission]:
        """
        Get all active permissions for captain

        Args:
            captain_id: Captain ID

        Returns:
            List of active permissions
        """
        return [
            perm for perm in self.active_permissions.values()
            if perm.captain_id == captain_id
        ]

    def get_standing_permissions(self, captain_id: str) -> List[ConsentPermission]:
        """
        Get all standing permissions for captain

        Args:
            captain_id: Captain ID

        Returns:
            List of standing permissions
        """
        return [
            perm for perm in self.standing_permissions.values()
            if perm.captain_id == captain_id
        ]
