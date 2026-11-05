from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "etldb"
    db_user: str = "etl"
    db_password: str = "etl123"

    etl_input: str = "clientes.csv"
    etl_target: Literal["postgres", "sqlite", "parquet"] = "sqlite"
    etl_table: str = "clientes"
    etl_mode: Literal["replace", "append", "upsert"] = "upsert"
    etl_sqlite_path: str = "etl.db"
    etl_parquet_dir: str = "output"
    etl_snapshots_dir: str = "snapshots"
    etl_rejected_dir: str = "rejected"
    etl_logs_dir: str = "logs"

    etl_validate_mx: bool = False
    etl_detect_anomalies: bool = True
    etl_anomaly_zscore: float = 3.0

    etl_cron: str = "0 */6 * * *"

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.etl_sqlite_path}"

    def ensure_dirs(self) -> None:
        for d in (self.etl_logs_dir, self.etl_rejected_dir, self.etl_snapshots_dir, self.etl_parquet_dir):
            Path(d).mkdir(parents=True, exist_ok=True)


settings = Settings()
