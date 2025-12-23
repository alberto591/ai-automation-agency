import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.container import container

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_multilang():
    test_cases = [
        {
            "name": "Italian Local",
            "phone": "+393331234567",
            "message": "Buongiorno, vorrei informazioni su un appartamento a Firenze.",
        },
        {
            "name": "English Tourist",
            "phone": "+447712345678",
            "message": "Hello, I'm looking for a villa in Tuscany for my summer holidays.",
        },
        {
            "name": "Spanish Tourist (English preference)",
            "phone": "+34600123456",
            "message": "Hi, do you have any houses for sale in Figline?",
        },
    ]

    print("\n" + "=" * 50)
    print("🌍 TESTING MULTI-LANGUAGE TOURIST FLOW")
    print("=" * 50 + "\n")

    for tc in test_cases:
        print(f"--- TEST: {tc['name']} ---")
        print(f"Input: {tc['phone']} | {tc['message']}")

        try:
            # We use the lead_processor which invokes the LangGraph
            result = container.lead_processor.process_incoming_message(tc["phone"], tc["message"])

            print("\n--- AI RESPONSE ---")
            print(result)
            print("-" * 50 + "\n")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_multilang()
