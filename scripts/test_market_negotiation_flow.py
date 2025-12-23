import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.container import container

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_negotiation():
    test_cases = [
        {
            "name": "Italian Negotiation",
            "phone": "+393331234567",
            "message": "L'appartamento a Figline a 250.000€ mi sembra caro. Possiamo offrire meno?",
            "context": "immobile: FIGLINE-123",
        }
    ]

    print("\n" + "=" * 50)
    print("🤝 TESTING ADVANCED NEGOTIATION FLOW")
    print("=" * 50 + "\n")

    for tc in test_cases:
        print(f"--- TEST: {tc['name']} ---")
        # In a real scenario, the context comes from the portal or previous messages
        # Here we simulate the PORTAL source by including the keyword
        full_message = tc["message"]
        if "context" in tc:
            full_message += f"\n[INTERNAL: {tc['context']}]"

        print(f"Input: {full_message}")

        try:
            result = container.lead_processor.process_incoming_message(tc["phone"], full_message)

            print("\n--- AI RESPONSE ---")
            print(result)
            print("-" * 50 + "\n")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_negotiation()
