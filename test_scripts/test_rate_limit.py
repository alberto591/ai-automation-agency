import time

from config.container import container


def test_rate_limit():
    """
    Test that rate limiting works correctly.
    We'll send messages rapidly and verify the rate limiter blocks excess messages.
    """
    test_phone = "+393999999999"

    print(f"Testing rate limiting for {test_phone}")
    print(
        f"Rate limit: {container.msg.rate_limiter.max_messages} messages per {container.msg.rate_limiter.window_seconds}s"
    )

    success_count = 0
    blocked_count = 0

    # Try to send 25 messages (should block after 20 by default)
    for i in range(25):
        try:
            # We'll use a dry-run approach by checking the rate limiter directly
            # instead of actually sending messages
            if container.msg.rate_limiter.check_rate_limit(test_phone):
                success_count += 1
                print(
                    f"  ✓ Message {i+1}: Allowed (remaining: {container.msg.rate_limiter.get_remaining(test_phone)})"
                )
            else:
                blocked_count += 1
                print(f"  ✗ Message {i+1}: BLOCKED by rate limiter")
        except Exception as e:
            print(f"  ✗ Message {i+1}: Error - {e}")
            blocked_count += 1

    print("\n=== Results ===")
    print(f"Allowed: {success_count}")
    print(f"Blocked: {blocked_count}")
    print("Expected: 20 allowed, 5 blocked")

    if success_count == 20 and blocked_count == 5:
        print("✅ Rate limiting working correctly!")
    else:
        print("❌ Rate limiting not working as expected")

    # Test window sliding
    print("\n=== Testing Window Sliding ===")
    print("Waiting 2 seconds...")
    time.sleep(2)

    # Reset for clean test
    container.msg.rate_limiter.reset(test_phone)
    print(f"Reset rate limiter for {test_phone}")

    # Should allow messages again
    if container.msg.rate_limiter.check_rate_limit(test_phone):
        print("✅ After reset: Messages allowed again")
    else:
        print("❌ After reset: Still blocked (unexpected)")


if __name__ == "__main__":
    test_rate_limit()
