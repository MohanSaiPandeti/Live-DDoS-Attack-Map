from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ABUSEIPDB_API_KEY: str = ""
    ABUSEIPDB_CONFIDENCE_THRESHOLD: int = 80
    ABUSEIPDB_LIMIT: int = 100
    CLOUDFLARE_API_TOKEN: str = ""
    GEO_API_BASE: str = "http://ip-api.com/json"
    ATTACK_POLL_INTERVAL: int = 60
    TRENDS_POLL_INTERVAL: int = 300

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()