import json
import time

import requests
from jose import jwt

from config.settings import settings


def generate_dev_token():
    secret = settings.SUPABASE_JWT_SECRET
    if not secret:
        print("Warning: SUPABASE_JWT_SECRET not set. Auth may fail.")
        return "dummy_token"

    payload = {
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
        "sub": "test-user-id",
        "email": "test@anzevino.ai",
        "role": "authenticated",
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def test_appraisal():
    url = "http://localhost:8000/api/appraisals/estimate"
    token = generate_dev_token()

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    payload = {
        "city": "Milan",
        "zone": "Porta Romana",
        "property_type": "apartment",
        "surface_sqm": 85,
        "condition": "renovated",
        "bedrooms": 2,
    }

    print(f"Sending request to {url}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers)

        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Appraisal Successful!")
            print(f"Estimated Value: €{data.get('estimated_value'):,.0f}")
            print(
                f"Range: €{data.get('estimated_range_min'):,.0f} - €{data.get('estimated_range_max'):,.0f}"
            )
            print(f"Avg Price/Sqm: €{data.get('avg_price_sqm'):,.0f}/mq")
            print(f"Reasoning: {data.get('reasoning')}")
            print("\nComparables Found:")
            for comp in data.get("comparables", []):
                print(f"- {comp['title']} (€{comp['price']:,.0f}, {comp['surface_sqm']}mq)")
        else:
            print("\n❌ Appraisal Failed")
            print(response.text)

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    test_appraisal()
