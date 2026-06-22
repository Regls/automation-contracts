import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    ZAPSIGN_URL: str = os.getenv("ZAPSIGN_URL")
    ZAPSIGN_API_KEY: str = os.getenv("ZAPSIGN_API_KEY")

    @classmethod
    def validate(cls):
        if not cls.SUPABASE_URL or not cls.SUPABASE_SERVICE_KEY:
            raise ValueError("❌ Environment variables for supabase are not set")
        if not cls.ZAPSIGN_URL or not cls.ZAPSIGN_API_KEY:
            raise ValueError("❌ Environment variables for zapsign are not set")

settings = Settings()
