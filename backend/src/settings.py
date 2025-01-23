import logging
import os
from functools import lru_cache
from typing import final

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=(
            "../.prod.env",
            "../.dev.env",
        ),  # first search .dev.env, then .prod.env
        env_file_encoding="utf-8",
    )

    debug: bool = True
    bot_token: str = None

    database_path: str = "/"
    base_dir: str = "/"
    logs_path: str = "/logs"

    username: str = "ADMIN"
    password: str = SecretStr("password")


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    try:
        return Settings()
    except Exception as e:
        logging.error(f"Error while loading settings: {e} path: {os.getcwd()}")
        raise e
