from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud Banking API"
    ENV: str = "development"

    # local development
    DATABASE_URL: str | None = None

    # Cloud Run variables (Terraform provides these)
    DB_HOST: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    GCP_PROJECT_ID: str
    PUBSUB_TOPIC_TRANSACTIONS: str = "transaction-events"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

    @property
    def database_url(self):

        # If DATABASE_URL exists (local development)
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Otherwise build Cloud SQL connection
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@/{self.DB_NAME}?unix_socket=/cloudsql/{self.DB_HOST}"
        )


settings = Settings()