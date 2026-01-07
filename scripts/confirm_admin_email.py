import os
import sys

from dotenv import load_dotenv
from supabase import Client, create_client

# Work from the root directory
load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")  # Need service role key for this

if not url or not service_key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in environment")
    print("\nTo confirm the user manually:")
    print("1. Go to Supabase Dashboard -> Authentication -> Users")
    print("2. Find admin@agenzia.ai")
    print("3. Click the three dots -> 'Confirm email'")
    sys.exit(1)

supabase: Client = create_client(url, service_key)

email = "admin@agenzia.ai"

try:
    # Get user by email
    response = supabase.auth.admin.list_users()

    user = None
    for u in response:
        if u.email == email:
            user = u
            break

    if not user:
        print(f"❌ User {email} not found")
        sys.exit(1)

    # Update user to confirm email
    supabase.auth.admin.update_user_by_id(user.id, {"email_confirm": True})

    print(f"✅ Email confirmed for {email}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAlternative: Confirm manually in Supabase Dashboard")
    print("1. Go to Authentication -> Users")
    print("2. Find admin@agenzia.ai")
    print("3. Click three dots -> 'Confirm email'")
