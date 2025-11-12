# 🔒 ADA.SEA PRIVACY-FIRST ARCHITECTURE

> **"Kaptan ne derse o olur. Nokta."** - Captain's word is final.

## Executive Summary

ADA.SEA implements a **zero-trust, edge-first privacy architecture** that fundamentally differs from cloud-based competitors like Zora. This document describes the privacy-first design that makes ADA.SEA the **most privacy-conscious maritime platform** in the industry.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Privacy Principles](#core-privacy-principles)
3. [Implementation Details](#implementation-details)
4. [API Reference](#api-reference)
5. [Compliance](#compliance)
6. [Comparison with Competitors](#comparison-with-competitors)
7. [Demo Scenarios](#demo-scenarios)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────┐
│                  CAPTAIN                         │
│              (Voice/UI Control)                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        CaptainControlInterface                   │
│  • Voice command processing (TR/EN/EL)          │
│  • Privacy status dashboard                      │
│  • Permission management                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         AdaSeaPrivacyCore                       │
│  • Zero-trust enforcement                        │
│  • Data classification (4 levels)                │
│  • Edge-first architecture                       │
│  • Captain authorization required                │
└────┬──────────┬──────────┬──────────┬───────────┘
     │          │          │          │
     ▼          ▼          ▼          ▼
┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
│Consent  │ │ Audit    │ │Encrypt │ │Compliance│
│Manager  │ │ Logger   │ │Service │ │KVKK/GDPR │
└─────────┘ └──────────┘ └────────┘ └──────────┘
```

### Data Flow

```
Captain Request
    ↓
Voice Command Detected
    ↓
Privacy Core Validates
    ↓
[REQUIRES CAPTAIN CONSENT?]
    ↓ YES
Captain Prompt (Voice/UI)
    ↓
Captain Approves/Denies
    ↓ APPROVED
Data Minimization Filter
    ↓
Encryption (AES-256-GCM)
    ↓
Audit Log Entry
    ↓
Secure Transfer (mTLS)
    ↓
[EXTERNAL DESTINATION]
```

---

## Core Privacy Principles

### 1. Zero Trust by Default

**NO automatic data sharing. Ever.**

```python
class AdaSeaPrivacyCore:
    def __init__(self):
        self.captain_auth_required = True  # ALWAYS
        self.cloud_sync_enabled = False    # Disabled by default
        self.edge_only_mode = True         # Data stays on device
```

### 2. Explicit Captain Consent

Every data transfer requires captain's explicit approval:

**Turkish Voice Prompt:**
```
"Kaptan, Yalikavak Marina'ya tekne ölçüleri
gönderilsin mi? Cevap: 'Evet paylaş' veya 'Hayır'"
```

**English Voice Prompt:**
```
"Captain, share vessel dimensions with Yalikavak Marina?
Reply: 'Yes, share' or 'No'"
```

### 3. Data Classification

Four levels of data protection:

| Level | Classification | Examples | Sharing Policy |
|-------|---------------|----------|----------------|
| **0** | PRIVATE | GPS history, financial data, passwords | NEVER without explicit command |
| **1** | RESTRICTED | Current position, vessel specs | Essential data only, captain approval |
| **2** | CONDITIONAL | Weather prefs, route style | Captain consent (one-time or standing) |
| **3** | ANONYMOUS | Popular routes, ratings | Anonymous/aggregated only |

### 4. Data Minimization

**Only send what's absolutely necessary:**

```python
# Marina booking example
minimal_data = {
    'vessel_length': 65,
    'vessel_beam': 5.5,
    'arrival_time': '2025-11-13T14:00:00Z'
    # NO: GPS history, crew info, financial data
}
```

### 5. Complete Audit Trail

Every data transfer is logged:

```python
transfer_log = {
    'timestamp': '2025-11-12T15:45:00Z',
    'destination': 'Yalikavak Marina',
    'data_type': 'vessel_specifications',
    'data_hash': 'sha256:abc123...',
    'captain_id': 'boss@ada.sea',
    'permission_id': 'perm_xyz789',
    'success': True
}
```

### 6. Edge Computing

**Data stays on device (Mac Mini M4):**

- All processing on-board
- No automatic cloud sync
- No remote admin access
- Captain's physical control

### 7. Zero-Knowledge Cloud Backup (Optional)

**If captain enables backup:**

- Client-side encryption ONLY
- Captain's key NEVER leaves device
- Ada.sea cannot read backups
- Captain can delete anytime

---

## Implementation Details

### Core Modules

#### 1. Privacy Core (`app/privacy/core.py`)

The foundational privacy enforcement layer.

**Key Features:**
- Zero-trust enforcement
- Data classification
- Captain authorization
- Secure data transfer

**Example Usage:**
```python
from app.privacy.core import AdaSeaPrivacyCore

privacy_core = AdaSeaPrivacyCore(
    consent_manager=consent_manager,
    audit_logger=audit_logger,
    encryption_service=encryption_service,
    captain_auth_required=True,
    edge_only_mode=True
)

# Attempt to share data (requires captain approval)
result = await privacy_core.share_data(
    destination='Yalikavak Marina',
    data={'vessel_length': 65, 'arrival_time': '14:00'},
    data_type='vessel_specifications',
    purpose='berth_assignment',
    captain_id='boss@ada.sea'
)
```

#### 2. Consent Manager (`app/privacy/consent.py`)

Manages captain consent for all data operations.

**Features:**
- Voice confirmation support
- Standing permissions (pre-approved)
- Granular field-level control
- Consent expiration
- Full audit trail

**Consent Flow:**
```python
# 1. Request permission
permission = await consent_manager.request_permission(
    destination='Yalikavak Marina',
    data_type='vessel_specifications',
    purpose='berth_assignment',
    captain_id='boss@ada.sea',
    language='tr'
)

# 2. Captain approves (via voice or UI)
approved_permission = consent_manager.grant_permission(
    request_id=permission.request_id,
    captain_id='boss@ada.sea',
    method=ConsentMethod.VOICE,
    duration=ConsentDuration.ONE_TIME
)

# 3. Use permission for data sharing
# (automatically validated by privacy core)
```

#### 3. Audit Logger (`app/privacy/audit.py`)

Complete transparency and audit trail.

**Features:**
- Tamper-proof logs (append-only)
- Encrypted storage
- Complete data transfer history
- Privacy setting changes
- Exportable for compliance

**Example:**
```python
# Log data transfer
transfer_log = await audit_logger.log_transfer(
    timestamp=datetime.utcnow(),
    destination='Yalikavak Marina',
    data_type='vessel_specifications',
    data_hash='sha256:...',
    captain_id='boss@ada.sea',
    permission_id='perm_123',
    purpose='berth_assignment',
    data_summary='vessel_length, vessel_beam, arrival_time'
)

# Get audit summary
summary = audit_logger.get_audit_summary('boss@ada.sea', days=7)
# Returns: transfers, destinations, data types shared
```

#### 4. Encryption Service (`app/privacy/encryption.py`)

Client-side encryption for data protection.

**Features:**
- AES-256-GCM encryption
- Client-side key generation
- Keys never leave device
- PBKDF2 key derivation

**Zero-Knowledge Backup:**
```python
# Enable backup (captain must provide passphrase)
await backup_system.enable_backup(
    captain_id='boss@ada.sea',
    passphrase='captain_secret_phrase'
)

# Backup data (encrypted client-side)
result = await backup_system.backup_data(
    data={'navigation_prefs': {...}},
    data_type='preferences',
    captain_id='boss@ada.sea'
)

# Ada.sea server stores encrypted blob
# Only captain can decrypt with their passphrase
```

#### 5. Captain Control Interface (`app/privacy/captain_control.py`)

Voice and UI controls for privacy management.

**Turkish Voice Commands:**
```
✓ "Ada, veri paylaşım geçmişini göster"
✓ "Ada, hangi bilgileri kimle paylaştım?"
✓ "Ada, tüm paylaşımları iptal et"
✓ "Ada, gizlilik durumunu göster"
✓ "Ada, yedeklemeyi aktif et"
```

#### 6. Compliance Layer (`app/privacy/compliance.py`)

KVKK and GDPR compliance.

**Features:**
- Data subject rights (access, erasure, portability)
- Legal basis tracking
- DPIA (Data Protection Impact Assessment)
- Breach notification
- Compliance reporting

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1/privacy
```

### Key Endpoints

#### Get Privacy Status

```http
GET /privacy/status
```

**Response:**
```json
{
  "status": "operational",
  "edge_only_mode": true,
  "cloud_sync_enabled": false,
  "captain_auth_required": true,
  "encryption": "AES-256-GCM",
  "compliance": ["KVKK", "GDPR"],
  "zero_trust": true
}
```

#### Process Voice Command

```http
POST /privacy/voice-command
Content-Type: application/json

{
  "command": "Ada, veri paylaşım geçmişini göster",
  "captain_id": "boss@ada.sea",
  "language": "tr"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Son 7 günde 3 veri paylaşımı yapıldı...",
  "summary": {
    "total_transfers": 3,
    "successful_transfers": 3,
    "destinations": ["Yalikavak Marina", "West Istanbul Marina"]
  }
}
```

#### Get Captain Privacy Status

```http
GET /privacy/captain/{captain_id}/status?language=tr
```

#### Share Data (Requires Consent)

```http
POST /privacy/share-data
Content-Type: application/json

{
  "destination": "Yalikavak Marina",
  "data": {
    "vessel_length": 65,
    "vessel_beam": 5.5,
    "arrival_time": "2025-11-13T14:00:00Z"
  },
  "data_type": "vessel_specifications",
  "purpose": "berth_assignment",
  "captain_id": "boss@ada.sea"
}
```

#### Revoke All Permissions

```http
POST /privacy/captain/{captain_id}/permissions/revoke-all
```

#### KVKK Access Request (Article 11)

```http
POST /privacy/compliance/kvkk/access-request?captain_id={captain_id}
```

**Returns all personal data held by the system.**

#### KVKK Erasure Request (Right to be Forgotten)

```http
POST /privacy/compliance/kvkk/erasure-request?captain_id={captain_id}&reason=Captain request
```

**Full API documentation:** `/docs` (Swagger UI)

---

## Compliance

### KVKK (Turkish Data Protection Law)

**Kişisel Verilerin Korunması Kanunu**

ADA.SEA complies with all KVKK requirements:

✓ **Article 5** - Lawfulness (explicit consent)
✓ **Article 6** - Purpose limitation
✓ **Article 7** - Data minimization
✓ **Article 8** - Accuracy
✓ **Article 9** - Storage limitation
✓ **Article 10** - Security measures
✓ **Article 11** - Data subject rights

**Captain Rights:**
- Access to all personal data
- Rectification of incorrect data
- Erasure (right to be forgotten)
- Restriction of processing
- Data portability
- Object to processing

**Data Controller:**
- Name: Ada.sea Platform
- Contact: privacy@ada.sea
- DPO: veri-sorumlusu@ada.sea
- VERBİS Registration: [To be obtained]

### GDPR (EU Data Protection Regulation)

ADA.SEA complies with GDPR for operations in EU waters:

✓ **Article 5** - Data processing principles
✓ **Article 6** - Legal basis for processing
✓ **Article 25** - Privacy by design and default
✓ **Article 32** - Security of processing
✓ **Article 33** - Breach notification (72 hours)
✓ **Article 35** - Data Protection Impact Assessment

**Legal Basis:**
- Consent (explicit captain approval)
- Contract (marina services)
- Vital interests (safety-critical operations)
- Legitimate interest (navigation assistance)

---

## Comparison with Competitors

### ADA.SEA vs Zora

| Feature | Zora | ADA.SEA |
|---------|------|---------|
| **Default Cloud Sync** | ✓ Enabled | ✗ Disabled |
| **Third-party Sharing** | Via SDK | Captain approval only |
| **Encryption** | TLS in transit | E2E + at-rest |
| **Data Ownership** | Unclear | 100% captain |
| **Audit Trail** | Limited | Complete |
| **Right to Delete** | Support ticket | Instant, captain command |
| **Anonymous Mode** | No | Yes (no cloud ever) |
| **KVKK Compliant** | Unknown | By design |
| **GDPR Compliant** | Likely | By design |
| **Backup Encryption** | Standard | Zero-knowledge |
| **Voice Privacy Controls** | No | Yes (Turkish/English/Greek) |

### Architecture Comparison

**Zora's Model:**
```
Zora Server (Cloud)
    ↓
Third-party Services
    ↓
User consent: Ambiguous
```

**ADA.SEA's Model:**
```
ADA.SEA (100% Edge - Mac Mini M4)
    ↓
NO automatic cloud sync
    ↓
NO third-party data sharing
    ↓
EXPLICIT captain command required for ANY data transfer
```

---

## Demo Scenarios

### Scenario 1: Marina Check-in

**Captain:** "Ada, West Istanbul Marina'ya check-in yap"

**Ada.sea:**
```
Marina'ya şu bilgileri göndermem gerekiyor:
• Tekne: Phisedelia
• Uzunluk: 65 feet
• Berth: C-42

Onaylıyor musunuz?
```

**Captain:** "Evet"

**Ada.sea:** ✓ "Check-in tamamlandı."

**Internally Logged:**
```json
{
  "timestamp": "2025-11-12T15:45:00Z",
  "destination": "West Istanbul Marina",
  "data_sent": ["vessel_name", "length", "berth_number"],
  "not_sent": ["gps_history", "crew_info", "financial_data"],
  "captain_approved": "voice_confirmation"
}
```

### Scenario 2: Review Privacy Status

**Captain:** "Ada, gizlilik durumunu göster"

**Ada.sea:**
```
═══ ADA.SEA GİZLİLİK DURUMU ═══

✓ Edge-Only Modu: AKTİF
✗ Bulut Senkronizasyonu: DEVREDİŞI
✗ Yedekleme: DEVREDİŞI

Aktif İzinler: 1
Sürekli İzinler: 0

Son 7 gün:
  • 3 veri transferi
  • 12 olay kaydı
  • 2 farklı hedef
```

### Scenario 3: Revoke All Permissions

**Captain:** "Ada, tüm paylaşımları iptal et"

**Ada.sea:**
```
✓ Tüm veri paylaşım izinleri iptal edildi.
Bundan sonra her paylaşım için onay isteyeceğim.
```

### Scenario 4: KVKK Access Request

**Captain (via UI):** Request all personal data

**Ada.sea Response:**
```json
{
  "captain_id": "boss@ada.sea",
  "request_type": "access",
  "processed_at": "2025-11-12T16:00:00Z",
  "data": {
    "transfer_logs": [...],
    "consent_history": [...],
    "active_permissions": 0,
    "summary": {
      "total_transfers": 3,
      "destinations": ["West Istanbul Marina", "Yalikavak Marina"]
    }
  }
}
```

---

## Testing the Privacy Layer

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/privacy/ -v

# Run privacy demo
python scripts/privacy_demo.py
```

### Manual Testing via API

```bash
# 1. Get privacy status
curl http://localhost:8000/api/v1/privacy/status

# 2. Process voice command
curl -X POST http://localhost:8000/api/v1/privacy/voice-command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "Ada, gizlilik durumunu göster",
    "captain_id": "boss@ada.sea",
    "language": "tr"
  }'

# 3. Get captain status
curl http://localhost:8000/api/v1/privacy/captain/boss@ada.sea/status?language=tr

# 4. Get sharing history
curl http://localhost:8000/api/v1/privacy/captain/boss@ada.sea/history?days=7

# 5. Revoke all permissions
curl -X POST http://localhost:8000/api/v1/privacy/captain/boss@ada.sea/permissions/revoke-all
```

---

## Security Best Practices

### For Deployment

1. **Enable HTTPS**: Always use TLS 1.3+
2. **Certificate Pinning**: Pin marina service certificates
3. **Network Isolation**: Firewall deny-all inbound
4. **Key Storage**: Use TPM/Secure Enclave for keys
5. **Regular Audits**: Review audit logs weekly
6. **Backup Encryption**: Enable zero-knowledge backup
7. **Access Control**: Biometric auth for captain

### For Development

1. **Never commit keys**: Use `.env` for secrets
2. **Test consent flow**: Verify all data sharing requires approval
3. **Audit logging**: Ensure all transfers are logged
4. **Data minimization**: Only send necessary fields
5. **Encryption**: Always encrypt sensitive data

---

## Troubleshooting

### Permission Denied Errors

**Problem:** Data transfer fails with "Captain denied permission"

**Solution:** Ensure captain has explicitly approved the transfer via voice or UI.

### Backup Not Working

**Problem:** Backup enabled but data not backing up

**Solution:** Verify captain has provided passphrase and encryption key exists.

### Audit Logs Not Appearing

**Problem:** Data transfers not showing in audit log

**Solution:** Check `audit_logger.log_transfer()` is called before transfer executes.

---

## Future Enhancements

### Phase 1 (Current)
✓ Core privacy architecture
✓ Consent management
✓ Audit logging
✓ KVKK/GDPR compliance

### Phase 2 (Next)
- Voice recognition integration
- Biometric authentication
- Real-time breach detection
- Advanced DPIA automation

### Phase 3 (Future)
- Federated learning (privacy-preserving AI)
- Blockchain audit trail
- Multi-signature authorization
- Homomorphic encryption

---

## Support & Contact

**Privacy Questions:**
- Email: privacy@ada.sea
- DPO: veri-sorumlusu@ada.sea

**Technical Support:**
- Documentation: https://docs.ada.sea
- GitHub: https://github.com/ahmetengin/ada-marina-wim

**Regulatory Compliance:**
- Turkish DPA: https://kvkk.gov.tr
- GDPR Helpdesk: dpo@ada.sea

---

## License

Copyright © 2025 ADA.SEA Platform

This privacy architecture is proprietary and confidential.

---

**Built with ❤️ for maritime privacy**
**"Kaptan ne derse o olur. Nokta."**
