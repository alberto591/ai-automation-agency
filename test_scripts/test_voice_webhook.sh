#!/bin/bash
# Test Voice Webhook - Simulates Twilio calling your endpoint

echo "🧪 Testing Voice Webhook..."
echo ""

# Test 1: Inbound call
echo "📞 Test 1: Simulating inbound call"
RESPONSE=$(curl -s -X POST https://agenzia-ai.vercel.app/api/webhooks/voice/inbound \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=+393331234567" \
  -d "CallSid=CAtest123456789" \
  -d "To=+12345678900")

echo "$RESPONSE"
echo ""

# Check if Italian consent prompt is in response
if echo "$RESPONSE" | grep -q "Questa chiamata potrebbe essere registrata"; then
    echo "✅ Italian consent prompt found!"
else
    echo "❌ Consent prompt NOT found"
fi

echo ""
echo "---"
echo ""

# Test 2: Consent given (user presses 1)
echo "📞 Test 2: Simulating user consent (pressing 1)"
RESPONSE2=$(curl -s -X POST https://agenzia-ai.vercel.app/api/webhooks/voice/consent \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Digits=1" \
  -d "From=+393331234567" \
  -d "CallSid=CAtest123456789")

echo "$RESPONSE2"
echo ""

# Check if recording starts
if echo "$RESPONSE2" | grep -q "Record"; then
    echo "✅ Recording enabled after consent!"
else
    echo "⚠️  Recording not found in response"
fi

echo ""
echo "---"
echo ""

# Test 3: Consent rejected (user presses anything else)
echo "📞 Test 3: Simulating user rejection (pressing 2)"
RESPONSE3=$(curl -s -X POST https://agenzia-ai.vercel.app/api/webhooks/voice/consent \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Digits=2" \
  -d "From=+393331234567" \
  -d "CallSid=CAtest123456789")

echo "$RESPONSE3"
echo ""

# Check if call hangs up
if echo "$RESPONSE3" | grep -q "Hangup"; then
    echo "✅ Call correctly terminated after rejection!"
else
    echo "❌ Hangup not found"
fi

echo ""
echo "🎉 Voice webhook tests complete!"
