import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    ZAPSIGN_URL: str = os.getenv("ZAPSIGN_URL")
    ZAPSIGN_API_KEY: str = os.getenv("ZAPSIGN_API_KEY")
    MAILTRAP_HOST: str = os.getenv("MAILTRAP_SMTP_HOST")
    MAILTRAP_PORT: int = int(os.getenv("MAILTRAP_SMTP_PORT", 2525))
    MAILTRAP_USER: str = os.getenv("MAILTRAP_SMTP_USER")
    MAILTRAP_PASSWORD: str = os.getenv("MAILTRAP_SMTP_PASSWORD")
    EVOLUTION_API_URL: str = os.getenv("EVOLUTION_API_URL")
    EVOLUTION_INSTANCE: str = os.getenv("EVOLUTION_INSTANCE")
    EVOLUTION_API_KEY: str = os.getenv("EVOLUTION_API_PASSWORD")

    @classmethod
    def validate(cls):
        if not cls.SUPABASE_URL or not cls.SUPABASE_SERVICE_KEY:
            raise ValueError("❌ Environment variables for supabase are not set")
        if not cls.ZAPSIGN_URL or not cls.ZAPSIGN_API_KEY:
            raise ValueError("❌ Environment variables for zapsign are not set")
        if not cls.MAILTRAP_HOST or not cls.MAILTRAP_PORT or not cls.MAILTRAP_USER or not cls.MAILTRAP_PASSWORD:
            raise ValueError("❌ Environment variables for mailtrap are not set")
        if not cls.EVOLUTION_API_URL or not cls.EVOLUTION_INSTANCE or not cls.EVOLUTION_API_KEY:
            raise ValueError("❌ Environment variables for evolutionapi are not set")

settings = Settings()
