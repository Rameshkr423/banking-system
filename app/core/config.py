from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud Banking API"
    ENV: str = "development"

    DATABASE_URL: str
    GCP_PROJECT_ID: str
    PUBSUB_TOPIC_TRANSACTIONS: str = "transaction-events"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
