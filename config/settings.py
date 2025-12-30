from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str | None = Field(default=None)

    # Mistral AI
    MISTRAL_API_KEY: str = Field(default="")
    MISTRAL_MODEL: str = Field(default="mistral-large-latest")
    MISTRAL_EMBEDDING_MODEL: str = Field(default="mistral-embed")

    # WhatsApp Messaging
    WHATSAPP_PROVIDER: str = Field(default="twilio")  # or "meta"

    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(default="")
    TWILIO_AUTH_TOKEN: str = Field(default="")
    TWILIO_PHONE_NUMBER: str = Field(default="")

    # Meta Cloud API
    META_ACCESS_TOKEN: str = Field(default="")
    META_PHONE_ID: str = Field(default="")

    # Security
    WEBHOOK_API_KEY: str = Field(default="")
    WEBHOOK_BASE_URL: str = Field(default="")

    # LLM Context
    MAX_CONTEXT_MESSAGES: int = Field(default=10)

    # Rate Limiting
    MESSAGE_RATE_LIMIT: int = Field(default=20)  # Max messages per window
    MESSAGE_RATE_WINDOW_SECONDS: int = Field(default=60)  # Time window in seconds

    # Google Calendar
    GOOGLE_CALENDAR_ID: str = Field(default="")
    GOOGLE_SERVICE_ACCOUNT_JSON: str = Field(default="")
    # Cal.com
    CALCOM_API_KEY: str = Field(default="")
    CALCOM_EVENT_TYPE_ID: str = Field(default="")  # Get from Cal.com dashboard
    CALCOM_WEBHOOK_SECRET: str = Field(default="")
    CALCOM_BOOKING_LINK: str = Field(default="https://cal.com/anzevino-ai")

    # Monitoring (Sentry)
    SENTRY_DSN: str = Field(default="")
    ENVIRONMENT: str = Field(default="development")

    # Google Sheets
    GOOGLE_SHEET_ID: str = Field(default="")
    GOOGLE_SHEETS_CREDENTIALS_JSON: str = Field(default="")

    # Agency Details
    AGENCY_OWNER_PHONE: str = Field(default="")
    AGENCY_OWNER_EMAIL: str = Field(default="")

    # Email / SMTP
    SMTP_SERVER: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")

    # Email / IMAP (Ingestion)
    IMAP_SERVER: str = Field(default="imap.gmail.com")
    IMAP_EMAIL: str = Field(default="")
    IMAP_PASSWORD: str = Field(default="")

    # External APIs
    RAPIDAPI_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
