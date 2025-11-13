"""
ADA.SEA Captain Control Interface
Voice and UI controls for privacy management

"Ada, veri paylaşım geçmişini göster"
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceCommand(Enum):
    """Supported voice commands for privacy control"""

    # Permission management
    ENABLE_SHARING = "enable_sharing"
    DISABLE_SHARING = "disable_sharing"
    REVOKE_ALL = "revoke_all"

    # Audit/review
    SHOW_HISTORY = "show_history"
    SHOW_PERMISSIONS = "show_permissions"
    SHOW_LAST_24H = "show_last_24h"

    # Data deletion
    DELETE_DATA = "delete_data"
    DELETE_BACKUPS = "delete_backups"
    CLEAR_HISTORY = "clear_history"

    # Backup control
    ENABLE_BACKUP = "enable_backup"
    DISABLE_BACKUP = "disable_backup"
    SHOW_BACKUP_STATUS = "show_backup_status"

    # Privacy settings
    SHOW_PRIVACY_STATUS = "show_privacy_status"
    ENABLE_EDGE_ONLY = "enable_edge_only"


class CaptainControlInterface:
    """
    Captain's control interface for privacy management

    Features:
    - Voice command processing (Turkish/English/Greek)
    - Privacy status dashboard
    - Data sharing history
    - Permission management
    - Backup control
    """

    def __init__(
        self,
        privacy_core,
        consent_manager,
        audit_logger,
        backup_system,
        default_language: str = "tr"
    ):
        """
        Initialize captain control interface

        Args:
            privacy_core: AdaSeaPrivacyCore instance
            consent_manager: ConsentManager instance
            audit_logger: AuditLogger instance
            backup_system: ZeroKnowledgeBackup instance
            default_language: Default language (tr, en, el)
        """
        self.privacy_core = privacy_core
        self.consent_manager = consent_manager
        self.audit_logger = audit_logger
        self.backup_system = backup_system
        self.default_language = default_language

        # Voice command patterns (Turkish)
        self.voice_patterns_tr = {
            # Sharing history
            r"veri paylaşım geçmişini göster": VoiceCommand.SHOW_HISTORY,
            r"hangi bilgileri kimle paylaştım": VoiceCommand.SHOW_HISTORY,
            r"ne paylaştım": VoiceCommand.SHOW_HISTORY,
            r"son 24 saatte ne paylaştın": VoiceCommand.SHOW_LAST_24H,

            # Permission management
            r"(.+) ile veri paylaşımını aktif et": VoiceCommand.ENABLE_SHARING,
            r"tüm otomatik paylaşımları durdur": VoiceCommand.REVOKE_ALL,
            r"tüm paylaşımları iptal et": VoiceCommand.REVOKE_ALL,

            # Data deletion
            r"(.+) verilerimi sil": VoiceCommand.DELETE_DATA,
            r"tüm bulut yedeklerini sil": VoiceCommand.DELETE_BACKUPS,
            r"veri paylaşım geçmişini temizle": VoiceCommand.CLEAR_HISTORY,

            # Backup control
            r"yedeklemeyi aktif et": VoiceCommand.ENABLE_BACKUP,
            r"yedeklemeyi durdur": VoiceCommand.DISABLE_BACKUP,
            r"yedek durumunu göster": VoiceCommand.SHOW_BACKUP_STATUS,

            # Privacy status
            r"gizlilik durumunu göster": VoiceCommand.SHOW_PRIVACY_STATUS,
            r"konumumu hiç kimseyle paylaşma": VoiceCommand.ENABLE_EDGE_ONLY,
        }

        logger.info("CaptainControlInterface initialized")
        logger.info(f"Default language: {default_language}")

    async def process_voice_command(
        self,
        command: str,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Process captain's voice command

        Args:
            command: Voice command text
            captain_id: Captain identifier
            language: Command language

        Returns:
            Command result
        """
        logger.info(f"Processing voice command: {command}")

        # Normalize command
        command_lower = command.lower().strip()

        # Match command pattern
        matched_command = self._match_command(command_lower, language)

        if not matched_command:
            return {
                'success': False,
                'message': self._translate("Komut anlaşılamadı", language),
                'suggestions': self._get_command_suggestions(language)
            }

        # Execute command
        result = await self._execute_command(
            matched_command,
            command_lower,
            captain_id,
            language
        )

        return result

    def _match_command(self, command: str, language: str) -> Optional[VoiceCommand]:
        """
        Match command string to VoiceCommand

        Args:
            command: Command string
            language: Language

        Returns:
            Matched VoiceCommand or None
        """
        patterns = self.voice_patterns_tr if language == "tr" else {}

        for pattern, voice_command in patterns.items():
            # Simple substring matching (in production, use NLP)
            if pattern.replace(r"(.+)", "").strip() in command:
                return voice_command

        return None

    async def _execute_command(
        self,
        command: VoiceCommand,
        raw_command: str,
        captain_id: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Execute matched voice command

        Args:
            command: Matched voice command
            raw_command: Original command string
            captain_id: Captain identifier
            language: Language

        Returns:
            Execution result
        """
        if command == VoiceCommand.SHOW_HISTORY:
            return await self.show_data_sharing_history(captain_id, days=7, language=language)

        elif command == VoiceCommand.SHOW_LAST_24H:
            return await self.show_data_sharing_history(captain_id, days=1, language=language)

        elif command == VoiceCommand.REVOKE_ALL:
            return await self.revoke_all_permissions(captain_id, language=language)

        elif command == VoiceCommand.DELETE_BACKUPS:
            return await self.delete_all_backups(captain_id, language=language)

        elif command == VoiceCommand.SHOW_BACKUP_STATUS:
            return await self.show_backup_status(language=language)

        elif command == VoiceCommand.SHOW_PRIVACY_STATUS:
            return await self.show_privacy_status(captain_id, language=language)

        elif command == VoiceCommand.ENABLE_EDGE_ONLY:
            return await self.enable_edge_only_mode(captain_id, language=language)

        else:
            return {
                'success': False,
                'message': self._translate("Komut henüz desteklenmiyor", language)
            }

    async def show_data_sharing_history(
        self,
        captain_id: str,
        days: int = 7,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Show captain's data sharing history

        Args:
            captain_id: Captain identifier
            days: Number of days to look back
            language: Language for response

        Returns:
            History summary
        """
        # Get transfer logs
        transfers = self.audit_logger.get_transfer_logs(
            captain_id=captain_id,
            days=days
        )

        # Get audit summary
        summary = self.audit_logger.get_audit_summary(captain_id, days)

        if language == "tr":
            message = (
                f"Son {days} günde {summary['total_transfers']} veri paylaşımı yapıldı.\n\n"
                f"Başarılı: {summary['successful_transfers']}\n"
                f"Başarısız: {summary['failed_transfers']}\n\n"
                f"Paylaşım yapılan yerler:\n"
            )
            for dest in summary['destinations']:
                dest_transfers = [t for t in transfers if t.destination == dest]
                message += f"  • {dest}: {len(dest_transfers)} transfer\n"

        else:
            message = (
                f"In the last {days} days: {summary['total_transfers']} data shares\n\n"
                f"Successful: {summary['successful_transfers']}\n"
                f"Failed: {summary['failed_transfers']}\n\n"
                f"Destinations:\n"
            )
            for dest in summary['destinations']:
                dest_transfers = [t for t in transfers if t.destination == dest]
                message += f"  • {dest}: {len(dest_transfers)} transfers\n"

        return {
            'success': True,
            'message': message,
            'summary': summary,
            'transfers': [
                {
                    'timestamp': t.timestamp.isoformat(),
                    'destination': t.destination,
                    'data_type': t.data_type,
                    'success': t.success
                }
                for t in transfers[:10]  # Last 10 transfers
            ]
        }

    async def show_active_permissions(
        self,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Show captain's active permissions

        Args:
            captain_id: Captain identifier
            language: Language

        Returns:
            Active permissions list
        """
        active = self.consent_manager.get_active_permissions(captain_id)
        standing = self.consent_manager.get_standing_permissions(captain_id)

        if language == "tr":
            message = f"Aktif izinler: {len(active)}\n"
            message += f"Sürekli izinler: {len(standing)}\n\n"

            if standing:
                message += "Sürekli izinler:\n"
                for perm in standing:
                    message += f"  • İzin ID: {perm.permission_id}\n"
        else:
            message = f"Active permissions: {len(active)}\n"
            message += f"Standing permissions: {len(standing)}\n\n"

            if standing:
                message += "Standing permissions:\n"
                for perm in standing:
                    message += f"  • Permission ID: {perm.permission_id}\n"

        return {
            'success': True,
            'message': message,
            'active_count': len(active),
            'standing_count': len(standing),
            'permissions': [
                {
                    'permission_id': p.permission_id,
                    'granted': p.granted,
                    'method': p.method.value,
                    'timestamp': p.timestamp.isoformat()
                }
                for p in active + standing
            ]
        }

    async def revoke_all_permissions(
        self,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Revoke all permissions for captain

        Args:
            captain_id: Captain identifier
            language: Language

        Returns:
            Result
        """
        self.consent_manager.revoke_all_permissions(captain_id)

        if language == "tr":
            message = "✓ Tüm veri paylaşım izinleri iptal edildi.\n" \
                     "Bundan sonra her paylaşım için onay isteyeceğim."
        else:
            message = "✓ All data sharing permissions revoked.\n" \
                     "I will ask for approval for each share from now on."

        return {
            'success': True,
            'message': message
        }

    async def delete_all_backups(
        self,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Delete all cloud backups for captain

        Args:
            captain_id: Captain identifier
            language: Language

        Returns:
            Result
        """
        await self.backup_system.disable_backup(
            captain_id=captain_id,
            delete_remote=True
        )

        if language == "tr":
            message = "✓ Tüm bulut yedekleri silindi.\n" \
                     "✓ Yedekleme devre dışı bırakıldı."
        else:
            message = "✓ All cloud backups deleted.\n" \
                     "✓ Backup disabled."

        return {
            'success': True,
            'message': message
        }

    async def show_backup_status(self, language: str = "tr") -> Dict[str, Any]:
        """
        Show backup system status

        Args:
            language: Language

        Returns:
            Backup status
        """
        status = self.backup_system.get_backup_status()

        if language == "tr":
            if status['enabled']:
                message = "✓ Yedekleme AKTİF\n" \
                         f"✓ Şifreleme: {status['encryption']}\n" \
                         f"✓ Zero-knowledge: Evet\n" \
                         f"✓ Ada.sea okuyabilir mi? Hayır"
            else:
                message = "✗ Yedekleme DEVREDİŞI\n" \
                         "Tüm veriler sadece cihazınızda."
        else:
            if status['enabled']:
                message = "✓ Backup ENABLED\n" \
                         f"✓ Encryption: {status['encryption']}\n" \
                         f"✓ Zero-knowledge: Yes\n" \
                         f"✓ Can Ada.sea read? No"
            else:
                message = "✗ Backup DISABLED\n" \
                         "All data stays on your device."

        return {
            'success': True,
            'message': message,
            'status': status
        }

    async def show_privacy_status(
        self,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Show complete privacy status for captain

        Args:
            captain_id: Captain identifier
            language: Language

        Returns:
            Privacy status dashboard
        """
        # Get various status info
        edge_only = self.privacy_core.check_edge_only_mode()
        cloud_enabled = self.privacy_core.cloud_sync_enabled
        backup_status = self.backup_system.get_backup_status()
        active_perms = len(self.consent_manager.get_active_permissions(captain_id))
        standing_perms = len(self.consent_manager.get_standing_permissions(captain_id))

        # Get recent activity
        summary = self.audit_logger.get_audit_summary(captain_id, days=7)

        if language == "tr":
            message = "═══ ADA.SEA GİZLİLİK DURUMU ═══\n\n"
            message += f"{'✓' if edge_only else '✗'} Edge-Only Modu: {'AKTİF' if edge_only else 'DEVREDİŞI'}\n"
            message += f"{'✗' if not cloud_enabled else '✓'} Bulut Senkronizasyonu: {'AKTİF' if cloud_enabled else 'DEVREDİŞI'}\n"
            message += f"{'✓' if backup_status['enabled'] else '✗'} Yedekleme: {'AKTİF' if backup_status['enabled'] else 'DEVREDİŞI'}\n\n"

            message += f"Aktif İzinler: {active_perms}\n"
            message += f"Sürekli İzinler: {standing_perms}\n\n"

            message += f"Son 7 gün:\n"
            message += f"  • {summary['total_transfers']} veri transferi\n"
            message += f"  • {summary['total_events']} olay kaydı\n"
            message += f"  • {len(summary['destinations'])} farklı hedef\n"

        else:
            message = "═══ ADA.SEA PRIVACY STATUS ═══\n\n"
            message += f"{'✓' if edge_only else '✗'} Edge-Only Mode: {'ENABLED' if edge_only else 'DISABLED'}\n"
            message += f"{'✗' if not cloud_enabled else '✓'} Cloud Sync: {'ENABLED' if cloud_enabled else 'DISABLED'}\n"
            message += f"{'✓' if backup_status['enabled'] else '✗'} Backup: {'ENABLED' if backup_status['enabled'] else 'DISABLED'}\n\n"

            message += f"Active Permissions: {active_perms}\n"
            message += f"Standing Permissions: {standing_perms}\n\n"

            message += f"Last 7 days:\n"
            message += f"  • {summary['total_transfers']} data transfers\n"
            message += f"  • {summary['total_events']} events logged\n"
            message += f"  • {len(summary['destinations'])} destinations\n"

        return {
            'success': True,
            'message': message,
            'status': {
                'edge_only': edge_only,
                'cloud_sync': cloud_enabled,
                'backup_enabled': backup_status['enabled'],
                'active_permissions': active_perms,
                'standing_permissions': standing_perms,
                'recent_activity': summary
            }
        }

    async def enable_edge_only_mode(
        self,
        captain_id: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Enable edge-only mode (no cloud)

        Args:
            captain_id: Captain identifier
            language: Language

        Returns:
            Result
        """
        self.privacy_core.disable_cloud_sync()

        if language == "tr":
            message = "✓ Edge-only modu AKTİF\n" \
                     "✓ Tüm veriler cihazınızda kalacak\n" \
                     "✓ Hiçbir otomatik bulut paylaşımı yapılmayacak"
        else:
            message = "✓ Edge-only mode ENABLED\n" \
                     "✓ All data will stay on your device\n" \
                     "✓ No automatic cloud sharing"

        return {
            'success': True,
            'message': message
        }

    def _translate(self, text: str, language: str) -> str:
        """
        Simple translation helper

        Args:
            text: Text to translate
            language: Target language

        Returns:
            Translated text
        """
        # In production, use proper i18n
        translations = {
            "Komut anlaşılamadı": {
                "en": "Command not understood",
                "el": "Η εντολή δεν κατανοήθηκε"
            },
            "Komut henüz desteklenmiyor": {
                "en": "Command not yet supported",
                "el": "Η εντολή δεν υποστηρίζεται ακόμα"
            }
        }

        if language == "tr":
            return text

        return translations.get(text, {}).get(language, text)

    def _get_command_suggestions(self, language: str) -> List[str]:
        """
        Get command suggestions for language

        Args:
            language: Language

        Returns:
            List of example commands
        """
        if language == "tr":
            return [
                "Ada, veri paylaşım geçmişini göster",
                "Ada, gizlilik durumunu göster",
                "Ada, tüm paylaşımları iptal et",
                "Ada, yedek durumunu göster"
            ]
        elif language == "en":
            return [
                "Ada, show data sharing history",
                "Ada, show privacy status",
                "Ada, revoke all permissions",
                "Ada, show backup status"
            ]
        else:
            return []
