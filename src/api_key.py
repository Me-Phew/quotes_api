from .config import settings
from .exceptions import InvalidApiKeyException
from fastapi import Depends
from fastapi.security import APIKeyHeader

api_key_scheme = APIKeyHeader(name='x-api-key')


def verify_api_key(api_key: str, invalid_credentials_exception) -> bool:
    if api_key == settings.QUOTES_API_KEY:
        return True
    else:
        raise invalid_credentials_exception


def authorize_client(api_key: str = Depends(api_key_scheme)) -> bool:

    return verify_api_key(api_key, InvalidApiKeyException)
