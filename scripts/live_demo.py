"""
Live Demo Script for Anzevino AI
Demonstrates all major flows including the new Fifi Appraisal feature
"""

import json
import os
import sys
import time
from datetime import datetime

import requests

# Ensure we can access config
sys.path.append(os.getcwd())

API_URL = os.getenv("API_URL", "http://localhost:8000")
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY", "prod_dev_secret_key_2025")

SCENARIOS = {
    "1": {
        "name": "Luxury Seeker (Marco) - PORTAL",
        "endpoint": "/api/leads",
        "phone": "+393335550001",
        "payload": {
            "name": "Marco Luxury",
            "agency": "Immobiliare.it",
            "phone": "+393335550001",
            "properties": "Attico vista Duomo, 2.5mln",
        },
        "description": "Tests portal integration and high-value lead routing",
    },
    "2": {
        "name": "Free Appraisal (Elena) - WEB_APPRAISAL (HOT)",
        "endpoint": "/api/leads",
        "phone": "+393335550002",
        "payload": {
            "name": "Elena Appraisal",
            "agency": "Website Widget",
            "phone": "+393335550002",
            "properties": "Valutazione via Roma 5, Milano #appraisal",
        },
        "description": "Tests legacy appraisal flow through lead ingestion",
    },
    "3": {
        "name": "Visit Request (Luca) - APPOINTMENT STEERING",
        "endpoint": "/api/leads",
        "phone": "+393335550003",
        "payload": {
            "name": "Luca Investor",
            "agency": "Idealista",
            "phone": "+393335550003",
            "properties": "Interessato al Rustico. Vorrei visitarlo domani.",
        },
        "description": "Tests appointment booking flow and calendar integration",
    },
    "4": {
        "name": "🆕 Direct Appraisal API - Fifi with Investment Metrics",
        "endpoint": "/api/appraisals/estimate",
        "phone": "+393335550004",
        "payload": {
            "city": "Milano",
            "zone": "Centro",
            "property_type": "apartment",
            "surface_sqm": 95,
            "condition": "good",
            "bedrooms": 2,
            "phone": "+393335550004",
            "email": "demo@anzevino.ai",
            "name": "Demo User",
        },
        "description": "Tests NEW appraisal endpoint with investment calculations (UI fix verified)",
    },
}


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_section(title, content, color="blue"):
    """Print a formatted section"""
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "end": "\033[0m",
    }
    print(f"{colors.get(color, '')}■ {title}:{colors['end']}")
    if isinstance(content, dict):
        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        print(f"  {content}")
    print()


def format_investment_metrics(metrics):
    """Format investment metrics for display"""
    if not metrics:
        return "No investment metrics available"

    output = []
    output.append(f"  💰 Cap Rate: {metrics.get('cap_rate', 'N/A')}%")
    output.append(f"  📊 ROI: {metrics.get('roi', 'N/A')}%")
    output.append(f"  💵 Monthly Cash Flow: €{metrics.get('monthly_cash_flow', 0):,}")
    output.append(f"  📈 Price-to-Rent Ratio: {metrics.get('price_to_rent_ratio', 'N/A')}")
    output.append(f"  ⏱️  Breakeven: {metrics.get('breakeven_years', 'N/A')} years")
    return "\n".join(output)


def run_demo(scenario_id):
    """Run a demo scenario with enhanced output"""
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        print("❌ Scenario not found.")
        return

    print_header(f"🌟 Demo: {scenario['name']}")
    print_section("Description", scenario["description"], "blue")
    print_section("Target API", API_URL, "blue")
    print_section("Endpoint", scenario["endpoint"], "blue")

    # Send request with timing
    print(f"🚀 Sending request for {scenario.get('phone', 'N/A')}...")
    start_time = time.time()

    try:
        response = requests.post(
            f"{API_URL}{scenario['endpoint']}",
            json=scenario["payload"],
            headers={"X-Webhook-Key": WEBHOOK_KEY},
            timeout=30,
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print_section("✅ Success", f"Response received in {elapsed:.2f}s", "green")

            # Display response based on endpoint type
            if scenario["endpoint"] == "/api/appraisals/estimate":
                # Appraisal response
                print_section("Estimated Value", f"€{data.get('estimated_value', 0):,.0f}", "green")
                print_section(
                    "Value Range",
                    f"€{data.get('estimated_range_min', 0):,.0f} - €{data.get('estimated_range_max', 0):,.0f}",
                    "green",
                )
                print_section(
                    "Confidence Level",
                    f"{data.get('confidence_level', 0)}% ({data.get('reliability_stars', 0)}⭐)",
                    "green",
                )
                print_section("Market Trend", data.get("market_trend", "N/A"), "yellow")

                if data.get("investment_metrics"):
                    print_section(
                        "Investment Metrics",
                        format_investment_metrics(data["investment_metrics"]),
                        "green",
                    )

                print_section(
                    "Comparables Found",
                    f"{len(data.get('comparables', []))} properties",
                    "blue",
                )

            else:
                # Lead response
                ai_response = data.get("ai_response", "")
                print_section(
                    "🤖 AI Response",
                    ai_response[:300] + "..." if len(ai_response) > 300 else ai_response,
                    "green",
                )

            # Option to see full JSON
            print("\n💡 TIP: Open the Dashboard to see the complete lead details and AI insights")
            view_full = input("\n📄 View full JSON response? (y/n): ").strip().lower()
            if view_full == "y":
                print_section("Full Response", data, "blue")

        else:
            print_section(f"❌ Error {response.status_code}", response.text, "red")

    except requests.exceptions.Timeout:
        print_section("❌ Request Timeout", "The API took too long to respond (>30s)", "red")
    except requests.exceptions.ConnectionError:
        print_section(
            "❌ Connection Failed",
            f"Could not connect to {API_URL}. Is the server running?",
            "red",
        )
    except Exception as e:
        print_section("❌ Unexpected Error", str(e), "red")


def main():
    """Main demo loop"""
    print_header("ANZEVINO AI - LIVE CLIENT DEMO TOOL")
    print("📅", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"🌐 API: {API_URL}\n")

    while True:
        print("\n" + "─" * 70)
        print("Available Scenarios:")
        print("─" * 70)

        for k, v in SCENARIOS.items():
            prefix = "🆕" if "🆕" in v["name"] else "  "
            print(f"{prefix} {k}. {v['name']}")
            print(f"     {v['description']}")

        print("\n0. Exit")
        print("─" * 70)

        choice = input("\n📝 Select Scenario (0-4): ").strip()

        if choice == "0":
            print("\n👋 Demo session ended. Thanks!\n")
            break
        elif choice in SCENARIOS:
            run_demo(choice)
        else:
            print("\n❌ Invalid choice. Please select 0-4.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!\n")
        sys.exit(0)
