import os

# Protocol Verification for ADR-040
# This script performs static-ish checks to verify that the ADR requirements are reflected in the codebase.


def test_fifi_avm_protocol():  # noqa: PLR0912
    print("🧪 Verifying ADR-040: Fifi AVM Development & Test Protocol...")

    # 1. Port Awareness
    print("\n🔍 Checking domain ports for AVM capabilities...")
    ports_path = "domain/ports.py"
    if os.path.exists(ports_path):
        with open(ports_path) as f:
            content = f.read()
            if "MarketDataPort" in content:
                print("✅ MarketDataPort found in domain/ports.py.")
            else:
                print("❌ MarketDataPort missing from domain/ports.py.")
    else:
        print(f"❌ {ports_path} not found.")

    # 2. Confidence Score Requirement (ADR 2.2)
    print("\n🔍 Checking for Confidence Score implementation requirements...")
    agents_path = "application/workflows/agents.py"
    if os.path.exists(agents_path):
        with open(agents_path) as f:
            content = f.read()
            # The ADR requires confidence logging
            if (
                "confidence" in content.lower()
                or "probabilità" in content.lower()
                or "source" in content
            ):
                print("✅ Confidence/Source awareness found in agents.py.")
            else:
                print("⚠️ WARNING: Confidence Score logic not yet fully implemented in agents.py.")
    else:
        print(f"❌ {agents_path} not found.")

    # 3. Ground truth docs (ADR 2.1)
    print("\n🔍 Verifying Grounding Data Documentation (OMI/Deeds)...")
    legal_path = "docs/legal/attorney_brief.md"
    if os.path.exists(legal_path):
        with open(legal_path) as f:
            content = f.read()
            if "OMI" in content or "Deeds" in content:
                print("✅ Ground truth references (OMI/Deeds) found in legal docs.")
            else:
                print("⚠️ WARNING: OMI/Deeds references not found in attorney brief.")
    else:
        print(f"❌ {legal_path} not found.")

    # 4. ADR Compliance Verification
    print("\n🔍 Checking ADR-040 file content...")
    adr_path = "docs/adr/ADR-040-fifi-avm-development-and-test-strategy.md"
    if os.path.exists(adr_path):
        with open(adr_path) as f:
            content = f.read()
            if "XGBoost" in content and "Backtesting" in content:
                print("✅ ADR-040 correctly specifies Development and Testing strategies.")
            else:
                print("❌ ADR-040 is missing key content.")
    else:
        print(f"❌ {adr_path} not found.")

    print("\n🏁 ADR-040 Protocol Verification Complete.")


if __name__ == "__main__":
    test_fifi_avm_protocol()
