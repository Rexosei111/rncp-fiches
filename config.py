from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    db_url: str

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


BASE_URL = "https://www.data.gouv.fr/fr/datasets/repertoire-national-des-certifications-professionnelles-et-repertoire-specifique/"
DL_BASE_URL = "https://www.data.gouv.fr/fr/datasets/r/"
