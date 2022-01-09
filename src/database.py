from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f'postgresql://' \
                          f'{settings.QUOTES_API_DATABASE_USERNAME}:' \
                          f'"{settings.QUOTES_API_DATABASE_PASSWORD}"@' \
                          f'{settings.QUOTES_API_DATABASE_HOSTNAME}:' \
                          f'{settings.QUOTES_API_DATABASE_PORT}/' \
                          f'{settings.QUOTES_API_DATABASE_NAME}'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
