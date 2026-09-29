"""
Application settings — all values from environment variables.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    postgres_host:     str = "localhost"
    postgres_port:     int = 5432
    postgres_db:       str = "manufacturing_db"
    postgres_user:     str = "mfg_user"
    postgres_password: str = ""

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
