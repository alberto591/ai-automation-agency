#!/usr/bin/env python3
"""
Quick test script to verify Idealista API credits are working.
Tests the market data service with a sample query.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from infrastructure.market_service import MarketDataService


def test_idealista_api():
    """Test Idealista API with a sample query."""
    print("🔍 Testing Idealista API Credits...")
    print(f"📍 API Key configured: {'✅ Yes' if settings.RAPIDAPI_KEY else '❌ No'}")
    print()
    
    # Create service
    service = MarketDataService()
    
    # Test with a known location (Milan)
    test_zone = "Milano"
    test_city = "Milano"
    
    print(f"🏙️  Testing market data for: {test_zone}")
    print("-" * 50)
    
    try:
        # Get market insights
        insights = service.get_market_insights(test_zone, test_city)
        
        print("✅ API Response received!")
        print()
        print("📊 Market Insights:")
        print(f"   Average Price/sqm: €{insights.get('avg_price_sqm', 'N/A')}")
        print(f"   Trend: {insights.get('trend', 'N/A')}")
        print(f"   Area: {insights.get('area', 'N/A')}")
        print(f"   Live Data: {'✅ Yes' if insights.get('is_live') else '❌ No (using fallback)'}")
        print()
        
        if insights.get('is_live'):
            print("🎉 SUCCESS! API credits are working!")
            print("   You can now use live market data.")
        else:
            print("⚠️  Using fallback data - API might be out of credits or unavailable")
            
        # Try to fetch some listings
        print()
        print("🏘️  Testing property listings...")
        listings = service.search_properties(test_zone, test_city)
        print(f"   Found {len(listings)} properties")
        
        if listings:
            print("   Sample property:")
            sample = listings[0]
            print(f"   - Price: €{sample.get('price', 'N/A')}")
            print(f"   - Size: {sample.get('size', 'N/A')} sqm")
            print(f"   - Location: {sample.get('address', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_idealista_api()
    sys.exit(0 if success else 1)
