"""
ADA.SEA Privacy-First Architecture
Zero-trust, edge-first privacy layer for maritime data protection
Compliant with KVKK (Turkish DPA) and GDPR
"""

from .core import AdaSeaPrivacyCore, DataClassification
from .consent import ConsentManager, ConsentRequest
from .audit import AuditLogger, DataTransferLog
from .encryption import EncryptionService, ZeroKnowledgeBackup
from .captain_control import CaptainControlInterface
from .compliance import KVKKCompliance, GDPRCompliance

__all__ = [
    'AdaSeaPrivacyCore',
    'ConsentManager',
    'ConsentRequest',
    'DataClassification',
    'AuditLogger',
    'DataTransferLog',
    'EncryptionService',
    'ZeroKnowledgeBackup',
    'CaptainControlInterface',
    'KVKKCompliance',
    'GDPRCompliance',
]

__version__ = '1.0.0'
