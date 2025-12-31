"""
Lead Scorer Service with Analytics Tracking

Centralizes lead scoring logic and provides analytics capabilities
for the qualification flow completion rates and metrics.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from domain.qualification import LeadCategory, LeadScore
from infrastructure.adapters.supabase_adapter import SupabaseAdapter


class LeadScorer:
    """Service for scoring leads and tracking qualification analytics."""

    def __init__(self, db: SupabaseAdapter):
        self.db = db

    def track_qualification_event(
        self,
        lead_id: UUID,
        event_type: str,
        question_number: int | None = None,
        answer_value: str | None = None,
        score_at_event: int | None = None,
    ) -> None:
        """
        Track a qualification flow event for analytics.

        Args:
            lead_id: UUID of the lead
            event_type: One of 'started', 'question_answered', 'completed', 'abandoned'
            question_number: Optional question number (1-7)
            answer_value: Optional answer value
            score_at_event: Optional current score at this event
        """
        event_data = {
            "lead_id": str(lead_id),
            "event_type": event_type,
            "question_number": question_number,
            "answer_value": answer_value,
            "score_at_event": score_at_event,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.db.client.table("qualification_events").insert(event_data).execute()

    def calculate_completion_rate(self, days: int = 7) -> dict[str, Any]:
        """
        Calculate qualification flow completion rate for the last N days.

        Args:
            days: Number of days to look back (default 7)

        Returns:
            Dict with started_count, completed_count, and completion_rate
        """
        since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Query started events
        started_response = (
            self.db.client.table("qualification_events")
            .select("id", count="exact")  # type: ignore[arg-type]
            .eq("event_type", "started")
            .gte("created_at", since_date)
            .execute()
        )
        started_count = started_response.count or 0

        # Query completed events
        completed_response = (
            self.db.client.table("qualification_events")
            .select("id", count="exact")  # type: ignore[arg-type]
            .eq("event_type", "completed")
            .gte("created_at", since_date)
            .execute()
        )
        completed_count = completed_response.count or 0

        completion_rate = (completed_count / started_count * 100) if started_count > 0 else 0.0

        return {
            "started_count": started_count,
            "completed_count": completed_count,
            "completion_rate": round(completion_rate, 2),
            "period_days": days,
        }

    def get_score_distribution(self, days: int = 30) -> dict[str, Any]:
        """
        Get the distribution of lead scores for the last N days.

        Returns:
            Dict with score histogram data
        """
        since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Get all leads with scores from the last N days
        response = (
            self.db.client.table("leads")
            .select("lead_score_normalized")
            .gte("created_at", since_date)
            .not_.is_("lead_score_normalized", "null")
            .execute()
        )

        scores = [lead["lead_score_normalized"] for lead in response.data]  # type: ignore[index]

        # Calculate distribution
        hot_count = sum(1 for s in scores if s >= 9)
        warm_count = sum(1 for s in scores if 6 <= s < 9)
        cold_count = sum(1 for s in scores if s < 6)

        return {
            "total_leads": len(scores),
            "hot_leads": hot_count,
            "warm_leads": warm_count,
            "cold_leads": cold_count,
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "period_days": days,
        }

    def route_lead(
        self, lead_id: UUID, score: LeadScore, agent_id: UUID | None = None
    ) -> dict[str, Any]:
        """
        Route a lead to an agent based on score.

        Args:
            lead_id: UUID of the lead
            score: LeadScore object with category and normalized score
            agent_id: Optional specific agent to assign (overrides auto-routing)

        Returns:
            Dict with routing decision
        """
        # Determine routing reason
        if score.category == LeadCategory.HOT:
            routing_reason = f"Score {score.normalized_score}/10 - HOT lead"
            priority = "high"
        elif score.category == LeadCategory.WARM:
            routing_reason = f"Score {score.normalized_score}/10 - WARM lead"
            priority = "medium"
        elif score.category == LeadCategory.DISQUALIFIED:
            routing_reason = "DISQUALIFIED - Budget too low"
            priority = "none"
        else:
            routing_reason = f"Score {score.normalized_score}/10 - COLD lead"
            priority = "low"

        # Update lead with routing info
        update_data = {
            "assigned_agent_id": str(agent_id) if agent_id else None,
            "routing_reason": routing_reason,
            "qualification_completed_at": datetime.utcnow().isoformat(),
        }

        self.db.client.table("leads").update(update_data).eq("id", str(lead_id)).execute()

        return {
            "lead_id": str(lead_id),
            "assigned_agent_id": str(agent_id) if agent_id else None,
            "routing_reason": routing_reason,
            "priority": priority,
            "category": score.category.value,
        }
