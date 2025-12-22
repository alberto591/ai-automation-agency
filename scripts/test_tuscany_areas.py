import logging

from lead_manager import handle_incoming_message

# Setup logging
logging.basicConfig(level=logging.INFO)


def run_tuscany_tests():
    test_cases = [
        {"name": "Grosseto", "addr": "Via Roma, Grosseto"},
        {"name": "Livorno", "addr": "Piazza della Repubblica, Livorno"},
        {"name": "Massa", "addr": "Piazza Aranci, Massa"},
        {"name": "Carrara", "addr": "Via Nuova, Carrara"},
        {"name": "Pistoia", "addr": "Piazza del Duomo, Pistoia"},
        {"name": "Prato", "addr": "Via Pier Cironi, Prato"},
        {"name": "Monte Argentario", "addr": "Via Panoramica, Monte Argentario"},
        {"name": "General Toscana", "addr": "Via della Campagna, Toscana"},
        {"name": "Arezzo", "addr": "Corso Italia, Arezzo"},
        {
            "name": "Figline e Incisa Valdarno",
            "addr": "via S. Martino Altoreggi, 72, 50063 Figline e Incisa Valdarno FI",
        },
    ]

    print("\n" + "=" * 60)
    print("🌍 TUSCANY AREA DETECTION TEST SUITE")
    print("=" * 60 + "\n")

    for tc in test_cases:
        print(f"--- TESTING: {tc['name']} ---")
        msg = f"RICHIESTA VALUTAZIONE: {tc['addr']}"
        # Using a Spanish number for one to verify language persistency if needed,
        # but here we'll use a neutral one or just check the Zone detection logic in the output.
        result = handle_incoming_message("+393330000000", msg)

        # Check if the correct zone name appears in the result
        if tc["name"].upper() in result.upper() or (
            tc["name"] == "General Toscana" and "TOSCANA" in result.upper()
        ):
            print(f"✅ Detection Success for {tc['name']}")
        else:
            print(f"❌ Detection Failed for {tc['name']}. Result: {result[:50]}...")

        # Check if price is reasonable (not 5200 which is Milano default)
        if "5200" in result and tc["name"] != "Milano":
            print(f"⚠️ Warning: Used Milano fallback instead of Tuscany data for {tc['name']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_tuscany_tests()
