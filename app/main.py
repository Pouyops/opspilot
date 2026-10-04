from contextlib import asynccontextmanager

from app.routers import tickets

import redis.asyncio as aioredis
from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.db import engine

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # app runs here
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title="OpsPilot", lifespan=lifespan)
app.include_router(tickets.router)

@app.get("/health")
async def health():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    await redis_client.ping()
    return {"status": "ok"}
