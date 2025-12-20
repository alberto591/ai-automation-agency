import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # --- Supabase ---
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # --- AI Models ---
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    
    # --- Twilio ---
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # --- Security ---
    WEBHOOK_API_KEY = os.getenv("WEBHOOK_API_KEY", "prod_dev_secret_key_2025")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    
    # --- Agency Settings ---
    AGENCY_OWNER_PHONE = os.getenv("AGENCY_OWNER_PHONE", "+39000000000")
    TAKEOVER_EXPIRY_HOURS = int(os.getenv("TAKEOVER_EXPIRY_HOURS", "24"))
    
    # --- Email (SMTP) ---
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    
    # --- Validation ---
    @classmethod
    def validate(cls):
        required = [
            "SUPABASE_URL", "SUPABASE_KEY", 
            "MISTRAL_API_KEY", 
            "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"
        ]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

config = Config
