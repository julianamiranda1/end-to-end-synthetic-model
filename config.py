from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    app_name: str = "Santo Garfo API"
    app_version: str = "1.0.0"
    app_description: str = "API do restaurante Santo Garfo"
    debug: bool = False
    max_mesas: int = 20
    max_pessoas_por_mesa: int = 10


settings = Settings()
