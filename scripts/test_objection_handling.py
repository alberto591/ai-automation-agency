import asyncio
import os
import sys
from typing import Any, Optional

# Ensure project root is in path
sys.path.append(os.getcwd())

from application.services.lead_processor import LeadProcessor
from application.services.lead_scoring_service import LeadScoringService
from domain.ports import AIPort, DatabasePort, MessagingPort


# Inline Mocks
class RequestMock:
    def model_dump(self):
        return {}


class MockDatabaseAdapter(DatabasePort):
    def get_lead(self, phone: str) -> Optional[dict[str, Any]]:
        return {"id": "test-id", "customer_phone": phone, "status": "active", "messages": []}

    def save_lead(self, lead_data: dict[str, Any]) -> None:
        pass

    def save_message(self, lead_id: str, message: dict[str, Any]) -> None:
        pass

    def get_market_stats(self, zone: str) -> dict[str, Any]:
        return {}

    def get_properties(
        self,
        query: str = "",
        filters: dict[str, Any] = None,
        limit: int = 5,
        use_mock_table: bool = False,
        embedding: list[float] = None,
    ) -> list[dict[str, Any]]:
        return []

    def get_cached_response(self, embedding: list[float], threshold: float = 0.9) -> Optional[str]:
        return None

    def save_to_cache(self, query: str, embedding: list[float], response: str) -> None:
        pass

    # Missing methods implemented
    def update_lead(self, lead_id: str, updates: dict[str, Any]) -> None:
        pass

    def update_lead_status(self, lead_id: str, status: str) -> None:
        pass

    def update_message_status(self, message_id: str, status: str) -> None:
        pass


class InteractiveMockAI(AIPort):
    def generate_response(self, prompt: str) -> str:
        print(f"\n[AI Received Prompt Context]: ...{prompt[-300:]}...\n")

        # Simple heuristic to see if objection handling was triggered in the prompt
        if "Empathy -> Pivot -> Value" in prompt:
            print("✅ TEST PASSED: Objection Handling instructions found in prompt.")
        else:
            print("❌ TEST FAILED: Objection Handling instructions NOT found.")

        return "Understandable. However, looking at the market data... (AI Simulation)"

    def get_embedding(self, text: str) -> list[float]:
        return [0.1] * 1536


class MockMessagingAdapter(MessagingPort):
    def send_message(self, to: str, content: str) -> bool:
        print(f"[MockMsg] Sending to {to}: {content}")
        return True


async def test_objection():
    print("--- Testing Objection Handling ---")

    # Setup
    db = MockDatabaseAdapter()
    ai = InteractiveMockAI()
    msg = MockMessagingAdapter()
    # We cheat a bit and don't strictly need a functional scorer for this test
    scorer = LeadScoringService()

    processor = LeadProcessor(db, ai, msg, scorer)

    # Simulate a user flow
    phone = "+393331234567"

    # 1. User expresses interest
    print(f"User ({phone}): Hello, I saw a villa.")
    # We can skip full processing and just check agent node, but using processor is more integration-testy
    processor.process_incoming_message(phone, "Hello, I saw a villa.", "WHATSAPP")

    # 2. User raises price objection
    print(f"User ({phone}): But it costs too much money!")
    processor.process_incoming_message(phone, "But it costs too much money!", "WHATSAPP")


if __name__ == "__main__":
    asyncio.run(test_objection())
