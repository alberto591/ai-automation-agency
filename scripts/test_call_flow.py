import os
import sys

from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.getcwd())

from presentation.api.api import app

client = TestClient(app)


def test_voice_flow():
    print("📞 Testing Voice Flow...")

    # 1. Inbound Call
    print("  - Simulating Inbound Call...")
    response = client.post(
        "/api/webhooks/voice/inbound", data={"From": "+393331234567", "CallSid": "CA12345"}
    )
    if response.status_code == 200 and "<Say>" in response.text:
        print("    ✅ Inbound Call Success (TwiML returned)")
    else:
        print(f"    ❌ Inbound Call Failed: {response.text}")

    # 2. Transcription
    print("  - Simulating Transcription (Voicemail)...")
    response = client.post(
        "/api/webhooks/voice/transcription",
        data={
            "From": "+393331234567",
            "TranscriptionText": "Hello, I am interested in the apartment in Rome.",
            "CallSid": "CA12345",
        },
    )

    if response.status_code == 200:
        print("    ✅ Transcription Processed")
    else:
        print(f"    ❌ Transcription Failed: {response.text}")


if __name__ == "__main__":
    test_voice_flow()
