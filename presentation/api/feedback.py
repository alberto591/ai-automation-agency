"""
Feedback API endpoint for collecting user feedback on appraisals
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """User feedback on an appraisal."""

    appraisal_phone: str | None = Field(None, description="Phone from appraisal request")
    appraisal_email: str | None = Field(None, description="Email from appraisal request")
    estimated_value: float | None = Field(None, description="Estimated property value")
    
    # Ratings (1-5 stars)
    rating: int = Field(..., ge=1, le=5, description="Overall rating (1-5 stars)")
    speed_rating: int = Field(..., ge=1, le=5, description="Speed rating (1-5 stars)")
    accuracy_rating: int = Field(..., ge=1, le=5, description="Accuracy rating (1-5 stars)")
    
    # Optional comment
    feedback_text: str | None = Field(None, max_length=1000, description="Optional feedback text")


@router.post("/submit")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback on an appraisal.
    
    This endpoint saves feedback to the appraisal_feedback table for analysis.
    """
    try:
        db = SupabaseAdapter()
        
        # Insert feedback
        result = db.client.table("appraisal_feedback").insert({
            "appraisal_phone": feedback.appraisal_phone,
            "appraisal_email": feedback.appraisal_email,
            "estimated_value": feedback.estimated_value,
            "rating": feedback.rating,
            "speed_rating": feedback.speed_rating,
            "accuracy_rating": feedback.accuracy_rating,
            "feedback_text": feedback.feedback_text,
            "source": "web_form",
        }).execute()
        
        logger.info(
            "FEEDBACK_SUBMITTED",
            context={
                "rating": feedback.rating,
                "speed_rating": feedback.speed_rating,
                "accuracy_rating": feedback.accuracy_rating,
            },
        )
        
        return {
            "success": True,
            "message": "Thank you for your feedback!",
            "feedback_id": result.data[0]["id"] if result.data else None,
        }
        
    except Exception as e:
        logger.error("FEEDBACK_SUBMISSION_FAILED", context={"error": str(e)})
        raise HTTPException(
            status_code=500,
            detail="Failed to submit feedback. Please try again later.",
        ) from e
