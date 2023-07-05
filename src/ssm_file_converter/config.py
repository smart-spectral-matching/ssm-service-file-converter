from pydantic import BaseSettings
from .version import __version__


class Settings(BaseSettings):
    project_name: str = "SSM File Converter Service"
    project_version: str = __version__


settings = Settings()
