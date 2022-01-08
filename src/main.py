from fastapi import FastAPI
from .routers import quotes
from .config import settings
import aioredis

from fastapi_limiter import FastAPILimiter

DESCRIPTION = """
*Made with ♡ and Fastapi*
# [Github repo](https://github.com/Me-Phew/quotes_api)
"""

app = FastAPI(docs_url=settings.QUOTES_API_BASE_URL + '/docs',
              redoc_url=settings.QUOTES_API_BASE_URL + '/redoc',
              openapi_url=settings.QUOTES_API_BASE_URL + '/openapi.json',
              title=settings.QUOTES_API_TITLE,
              version=settings.QUOTES_API_VERSION,
              description=DESCRIPTION)
print(settings)

app.include_router(quotes.router)


@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(settings.QUOTES_API_REDIS_ADDRESS,
                                    encoding="utf-8",
                                    decode_responses=True,
                                    password=settings.QUOTES_API_REDIS_PASSWORD)
    await FastAPILimiter.init(redis)
