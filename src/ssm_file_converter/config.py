from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "SSM File Converter Service"
    project_version: str = "0.0.0"


settings = Settings()
