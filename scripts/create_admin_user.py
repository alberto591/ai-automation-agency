import os
import sys

from dotenv import load_dotenv
from supabase import Client, create_client

# Work from the root directory
load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment")
    sys.exit(1)

supabase: Client = create_client(url, key)

email = "admin@agenzia.ai"
password = "Password123!"

try:
    print(f"Attempting to register {email}...")
    res = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"data": {"agency_name": "Admin Agency", "phone": "+3900000000"}},
        }
    )

    if res.user:
        print(f"✅ User {email} created successfully!")
        print("Note: Check your email for a confirmation link if email confirmation is enabled.")
    else:
        print("❌ Registration failed. No user returned.")
except Exception as e:
    if "already registered" in str(e).lower():
        print(f"ℹ️ User {email} is already registered.")
    else:
        print(f"❌ Error: {e}")
