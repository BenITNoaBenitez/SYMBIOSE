from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    environment: str = "production"
    debug: bool = False
    allowed_hosts: str = "100.64.0.1"

    # Database
    database_url: str

    # Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8

    # LLM — paliers
    anthropic_api_key: str
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_light: str = "mistral:7b"

    # Langfuse
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_host: str = "http://langfuse-server:3000"

    # Daytona (optionnel)
    daytona_api_key: Optional[str] = None

    # Schedule
    access_start_hour: int = 7
    access_end_hour: int = 19

    class Config:
        env_file = ".env"


settings = Settings()
