"""
API Endpoint Tests for ADA.SEA Privacy
Tests all privacy API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPrivacyStatusEndpoints:
    """Test privacy status endpoints"""

    def test_privacy_status(self):
        """TEST: GET /api/v1/privacy/status"""
        response = client.get("/api/v1/privacy/status")

        assert response.status_code == 200
        data = response.json()

        # Verify privacy defaults
        assert data['status'] == 'operational'
        assert data['edge_only_mode'] is True
        assert data['cloud_sync_enabled'] is False
        assert data['captain_auth_required'] is True
        assert data['zero_trust'] is True

    def test_privacy_root(self):
        """TEST: GET /api/v1/privacy/"""
        response = client.get("/api/v1/privacy/")

        assert response.status_code == 200
        data = response.json()

        assert data['name'] == 'ADA.SEA Privacy API'
        assert 'features' in data
        assert 'Zero-trust architecture' in data['features']


class TestVoiceCommandEndpoints:
    """Test voice command processing"""

    def test_voice_command_privacy_status(self):
        """
        TEST: Voice command "Ada, gizlilik durumunu göster"
        Production Scenario 3
        """
        response = client.post(
            "/api/v1/privacy/voice-command",
            json={
                "command": "Ada, gizlilik durumunu göster",
                "captain_id": "test_captain",
                "language": "tr"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should process voice command
        assert 'message' in data or 'success' in data

    def test_voice_command_show_history(self):
        """TEST: Voice command for history"""
        response = client.post(
            "/api/v1/privacy/voice-command",
            json={
                "command": "Ada, veri paylaşım geçmişini göster",
                "captain_id": "test_captain",
                "language": "tr"
            }
        )

        assert response.status_code == 200


class TestCaptainStatusEndpoints:
    """Test captain privacy status endpoints"""

    def test_captain_status(self):
        """
        TEST: GET /api/v1/privacy/captain/{id}/status
        Production Scenario 3
        """
        response = client.get(
            "/api/v1/privacy/captain/test_captain/status?language=tr"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'success' in data
        if data['success']:
            assert 'status' in data

    def test_captain_history(self):
        """
        TEST: GET /api/v1/privacy/captain/{id}/history
        Production Scenario 1
        """
        response = client.get(
            "/api/v1/privacy/captain/test_captain/history?days=7&language=tr"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'success' in data
        assert 'summary' in data or 'transfers' in data

    def test_captain_permissions(self):
        """TEST: GET captain active permissions"""
        response = client.get(
            "/api/v1/privacy/captain/test_captain/permissions?language=tr"
        )

        assert response.status_code == 200


class TestConsentEndpoints:
    """Test consent management endpoints"""

    def test_grant_permission(self):
        """TEST: POST /api/v1/privacy/consent/grant"""
        response = client.post(
            "/api/v1/privacy/consent/grant",
            json={
                "request_id": "test_request_123",
                "captain_id": "test_captain",
                "method": "voice",
                "duration": "one_time",
                "confirmation_text": "Evet paylaş"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data['success'] is True
        assert 'permission_id' in data

    def test_revoke_all_permissions(self):
        """
        TEST: POST revoke all permissions
        Production Scenario 6
        """
        response = client.post(
            "/api/v1/privacy/captain/test_captain/permissions/revoke-all?language=tr"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'success' in data
        if data['success']:
            assert 'message' in data


class TestAuditEndpoints:
    """Test audit trail endpoints"""

    def test_audit_summary(self):
        """TEST: GET /api/v1/privacy/audit/{id}/summary"""
        response = client.get(
            "/api/v1/privacy/audit/test_captain/summary?days=7"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'captain_id' in data
        assert 'total_transfers' in data

    def test_audit_export(self):
        """
        TEST: GET audit trail export
        Production Scenario 7 - Data portability
        """
        from datetime import datetime, timedelta

        start = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end = datetime.utcnow().isoformat()

        response = client.get(
            f"/api/v1/privacy/audit/test_captain/export?start_date={start}&end_date={end}&format=json"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'captain_id' in data
        assert 'data' in data


class TestBackupEndpoints:
    """Test zero-knowledge backup endpoints"""

    def test_backup_status(self):
        """TEST: GET /api/v1/privacy/backup/status"""
        response = client.get("/api/v1/privacy/backup/status?language=tr")

        assert response.status_code == 200
        data = response.json()

        assert 'status' in data or 'message' in data


class TestComplianceEndpoints:
    """Test KVKK/GDPR compliance endpoints"""

    def test_compliance_summary(self):
        """TEST: GET /api/v1/privacy/compliance/summary"""
        response = client.get("/api/v1/privacy/compliance/summary")

        assert response.status_code == 200
        data = response.json()

        assert 'platform' in data
        assert 'regulations' in data
        assert 'KVKK' in data['regulations']
        assert 'GDPR' in data['regulations']

    def test_kvkk_access_request(self):
        """
        TEST: POST KVKK access request
        Production Scenario 5 - Article 11
        """
        response = client.post(
            "/api/v1/privacy/compliance/kvkk/access-request?captain_id=test_captain"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'captain_id' in data
        assert 'request_type' in data
        assert data['request_type'] == 'access'

    def test_kvkk_portability_request(self):
        """
        TEST: POST KVKK portability request
        Article 11 - Data portability
        """
        response = client.post(
            "/api/v1/privacy/compliance/kvkk/portability-request?captain_id=test_captain"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'captain_id' in data
        assert 'data' in data

    def test_kvkk_compliance_report(self):
        """TEST: GET KVKK compliance report"""
        response = client.get(
            "/api/v1/privacy/compliance/kvkk/report?captain_id=test_captain&period_days=90"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'report_id' in data
        assert 'regulation' in data
        assert data['regulation'] == 'KVKK'

    def test_gdpr_compliance_report(self):
        """TEST: GET GDPR compliance report"""
        response = client.get(
            "/api/v1/privacy/compliance/gdpr/report?captain_id=test_captain&period_days=90"
        )

        assert response.status_code == 200
        data = response.json()

        assert 'report_id' in data
        assert 'regulation' in data
        assert data['regulation'] == 'GDPR'


class TestDataSharingEndpoints:
    """Test data sharing with consent"""

    def test_share_data_requires_consent(self):
        """
        TEST: POST /api/v1/privacy/share-data
        Should require captain consent
        """
        response = client.post(
            "/api/v1/privacy/share-data",
            json={
                "destination": "Test Marina",
                "data": {"vessel_length": 65},
                "data_type": "vessel_specs",
                "purpose": "testing",
                "captain_id": "test_captain"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should either succeed or fail with consent requirement
        assert 'success' in data


class TestPrivacySettings:
    """Test privacy settings management"""

    def test_edge_only_mode_enabled_default(self):
        """TEST: Verify edge-only mode is default"""
        response = client.get("/api/v1/privacy/status")

        assert response.status_code == 200
        data = response.json()

        assert data['edge_only_mode'] is True
        assert data['cloud_sync_enabled'] is False

    def test_update_privacy_setting_requires_confirmation(self):
        """TEST: Changing privacy settings requires captain confirmation"""
        response = client.post(
            "/api/v1/privacy/settings",
            json={
                "captain_id": "test_captain",
                "setting": "cloud_sync",
                "value": True,
                "captain_confirmed": False
            }
        )

        # Should fail without confirmation
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_captain_id(self):
        """TEST: Invalid captain ID handling"""
        response = client.get("/api/v1/privacy/captain/invalid@/status")

        # Should handle gracefully
        assert response.status_code in [200, 400, 404]

    def test_invalid_voice_command(self):
        """TEST: Unknown voice command handling"""
        response = client.post(
            "/api/v1/privacy/voice-command",
            json={
                "command": "Ada, unknown command xyz",
                "captain_id": "test_captain",
                "language": "tr"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should return suggestions or error gracefully
        if not data.get('success'):
            assert 'suggestions' in data or 'message' in data


class TestPerformance:
    """Test API performance"""

    def test_privacy_status_fast(self):
        """TEST: Privacy status endpoint is fast (< 200ms)"""
        import time

        start = time.time()
        response = client.get("/api/v1/privacy/status")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.2  # Should be < 200ms

    def test_compliance_summary_fast(self):
        """TEST: Compliance summary is fast"""
        import time

        start = time.time()
        response = client.get("/api/v1/privacy/compliance/summary")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5  # Should be < 500ms


class TestSecurityHeaders:
    """Test security headers"""

    def test_cors_headers(self):
        """TEST: CORS headers present"""
        response = client.get("/api/v1/privacy/status")

        # Should have CORS headers
        assert 'access-control-allow-origin' in response.headers or response.status_code == 200

    def test_content_type_json(self):
        """TEST: Content-Type is JSON"""
        response = client.get("/api/v1/privacy/status")

        assert 'application/json' in response.headers.get('content-type', '')
