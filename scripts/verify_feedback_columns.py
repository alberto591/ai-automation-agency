import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def verify_schema():
    print("Verifying appraisal_feedback schema...")
    try:
        db = SupabaseAdapter()

        # Test data with all new columns
        test_data = {
            "overall_rating": 5,
            "speed_rating": 5,
            "accuracy_rating": 5,
            "feedback_text": "Schema verification test",
            "appraisal_id": "test-id-" + str(uuid.uuid4()),
            "appraisal_phone": "+1234567890",
            "appraisal_email": "test@example.com",
        }

        print("Attempting to insert test record with new columns...")

        # We use the client directly to catch specific errors
        res = db.client.table("appraisal_feedback").insert(test_data).execute()

        if res.data:
            print("SUCCESS: Insert successful. Columns exist.")
            # Cleanup
            print("Cleaning up test record...")
            row_id = res.data[0]["id"]
            db.client.table("appraisal_feedback").delete().eq("id", row_id).execute()
            print("Cleanup done.")
            return True
        else:
            print("FAILURE: Insert returned no data.")
            return False

    except Exception as e:
        print(f"FAILURE: Insert failed. Error: {e}")
        return False


if __name__ == "__main__":
    if verify_schema():
        sys.exit(0)
    else:
        sys.exit(1)
