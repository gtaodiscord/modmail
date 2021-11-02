from functools import lru_cache
from os import getenv
from pathlib import Path

from pydantic import BaseModel
from yaml import safe_load


class ModmailConfig(BaseModel):
    token: str
    prefix: str = "!"


@lru_cache()
def get_config() -> ModmailConfig:
    data = safe_load(Path(getenv("CONFIG_LOCATION", "./config.yml")).read_text())

    return ModmailConfig(**data)
