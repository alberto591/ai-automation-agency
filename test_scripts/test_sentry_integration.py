#!/usr/bin/env python3
"""Test script to verify Sentry integration.

Tests:
1. Sentry module initialization
2. Configuration validation
3. Error capture simulation
4. Breadcrumb tracking
5. User context setting
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from domain.services.logging import get_logger
from infrastructure.monitoring.sentry import (
    add_breadcrumb,
    capture_exception,
    capture_message,
    init_sentry,
    set_user_context,
)

logger = get_logger(__name__)


def test_configuration():
    """Test Sentry configuration."""
    print("\n" + "=" * 80)
    print("TEST 1: Configuration")
    print("=" * 80)

    checks = {
        "Sentry DSN": bool(settings.SENTRY_DSN),
        "Environment": bool(settings.ENVIRONMENT),
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "⚠️  SKIP"
        value = "configured" if passed else "not configured (optional)"
        print(f"{status} - {check}: {value}")

    if settings.SENTRY_DSN:
        print(f"\n✅ Sentry DSN configured: {settings.SENTRY_DSN[:30]}...")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        return True
    else:
        print("\n⚠️  Sentry DSN not configured (will use placeholder)")
        return False


def test_initialization():
    """Test Sentry initialization."""
    print("\n" + "=" * 80)
    print("TEST 2: Initialization")
    print("=" * 80)

    try:
        # Test with placeholder DSN if not configured
        test_dsn = settings.SENTRY_DSN or "https://placeholder@sentry.io/0"

        init_sentry(dsn=test_dsn, environment=settings.ENVIRONMENT, traces_sample_rate=1.0)

        print("✅ PASS - Sentry initialized successfully")
        print(f"   - DSN: {test_dsn[:30]}...")
        print(f"   - Environment: {settings.ENVIRONMENT}")
        return True

    except Exception as e:
        print(f"❌ FAIL - Initialization failed: {e}")
        return False


def test_error_capture():
    """Test error capture functionality."""
    print("\n" + "=" * 80)
    print("TEST 3: Error Capture")
    print("=" * 80)

    try:
        # Simulate an error
        test_error = ValueError("Test error for Sentry integration")

        capture_exception(test_error, context={"test": "error_capture", "component": "test_script"})

        print("✅ PASS - Error captured successfully")
        print(f"   - Error: {test_error}")
        print("   - Context: test error capture")
        return True

    except Exception as e:
        print(f"❌ FAIL - Error capture failed: {e}")
        return False


def test_message_capture():
    """Test message capture functionality."""
    print("\n" + "=" * 80)
    print("TEST 4: Message Capture")
    print("=" * 80)

    try:
        capture_message(
            "Test message for Sentry integration", level="info", context={"test": "message_capture"}
        )

        print("✅ PASS - Message captured successfully")
        print("   - Message: Test message for Sentry integration")
        print("   - Level: info")
        return True

    except Exception as e:
        print(f"❌ FAIL - Message capture failed: {e}")
        return False


def test_user_context():
    """Test user context setting."""
    print("\n" + "=" * 80)
    print("TEST 5: User Context")
    print("=" * 80)

    try:
        set_user_context(user_id="test_user_123", email="test@example.com", phone="+39123456789")

        print("✅ PASS - User context set successfully")
        print("   - User ID: test_user_123")
        print("   - Email: test@example.com")
        return True

    except Exception as e:
        print(f"❌ FAIL - User context failed: {e}")
        return False


def test_breadcrumbs():
    """Test breadcrumb tracking."""
    print("\n" + "=" * 80)
    print("TEST 6: Breadcrumbs")
    print("=" * 80)

    try:
        add_breadcrumb(
            category="test",
            message="Test breadcrumb",
            level="info",
            data={"step": 1, "action": "test"},
        )

        print("✅ PASS - Breadcrumb added successfully")
        print("   - Category: test")
        print("   - Message: Test breadcrumb")
        return True

    except Exception as e:
        print(f"❌ FAIL - Breadcrumb failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("SENTRY INTEGRATION TEST SUITE")
    print("=" * 80)

    results = {}

    # Test 1: Configuration
    results["Configuration"] = test_configuration()

    # Test 2: Initialization
    results["Initialization"] = test_initialization()

    # Test 3: Error Capture
    results["Error Capture"] = test_error_capture()

    # Test 4: Message Capture
    results["Message Capture"] = test_message_capture()

    # Test 5: User Context
    results["User Context"] = test_user_context()

    # Test 6: Breadcrumbs
    results["Breadcrumbs"] = test_breadcrumbs()

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
        print("🎉 All tests passed! Sentry integration is ready.")
        print("\n📝 Next Steps:")
        print("1. Create Sentry account at https://sentry.io")
        print("2. Create projects for 'backend' and 'dashboard'")
        print("3. Add DSNs to .env files")
        print("4. Test with real errors in production")
        return 0
    else:
        print("⚠️  Some tests failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
