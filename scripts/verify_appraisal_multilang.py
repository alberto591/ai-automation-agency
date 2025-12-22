import logging

from lead_manager import handle_incoming_message

# Setup logging
logging.basicConfig(level=logging.INFO)


def run_tests():
    test_cases = [
        {
            "name": "Tuscany Address + Spanish Number",
            "phone": "+34600123456",
            "message": "RICHIESTA VALUTAZIONE: via S. Martino Altoreggi, 72, 50063 Figline e Incisa Valdarno FI",
        },
        {
            "name": "Tuscany Address + Italian Number",
            "phone": "+393331234567",
            "message": "RICHIESTA VALUTAZIONE: via Ghibellina, Firenze",
        },
        {
            "name": "Milano Address (Outlier) + English/Unknown Number",
            "phone": "+1234567890",
            "message": "RICHIESTA VALUTAZIONE: Corso Buenos Aires, Milano",
        },
    ]

    print("\n" + "=" * 50)
    print("🚀 STARTING MULTILINGUAL APPRAISAL TESTS")
    print("=" * 50 + "\n")

    for tc in test_cases:
        print(f"--- TEST: {tc['name']} ---")
        print(f"Input: {tc['phone']} | {tc['message']}")

        # Execute
        result = handle_incoming_message(tc["phone"], tc["message"])

        print("\n--- RESULT ---")
        print(result)
        print("-" * 50 + "\n")


if __name__ == "__main__":
    run_tests()
