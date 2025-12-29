#!/usr/bin/env python3
"""Terminal Demo Test - Interactive CLI for testing lead conversations without API costs.

This script simulates WhatsApp conversations by invoking the LeadProcessor
with mocked external dependencies (Twilio, Supabase, etc.).

Usage:
    python scripts/terminal_demo.py
    python scripts/terminal_demo.py --language en
    python scripts/terminal_demo.py --phone "+39333123456"
"""

import os
import sys
from typing import Any
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.services.journey_manager import JourneyManager
from application.services.lead_processor import LeadProcessor, LeadScorer
from domain.ports import CalendarPort, DatabasePort, MessagingPort
from infrastructure.adapters.langchain_adapter import LangChainAdapter


class TerminalMessagingAdapter(MessagingPort):
    """Mock messaging adapter that prints to terminal instead of sending WhatsApp."""

    def send_message(self, phone: str, message: str, media_url: str | None = None) -> None:
        print("\n" + "=" * 80)
        print("📱 OUTGOING MESSAGE")
        print("=" * 80)
        print(f"To: {phone}")
        if media_url:
            print(f"Media: {media_url}")
        print(f"\n{message}\n")
        print("=" * 80)


class TerminalDatabaseAdapter(DatabasePort):
    """Mock database adapter with in-memory storage."""

    def __init__(self):
        self.leads: dict[str, dict[str, Any]] = {}
        self.properties = [
            {
                "id": "prop_001",
                "title": "Villa Toscana con Vista",
                "price": 450000,
                "location": "Firenze",
                "rooms": 4,
                "bathrooms": 3,
                "sqm": 180,
                "description": "Splendida villa con giardino e piscina",
                "similarity": 0.92,
            },
            {
                "id": "prop_002",
                "title": "Appartamento Centro Milano",
                "price": 380000,
                "location": "Milano",
                "rooms": 3,
                "bathrooms": 2,
                "sqm": 120,
                "description": "Moderno appartamento in zona Brera",
                "similarity": 0.88,
            },
            {
                "id": "prop_003",
                "title": "Rustico Chianti",
                "price": 520000,
                "location": "Siena",
                "rooms": 5,
                "bathrooms": 3,
                "sqm": 220,
                "description": "Casale ristrutturato con vigneto",
                "similarity": 0.85,
            },
        ]
        self.cache: dict[str, str] = {}

    def get_lead(self, phone: str) -> dict[str, Any] | None:
        return self.leads.get(phone)

    def save_lead(self, lead_data: dict[str, Any]) -> None:
        phone = lead_data["customer_phone"]
        if phone in self.leads:
            self.leads[phone].update(lead_data)
        else:
            self.leads[phone] = lead_data

    def update_lead(self, phone: str, data: dict[str, Any]) -> None:
        if phone in self.leads:
            self.leads[phone].update(data)
        else:
            data["customer_phone"] = phone
            self.leads[phone] = data

    def update_lead_status(self, phone: str, status: str) -> None:
        if phone in self.leads:
            self.leads[phone]["status"] = status
        else:
            self.leads[phone] = {"customer_phone": phone, "status": status}

    def get_properties(
        self,
        query: str | None = None,
        embedding: list[float] | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        results = self.properties.copy()

        # Apply budget filter
        if filters and "max_price" in filters:
            max_price = filters["max_price"]
            results = [p for p in results if p["price"] <= max_price]

        return results[:limit]

    def get_cached_response(self, embedding: list[float]) -> str | None:
        # Simple cache key based on first few embedding values
        cache_key = str(embedding[:5])
        return self.cache.get(cache_key)

    def save_to_cache(self, query: str, embedding: list[float], response: str) -> None:
        cache_key = str(embedding[:5])
        self.cache[cache_key] = response

    def get_market_stats(self, zone: str) -> dict[str, Any]:
        return {
            "avg_price_sqm": 3500,
            "total_properties": 42,
            "zone": zone,
        }


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 80)
    print("🤖 AGENZIA AI - TERMINAL DEMO TEST")
    print("=" * 80)
    print("Simulate WhatsApp conversations without API costs")
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'reset' to start a new conversation")
    print("=" * 80 + "\n")


def print_state_info(state: dict[str, Any]):
    """Print extracted state information."""
    print("\n" + "-" * 80)
    print("📊 EXTRACTED STATE")
    print("-" * 80)

    if state.get("intent"):
        print(f"Intent: {state['intent']}")
    if state.get("budget"):
        print(f"Budget: €{state['budget']:,}")
    if state.get("entities"):
        print(f"Entities: {', '.join(state['entities'])}")

    sentiment = state.get("sentiment")
    if sentiment and hasattr(sentiment, "sentiment"):
        print(f"Sentiment: {sentiment.sentiment} (Urgency: {sentiment.urgency})")

    preferences = state.get("preferences")
    if preferences and hasattr(preferences, "zones") and preferences.zones:
        print(f"Preferences: {preferences.zones}")

    properties = state.get("retrieved_properties", [])
    if properties:
        print(f"\nMatched Properties ({len(properties)}):")
        for prop in properties[:3]:
            print(f"  • {prop['title']} - €{prop['price']:,} ({prop.get('similarity', 0):.2f})")

    print("-" * 80)


def main():
    """Run the terminal demo."""
    import argparse

    parser = argparse.ArgumentParser(description="Terminal Demo Test")
    parser.add_argument("--phone", default="+39333999000", help="Phone number to simulate")
    parser.add_argument(
        "--language", choices=["it", "en"], default="it", help="Conversation language"
    )
    args = parser.parse_args()

    print_banner()

    # Initialize mocked dependencies
    db = TerminalDatabaseAdapter()
    ai = LangChainAdapter()
    msg = TerminalMessagingAdapter()
    scorer = LeadScorer()

    # Initialize journey manager with mocks
    mock_calendar = MagicMock(spec=CalendarPort)
    mock_calendar.create_event.return_value = "https://calendar.google.com/event/123"

    # Mock document generator
    from domain.ports import DocumentPort

    mock_doc_gen = MagicMock(spec=DocumentPort)
    mock_doc_gen.generate_pdf.return_value = "/tmp/mock_brochure.pdf"

    journey = JourneyManager(db, mock_calendar, mock_doc_gen, msg)

    # Initialize lead processor
    processor = LeadProcessor(
        db=db,
        ai=ai,
        msg=msg,
        scorer=scorer,
        journey=journey,
        scraper=None,
        market=None,
        calendar=mock_calendar,
    )

    phone = args.phone
    name = "Demo User"

    print(f"📞 Simulating conversation for: {phone}")
    print(f"🌍 Language: {args.language.upper()}\n")

    # Conversation loop
    while True:
        try:
            user_input = input("👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() == "reset":
                db.leads.pop(phone, None)
                print("\n🔄 Conversation reset.\n")
                continue

            # Process the message
            print("\n⏳ Processing...\n")

            response = processor.process_incoming_message(
                phone=phone, text=user_input, source="WHATSAPP"
            )

            # Get lead state for debugging
            lead = db.get_lead(phone)
            if lead:
                metadata = lead.get("metadata", {})
                print_state_info(metadata)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
