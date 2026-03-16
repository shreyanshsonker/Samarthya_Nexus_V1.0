from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str = "localhost"
    
    INFLUXDB_URL: str
    INFLUXDB_TOKEN: str
    INFLUXDB_ORG: str
    INFLUXDB_BUCKET: str

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    INVERTER_BRAND: str = "mock"
    USE_MOCK: bool = True

    GROWATT_USER: str = ""
    GROWATT_PASS: str = ""
    SMA_CLIENT_ID: str = ""
    SMA_SECRET: str = ""
    ELECTRICITY_MAPS_TOKEN: str = ""

    # ML Pipeline settings
    ML_MODELS_DIR: str = "models"
    ML_TRAINING_INTERVAL_HOURS: int = 4
    ML_FORECAST_CACHE_TTL_HOURS: int = 4
    ML_MAE_WARN_THRESHOLD: float = 0.6

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
