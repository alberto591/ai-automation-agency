import os
import sys
from unittest.mock import patch

# Add project root to path
sys.path.append(os.getcwd())

# 1. Set Mock Env Var BEFORE importing settings/api
os.environ["SUPABASE_JWT_SECRET"] = "super-secret-test-key"

from fastapi.testclient import TestClient
from jose import jwt

# Mock dependencies before importing api
with patch("config.container.container") as mock_container:
    from presentation.api.api import app

    client = TestClient(app)

    def generate_token():
        return jwt.encode(
            {"sub": "1234567890", "role": "authenticated", "aud": "authenticated"},
            "super-secret-test-key",
            algorithm="HS256",
        )

    def test_unauthorized_access():
        print("\n[TEST] Unauthorized Access (No Token)")
        response = client.post("/api/leads/takeover", json={"phone": "+391234567890"})
        print(f"Status: {response.status_code}")
        assert response.status_code in {401, 403}
        print("PASS")

    def test_authorized_access():
        print("\n[TEST] Authorized Access (With Token)")
        token = generate_token()

        # Mock container method
        mock_container.lead_processor.takeover.return_value = None

        response = client.post(
            "/api/leads/takeover",
            json={"phone": "+391234567890"},
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        print("PASS")

    def test_summary_endpoint():
        print("\n[TEST] Summary Endpoint")
        token = generate_token()

        mock_data = {
            "summary": "User is interested in a villa.",
            "sentiment": "POSITIVE",
            "suggested_action": "Schedule visit",
        }
        mock_container.lead_processor.summarize_lead.return_value = mock_data

        response = client.get(
            "/api/leads/+391234567890/summary", headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json() == mock_data
        print("PASS")

    def test_market_endpoint():
        print("\n[TEST] Market Valuation Endpoint")
        token = generate_token()

        mock_data = {"zone": "Centro", "avg_price_sqm": 3500, "trend": "UP"}
        mock_container.market.get_market_insights.return_value = mock_data

        response = client.get(
            "/api/market/valuation?zone=Centro&city=Milano",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["data"] == mock_data
        print("PASS")

    if __name__ == "__main__":
        try:
            test_unauthorized_access()
            test_authorized_access()
            test_summary_endpoint()
            test_market_endpoint()
            print("\nALL TESTS PASSED ✨")
        except AssertionError as e:
            print("\nTEST FAILED ❌")
            raise e
        except Exception as e:
            print(f"\nERROR: {e}")
            raise e
