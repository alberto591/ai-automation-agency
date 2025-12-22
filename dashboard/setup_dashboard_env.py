import os

from dotenv import load_dotenv

# Load root .env
load_dotenv("../.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

env_content = f"""VITE_SUPABASE_URL={url}
VITE_SUPABASE_ANON_KEY={key}
"""

with open(".env", "w") as f:
    f.write(env_content)

print("✅ Created dashboard/.env with Supabase keys.")
