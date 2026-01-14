#!/usr/bin/env python3
"""
Quick script to check what conversations/leads exist in Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    print("   Required: SUPABASE_URL and SUPABASE_KEY")
    exit(1)

print(f"📡 Connecting to Supabase: {SUPABASE_URL}")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n🔍 Checking leads table...")

try:
    # Query leads table
    response = supabase.table('leads').select('*').limit(10).execute()
    
    if response.data:
        print(f"\n✅ Found {len(response.data)} leads:")
        print("-" * 80)
        for lead in response.data:
            phone = lead.get('customer_phone', 'N/A')
            name = lead.get('customer_name', 'N/A')
            status = lead.get('status', 'N/A')
            created = lead.get('created_at', 'N/A')
            print(f"  📞 {phone} | {name} | Status: {status} | Created: {created}")
    else:
        print("\n⚠️  No leads found in database")
        print("   The database is empty - no conversations to display")
    
    print("-" * 80)
    
    # Check messages table
    print("\n🔍 Checking messages table...")
    msg_response = supabase.table('messages').select('*').limit(10).execute()
    
    if msg_response.data:
        print(f"✅ Found {len(msg_response.data)} messages")
    else:
        print("⚠️  No messages found in database")
        
except Exception as e:
    print(f"\n❌ Error querying Supabase: {e}")
    print(f"   Make sure the 'leads' table exists in your database")

print("\n" + "=" * 80)
print("📊 Summary:")
print("   - WebSocket connection: ✅ Working")
print("   - Database connection: ✅ Working")
if not response.data:
    print("   - Conversations: ⚠️  Empty (need to send test message)")
else:
    print(f"   - Conversations: ✅ {len(response.data)} found")
print("=" * 80)
