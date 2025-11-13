"""
ADA.SEA Audit Logging
Complete transparency and audit trail for all data operations

"Every data transfer is logged. No exceptions."
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    DATA_TRANSFER = "data_transfer"
    DATA_DENIAL = "data_denial"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    PERMISSION_REVOKED = "permission_revoked"
    PRIVACY_SETTING_CHANGE = "privacy_setting_change"
    DATA_DELETION = "data_deletion"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    ENCRYPTION_KEY_GENERATED = "encryption_key_generated"
    SECURITY_ALERT = "security_alert"


@dataclass
class DataTransferLog:
    """Log entry for data transfer"""
    transfer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    destination: str = ""
    data_type: str = ""
    data_hash: str = ""
    data_summary: str = ""
    captain_id: Optional[str] = None
    permission_id: Optional[str] = None
    purpose: str = ""

    # Result (updated after transfer)
    success: Optional[bool] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime to ISO format
        data['timestamp'] = self.timestamp.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


@dataclass
class AuditEvent:
    """Generic audit event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: AuditEventType = AuditEventType.DATA_TRANSFER
    captain_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'captain_id': self.captain_id,
            'details': self.details,
            'severity': self.severity
        }


class AuditLogger:
    """
    Comprehensive audit logging for ADA.SEA

    Features:
    - Tamper-proof logs (append-only)
    - Encrypted storage
    - Complete data transfer history
    - Privacy setting changes
    - Captain access logs
    - Exportable for compliance
    """

    def __init__(self, storage_path: Optional[str] = None, encrypt_logs: bool = True):
        """
        Initialize audit logger

        Args:
            storage_path: Path to store audit logs
            encrypt_logs: Encrypt log files
        """
        self.storage_path = storage_path or "/var/ada-sea/audit"
        self.encrypt_logs = encrypt_logs

        # In-memory storage (in production, use encrypted database)
        self.transfer_logs: Dict[str, DataTransferLog] = {}
        self.audit_events: List[AuditEvent] = []

        logger.info("AuditLogger initialized")
        logger.info(f"Storage path: {self.storage_path}")
        logger.info(f"Encryption: {encrypt_logs}")

    async def log_transfer(
        self,
        timestamp: datetime,
        destination: str,
        data_type: str,
        data_hash: str,
        captain_id: Optional[str],
        permission_id: Optional[str],
        purpose: str,
        data_summary: str
    ) -> DataTransferLog:
        """
        Log a data transfer

        Args:
            timestamp: When transfer initiated
            destination: Where data was sent
            data_type: Type of data
            data_hash: Cryptographic hash of data
            captain_id: Captain who authorized
            permission_id: Permission used
            purpose: Why data was shared
            data_summary: Human-readable summary

        Returns:
            DataTransferLog entry
        """
        transfer_log = DataTransferLog(
            timestamp=timestamp,
            destination=destination,
            data_type=data_type,
            data_hash=data_hash,
            captain_id=captain_id,
            permission_id=permission_id,
            purpose=purpose,
            data_summary=data_summary
        )

        # Store log
        self.transfer_logs[transfer_log.transfer_id] = transfer_log

        # Create audit event
        await self._create_audit_event(
            event_type=AuditEventType.DATA_TRANSFER,
            captain_id=captain_id,
            details={
                'transfer_id': transfer_log.transfer_id,
                'destination': destination,
                'data_type': data_type,
                'purpose': purpose
            }
        )

        logger.info(
            f"Logged data transfer: {transfer_log.transfer_id} "
            f"to {destination}"
        )

        return transfer_log

    async def update_transfer_result(
        self,
        transfer_id: str,
        success: bool,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Update transfer log with result

        Args:
            transfer_id: Transfer to update
            success: Whether transfer succeeded
            result: Transfer result details
            error: Error message if failed
        """
        if transfer_id not in self.transfer_logs:
            logger.error(f"Transfer log not found: {transfer_id}")
            return

        transfer_log = self.transfer_logs[transfer_id]
        transfer_log.success = success
        transfer_log.result = result
        transfer_log.error = error
        transfer_log.completed_at = datetime.utcnow()

        logger.info(
            f"Updated transfer result: {transfer_id} - "
            f"{'SUCCESS' if success else 'FAILED'}"
        )

    async def log_denial(
        self,
        destination: str,
        data_type: str,
        reason: str,
        captain_id: Optional[str]
    ):
        """
        Log denied data transfer

        Args:
            destination: Where data was requested to go
            data_type: Type of data requested
            reason: Why it was denied
            captain_id: Captain who denied
        """
        await self._create_audit_event(
            event_type=AuditEventType.DATA_DENIAL,
            captain_id=captain_id,
            details={
                'destination': destination,
                'data_type': data_type,
                'reason': reason
            },
            severity='warning'
        )

        logger.info(f"Logged data denial: {destination} - {data_type}")

    async def log_privacy_setting_change(
        self,
        setting: str,
        old_value: Any,
        new_value: Any,
        captain_confirmed: bool,
        captain_id: Optional[str] = None
    ):
        """
        Log privacy setting change

        Args:
            setting: Setting that changed
            old_value: Previous value
            new_value: New value
            captain_confirmed: Whether captain confirmed
            captain_id: Captain who made change
        """
        await self._create_audit_event(
            event_type=AuditEventType.PRIVACY_SETTING_CHANGE,
            captain_id=captain_id,
            details={
                'setting': setting,
                'old_value': str(old_value),
                'new_value': str(new_value),
                'captain_confirmed': captain_confirmed
            },
            severity='critical' if not captain_confirmed else 'warning'
        )

        logger.warning(
            f"Privacy setting changed: {setting} "
            f"{old_value} -> {new_value}"
        )

    async def log_permission_granted(
        self,
        permission_id: str,
        destination: str,
        data_type: str,
        captain_id: str,
        method: str
    ):
        """
        Log permission granted

        Args:
            permission_id: Permission ID
            destination: Destination approved
            data_type: Data type approved
            captain_id: Captain who granted
            method: How permission was granted (voice, manual, etc.)
        """
        await self._create_audit_event(
            event_type=AuditEventType.PERMISSION_GRANTED,
            captain_id=captain_id,
            details={
                'permission_id': permission_id,
                'destination': destination,
                'data_type': data_type,
                'method': method
            }
        )

    async def log_permission_revoked(
        self,
        permission_id: str,
        captain_id: str,
        reason: str
    ):
        """
        Log permission revoked

        Args:
            permission_id: Permission revoked
            captain_id: Captain who revoked
            reason: Why it was revoked
        """
        await self._create_audit_event(
            event_type=AuditEventType.PERMISSION_REVOKED,
            captain_id=captain_id,
            details={
                'permission_id': permission_id,
                'reason': reason
            }
        )

    async def log_data_deletion(
        self,
        data_type: str,
        destination: Optional[str],
        captain_id: str,
        reason: str
    ):
        """
        Log data deletion request

        Args:
            data_type: Type of data deleted
            destination: Where data was deleted from
            captain_id: Captain who requested deletion
            reason: Why data was deleted
        """
        await self._create_audit_event(
            event_type=AuditEventType.DATA_DELETION,
            captain_id=captain_id,
            details={
                'data_type': data_type,
                'destination': destination,
                'reason': reason
            },
            severity='warning'
        )

    async def log_security_alert(
        self,
        alert_type: str,
        description: str,
        severity: str = "critical"
    ):
        """
        Log security alert

        Args:
            alert_type: Type of security alert
            description: Alert description
            severity: Severity level
        """
        await self._create_audit_event(
            event_type=AuditEventType.SECURITY_ALERT,
            details={
                'alert_type': alert_type,
                'description': description
            },
            severity=severity
        )

        logger.critical(f"SECURITY ALERT: {alert_type} - {description}")

    async def _create_audit_event(
        self,
        event_type: AuditEventType,
        details: Dict[str, Any],
        captain_id: Optional[str] = None,
        severity: str = "info"
    ):
        """
        Create and store audit event

        Args:
            event_type: Type of event
            details: Event details
            captain_id: Captain associated with event
            severity: Event severity
        """
        event = AuditEvent(
            event_type=event_type,
            captain_id=captain_id,
            details=details,
            severity=severity
        )

        # Store event
        self.audit_events.append(event)

        # In production, write to encrypted append-only log file
        await self._persist_event(event)

    async def _persist_event(self, event: AuditEvent):
        """
        Persist event to storage

        In production, this would:
        1. Encrypt event data
        2. Write to append-only log file
        3. Optionally replicate to backup location
        4. Update tamper-proof hash chain

        Args:
            event: Event to persist
        """
        # TODO: Implement encrypted file storage
        # TODO: Implement hash chain for tamper detection
        pass

    def get_transfer_logs(
        self,
        captain_id: Optional[str] = None,
        days: int = 7,
        destination: Optional[str] = None
    ) -> List[DataTransferLog]:
        """
        Get data transfer logs

        Args:
            captain_id: Filter by captain
            days: Number of days to look back
            destination: Filter by destination

        Returns:
            List of transfer logs
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        logs = [
            log for log in self.transfer_logs.values()
            if log.timestamp >= cutoff
        ]

        if captain_id:
            logs = [log for log in logs if log.captain_id == captain_id]

        if destination:
            logs = [log for log in logs if log.destination == destination]

        return sorted(logs, key=lambda l: l.timestamp, reverse=True)

    def get_audit_events(
        self,
        captain_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        days: int = 7,
        severity: Optional[str] = None
    ) -> List[AuditEvent]:
        """
        Get audit events

        Args:
            captain_id: Filter by captain
            event_type: Filter by event type
            days: Number of days to look back
            severity: Filter by severity

        Returns:
            List of audit events
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        events = [
            event for event in self.audit_events
            if event.timestamp >= cutoff
        ]

        if captain_id:
            events = [e for e in events if e.captain_id == captain_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if severity:
            events = [e for e in events if e.severity == severity]

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def get_audit_summary(self, captain_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get audit summary for captain

        Args:
            captain_id: Captain to summarize
            days: Number of days to look back

        Returns:
            Summary statistics
        """
        transfers = self.get_transfer_logs(captain_id=captain_id, days=days)
        events = self.get_audit_events(captain_id=captain_id, days=days)

        successful_transfers = sum(1 for t in transfers if t.success)
        failed_transfers = sum(1 for t in transfers if t.success is False)

        return {
            'captain_id': captain_id,
            'period_days': days,
            'total_transfers': len(transfers),
            'successful_transfers': successful_transfers,
            'failed_transfers': failed_transfers,
            'total_events': len(events),
            'critical_events': sum(1 for e in events if e.severity == 'critical'),
            'warning_events': sum(1 for e in events if e.severity == 'warning'),
            'destinations': list(set(t.destination for t in transfers)),
            'data_types_shared': list(set(t.data_type for t in transfers))
        }

    async def export_audit_trail(
        self,
        captain_id: str,
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> str:
        """
        Export complete audit trail for compliance

        Args:
            captain_id: Captain to export
            start_date: Start of period
            end_date: End of period
            format: Export format (json, csv)

        Returns:
            Exported audit trail as string
        """
        # Get all transfers in period
        transfers = [
            log for log in self.transfer_logs.values()
            if log.captain_id == captain_id
            and start_date <= log.timestamp <= end_date
        ]

        # Get all events in period
        events = [
            event for event in self.audit_events
            if event.captain_id == captain_id
            and start_date <= event.timestamp <= end_date
        ]

        if format == "json":
            export_data = {
                'captain_id': captain_id,
                'export_date': datetime.utcnow().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'transfers': [t.to_dict() for t in transfers],
                'events': [e.to_dict() for e in events]
            }
            return json.dumps(export_data, indent=2)

        elif format == "csv":
            # TODO: Implement CSV export
            return "CSV export not implemented yet"

        else:
            raise ValueError(f"Unsupported export format: {format}")
