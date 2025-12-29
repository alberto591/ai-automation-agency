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

    # LLM Context
    MAX_CONTEXT_MESSAGES: int = Field(default=10)

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

    # Agency Details
    AGENCY_OWNER_PHONE: str = Field(default="")
    AGENCY_OWNER_EMAIL: str = Field(default="")

    # Email / SMTP
    SMTP_SERVER: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")

    # External APIs
    RAPIDAPI_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
