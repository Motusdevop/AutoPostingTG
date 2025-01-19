import logging
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import final


@final
class Settings(BaseSettings):

        model_config = SettingsConfigDict(
            env_file=('../.prod.env', '../.dev.env'),  # first search .dev.env, then .prod.env
            env_file_encoding='utf-8')

        debug: bool = True
        bot_token: str = None
        database_name: str = 'db'

        username: str = "ADMIN"
        password: str = SecretStr('password')

        # redis_url: str = 'redis://localhost:6379/0'
        # base_webhook_url: str = 'https://my.host.name'
        # webhook_path: str = '/path/to/webhook'
        # telegram_my_token: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # Additional security token for webhook



@lru_cache()  # get it from memory
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        logging.error(f'Error while loading settings: {e} path: {os.getcwd()}')
        raise e