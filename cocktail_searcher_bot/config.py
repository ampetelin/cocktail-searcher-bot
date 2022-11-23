import logging
from typing import Optional

import sentry_sdk
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    TELEGRAM_API_TOKEN: str
    LOG_LEVEL: str = 'INFO'
    COCKTAIL_SEARCHER_URL: AnyHttpUrl
    COCKTAIL_SEARCHER_API_TOKEN: str
    SENTRY_DSN: Optional[AnyHttpUrl]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()

logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s', level=settings.LOG_LEVEL)

sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)
