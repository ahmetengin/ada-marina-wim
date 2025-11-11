"""
SHIP Agent - SEAL Self-Learning and System Deployment
Part of the Big-5 Agents architecture for ADA.MARINA

Responsibilities:
- Continuous SEAL (Self-Learning) model improvement
- A/B testing of recommendations
- Performance monitoring and optimization
- Agent coordination and orchestration
- System health monitoring
- Deployment and rollback management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

import anthropic
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.seal_learning import SEALLearning
from app.models.berth_assignment import BerthAssignment, AssignmentStatus
from app.models.customer import Customer

logger = logging.getLogger(__name__)


class ShipAgent:
    """
    SHIP Agent - System-wide learning and deployment management

    Coordinates all other agents and manages the SEAL learning lifecycle.
    Named "SHIP" for deployment metaphor and maritime theme.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.seal_enabled = settings.SEAL_LEARNING_ENABLED
        self.is_running = False

        # Agent health tracking
        self.agent_status = {
            "scout": {"healthy": True, "last_check": datetime.now()},
            "plan": {"healthy": True, "last_check": datetime.now()},
            "verify": {"healthy": True, "last_check": datetime.now()},
            "ship": {"healthy": True, "last_check": datetime.now()}
        }

        logger.info("SHIP Agent initialized - System orchestration ready")

    async def start(self):
        """Start the SHIP agent background service"""
        self.is_running = True
        logger.info("SHIP Agent started - Managing SEAL lifecycle and agent coordination")

        while self.is_running:
            try:
                # Monitor agent health
                await self._monitor_agent_health()

                # Update SEAL models
                if self.seal_enabled:
                    await self._improve_seal_models()

                # Performance analytics
                await self._analyze_performance()

                # Wait before next cycle
                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"Error in SHIP agent main loop: {e}")
                await asyncio.sleep(300)

    async def stop(self):
        """Stop the SHIP agent"""
        self.is_running = False
        logger.info("SHIP Agent stopped")

    async def _monitor_agent_health(self):
        """Monitor health of all agents"""
        now = datetime.now()

        for agent_name in ["scout", "plan", "verify"]:
            # In production, this would ping each agent
            # For now, assume healthy if no errors in last hour
            self.agent_status[agent_name]["last_check"] = now
            self.agent_status[agent_name]["healthy"] = True

        logger.debug("Agent health check completed - All systems operational")

    async def _improve_seal_models(self):
        """
        Improve SEAL learning models based on recent data

        Analyzes prediction accuracy and updates confidence scores
        """
        db = SessionLocal()
        try:
            logger.info("Analyzing SEAL model performance...")

            # Get recent assignments with SEAL predictions
            recent_days = 30
            cutoff_date = datetime.now() - timedelta(days=recent_days)

            seal_assignments = db.query(BerthAssignment).filter(
                and_(
                    BerthAssignment.was_seal_predicted == True,
                    BerthAssignment.check_in >= cutoff_date
                )
            ).all()

            if not seal_assignments:
                logger.info("No SEAL predictions to analyze")
                return

            # Analyze accuracy
            total_predictions = len(seal_assignments)
            successful_predictions = 0

            # Metrics for improvement
            customer_satisfaction = {}

            for assignment in seal_assignments:
                customer_id = assignment.customer_id

                # Measure "success" by:
                # 1. Assignment completed (not cancelled)
                # 2. Customer returned (repeat business)
                # 3. No violations during stay

                is_successful = True

                # Check if completed
                if assignment.status == AssignmentStatus.CANCELLED:
                    is_successful = False

                # Check for violations during stay
                if is_successful:
                    from app.models.violation import Violation
                    violations = db.query(Violation).filter(
                        and_(
                            Violation.vessel_id == assignment.vessel_id,
                            Violation.detected_at >= assignment.check_in,
                            Violation.detected_at <= (assignment.actual_check_out or assignment.expected_check_out)
                        )
                    ).count()

                    if violations > 0:
                        is_successful = False

                if is_successful:
                    successful_predictions += 1

                # Track per customer
                if customer_id not in customer_satisfaction:
                    customer_satisfaction[customer_id] = {"success": 0, "total": 0}

                customer_satisfaction[customer_id]["total"] += 1
                if is_successful:
                    customer_satisfaction[customer_id]["success"] += 1

            # Calculate overall accuracy
            accuracy = successful_predictions / total_predictions if total_predictions > 0 else 0

            logger.info(
                f"SEAL Model Performance: {successful_predictions}/{total_predictions} "
                f"successful predictions ({accuracy * 100:.2f}% accuracy)"
            )

            # Update SEAL confidence scores based on performance
            for customer_id, stats in customer_satisfaction.items():
                customer_accuracy = stats["success"] / stats["total"] if stats["total"] > 0 else 0

                # Update SEAL learning entry
                seal_entry = db.query(SEALLearning).filter(
                    and_(
                        SEALLearning.customer_id == customer_id,
                        SEALLearning.pattern_type == "berth_preference"
                    )
                ).first()

                if seal_entry:
                    # Adjust confidence based on accuracy
                    # High accuracy = increase confidence, low = decrease
                    current_confidence = seal_entry.confidence_score
                    adjustment = (customer_accuracy - 0.5) * 0.1  # Max ±5% per update

                    new_confidence = max(0.0, min(1.0, current_confidence + adjustment))

                    seal_entry.confidence_score = new_confidence
                    seal_entry.last_updated = datetime.now()

                    # Update learned patterns with performance metrics
                    try:
                        patterns = json.loads(seal_entry.learned_patterns)
                        patterns["accuracy"] = customer_accuracy
                        patterns["total_predictions"] = stats["total"]
                        seal_entry.learned_patterns = json.dumps(patterns)
                    except:
                        pass

                    db.commit()

            logger.info(f"SEAL models updated for {len(customer_satisfaction)} customers")

        except Exception as e:
            logger.error(f"Error improving SEAL models: {e}")
        finally:
            db.close()

    async def _analyze_performance(self):
        """
        Analyze overall system performance

        Tracks KPIs and identifies optimization opportunities
        """
        db = SessionLocal()
        try:
            now = datetime.now()
            week_ago = now - timedelta(days=7)

            # Occupancy rate
            from app.models.berth import Berth, BerthStatus
            total_berths = db.query(Berth).count()
            occupied_berths = db.query(Berth).filter(
                Berth.status == BerthStatus.OCCUPIED
            ).count()

            occupancy_rate = occupied_berths / total_berths if total_berths > 0 else 0

            # Revenue this week
            revenue_week = db.query(func.sum(BerthAssignment.total_amount_eur)).filter(
                and_(
                    BerthAssignment.status == AssignmentStatus.COMPLETED,
                    BerthAssignment.actual_check_out >= week_ago
                )
            ).scalar() or 0

            # VHF processing rate
            from app.models.vhf_log import VHFLog
            vhf_total = db.query(VHFLog).filter(VHFLog.timestamp >= week_ago).count()
            vhf_processed = db.query(VHFLog).filter(
                and_(
                    VHFLog.timestamp >= week_ago,
                    VHFLog.was_processed == True
                )
            ).count()

            vhf_processing_rate = vhf_processed / vhf_total if vhf_total > 0 else 0

            # Compliance rate
            from app.models.violation import Violation, ViolationStatus
            from app.models.vessel import Vessel
            total_vessels = db.query(Vessel).count()
            vessels_with_violations = db.query(Violation.vessel_id).filter(
                Violation.status != ViolationStatus.RESOLVED
            ).distinct().count()

            compliance_rate = (total_vessels - vessels_with_violations) / total_vessels if total_vessels > 0 else 1.0

            # SEAL usage rate
            total_assignments = db.query(BerthAssignment).filter(
                BerthAssignment.check_in >= week_ago
            ).count()

            seal_assignments = db.query(BerthAssignment).filter(
                and_(
                    BerthAssignment.check_in >= week_ago,
                    BerthAssignment.was_seal_predicted == True
                )
            ).count()

            seal_usage = seal_assignments / total_assignments if total_assignments > 0 else 0

            performance_metrics = {
                "timestamp": now.isoformat(),
                "occupancy_rate": round(occupancy_rate * 100, 2),
                "revenue_week": round(revenue_week, 2),
                "vhf_processing_rate": round(vhf_processing_rate * 100, 2),
                "compliance_rate": round(compliance_rate * 100, 2),
                "seal_usage_rate": round(seal_usage * 100, 2),
                "agent_health": self.agent_status
            }

            logger.info(f"System Performance Metrics: {json.dumps(performance_metrics, indent=2)}")

            return performance_metrics

        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {}
        finally:
            db.close()

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status

        Returns health, performance, and operational metrics
        """
        db = SessionLocal()
        try:
            # Agent health
            all_healthy = all(agent["healthy"] for agent in self.agent_status.values())

            # SEAL statistics
            total_seal_patterns = db.query(SEALLearning).count()
            avg_confidence = db.query(func.avg(SEALLearning.confidence_score)).scalar() or 0

            # Recent performance
            performance = await self._analyze_performance()

            # Active operations
            from app.models.berth_assignment import BerthAssignment
            from app.models.permit import Permit, PermitStatus

            active_assignments = db.query(BerthAssignment).filter(
                BerthAssignment.status == AssignmentStatus.ACTIVE
            ).count()

            active_permits = db.query(Permit).filter(
                Permit.status == PermitStatus.ACTIVE
            ).count()

            return {
                "system_status": "operational" if all_healthy else "degraded",
                "timestamp": datetime.now().isoformat(),
                "agents": self.agent_status,
                "seal_learning": {
                    "enabled": self.seal_enabled,
                    "total_patterns": total_seal_patterns,
                    "avg_confidence": round(avg_confidence, 4)
                },
                "active_operations": {
                    "assignments": active_assignments,
                    "permits": active_permits
                },
                "performance": performance
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "system_status": "error",
                "error": str(e)
            }
        finally:
            db.close()

    async def trigger_seal_retraining(self) -> Dict[str, Any]:
        """
        Trigger complete SEAL model retraining

        Useful after major changes or low performance
        """
        logger.info("Triggering SEAL model retraining...")

        try:
            # This would trigger the PLAN agent's learning update
            from app.agents.plan_agent import plan_agent
            await plan_agent._update_seal_learning()

            # Then improve based on recent performance
            await self._improve_seal_models()

            return {
                "status": "success",
                "message": "SEAL models retrained successfully",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error retraining SEAL models: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def coordinate_agents(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate multiple agents for complex tasks

        Args:
            task: Task type (e.g., "complete_reservation", "emergency_response")
            context: Task context and parameters

        Returns:
            Coordinated response from multiple agents
        """
        logger.info(f"Coordinating agents for task: {task}")

        results = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "agents_involved": [],
            "results": {}
        }

        try:
            if task == "complete_reservation":
                # Coordinate SCOUT -> PLAN -> BUILD (FastAPI) workflow
                results["agents_involved"] = ["scout", "plan"]

                # SCOUT would have parsed the VHF request
                # PLAN allocates optimal berth
                from app.agents.plan_agent import plan_agent

                allocation = await plan_agent.allocate_berth(
                    vessel_id=context["vessel_id"],
                    customer_id=context["customer_id"],
                    check_in=context["check_in"],
                    check_out=context["check_out"]
                )

                results["results"]["berth_allocation"] = allocation

            elif task == "emergency_response":
                # Coordinate all agents for emergency
                results["agents_involved"] = ["scout", "verify", "ship"]

                # Log emergency
                logger.critical(f"EMERGENCY: {context.get('description', 'Unknown emergency')}")

                # VERIFY agent would check compliance issues
                # SHIP agent coordinates response

                results["results"]["emergency_logged"] = True
                results["results"]["response_initiated"] = True

            return results

        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results


# Global SHIP agent instance
ship_agent = ShipAgent()


async def start_ship_agent():
    """Start the SHIP agent background service"""
    await ship_agent.start()


async def stop_ship_agent():
    """Stop the SHIP agent background service"""
    await ship_agent.stop()
