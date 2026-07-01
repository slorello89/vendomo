"""Vendomo API entrypoint."""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .db import Base, SessionLocal, engine
from .redis_client import redis_client
from .routers import machines, service, stats
from .seed import seed_if_empty

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("vendomo")


async def _wait_for_db(retries: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except Exception as exc:  # noqa: BLE001
            log.warning("Postgres not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)
    raise RuntimeError("Postgres did not become ready in time")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.seed_on_startup:
        async with SessionLocal() as session:
            await seed_if_empty(session)
    try:
        await redis_client.ping()
        log.info("Connected to Redis.")
    except Exception as exc:  # noqa: BLE001
        log.warning("Redis ping failed: %s", exc)
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title="Vendomo API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(machines.router)
app.include_router(service.router)
app.include_router(stats.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
