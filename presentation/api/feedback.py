"""
User Feedback API
Provides endpoints for collecting user feedback on appraisals.
"""

from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class FeedbackRequest(BaseModel):
    """Request model for appraisal feedback."""

    appraisal_id: UUID | None = Field(
        None, description="Linked appraisal ID from performance metrics"
    )
    appraisal_phone: str | None = Field(None, description="User phone for correlation")
    appraisal_email: str | None = Field(None, description="User email for correlation")

    # Ratings (1-5 stars)
    overall_rating: int = Field(..., ge=1, le=5, description="Overall satisfaction (1-5 stars)")
    speed_rating: int = Field(..., ge=1, le=5, description="Speed rating (1-5 stars)")
    accuracy_rating: int = Field(..., ge=1, le=5, description="Accuracy rating (1-5 stars)")

    # Optional comment
    feedback_text: str | None = Field(None, max_length=1000, description="Optional feedback text")

    @field_validator("appraisal_id", mode="before")
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID | None:
        """Coerces string to UUID if possible."""
        if isinstance(v, str) and v:
            try:
                return UUID(v)
            except ValueError:
                return None
        return cast(UUID | None, v)


@router.post("/submit")
async def submit_feedback(feedback: FeedbackRequest) -> dict[str, Any]:
    """
    Submit user feedback on an appraisal.

    This endpoint saves feedback to the appraisal_feedback table for analysis.
    """
    try:
        db = SupabaseAdapter()

        # Prepare insert data
        insert_data = {
            "appraisal_phone": feedback.appraisal_phone,
            "appraisal_email": feedback.appraisal_email,
            "overall_rating": feedback.overall_rating,
            "speed_rating": feedback.speed_rating,
            "accuracy_rating": feedback.accuracy_rating,
            "feedback_text": feedback.feedback_text,
        }

        # Add appraisal_id if provided
        if feedback.appraisal_id:
            insert_data["appraisal_id"] = str(feedback.appraisal_id)

        logger.info(
            "SUBMITTING_FEEDBACK",
            context={
                "id": str(feedback.appraisal_id) if feedback.appraisal_id else "N/A",
                "overall": feedback.overall_rating,
            },
        )

        # Insert into database
        result = db.client.table("appraisal_feedback").insert(insert_data).execute()

        # Check for success
        data_list = cast(list[Any], result.data)
        if data_list and len(data_list) > 0:
            feedback_id = cast(dict[str, Any], data_list[0]).get("id")
            return {
                "success": True,
                "message": "Thank you for your feedback!",
                "feedback_id": feedback_id,
            }

        return {
            "success": True,
            "message": "Thank you for your feedback!",
            "feedback_id": None,
        }

    except Exception as e:
        logger.error("FEEDBACK_SUBMISSION_FAILED", context={"error": str(e)})
        # We don't want to crash the user experience if feedback fails, but we should inform
        raise HTTPException(
            status_code=500, detail="Failed to submit feedback. Please try again later."
        ) from e
