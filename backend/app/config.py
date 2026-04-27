from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "AutoGrowth Pro"
    APP_ENV: str = "production"
    SECRET_KEY: str = "change-me-in-production-use-256bit-random"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/autogrowth"
    REDIS_URL: str = "redis://redis:6379/0"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_STARTER: str = ""   # €299/month
    STRIPE_PRICE_GROWTH: str = ""    # €599/month
    STRIPE_PRICE_PRO: str = ""       # €999/month

    # Anthropic (content generation)
    ANTHROPIC_API_KEY: str = ""

    # Email (SMTP)
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "contact@autogrowth.pro"
    FROM_NAME: str = "AutoGrowth Pro"

    # Lead scraping
    GOOGLE_PLACES_API_KEY: str = ""
    HUNTER_IO_API_KEY: str = ""

    # Frontend
    FRONTEND_URL: str = "https://autogrowth.pro"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
