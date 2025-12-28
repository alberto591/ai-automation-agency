import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from application.services.lead_processor import LeadProcessor, LeadScorer
from infrastructure.adapters.langchain_adapter import LangChainAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.market_service import MarketDataService


class MockMessaging:
    def send_message(self, to, body, media_url=None):
        print(f"\n[WHATSAPP TO {to}]:\n{body}\n")
        return "mock_sid"


def verify_clever_ai():
    print("🚀 Verifying 'Clever AI' Logic...")

    db = SupabaseAdapter()
    ai = LangChainAdapter()
    msg = MockMessaging()
    scorer = LeadScorer()
    market = MarketDataService()

    processor = LeadProcessor(db, ai, msg, scorer, market=market)

    test_cases = [
        {
            "name": "Valuation Request",
            "phone": "+393331234567",
            "query": "Ciao, vorrei una valutazione per il mio appartamento a Milano in zona Brera. È circa 100mq.",
            "source": "WEB_APPRAISAL",
        },
        {
            "name": "Tourist Negotiation",
            "phone": "+14155552671",
            "query": "I am looking for a charming villa in Tuscany. My budget is around 500k. Is the price for the one in 'Firenze' negotiable?",
            "source": "PORTAL",
        },
    ]

    for case in test_cases:
        print(f"\n--- Test Case: {case['name']} ---")
        processor.process_incoming_message(
            phone=case["phone"], text=case["query"], source=case["source"]
        )


if __name__ == "__main__":
    verify_clever_ai()
