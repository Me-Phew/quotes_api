from pydantic import BaseSettings


class Settings(BaseSettings):
    API_VERSION: str
    API_TITLE: str
    BASE_URL: str

    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    API_KEY: str

    REDIS_ADDRESS: str
    REDIS_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
