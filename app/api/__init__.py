"""
API routes for ADA.MARINA
"""

from fastapi import APIRouter
from app.api.endpoints import berths, customers, vessels, assignments, vhf, violations, permits, dashboard, maritime
from app.api.endpoints import berths, customers, vessels, assignments, vhf, violations, permits, dashboard, privacy

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(berths.router, prefix="/berths", tags=["Berths"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(vessels.router, prefix="/vessels", tags=["Vessels"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Berth Assignments"])
api_router.include_router(vhf.router, prefix="/vhf", tags=["VHF Communications"])
api_router.include_router(violations.router, prefix="/violations", tags=["Violations"])
api_router.include_router(permits.router, prefix="/permits", tags=["Permits"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(maritime.router, prefix="/maritime", tags=["Maritime Services 🌊"])

# ADA.SEA Privacy API
api_router.include_router(privacy.router, prefix="/privacy", tags=["Privacy"])
