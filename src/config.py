from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = "config"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: PostgresDsn
    kms_key_id: str
    celery_broker_url: str
    celery_result_backend: str
    redis_url: RedisDsn
    headless_url: AnyHttpUrl


config = Settings()
