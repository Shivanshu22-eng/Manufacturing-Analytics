"""
ETL Configuration
Reads all settings from environment variables (never hardcoded).
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ETLConfig:
    # Database
    db_host:     str = os.getenv("POSTGRES_HOST",     "localhost")
    db_port:     int = int(os.getenv("POSTGRES_PORT", "5432"))
    db_name:     str = os.getenv("POSTGRES_DB",       "manufacturing_db")
    db_user:     str = os.getenv("POSTGRES_USER",     "mfg_user")
    db_password: str = os.getenv("POSTGRES_PASSWORD", "")

    # Directories
    raw_data_dir: str = os.getenv("ETL_RAW_DATA_DIR", "../data/raw")

    # ETL behaviour
    batch_size:      int = int(os.getenv("ETL_BATCH_SIZE",  "5000"))
    log_level:       str = os.getenv("ETL_LOG_LEVEL",       "INFO")
    truncate_before: bool = os.getenv("ETL_TRUNCATE", "false").lower() == "true"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Singleton
config = ETLConfig()
