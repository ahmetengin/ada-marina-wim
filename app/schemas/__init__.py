"""
Pydantic schemas for API requests and responses
"""

# Berth schemas
from app.schemas.berth import (
    BerthBase,
    BerthCreate,
    BerthUpdate,
    BerthResponse,
    BerthSection,
    BerthStatus,
)

# Customer schemas
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)

# Vessel schemas
from app.schemas.vessel import (
    VesselBase,
    VesselCreate,
    VesselUpdate,
    VesselResponse,
    VesselType,
)

# Assignment schemas
from app.schemas.assignment import (
    AssignmentBase,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentResponse,
    AssignmentStatus,
)

# VHF Log schemas
from app.schemas.vhf import (
    VHFLogBase,
    VHFLogCreate,
    VHFLogResponse,
    VHFDirection,
    VHFIntent,
)

# Invoice schemas
from app.schemas.invoice import (
    InvoiceBase,
    InvoiceCreate,
    InvoiceResponse,
    InvoiceStatus,
)

# Violation schemas
from app.schemas.violation import (
    ViolationBase,
    ViolationCreate,
    ViolationUpdate,
    ViolationResponse,
    ViolationSeverity,
    ViolationStatus,
)

# Permit schemas
from app.schemas.permit import (
    PermitBase,
    PermitCreate,
    PermitUpdate,
    PermitResponse,
    PermitType,
    PermitStatus,
)

# SEAL Learning schemas
from app.schemas.seal_learning import (
    SEALLearningBase,
    SEALLearningCreate,
    SEALLearningResponse,
)

__all__ = [
    # Berth
    "BerthBase",
    "BerthCreate",
    "BerthUpdate",
    "BerthResponse",
    "BerthSection",
    "BerthStatus",
    # Customer
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    # Vessel
    "VesselBase",
    "VesselCreate",
    "VesselUpdate",
    "VesselResponse",
    "VesselType",
    # Assignment
    "AssignmentBase",
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "AssignmentStatus",
    # VHF Log
    "VHFLogBase",
    "VHFLogCreate",
    "VHFLogResponse",
    "VHFDirection",
    "VHFIntent",
    # Invoice
    "InvoiceBase",
    "InvoiceCreate",
    "InvoiceResponse",
    "InvoiceStatus",
    # Violation
    "ViolationBase",
    "ViolationCreate",
    "ViolationUpdate",
    "ViolationResponse",
    "ViolationSeverity",
    "ViolationStatus",
    # Permit
    "PermitBase",
    "PermitCreate",
    "PermitUpdate",
    "PermitResponse",
    "PermitType",
    "PermitStatus",
    # SEAL Learning
    "SEALLearningBase",
    "SEALLearningCreate",
    "SEALLearningResponse",
]
