from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rafam_workflow.db"
    storage_base_dir: str = "storage"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
