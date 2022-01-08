from fastapi import FastAPI
from .routers import quotes
from .config import settings
import aioredis

from fastapi_limiter import FastAPILimiter

DESCRIPTION = """
*Made with ♡ and Fastapi*
# [Github repo](https://github.com/Me-Phew/quotes_api)
"""

app = FastAPI(docs_url=settings.BASE_URL + '/docs',
              redoc_url=settings.BASE_URL + '/redoc',
              openapi_url=settings.BASE_URL + '/openapi.json',
              title=settings.API_TITLE,
              version=settings.API_VERSION,
              description=DESCRIPTION)
print(settings)

app.include_router(quotes.router)


@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(settings.REDIS_ADDRESS,
                                    encoding="utf-8",
                                    decode_responses=True,
                                    password=settings.REDIS_PASSWORD)
    await FastAPILimiter.init(redis)
