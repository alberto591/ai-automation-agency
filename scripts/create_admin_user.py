import os
import sys

from dotenv import load_dotenv
from supabase import Client, create_client

# Load env variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    print("Please ensure you have the SERVICE_ROLE_KEY (not just anon key) in your .env file.")
    sys.exit(1)

supabase: Client = create_client(url, key)


def create_user():
    email = "admin@agenzia.ai"
    password = "Password123!"

    print(f"Creating user: {email}...")

    try:
        # Create user with auto-confirmation
        response = supabase.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        print("\n✅ Admin User Created Successfully!")
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print(
            "\n👉 You can use these credentials to log in to the dashboard locally or in production."
        )

    except Exception as e:
        print(f"\n❌ Failed to create user: {e}")
        print("Note: If the user already exists, try logging in with the existing password.")


if __name__ == "__main__":
    create_user()
