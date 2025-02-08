from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "StockWave"
    debug: bool = False
    redis_url: str = "redis://localhost"

settings = Settings()