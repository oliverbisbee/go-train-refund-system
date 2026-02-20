from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENMETROLINX_API_KEY: str
    GTFS_REALTIME_URL: str
    GTFS_STATIC_URL: str
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()