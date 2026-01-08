import random

from domain.models import Agent, Lead
from domain.ports import DatabasePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class RoutingService:
    def __init__(self, db: DatabasePort):
        self.db = db

    def assign_lead(self, lead: Lead) -> str | None:
        """
        Assigns a lead to the best available agent based on Zone matches.
        Fallback: Round-robin (or random if load is low).
        """
        try:
            # 1. Fetch active agents
            agents_data = self.db.get_active_agents()
            if not agents_data:
                logger.warning("NO_ACTIVE_AGENTS", context={"lead_phone": lead.phone})
                return None

            agents = [
                Agent(
                    id=a["id"],
                    email=a.get("email", ""),
                    full_name=a.get("full_name"),
                    zones=a.get("zones") or [],
                )
                for a in agents_data
            ]

            # 2. Zone Matching
            matched_agents = []
            lead_zone = self._extract_zone(lead)

            if lead_zone:
                matched_agents = [
                    a for a in agents if any(z.lower() in lead_zone.lower() for z in a.zones)
                ]

            if matched_agents:
                # Pick one (Random for now, could be Load Based)
                chosen = random.choice(matched_agents)
                logger.info(
                    "AGENT_ZONE_MATCH",
                    context={"lead_id": lead.phone, "agent": chosen.email, "zone": lead_zone},
                )
            else:
                # 3. Fallback: Random/Round Robin
                chosen = random.choice(agents)
                logger.info(
                    "AGENT_FALLBACK_ASSIGNMENT",
                    context={"lead_id": lead.phone, "agent": chosen.email},
                )

            # 4. Persist
            # Note: lead.id might be None if it's new, but assign_lead_to_agent works on ID.
            # Usually we process lead first to get ID, then assign.
            # But LeadProcessor flow: save_lead -> process -> assign.
            # We assume we have ID. If not, we return agent_id and let caller save it.

            return chosen.id

        except Exception as e:
            logger.error("ROUTING_FAILED", context={"error": str(e)})
            return None

    def _extract_zone(self, lead: Lead) -> str | None:
        """Helper to find zone from lead query or postcode."""
        # Simple heuristic extraction from 'interest' or 'query'
        # In real world, would use NLU extraction
        if lead.postcode:
            return lead.postcode

        # Check against common zones in messages? Too complex for MVP.
        return None
