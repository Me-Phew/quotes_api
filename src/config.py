from pydantic import BaseSettings


class Settings(BaseSettings):
    QUOTES_API_VERSION: str
    QUOTES_API_TITLE: str
    QUOTES_API_BASE_URL: str

    QUOTES_API_DATABASE_USERNAME: str
    QUOTES_API_DATABASE_PASSWORD: str
    QUOTES_API_DATABASE_HOSTNAME: str
    QUOTES_API_DATABASE_PORT: str
    QUOTES_API_DATABASE_NAME: str

    QUOTES_API_KEY: str

    QUOTES_API_REDIS_ADDRESS: str
    QUOTES_API_REDIS_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
