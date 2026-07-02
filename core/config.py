import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY     = os.getenv("SECRET_KEY", "dev-secret-change-me")
    REDIS_URL      = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL      = int(os.getenv("CACHE_TTL_SECONDS", 3600))
    DEBUG          = os.getenv("APP_ENV", "development") == "development"
