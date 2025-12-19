#!/usr/bin/env python3
"""
Conversational Analytics Dashboard

Generates insights from lead conversations stored in Supabase.
Run manually or schedule weekly: `python scripts/analytics.py`

Metrics calculated:
- Total leads
- Hot lead percentage (score >= 50)
- Takeover rate
- Most requested property types
- Follow-up engagement
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from collections import Counter
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


def get_analytics(days=30):
    """Generate analytics for the last N days"""
    
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    
    print(f"\n📊 Agenzia AI Analytics - Last {days} Days")
    print("=" * 50)
    
    try:
        # Fetch all records from the period
        response = supabase.table("lead_conversations")\
            .select("*")\
            .gte("created_at", cutoff_date)\
            .execute()
        
        records = response.data
        total_records = len(records)
        
        print(f"\n📈 VOLUME METRICS")
        print(f"   Total Conversations: {total_records}")
        
        # Unique leads (by phone number)
        unique_phones = set(r["customer_phone"] for r in records if r.get("customer_name") != "System")
        print(f"   Unique Leads: {len(unique_phones)}")
        
        # Hot leads (from ai_summary containing score indicators)
        hot_leads = [r for r in records if "🔥 HOT LEAD" in r.get("ai_summary", "")]
        warm_leads = [r for r in records if "⭐ Warm Lead" in r.get("ai_summary", "")]
        print(f"   🔥 Hot Leads: {len(hot_leads)} ({len(hot_leads)/total_records*100:.1f}%)" if total_records else "   Hot Leads: 0")
        print(f"   ⭐ Warm Leads: {len(warm_leads)}")
        
        # Takeover events
        takeovers = [r for r in records if r.get("status") == "TAKEOVER"]
        takeover_rate = (len(takeovers) / total_records * 100) if total_records else 0
        print(f"   🚨 Takeover Rate: {takeover_rate:.1f}%")
        
        # Most mentioned property types (extract from last_message)
        print(f"\n🏠 PROPERTY INTERESTS")
        property_keywords = ["villa", "attico", "trilocale", "bilocale", "appartamento", "casa"]
        property_mentions = Counter()
        
        for record in records:
            msg = record.get("last_message", "").lower()
            for prop in property_keywords:
                if prop in msg:
                    property_mentions[prop] += 1
        
        for prop, count in property_mentions.most_common(5):
            print(f"   {prop.capitalize()}: {count} mentions")
        
        # Engagement metrics
        print(f"\n💬 ENGAGEMENT")
        follow_ups = [r for r in records if r.get("status") == "FOLLOW_UP"]
        print(f"   Follow-up Messages Sent: {len(follow_ups)}")
        
        # Status breakdown
        statuses = Counter(r.get("status", "Unknown") for r in records)
        print(f"\n📋 STATUS BREAKDOWN")
        for status, count in statuses.most_common():
            print(f"   {status}: {count}")
        
        # Daily average
        avg_per_day = total_records / days
        print(f"\n⏱️  ACTIVITY")
        print(f"   Average Conversations/Day: {avg_per_day:.1f}")
        
        print("\n" + "=" * 50)
        print(f"Analytics generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error generating analytics: {e}")


def export_to_csv():
    """Export analytics to CSV for Google Sheets upload"""
    try:
        from datetime import datetime
        import csv
        
        response = supabase.table("lead_conversations").select("*").limit(1000).execute()
        records = response.data
        
        if not records:
            print("No data to export")
            return
        
        filename = f"analytics_export_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        
        print(f"✅ Exported {len(records)} records to {filename}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        export_to_csv()
    else:
        # Default: show analytics for last 30 days
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
        get_analytics(days)
