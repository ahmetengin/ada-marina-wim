"""
ADA.SEA Privacy API Endpoints
RESTful API for privacy controls and captain interface
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Privacy system imports
from app.privacy.core import AdaSeaPrivacyCore, DataClassification
from app.privacy.consent import ConsentManager, ConsentDuration, ConsentMethod
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService, ZeroKnowledgeBackup
from app.privacy.captain_control import CaptainControlInterface
from app.privacy.compliance import KVKKCompliance, GDPRCompliance, get_compliance_summary

router = APIRouter(tags=["privacy"])


# Pydantic models for API
class DataShareRequest(BaseModel):
    """Request to share data"""
    destination: str
    data: dict
    data_type: str
    purpose: str
    captain_id: str


class VoiceCommandRequest(BaseModel):
    """Voice command from captain"""
    command: str
    captain_id: str
    language: str = "tr"


class ConsentGrantRequest(BaseModel):
    """Grant permission"""
    request_id: str
    captain_id: str
    method: str = "manual"
    duration: str = "one_time"
    allowed_fields: Optional[List[str]] = None
    confirmation_text: Optional[str] = None


class BackupEnableRequest(BaseModel):
    """Enable backup"""
    captain_id: str
    passphrase: str


class PrivacySettingRequest(BaseModel):
    """Change privacy setting"""
    captain_id: str
    setting: str
    value: bool
    captain_confirmed: bool = False


# Dependency to get privacy system instances
# In production, these would be singletons or from dependency injection
def get_privacy_system():
    """Get privacy system components"""
    encryption_service = EncryptionService()
    audit_logger = AuditLogger()
    consent_manager = ConsentManager()
    backup_system = ZeroKnowledgeBackup(encryption_service)

    privacy_core = AdaSeaPrivacyCore(
        consent_manager=consent_manager,
        audit_logger=audit_logger,
        encryption_service=encryption_service,
        captain_auth_required=True,
        cloud_sync_enabled=False,
        edge_only_mode=True
    )

    captain_control = CaptainControlInterface(
        privacy_core=privacy_core,
        consent_manager=consent_manager,
        audit_logger=audit_logger,
        backup_system=backup_system
    )

    kvkk_compliance = KVKKCompliance(audit_logger, consent_manager)
    gdpr_compliance = GDPRCompliance(audit_logger, consent_manager)

    return {
        'privacy_core': privacy_core,
        'consent_manager': consent_manager,
        'audit_logger': audit_logger,
        'encryption_service': encryption_service,
        'backup_system': backup_system,
        'captain_control': captain_control,
        'kvkk_compliance': kvkk_compliance,
        'gdpr_compliance': gdpr_compliance
    }


@router.get("/privacy/status")
async def get_privacy_status():
    """
    Get overall privacy system status

    Returns edge-only mode, encryption status, compliance info
    """
    system = get_privacy_system()

    return {
        'status': 'operational',
        'edge_only_mode': system['privacy_core'].edge_only_mode,
        'cloud_sync_enabled': system['privacy_core'].cloud_sync_enabled,
        'captain_auth_required': system['privacy_core'].captain_auth_required,
        'encryption': 'AES-256-GCM',
        'compliance': ['KVKK', 'GDPR'],
        'zero_trust': True,
        'privacy_first': True
    }


@router.post("/privacy/voice-command")
async def process_voice_command(request: VoiceCommandRequest):
    """
    Process captain's voice command for privacy control

    Example commands (Turkish):
    - "Ada, veri paylaşım geçmişini göster"
    - "Ada, gizlilik durumunu göster"
    - "Ada, tüm paylaşımları iptal et"
    """
    system = get_privacy_system()

    result = await system['captain_control'].process_voice_command(
        command=request.command,
        captain_id=request.captain_id,
        language=request.language
    )

    return result


@router.get("/privacy/captain/{captain_id}/status")
async def get_captain_privacy_status(captain_id: str, language: str = "tr"):
    """
    Get complete privacy status for captain

    Shows:
    - Edge-only mode status
    - Active permissions
    - Recent data sharing activity
    - Backup status
    """
    system = get_privacy_system()

    status = await system['captain_control'].show_privacy_status(
        captain_id=captain_id,
        language=language
    )

    return status


@router.get("/privacy/captain/{captain_id}/history")
async def get_sharing_history(captain_id: str, days: int = 7, language: str = "tr"):
    """
    Get captain's data sharing history

    Args:
        captain_id: Captain identifier
        days: Number of days to look back
        language: Response language
    """
    system = get_privacy_system()

    history = await system['captain_control'].show_data_sharing_history(
        captain_id=captain_id,
        days=days,
        language=language
    )

    return history


@router.get("/privacy/captain/{captain_id}/permissions")
async def get_permissions(captain_id: str, language: str = "tr"):
    """
    Get captain's active and standing permissions
    """
    system = get_privacy_system()

    permissions = await system['captain_control'].show_active_permissions(
        captain_id=captain_id,
        language=language
    )

    return permissions


@router.post("/privacy/captain/{captain_id}/permissions/revoke-all")
async def revoke_all_permissions(captain_id: str, language: str = "tr"):
    """
    Revoke all permissions for captain

    This will disable all automatic data sharing
    """
    system = get_privacy_system()

    result = await system['captain_control'].revoke_all_permissions(
        captain_id=captain_id,
        language=language
    )

    return result


@router.post("/privacy/share-data")
async def share_data(request: DataShareRequest):
    """
    Share data with external destination

    Requires captain authorization unless standing permission exists
    """
    system = get_privacy_system()

    result = await system['privacy_core'].share_data(
        destination=request.destination,
        data=request.data,
        data_type=request.data_type,
        purpose=request.purpose,
        captain_id=request.captain_id
    )

    return result


@router.post("/privacy/consent/grant")
async def grant_consent(request: ConsentGrantRequest):
    """
    Grant permission for data sharing

    Called after captain explicitly approves
    """
    system = get_privacy_system()

    permission = system['consent_manager'].grant_permission(
        request_id=request.request_id,
        captain_id=request.captain_id,
        method=ConsentMethod[request.method.upper()],
        duration=ConsentDuration[request.duration.upper()],
        allowed_fields=request.allowed_fields,
        confirmation_text=request.confirmation_text
    )

    return {
        'success': True,
        'permission_id': permission.permission_id,
        'granted': permission.granted
    }


@router.get("/privacy/audit/{captain_id}/summary")
async def get_audit_summary(captain_id: str, days: int = 7):
    """
    Get audit summary for captain

    Shows statistics about data sharing over period
    """
    system = get_privacy_system()

    summary = system['audit_logger'].get_audit_summary(captain_id, days)

    return summary


@router.get("/privacy/audit/{captain_id}/export")
async def export_audit_trail(
    captain_id: str,
    start_date: datetime,
    end_date: datetime,
    format: str = "json"
):
    """
    Export complete audit trail for compliance

    Supports KVKK/GDPR data portability rights
    """
    system = get_privacy_system()

    export = await system['audit_logger'].export_audit_trail(
        captain_id=captain_id,
        start_date=start_date,
        end_date=end_date,
        format=format
    )

    return {
        'captain_id': captain_id,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'format': format,
        'data': export
    }


@router.post("/privacy/backup/enable")
async def enable_backup(request: BackupEnableRequest):
    """
    Enable zero-knowledge cloud backup

    Captain's passphrase is used to generate encryption key
    Key NEVER leaves device
    """
    system = get_privacy_system()

    success = await system['backup_system'].enable_backup(
        captain_id=request.captain_id,
        passphrase=request.passphrase
    )

    return {
        'success': success,
        'zero_knowledge': True,
        'encryption': 'AES-256-GCM',
        'readable_by_ada_sea': False
    }


@router.post("/privacy/backup/disable")
async def disable_backup(captain_id: str, delete_remote: bool = True):
    """
    Disable backup and optionally delete remote backups
    """
    system = get_privacy_system()

    await system['backup_system'].disable_backup(
        captain_id=captain_id,
        delete_remote=delete_remote
    )

    return {
        'success': True,
        'backup_disabled': True,
        'remote_deleted': delete_remote
    }


@router.get("/privacy/backup/status")
async def get_backup_status(language: str = "tr"):
    """
    Get backup system status
    """
    system = get_privacy_system()

    status = await system['captain_control'].show_backup_status(language=language)

    return status


@router.post("/privacy/settings")
async def update_privacy_setting(request: PrivacySettingRequest):
    """
    Update privacy setting

    Requires captain confirmation for critical changes
    """
    system = get_privacy_system()

    if request.setting == "cloud_sync":
        if request.value:
            # Enable cloud sync
            try:
                system['privacy_core'].enable_cloud_sync(
                    captain_confirmed=request.captain_confirmed
                )
                return {
                    'success': True,
                    'setting': 'cloud_sync',
                    'value': True
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            # Disable cloud sync
            system['privacy_core'].disable_cloud_sync()
            return {
                'success': True,
                'setting': 'cloud_sync',
                'value': False
            }

    elif request.setting == "edge_only":
        if request.value:
            result = await system['captain_control'].enable_edge_only_mode(
                captain_id=request.captain_id,
                language="tr"
            )
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail="Cannot disable edge-only mode without enabling cloud sync"
            )

    else:
        raise HTTPException(status_code=400, detail=f"Unknown setting: {request.setting}")


# KVKK/GDPR Compliance Endpoints

@router.get("/privacy/compliance/summary")
async def get_compliance_info():
    """
    Get compliance summary

    Shows KVKK and GDPR compliance features
    """
    return get_compliance_summary()


@router.post("/privacy/compliance/kvkk/access-request")
async def kvkk_access_request(captain_id: str):
    """
    Handle KVKK Article 11 access request

    Captain's right to access all personal data
    """
    system = get_privacy_system()

    data = await system['kvkk_compliance'].handle_access_request(captain_id)

    return data


@router.post("/privacy/compliance/kvkk/erasure-request")
async def kvkk_erasure_request(captain_id: str, reason: str = "Captain request"):
    """
    Handle KVKK Article 11 erasure request

    Right to be forgotten
    """
    system = get_privacy_system()

    result = await system['kvkk_compliance'].handle_erasure_request(
        captain_id=captain_id,
        reason=reason
    )

    return result


@router.post("/privacy/compliance/kvkk/portability-request")
async def kvkk_portability_request(captain_id: str):
    """
    Handle KVKK Article 11 portability request

    Export all data in portable format
    """
    system = get_privacy_system()

    export = await system['kvkk_compliance'].handle_portability_request(captain_id)

    return {
        'captain_id': captain_id,
        'format': 'json',
        'data': export
    }


@router.get("/privacy/compliance/kvkk/report")
async def get_kvkk_compliance_report(captain_id: str, period_days: int = 90):
    """
    Generate KVKK compliance report
    """
    system = get_privacy_system()

    report = await system['kvkk_compliance'].generate_compliance_report(
        captain_id=captain_id,
        period_days=period_days
    )

    return {
        'report_id': report.report_id,
        'generated_at': report.generated_at.isoformat(),
        'captain_id': report.captain_id,
        'regulation': report.regulation,
        'compliant': report.compliant,
        'findings': report.findings,
        'summary': {
            'data_transfers': report.data_transfers,
            'consent_records': report.consent_records
        }
    }


@router.get("/privacy/compliance/gdpr/report")
async def get_gdpr_compliance_report(captain_id: str, period_days: int = 90):
    """
    Generate GDPR compliance report
    """
    system = get_privacy_system()

    report = await system['gdpr_compliance'].generate_compliance_report(
        captain_id=captain_id,
        period_days=period_days
    )

    return {
        'report_id': report.report_id,
        'generated_at': report.generated_at.isoformat(),
        'captain_id': report.captain_id,
        'regulation': report.regulation,
        'compliant': report.compliant,
        'findings': report.findings
    }


@router.get("/")
async def privacy_root():
    """
    Privacy API root - shows available endpoints
    """
    return {
        'name': 'ADA.SEA Privacy API',
        'version': '1.0.0',
        'tagline': 'Kaptan ne derse o olur. Nokta.',
        'features': [
            'Zero-trust architecture',
            'Edge-first computing',
            'Explicit captain consent',
            'Complete audit trail',
            'KVKK/GDPR compliant',
            'Zero-knowledge backup'
        ],
        'endpoints': {
            'status': '/privacy/status',
            'voice_command': '/privacy/voice-command',
            'captain_status': '/privacy/captain/{captain_id}/status',
            'sharing_history': '/privacy/captain/{captain_id}/history',
            'compliance': '/privacy/compliance/summary'
        }
    }
