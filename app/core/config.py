import os
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud Banking API"
    ENV: str = "development"

    DATABASE_URL: str | None = None

    DB_HOST: str | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    GCP_PROJECT_ID: str = "unknown"
    PUBSUB_TOPIC_TRANSACTIONS: str = "transaction-events"

    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env" if os.getenv("ENV", "development") != "production" else None

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        missing = [k for k, v in {
            "DB_HOST": self.DB_HOST,
            "DB_USER": self.DB_USER,
            "DB_PASSWORD": self.DB_PASSWORD,
            "DB_NAME": self.DB_NAME,
        }.items() if not v]

        if missing:
            raise ValueError(f"Missing DB env vars: {missing}. ENV={self.ENV}")

        password = quote_plus(self.DB_PASSWORD)

        # NOTE: For production Unix socket, engine is built in session.py
        # using connect_args={"unix_socket": ...} — NOT in the URL string.
        # PyMySQL ignores unix_socket when passed as a query parameter.
        if self.ENV == "production":
            return (
                f"mysql+pymysql://{self.DB_USER}:{password}@/{self.DB_NAME}"
            )

        return (
            f"mysql+pymysql://{self.DB_USER}:{password}"
            f"@{self.DB_HOST}:3306/{self.DB_NAME}"
        )


settings = Settings()