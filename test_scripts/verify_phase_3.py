import os
from datetime import datetime

import dotenv

# Load environment
dotenv.load_dotenv()

from config.container import container


def verify_market_endpoints():
    print("\n--- Verifying Market Intelligence Endpoints ---")
    try:
        # 1. Market Analysis
        print("Testing Market Analysis for Milano...")
        analysis = container.market_intel.get_market_analysis(city="Milano")
        print(f"✅ Sentiment: {analysis.get('sentiment')}")
        print(f"✅ Summary: {analysis.get('summary')[:100]}...")
        print(f"✅ Stats: {analysis.get('stats')}")

        # 2. Market Trends
        print("\nTesting Market Trends for 'Centro' in Milano...")
        trends = container.market_intel.predict_market_trend(zone="Centro", city="Milano")
        print(f"✅ Trend: {trends.get('trend')}")
        print(f"✅ Change: {trends.get('change_pct')}%")
    except Exception as e:
        print(f"❌ Market Endpoints Failed: {e}")


def verify_outreach_logic():
    print("\n--- Verifying Outreach Logic ---")
    try:
        from scripts.agency_outreach import search_agencies

        print("Searching for real agencies in Milano...")
        agencies = search_agencies(city="Milano")
        if agencies:
            print(f"✅ Found {len(agencies)} agencies.")
            print(f"✅ Sample: {agencies[0]['name']} ({agencies[0]['phone']})")
        else:
            print("⚠️ No agencies found (might be normal if API limit or no listings).")
    except Exception as e:
        print(f"❌ Outreach Logic Failed: {e}")


def verify_report_generation():
    print("\n--- Verifying Sales Report Generation ---")
    try:
        # Mock data for report
        report_data = {
            "property_id": "test-prop-001",
            "property_title": "Attico Brera Milano",
            "total_leads": 15,
            "hot_leads": 6,
            "scheduled_viewings": 4,
            "market_value": 1250000,
            "market_analysis": "Zona Brera in forte crescita (+3.5% anno).",
            "ai_advice": "Migliorare illuminazione foto serali.",
        }

        output_path = "temp/documents/test_sales_report.pdf"
        pdf_path = container.doc_gen.generate_pdf("sales_report", report_data)

        if os.path.exists(pdf_path):
            print(f"✅ Sales Report PDF generated: {pdf_path}")
            print(f"✅ File size: {os.path.getsize(pdf_path)} bytes")
        else:
            print("❌ Sales Report PDF not found at expected path.")
    except Exception as e:
        print(f"❌ Report Generation Failed: {e}")


if __name__ == "__main__":
    try:
        print(f"🚀 Starting Phase 3 Verification - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        verify_market_endpoints()
        verify_outreach_logic()
        verify_report_generation()
        print("\n🚀 Verification Complete.")
    except Exception:
        import traceback

        traceback.print_exc()
