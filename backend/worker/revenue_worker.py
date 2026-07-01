"""Revenue event generator.

Simulates the vending fleet phoning home with sales. Every machine in the
fleet occasionally "sells" an item; each sale is appended to a Redis Stream as
a single entry. Downstream consumers (analytics, dashboards) read from this
stream and aggregate sales per machine and per region.

Stream:   vendomo:revenue:events   (see VENDOMO_REVENUE_STREAM / config)
Fields per entry:
    machine_id : str (uuid)
    region     : str (US state, e.g. "CA")
    item       : str (product sold)
    amount     : str (USD, e.g. "2.50")
    ts         : str (epoch milliseconds)
"""
import asyncio
import logging
import os
import random
import time

import redis.asyncio as redis
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s worker: %(message)s")
log = logging.getLogger("vendomo.worker")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://vendomo:vendomo@postgres:5432/vendomo")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
STREAM = os.getenv("VENDOMO_REVENUE_STREAM", "vendomo:revenue:events")
STREAM_MAXLEN = int(os.getenv("VENDOMO_REVENUE_STREAM_MAXLEN", "50000"))
EVENTS_PER_SEC = float(os.getenv("VENDOMO_REVENUE_EVENTS_PER_SEC", "8"))
RELOAD_EVERY_SEC = int(os.getenv("VENDOMO_REVENUE_RELOAD_SEC", "60"))

ITEMS = [
    ("Cola", 2.00), ("Diet Cola", 2.00), ("Spring Water", 1.50), ("Sparkling Water", 1.75),
    ("Energy Drink", 3.50), ("Iced Coffee", 3.00), ("Potato Chips", 1.75), ("Pretzels", 1.50),
    ("Chocolate Bar", 2.25), ("Granola Bar", 2.00), ("Trail Mix", 2.75), ("Gum", 1.25),
    ("Fruit Snacks", 1.75), ("Cookies", 2.25), ("Protein Bar", 3.25),
]

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def _wait_for_db(retries: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except Exception as exc:  # noqa: BLE001
            log.warning("Postgres not ready (%s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)
    raise RuntimeError("Postgres did not become ready")


async def _load_machines() -> list[tuple[str, str]]:
    async with Session() as session:
        rows = await session.execute(text("SELECT id, region FROM vending_machines"))
        return [(str(mid), region) for mid, region in rows.all()]


async def main() -> None:
    await _wait_for_db()
    r = redis.from_url(REDIS_URL, decode_responses=True)

    # The backend owns the schema: it creates the tables and seeds the fleet in
    # its startup lifespan. The worker may win the boot race and connect before
    # that finishes, so tolerate "table doesn't exist yet" / "no rows yet" and
    # keep polling until the fleet shows up.
    machines: list[tuple[str, str]] = []
    while not machines:
        try:
            machines = await _load_machines()
        except Exception as exc:  # noqa: BLE001 — table not created/seeded yet
            log.info("Fleet not ready (%s) — waiting for backend to create/seed tables...", type(exc).__name__)
            machines = []
        if not machines:
            await asyncio.sleep(3)

    log.info("Revenue worker live: %s machines, ~%.0f events/sec -> %s", len(machines), EVENTS_PER_SEC, STREAM)
    rng = random.Random()
    last_reload = time.monotonic()
    interval = 1.0 / max(EVENTS_PER_SEC, 0.1)

    while True:
        mid, region = rng.choice(machines)
        item, price = rng.choice(ITEMS)
        await r.xadd(
            STREAM,
            {
                "machine_id": mid,
                "region": region,
                "item": item,
                "amount": f"{price:.2f}",
                "ts": str(int(time.time() * 1000)),
            },
            maxlen=STREAM_MAXLEN,
            approximate=True,
        )
        await asyncio.sleep(interval)

        if time.monotonic() - last_reload > RELOAD_EVERY_SEC:
            try:
                refreshed = await _load_machines()
                if refreshed:
                    machines = refreshed
            except Exception as exc:  # noqa: BLE001 — keep running on transient errors
                log.warning("Machine reload failed (%s) — keeping current list", type(exc).__name__)
            last_reload = time.monotonic()


if __name__ == "__main__":
    asyncio.run(main())
