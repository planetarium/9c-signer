from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    PostgresDsn = str
    RedisDsn = str
else:
    from pydantic import PostgresDsn, RedisDsn


__all__ = "config"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: PostgresDsn
    kms_key_id: str
    aws_default_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    celery_broker_url: str
    celery_result_backend: str
    redis_url: RedisDsn


config = Settings()
