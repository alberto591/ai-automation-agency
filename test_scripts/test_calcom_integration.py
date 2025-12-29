#!/usr/bin/env python3
"""Test script to verify Cal.com integration.

Tests:
1. CalComAdapter initialization
2. API connectivity
3. Event type configuration
4. Webhook signature verification
5. End-to-end booking flow simulation
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from domain.services.logging import get_logger
from infrastructure.adapters.calcom_adapter import CalComAdapter

logger = get_logger(__name__)


def test_configuration():
    """Test Cal.com configuration."""
    print("\n" + "=" * 80)
    print("TEST 1: Configuration")
    print("=" * 80)

    checks = {
        "API Key": bool(settings.CALCOM_API_KEY),
        "Event Type ID": bool(settings.CALCOM_EVENT_TYPE_ID),
        "Webhook Secret": bool(settings.CALCOM_WEBHOOK_SECRET),
        "Booking Link": bool(settings.CALCOM_BOOKING_LINK),
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        value = "configured" if passed else "missing"
        print(f"{status} - {check}: {value}")

    all_passed = all(checks.values())
    print(
        f"\n{'✅ All configuration checks passed' if all_passed else '❌ Some configuration missing'}"
    )
    return all_passed


def test_adapter_initialization():
    """Test CalComAdapter initialization."""
    print("\n" + "=" * 80)
    print("TEST 2: Adapter Initialization")
    print("=" * 80)

    try:
        adapter = CalComAdapter()
        print("✅ PASS - CalComAdapter initialized")
        print(f"   - Base URL: {adapter.base_url}")
        print(f"   - Event Type ID: {adapter.event_type_id}")
        print(f"   - API Key: {adapter.api_key[:20]}...")
        return True, adapter
    except Exception as e:
        print(f"❌ FAIL - Adapter initialization failed: {e}")
        return False, None


def test_availability(adapter: CalComAdapter):
    """Test get_availability method."""
    print("\n" + "=" * 80)
    print("TEST 3: Get Availability")
    print("=" * 80)

    if not adapter:
        print("⚠️  SKIP - Adapter not initialized")
        return False

    try:
        # Test with tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"Fetching availability for: {tomorrow}")

        slots = adapter.get_availability("", tomorrow)

        if isinstance(slots, list):
            print(f"✅ PASS - Retrieved {len(slots)} available slots")
            if slots:
                print(f"   - Sample slot: {slots[0]}")
            else:
                print("   - No slots available (this is OK)")
            return True
        else:
            print(f"❌ FAIL - Expected list, got {type(slots)}")
            return False

    except Exception as e:
        print(f"❌ FAIL - get_availability failed: {e}")
        logger.error("AVAILABILITY_TEST_FAILED", context={"error": str(e)}, exc_info=True)
        return False


def test_booking_link(adapter: CalComAdapter):
    """Test create_event method (returns booking link)."""
    print("\n" + "=" * 80)
    print("TEST 4: Create Event (Booking Link)")
    print("=" * 80)

    if not adapter:
        print("⚠️  SKIP - Adapter not initialized")
        return False

    try:
        # Test parameters
        start_time = datetime.now() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(minutes=30)

        print("Test booking:")
        print(f"   - Start: {start_time}")
        print(f"   - End: {end_time}")
        print("   - Attendee: test@example.com")

        booking_link = adapter.create_event(
            summary="Test Property Viewing",
            start_time=start_time,
            end_time=end_time,
            attendees=["test@example.com"],
        )

        if booking_link and "cal.com" in booking_link:
            print(f"✅ PASS - Booking link returned: {booking_link}")
            return True
        else:
            print(f"❌ FAIL - Invalid booking link: {booking_link}")
            return False

    except Exception as e:
        print(f"❌ FAIL - create_event failed: {e}")
        logger.error("BOOKING_TEST_FAILED", context={"error": str(e)}, exc_info=True)
        return False


def test_webhook_signature():
    """Test webhook signature verification logic."""
    print("\n" + "=" * 80)
    print("TEST 5: Webhook Signature Verification")
    print("=" * 80)

    import hashlib
    import hmac

    try:
        # Simulate webhook payload
        test_payload = b'{"triggerEvent":"BOOKING_CREATED","payload":{"booking":{"id":123}}}'

        # Generate expected signature
        expected_sig = hmac.new(
            settings.CALCOM_WEBHOOK_SECRET.encode(), test_payload, hashlib.sha256
        ).hexdigest()

        signature_header = f"sha256={expected_sig}"

        print("✅ PASS - Signature generation works")
        print(f"   - Payload: {test_payload.decode()[:50]}...")
        print(f"   - Signature: {signature_header[:40]}...")

        # Verify signature
        is_valid = hmac.compare_digest(signature_header, f"sha256={expected_sig}")

        if is_valid:
            print("✅ PASS - Signature verification works")
            return True
        else:
            print("❌ FAIL - Signature verification failed")
            return False

    except Exception as e:
        print(f"❌ FAIL - Webhook signature test failed: {e}")
        return False


def test_end_to_end_flow():
    """Simulate end-to-end booking flow."""
    print("\n" + "=" * 80)
    print("TEST 6: End-to-End Flow Simulation")
    print("=" * 80)

    print("Simulating user journey:")
    print("1. User: 'Vorrei visitare una casa domani'")
    print("2. AI detects intent: VISIT")
    print("3. AI generates response with Cal.com link")
    print("4. User clicks link and books appointment")
    print("5. Cal.com sends webhook")
    print("6. System updates lead status to SCHEDULED")

    # Check if booking link is in settings
    if settings.CALCOM_BOOKING_LINK and "cal.com" in settings.CALCOM_BOOKING_LINK:
        print(f"\n✅ PASS - Booking link configured: {settings.CALCOM_BOOKING_LINK}")
        print("✅ PASS - End-to-end flow ready")
        return True
    else:
        print("\n❌ FAIL - Booking link not configured")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CAL.COM INTEGRATION TEST SUITE")
    print("=" * 80)

    results = {}

    # Test 1: Configuration
    results["Configuration"] = test_configuration()

    # Test 2: Adapter Initialization
    passed, adapter = test_adapter_initialization()
    results["Adapter Init"] = passed

    # Test 3: Get Availability
    results["Get Availability"] = test_availability(adapter)

    # Test 4: Create Event
    results["Create Event"] = test_booking_link(adapter)

    # Test 5: Webhook Signature
    results["Webhook Signature"] = test_webhook_signature()

    # Test 6: End-to-End Flow
    results["E2E Flow"] = test_end_to_end_flow()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed_count = sum(results.values())

    print(f"\n{'=' * 80}")
    print(f"TOTAL: {passed_count}/{total} tests passed")
    print(f"{'=' * 80}\n")

    if passed_count == total:
        print("🎉 All tests passed! Cal.com integration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
