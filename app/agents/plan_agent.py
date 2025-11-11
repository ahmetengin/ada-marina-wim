"""
PLAN Agent - Berth Allocation and SEAL Learning
Part of the Big-5 Agents architecture for ADA.MARINA

Responsibilities:
- Optimal berth allocation based on vessel dimensions
- Customer preference learning (SEAL - Self-Learning)
- Historical pattern analysis
- Predictive berth recommendations
- Revenue optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import json

import anthropic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.berth import Berth, BerthStatus, BerthSection
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.vessel import Vessel
from app.models.customer import Customer
from app.models.seal_learning import SEALLearning

logger = logging.getLogger(__name__)


class PlanAgent:
    """
    PLAN Agent - Intelligent berth allocation with SEAL learning

    Uses historical data and Claude AI to make optimal berth assignments
    that maximize customer satisfaction and revenue.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.seal_enabled = settings.SEAL_LEARNING_ENABLED
        self.confidence_threshold = settings.SEAL_CONFIDENCE_THRESHOLD
        self.is_running = False

        logger.info("PLAN Agent initialized with SEAL learning")

    async def start(self):
        """Start the PLAN agent background service"""
        self.is_running = True
        logger.info("PLAN Agent started - Learning customer preferences")

        while self.is_running:
            try:
                # Periodically analyze patterns and update SEAL data
                await asyncio.sleep(settings.SEAL_UPDATE_INTERVAL)

                if self.seal_enabled:
                    await self._update_seal_learning()

            except Exception as e:
                logger.error(f"Error in PLAN agent main loop: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Stop the PLAN agent"""
        self.is_running = False
        logger.info("PLAN Agent stopped")

    async def allocate_berth(
        self,
        vessel_id: int,
        customer_id: int,
        check_in: datetime,
        check_out: datetime,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Allocate optimal berth for a vessel

        Args:
            vessel_id: ID of the vessel
            customer_id: ID of the customer
            check_in: Check-in datetime
            check_out: Check-out datetime
            preferences: Optional customer preferences

        Returns:
            Berth allocation recommendation with alternatives
        """
        db = SessionLocal()
        try:
            # Get vessel details
            vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
            if not vessel:
                raise ValueError(f"Vessel {vessel_id} not found")

            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")

            # Find available berths
            available_berths = self._find_available_berths(
                db, vessel, check_in, check_out
            )

            if not available_berths:
                return {
                    "success": False,
                    "message": "No available berths for specified dates and vessel size",
                    "alternatives": []
                }

            # Get customer history and preferences
            customer_history = self._get_customer_history(db, customer_id)

            # Score berths using SEAL learning
            scored_berths = []
            for berth in available_berths:
                score = await self._score_berth(
                    db, berth, vessel, customer, customer_history, preferences
                )
                scored_berths.append((berth, score))

            # Sort by score (highest first)
            scored_berths.sort(key=lambda x: x[1]["total_score"], reverse=True)

            # Prepare recommendations
            recommendations = []
            for berth, score in scored_berths[:5]:  # Top 5 recommendations
                days = (check_out - check_in).days or 1
                total_cost = berth.daily_rate_eur * days

                recommendations.append({
                    "berth_id": berth.id,
                    "berth_number": berth.berth_number,
                    "section": berth.section.value,
                    "total_score": round(score["total_score"], 2),
                    "is_seal_recommended": score["seal_score"] > self.confidence_threshold,
                    "daily_rate": berth.daily_rate_eur,
                    "total_cost": total_cost,
                    "score_breakdown": score
                })

            # Mark the top recommendation as SEAL-predicted if confidence is high
            use_seal = (
                self.seal_enabled and
                scored_berths[0][1]["seal_score"] >= self.confidence_threshold
            )

            return {
                "success": True,
                "recommended_berth": recommendations[0],
                "alternatives": recommendations[1:],
                "seal_prediction": use_seal,
                "seal_confidence": scored_berths[0][1]["seal_score"],
                "total_available": len(available_berths)
            }

        except Exception as e:
            logger.error(f"Error allocating berth: {e}")
            raise
        finally:
            db.close()

    def _find_available_berths(
        self,
        db: Session,
        vessel: Vessel,
        check_in: datetime,
        check_out: datetime
    ) -> List[Berth]:
        """
        Find berths that can accommodate the vessel for given dates

        Args:
            db: Database session
            vessel: Vessel object
            check_in: Check-in datetime
            check_out: Check-out datetime

        Returns:
            List of available berths
        """
        # Find suitable berths by dimensions
        suitable = db.query(Berth).filter(
            and_(
                Berth.length_meters >= vessel.length_meters,
                Berth.width_meters >= vessel.width_meters,
                Berth.depth_meters >= vessel.draft_meters,
                Berth.status.in_([BerthStatus.AVAILABLE, BerthStatus.RESERVED])
            )
        ).all()

        # Filter out berths with conflicting assignments
        available = []
        for berth in suitable:
            conflicts = db.query(BerthAssignment).filter(
                and_(
                    BerthAssignment.berth_id == berth.id,
                    BerthAssignment.status == AssignmentStatus.ACTIVE,
                    or_(
                        and_(
                            BerthAssignment.check_in <= check_in,
                            BerthAssignment.expected_check_out >= check_in
                        ),
                        and_(
                            BerthAssignment.check_in <= check_out,
                            BerthAssignment.expected_check_out >= check_out
                        ),
                        and_(
                            BerthAssignment.check_in >= check_in,
                            BerthAssignment.expected_check_out <= check_out
                        )
                    )
                )
            ).first()

            if not conflicts:
                available.append(berth)

        return available

    def _get_customer_history(self, db: Session, customer_id: int) -> Dict[str, Any]:
        """Get customer's historical berth preferences"""
        past_assignments = db.query(BerthAssignment).filter(
            BerthAssignment.customer_id == customer_id
        ).order_by(BerthAssignment.check_in.desc()).limit(10).all()

        # Analyze preferred sections
        section_counts = {}
        berth_counts = {}

        for assignment in past_assignments:
            berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
            if berth:
                section_counts[berth.section.value] = section_counts.get(berth.section.value, 0) + 1
                berth_counts[berth.id] = berth_counts.get(berth.id, 0) + 1

        preferred_section = max(section_counts.items(), key=lambda x: x[1])[0] if section_counts else None
        preferred_berth_id = max(berth_counts.items(), key=lambda x: x[1])[0] if berth_counts else None

        return {
            "total_stays": len(past_assignments),
            "preferred_section": preferred_section,
            "preferred_berth_id": preferred_berth_id,
            "section_distribution": section_counts,
            "avg_stay_days": sum([a.total_days for a in past_assignments]) / len(past_assignments) if past_assignments else 0
        }

    async def _score_berth(
        self,
        db: Session,
        berth: Berth,
        vessel: Vessel,
        customer: Customer,
        history: Dict[str, Any],
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Score a berth for allocation using multiple factors

        Returns score breakdown and total score (0-100)
        """
        scores = {
            "size_fit": 0.0,
            "preference": 0.0,
            "price": 0.0,
            "services": 0.0,
            "seal_score": 0.0,
            "total_score": 0.0
        }

        # Size fit score (0-30 points)
        # Optimal: vessel uses 70-95% of berth length
        usage_percent = (vessel.length_meters / berth.length_meters) * 100
        if 70 <= usage_percent <= 95:
            scores["size_fit"] = 30.0
        elif 60 <= usage_percent < 70 or 95 < usage_percent <= 100:
            scores["size_fit"] = 20.0
        elif 50 <= usage_percent < 60:
            scores["size_fit"] = 10.0
        else:
            scores["size_fit"] = 5.0

        # Customer preference score (0-25 points)
        if history["total_stays"] > 0:
            # Preferred section
            if berth.section.value == history["preferred_section"]:
                scores["preference"] += 15.0

            # Exact preferred berth
            if berth.id == history["preferred_berth_id"]:
                scores["preference"] += 10.0

        # Customer's stated preference
        if preferences:
            if preferences.get("section") == berth.section.value:
                scores["preference"] += 10.0

        # VIP customers get preference for better berths
        if customer.is_vip:
            scores["preference"] += 5.0

        # Price optimization score (0-20 points)
        # Lower price = higher score for non-VIP
        # For VIP, price is less important
        if not customer.is_vip:
            # Normalize price (assume range 50-500 EUR/day)
            price_score = max(0, 20 - (berth.daily_rate_eur - 50) / 450 * 20)
            scores["price"] = price_score
        else:
            scores["price"] = 10.0  # VIPs get moderate price score

        # Services score (0-15 points)
        if berth.has_electricity:
            scores["services"] += 5.0
        if berth.has_water:
            scores["services"] += 5.0
        if berth.has_wifi:
            scores["services"] += 5.0

        # SEAL learning score (0-10 points)
        # This would use Neo4j graph patterns in production
        # For now, use simple heuristics
        seal_score = await self._get_seal_score(db, berth, vessel, customer, history)
        scores["seal_score"] = seal_score / 100 * 10  # Normalize to 0-10

        # Total score
        scores["total_score"] = sum(scores.values()) - scores["seal_score"]  # Don't double count
        scores["seal_score"] = seal_score  # Keep original 0-100 for confidence check

        return scores

    async def _get_seal_score(
        self,
        db: Session,
        berth: Berth,
        vessel: Vessel,
        customer: Customer,
        history: Dict[str, Any]
    ) -> float:
        """
        Get SEAL (Self-Learning) confidence score for berth recommendation

        This uses historical patterns to predict customer satisfaction.
        In production, this would query Neo4j graph database.

        Returns: Confidence score 0-100
        """
        if not self.seal_enabled:
            return 50.0  # Neutral score if SEAL is disabled

        score = 50.0  # Base score

        # Historical preference match
        if history["total_stays"] > 0:
            if berth.section.value == history["preferred_section"]:
                score += 20.0

            if berth.id == history["preferred_berth_id"]:
                score += 30.0

        # Check SEAL learning table
        seal_data = db.query(SEALLearning).filter(
            and_(
                SEALLearning.customer_id == customer.id,
                SEALLearning.pattern_type == "berth_preference"
            )
        ).first()

        if seal_data:
            try:
                learned_patterns = json.loads(seal_data.learned_patterns)
                if berth.section.value in learned_patterns.get("preferred_sections", []):
                    score += 10.0
            except:
                pass

        # VIP customers get slight boost
        if customer.is_vip:
            score += 5.0

        return min(100.0, score)

    async def _update_seal_learning(self):
        """
        Update SEAL learning patterns based on historical data

        Analyzes completed assignments to learn customer preferences
        """
        db = SessionLocal()
        try:
            logger.info("Updating SEAL learning patterns...")

            # Get all customers with multiple stays
            customers = db.query(Customer).filter(Customer.is_active == True).all()

            for customer in customers:
                # Analyze their assignment history
                assignments = db.query(BerthAssignment).filter(
                    and_(
                        BerthAssignment.customer_id == customer.id,
                        BerthAssignment.status == AssignmentStatus.COMPLETED
                    )
                ).all()

                if len(assignments) < 2:
                    continue  # Need at least 2 stays to learn patterns

                # Extract patterns
                patterns = self._extract_customer_patterns(db, customer, assignments)

                # Update or create SEAL learning entry
                seal_entry = db.query(SEALLearning).filter(
                    and_(
                        SEALLearning.customer_id == customer.id,
                        SEALLearning.pattern_type == "berth_preference"
                    )
                ).first()

                if seal_entry:
                    seal_entry.learned_patterns = json.dumps(patterns)
                    seal_entry.confidence_score = patterns.get("confidence", 0.5)
                    seal_entry.last_updated = datetime.now()
                else:
                    seal_entry = SEALLearning(
                        customer_id=customer.id,
                        pattern_type="berth_preference",
                        learned_patterns=json.dumps(patterns),
                        confidence_score=patterns.get("confidence", 0.5)
                    )
                    db.add(seal_entry)

                db.commit()

            logger.info(f"SEAL learning updated for {len(customers)} customers")

        except Exception as e:
            logger.error(f"Error updating SEAL learning: {e}")
        finally:
            db.close()

    def _extract_customer_patterns(
        self,
        db: Session,
        customer: Customer,
        assignments: List[BerthAssignment]
    ) -> Dict[str, Any]:
        """Extract learned patterns from customer's assignment history"""
        # Analyze section preferences
        section_counts = {}
        stay_durations = []

        for assignment in assignments:
            berth = db.query(Berth).filter(Berth.id == assignment.berth_id).first()
            if berth:
                section_counts[berth.section.value] = section_counts.get(berth.section.value, 0) + 1
            stay_durations.append(assignment.total_days)

        # Most preferred sections
        sorted_sections = sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
        preferred_sections = [s[0] for s in sorted_sections[:2]]

        # Average stay duration
        avg_duration = sum(stay_durations) / len(stay_durations) if stay_durations else 0

        # Confidence based on number of stays
        confidence = min(1.0, len(assignments) / 10.0)

        return {
            "preferred_sections": preferred_sections,
            "section_distribution": section_counts,
            "avg_stay_duration": avg_duration,
            "total_stays": len(assignments),
            "confidence": confidence
        }


# Global PLAN agent instance
plan_agent = PlanAgent()


async def start_plan_agent():
    """Start the PLAN agent background service"""
    await plan_agent.start()


async def stop_plan_agent():
    """Stop the PLAN agent background service"""
    await plan_agent.stop()
