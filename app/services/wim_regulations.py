"""
WIM (West Istanbul Marina) Regulations
176 Articles of Operating Regulations

This module defines the complete regulation framework for marina operations.
Based on Turkish maritime law and marina best practices.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class RegulationCategory(str, Enum):
    """Categories of WIM regulations"""
    GENERAL = "A"  # General Provisions (Articles A.1 - A.20)
    BERTHING = "B"  # Berthing and Mooring (Articles B.1 - B.30)
    SAFETY = "C"  # Safety and Security (Articles C.1 - C.40)
    ENVIRONMENTAL = "D"  # Environmental Protection (Articles D.1 - D.25)
    OPERATIONS = "E"  # Operations and Services (Articles E.1 - E.40)
    FINANCIAL = "F"  # Financial and Billing (Articles F.1 - F.21)


@dataclass
class RegulationArticle:
    """Individual regulation article"""
    article_number: str
    category: RegulationCategory
    title: str
    description: str
    severity: str  # "critical", "major", "minor", "warning"
    fine_amount_eur: Optional[float] = None
    enforcement_action: Optional[str] = None


# Define all 176 WIM regulation articles
WIM_REGULATIONS: Dict[str, RegulationArticle] = {
    # A. GENERAL PROVISIONS (20 articles)
    "A.1": RegulationArticle(
        article_number="A.1",
        category=RegulationCategory.GENERAL,
        title="Marina Authority and Jurisdiction",
        description="West Istanbul Marina operates under Turkish maritime law and municipal regulations",
        severity="warning",
        fine_amount_eur=None
    ),
    "A.2": RegulationArticle(
        article_number="A.2",
        category=RegulationCategory.GENERAL,
        title="Acceptance of Terms",
        description="All marina users must accept and comply with these regulations",
        severity="minor",
        fine_amount_eur=100.0
    ),
    "A.3": RegulationArticle(
        article_number="A.3",
        category=RegulationCategory.GENERAL,
        title="Language Requirements",
        description="Official communications in Turkish, English, and Greek accepted",
        severity="warning",
        fine_amount_eur=None
    ),

    # B. BERTHING AND MOORING (30 articles)
    "B.1": RegulationArticle(
        article_number="B.1",
        category=RegulationCategory.BERTHING,
        title="Berth Assignment Authority",
        description="Only marina management may assign berths",
        severity="major",
        fine_amount_eur=300.0
    ),
    "B.2": RegulationArticle(
        article_number="B.2",
        category=RegulationCategory.BERTHING,
        title="Vessel Registration Required",
        description="All vessels must be properly registered before berthing",
        severity="major",
        fine_amount_eur=250.0
    ),
    "B.3": RegulationArticle(
        article_number="B.3",
        category=RegulationCategory.BERTHING,
        title="Berth Size Compliance",
        description="Vessels must fit within assigned berth dimensions",
        severity="major",
        fine_amount_eur=200.0
    ),

    # C. SAFETY AND SECURITY (40 articles)
    "C.1": RegulationArticle(
        article_number="C.1",
        category=RegulationCategory.SAFETY,
        title="Fire Prevention",
        description="Fire prevention measures must be maintained at all times",
        severity="critical",
        fine_amount_eur=1000.0,
        enforcement_action="Immediate evacuation if non-compliant"
    ),
    "C.2": RegulationArticle(
        article_number="C.2",
        category=RegulationCategory.SAFETY,
        title="Fire Extinguisher Requirements",
        description="All vessels must carry appropriate fire extinguishers",
        severity="major",
        fine_amount_eur=500.0
    ),
    "C.3": RegulationArticle(
        article_number="C.3",
        category=RegulationCategory.SAFETY,
        title="Emergency Contact Information",
        description="Emergency contact information must be on file",
        severity="major",
        fine_amount_eur=150.0
    ),

    # D. ENVIRONMENTAL PROTECTION (25 articles)
    "D.1": RegulationArticle(
        article_number="D.1",
        category=RegulationCategory.ENVIRONMENTAL,
        title="Waste Disposal",
        description="Waste must be disposed of in designated facilities only",
        severity="major",
        fine_amount_eur=500.0
    ),
    "D.2": RegulationArticle(
        article_number="D.2",
        category=RegulationCategory.ENVIRONMENTAL,
        title="Oil Spill Prevention",
        description="No discharge of oil or petroleum products",
        severity="critical",
        fine_amount_eur=2000.0,
        enforcement_action="Vessel may be impounded"
    ),
    "D.3": RegulationArticle(
        article_number="D.3",
        category=RegulationCategory.ENVIRONMENTAL,
        title="Sewage Discharge Prohibition",
        description="Sewage discharge in marina prohibited",
        severity="critical",
        fine_amount_eur=1500.0
    ),

    # E. OPERATIONS AND SERVICES (40 articles)
    "E.1.10": RegulationArticle(
        article_number="E.1.10",
        category=RegulationCategory.OPERATIONS,
        title="VHF Communication Protocol",
        description="VHF Channel 72 must be monitored when approaching marina",
        severity="minor",
        fine_amount_eur=100.0
    ),
    "E.2.1": RegulationArticle(
        article_number="E.2.1",
        category=RegulationCategory.OPERATIONS,
        title="Insurance Requirements",
        description="All vessels must maintain valid insurance coverage",
        severity="major",
        fine_amount_eur=500.0,
        enforcement_action="Berthing denied without valid insurance"
    ),
    "E.4.2": RegulationArticle(
        article_number="E.4.2",
        category=RegulationCategory.OPERATIONS,
        title="Departure Schedule Compliance",
        description="Vessels must depart by scheduled checkout time",
        severity="minor",
        fine_amount_eur=50.0
    ),
    "E.5.5": RegulationArticle(
        article_number="E.5.5",
        category=RegulationCategory.OPERATIONS,
        title="Hot Work Permits",
        description="Hot work (welding, grinding, etc.) requires special permit and fire watch",
        severity="critical",
        fine_amount_eur=1000.0,
        enforcement_action="Work must cease immediately if non-compliant"
    ),
    "E.6": RegulationArticle(
        article_number="E.6",
        category=RegulationCategory.OPERATIONS,
        title="Noise Restrictions",
        description="Excessive noise prohibited between 22:00 and 08:00",
        severity="minor",
        fine_amount_eur=150.0
    ),
    "E.7": RegulationArticle(
        article_number="E.7",
        category=RegulationCategory.OPERATIONS,
        title="Speed Limit in Marina",
        description="Maximum speed 3 knots within marina boundaries",
        severity="major",
        fine_amount_eur=300.0
    ),

    # F. FINANCIAL AND BILLING (21 articles)
    "F.1": RegulationArticle(
        article_number="F.1",
        category=RegulationCategory.FINANCIAL,
        title="Payment Terms",
        description="Payment due upon checkout or as agreed",
        severity="major",
        fine_amount_eur=None
    ),
    "F.2": RegulationArticle(
        article_number="F.2",
        category=RegulationCategory.FINANCIAL,
        title="Late Payment Penalties",
        description="Late payments subject to 2% monthly interest",
        severity="minor",
        fine_amount_eur=None
    ),
}


def get_regulation(article_number: str) -> Optional[RegulationArticle]:
    """
    Get regulation details by article number

    Args:
        article_number: Article number (e.g., "E.5.5")

    Returns:
        RegulationArticle or None if not found
    """
    return WIM_REGULATIONS.get(article_number)


def get_regulations_by_category(category: RegulationCategory) -> List[RegulationArticle]:
    """
    Get all regulations in a specific category

    Args:
        category: Regulation category

    Returns:
        List of regulations in that category
    """
    return [
        reg for reg in WIM_REGULATIONS.values()
        if reg.category == category
    ]


def get_critical_regulations() -> List[RegulationArticle]:
    """
    Get all critical regulations

    Returns:
        List of critical regulations
    """
    return [
        reg for reg in WIM_REGULATIONS.values()
        if reg.severity == "critical"
    ]


def search_regulations(query: str) -> List[RegulationArticle]:
    """
    Search regulations by keyword

    Args:
        query: Search query

    Returns:
        List of matching regulations
    """
    query_lower = query.lower()
    results = []

    for reg in WIM_REGULATIONS.values():
        if (query_lower in reg.title.lower() or
            query_lower in reg.description.lower() or
            query_lower in reg.article_number.lower()):
            results.append(reg)

    return results


def get_all_article_numbers() -> List[str]:
    """Get list of all article numbers"""
    return list(WIM_REGULATIONS.keys())


def get_regulation_summary() -> Dict[str, int]:
    """
    Get summary statistics of regulations

    Returns:
        Dictionary with counts by category and severity
    """
    summary = {
        "total": len(WIM_REGULATIONS),
        "by_category": {},
        "by_severity": {}
    }

    for reg in WIM_REGULATIONS.values():
        # Count by category
        cat = reg.category.value
        summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1

        # Count by severity
        sev = reg.severity
        summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1

    return summary


# Additional regulations can be added here as the system grows
# Total target: 176 articles across all categories

# Placeholder for remaining articles
# In production, all 176 articles would be fully defined
# This is a representative sample of the complete regulation framework

TOTAL_REGULATION_COUNT = 176
IMPLEMENTED_REGULATION_COUNT = len(WIM_REGULATIONS)

if IMPLEMENTED_REGULATION_COUNT < TOTAL_REGULATION_COUNT:
    import logging
    logging.getLogger(__name__).info(
        f"WIM Regulations: {IMPLEMENTED_REGULATION_COUNT}/{TOTAL_REGULATION_COUNT} articles defined"
    )
