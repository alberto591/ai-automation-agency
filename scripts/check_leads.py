#!/usr/bin/env python3
"""
Quick script to check if there are any leads in Supabase database.
"""
import os
import sys

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for admin access

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env")
    sys.exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Checking Supabase for existing leads...")
print(f"📍 URL: {SUPABASE_URL}")
print()

try:
    # Query all leads
    response = supabase.table("leads").select("*").execute()
    
    total_leads = len(response.data) if response.data else 0
    
    print(f"📊 Total leads in database: {total_leads}")
    print()
    
    if total_leads > 0:
        print("✅ You have existing leads!")
        print()
        
        # Group by status
        status_counts = {}
        tenant_counts = {}
        
        for lead in response.data:
            status = lead.get("status", "unknown")
            tenant_id = lead.get("tenant_id", "no_tenant")
            
            status_counts[status] = status_counts.get(status, 0) + 1
            tenant_counts[tenant_id] = tenant_counts.get(tenant_id, 0) + 1
        
        print("By Status:")
        for status, count in sorted(status_counts.items()):
            print(f"  - {status}: {count}")
        
        print()
        print("By Tenant:")
        for tenant, count in sorted(tenant_counts.items()):
            print(f"  - {tenant}: {count}")
        
        print()
        print("Recent leads:")
        # Show most recent 5
        recent = supabase.table("leads").select(
            "customer_name, customer_phone, status, tenant_id, updated_at"
        ).order("updated_at", desc=True).limit(5).execute()
        
        for lead in recent.data:
            print(f"  📞 {lead.get('customer_name', 'Unknown')} ({lead.get('customer_phone', 'N/A')})")
            print(f"     Status: {lead.get('status')} | Tenant: {lead.get('tenant_id', 'none')[:8]}...")
            print(f"     Updated: {lead.get('updated_at', 'N/A')}")
            print()
        
        # Check what the dashboard would see
        dashboard_tenant = "3d01c6f0-7dca-43ea-946c-7509f9a996d1"
        dashboard_query = supabase.table("leads").select("*").eq(
            "tenant_id", dashboard_tenant
        ).in_("status", ["new", "active", "qualified"]).execute()
        
        dashboard_count = len(dashboard_query.data) if dashboard_query.data else 0
        
        print(f"🎯 Dashboard would see: {dashboard_count} leads")
        print(f"   (tenant_id: {dashboard_tenant[:16]}...)")
        print("   (status: new, active, or qualified)")
        
        if dashboard_count == 0:
            print()
            print("⚠️  No leads match the dashboard filters!")
            print("   Possible reasons:")
            print("   - Wrong tenant_id")
            print("   - All leads have status other than 'new', 'active', or 'qualified'")
        
    else:
        print("❌ No leads found in database")
        print()
        print("💡 To create a test lead, use:")
        print("   curl -X POST https://agenzia-ai.vercel.app/api/leads \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"name\": \"Test User\", \"agency\": \"Test Agency\", \"phone\": \"+393331234567\", \"properties\": \"test\"}'")

except Exception as e:
    print(f"❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()
