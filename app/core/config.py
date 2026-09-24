from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Ayadi Cloudversity API"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str
    DIRECT_URL: str

    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str

    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()