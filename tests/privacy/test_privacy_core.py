"""
Test ADA.SEA Privacy Core
"""

import pytest
from datetime import datetime
from app.privacy.core import (
    AdaSeaPrivacyCore,
    DataClassification,
    UnauthorizedDataShareException
)
from app.privacy.consent import ConsentManager
from app.privacy.audit import AuditLogger
from app.privacy.encryption import EncryptionService


@pytest.fixture
def encryption_service():
    """Encryption service fixture"""
    return EncryptionService()


@pytest.fixture
def audit_logger():
    """Audit logger fixture"""
    return AuditLogger()


@pytest.fixture
def consent_manager():
    """Consent manager fixture"""
    return ConsentManager()


@pytest.fixture
def privacy_core(consent_manager, audit_logger, encryption_service):
    """Privacy core fixture"""
    return AdaSeaPrivacyCore(
        consent_manager=consent_manager,
        audit_logger=audit_logger,
        encryption_service=encryption_service,
        captain_auth_required=True,
        edge_only_mode=True
    )


class TestDataClassification:
    """Test data classification"""

    def test_classify_private_data(self, privacy_core):
        """Test that sensitive data is classified as PRIVATE"""
        classification = privacy_core.classify_data('gps_history')
        assert classification == DataClassification.PRIVATE

    def test_classify_restricted_data(self, privacy_core):
        """Test that vessel specs are RESTRICTED"""
        classification = privacy_core.classify_data('vessel_specifications')
        assert classification == DataClassification.RESTRICTED

    def test_classify_anonymous_data(self, privacy_core):
        """Test that ratings are ANONYMOUS"""
        classification = privacy_core.classify_data('anchorage_ratings')
        assert classification == DataClassification.ANONYMOUS

    def test_unknown_data_defaults_to_private(self, privacy_core):
        """Test that unknown data types default to PRIVATE (fail-safe)"""
        classification = privacy_core.classify_data('unknown_data_type')
        assert classification == DataClassification.PRIVATE


class TestEdgeOnlyMode:
    """Test edge-only mode enforcement"""

    def test_edge_only_mode_enabled_by_default(self, privacy_core):
        """Test that edge-only mode is enabled by default"""
        assert privacy_core.edge_only_mode is True
        assert privacy_core.cloud_sync_enabled is False

    def test_enable_cloud_sync_requires_confirmation(self, privacy_core):
        """Test that enabling cloud sync requires captain confirmation"""
        with pytest.raises(Exception, match="Captain confirmation"):
            privacy_core.enable_cloud_sync(captain_confirmed=False)

    def test_enable_cloud_sync_with_confirmation(self, privacy_core):
        """Test enabling cloud sync with captain confirmation"""
        privacy_core.enable_cloud_sync(captain_confirmed=True)
        assert privacy_core.cloud_sync_enabled is True
        assert privacy_core.edge_only_mode is False

    def test_disable_cloud_sync(self, privacy_core):
        """Test disabling cloud sync"""
        privacy_core.enable_cloud_sync(captain_confirmed=True)
        privacy_core.disable_cloud_sync()
        assert privacy_core.cloud_sync_enabled is False
        assert privacy_core.edge_only_mode is True


class TestDataSharing:
    """Test data sharing with consent"""

    @pytest.mark.asyncio
    async def test_share_data_requires_captain_auth(
        self,
        privacy_core,
        consent_manager
    ):
        """Test that data sharing requires captain authorization"""
        # Without granting permission, share should fail or request permission
        result = await privacy_core.share_data(
            destination='Test Marina',
            data={'vessel_length': 65},
            data_type='vessel_specifications',
            purpose='test',
            captain_id='test_captain'
        )

        # Should either fail or return success=False
        assert result['success'] is False
        assert 'permission' in result['reason'].lower()

    @pytest.mark.asyncio
    async def test_data_hash_calculation(self, privacy_core):
        """Test that data hash is calculated correctly"""
        data = {'vessel_length': 65, 'vessel_beam': 5.5}
        hash1 = privacy_core.calculate_data_hash(data)
        hash2 = privacy_core.calculate_data_hash(data)

        # Same data should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest length


class TestConsentManagement:
    """Test consent management"""

    @pytest.mark.asyncio
    async def test_request_permission(self, consent_manager):
        """Test requesting captain permission"""
        permission = await consent_manager.request_permission(
            destination='Test Marina',
            data_type='vessel_specifications',
            purpose='berth_assignment',
            captain_id='test_captain'
        )

        assert permission is not None
        assert permission.request_id is not None

    def test_grant_permission(self, consent_manager):
        """Test granting permission"""
        from app.privacy.consent import ConsentMethod, ConsentDuration

        permission = consent_manager.grant_permission(
            request_id='test_request',
            captain_id='test_captain',
            method=ConsentMethod.MANUAL,
            duration=ConsentDuration.ONE_TIME
        )

        assert permission.granted is True
        assert permission.captain_id == 'test_captain'

    def test_deny_permission(self, consent_manager):
        """Test denying permission"""
        permission = consent_manager.deny_permission(
            request_id='test_request',
            captain_id='test_captain',
            reason='Captain denied'
        )

        assert permission.granted is False
        assert permission.denial_reason == 'Captain denied'

    def test_revoke_permission(self, consent_manager):
        """Test revoking permission"""
        from app.privacy.consent import ConsentMethod, ConsentDuration

        # Grant permission
        permission = consent_manager.grant_permission(
            request_id='test_request',
            captain_id='test_captain',
            method=ConsentMethod.MANUAL,
            duration=ConsentDuration.STANDING
        )

        # Revoke it
        success = consent_manager.revoke_permission(
            permission.permission_id,
            'test_captain'
        )

        assert success is True


class TestAuditLogging:
    """Test audit logging"""

    @pytest.mark.asyncio
    async def test_log_transfer(self, audit_logger):
        """Test logging data transfer"""
        transfer_log = await audit_logger.log_transfer(
            timestamp=datetime.utcnow(),
            destination='Test Marina',
            data_type='vessel_specifications',
            data_hash='test_hash',
            captain_id='test_captain',
            permission_id='test_permission',
            purpose='test',
            data_summary='length, beam'
        )

        assert transfer_log is not None
        assert transfer_log.destination == 'Test Marina'
        assert transfer_log.captain_id == 'test_captain'

    @pytest.mark.asyncio
    async def test_update_transfer_result(self, audit_logger):
        """Test updating transfer result"""
        # Log transfer
        transfer_log = await audit_logger.log_transfer(
            timestamp=datetime.utcnow(),
            destination='Test Marina',
            data_type='vessel_specifications',
            data_hash='test_hash',
            captain_id='test_captain',
            permission_id='test_permission',
            purpose='test',
            data_summary='length, beam'
        )

        # Update result
        await audit_logger.update_transfer_result(
            transfer_log.transfer_id,
            success=True,
            result={'status': 'completed'}
        )

        # Verify update
        logs = audit_logger.get_transfer_logs(captain_id='test_captain')
        assert len(logs) > 0
        assert logs[0].success is True

    def test_get_audit_summary(self, audit_logger):
        """Test getting audit summary"""
        summary = audit_logger.get_audit_summary('test_captain', days=7)

        assert 'captain_id' in summary
        assert 'total_transfers' in summary
        assert summary['captain_id'] == 'test_captain'


class TestEncryption:
    """Test encryption service"""

    def test_generate_key(self, encryption_service):
        """Test generating encryption key"""
        key = encryption_service.generate_key('test_key')

        assert key is not None
        assert key.key_id == 'test_key'
        assert key.algorithm == 'AES-256-GCM'

    @pytest.mark.asyncio
    async def test_encrypt_decrypt(self, encryption_service):
        """Test encryption and decryption"""
        # Generate key
        encryption_service.generate_key('test_key')

        # Test data
        original_data = {'test': 'data', 'number': 123}

        # Encrypt
        encrypted = await encryption_service.encrypt(original_data, 'test_key')
        assert encrypted is not None
        assert isinstance(encrypted, bytes)

        # Decrypt
        decrypted = await encryption_service.decrypt(encrypted, 'test_key')
        assert decrypted == original_data

    def test_hash_data(self, encryption_service):
        """Test data hashing"""
        data = "test data"
        hash1 = encryption_service.hash_data(data)
        hash2 = encryption_service.hash_data(data)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256


class TestComplianceReporting:
    """Test KVKK/GDPR compliance"""

    @pytest.mark.asyncio
    async def test_kvkk_access_request(self, audit_logger, consent_manager):
        """Test KVKK access request"""
        from app.privacy.compliance import KVKKCompliance

        kvkk = KVKKCompliance(audit_logger, consent_manager)

        data = await kvkk.handle_access_request('test_captain')

        assert 'captain_id' in data
        assert data['captain_id'] == 'test_captain'
        assert 'data' in data

    @pytest.mark.asyncio
    async def test_kvkk_erasure_request(self, audit_logger, consent_manager):
        """Test KVKK erasure request (right to be forgotten)"""
        from app.privacy.compliance import KVKKCompliance

        kvkk = KVKKCompliance(audit_logger, consent_manager)

        result = await kvkk.handle_erasure_request('test_captain')

        assert 'captain_id' in result
        assert result['captain_id'] == 'test_captain'
        assert result['status'] == 'completed'

    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, audit_logger, consent_manager):
        """Test generating KVKK compliance report"""
        from app.privacy.compliance import KVKKCompliance

        kvkk = KVKKCompliance(audit_logger, consent_manager)

        report = await kvkk.generate_compliance_report('test_captain', period_days=7)

        assert report is not None
        assert report.captain_id == 'test_captain'
        assert report.regulation == 'KVKK'
        assert isinstance(report.compliant, bool)
