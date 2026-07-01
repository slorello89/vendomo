"""Idempotent fleet seeding, run once on startup."""
import logging
import random

from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import ServiceLog, VendingMachine
from .seed_data import generate_machines, generate_service_logs

log = logging.getLogger("vendomo.seed")

_BATCH = 2000


async def seed_if_empty(session: AsyncSession) -> None:
    existing = await session.scalar(select(func.count()).select_from(VendingMachine))
    if existing and existing > 0:
        log.info("Fleet already has %s machines — skipping seed.", existing)
        return

    count = settings.seed_count
    log.info("Seeding %s vending machines...", count)
    rng = random.Random(42)  # stable across restarts

    machines = generate_machines(count, rng)
    for start in range(0, len(machines), _BATCH):
        batch = machines[start : start + _BATCH]
        await session.execute(insert(VendingMachine), batch)
        await session.commit()
        log.info("  inserted %s/%s machines", min(start + _BATCH, len(machines)), len(machines))

    logs = generate_service_logs(machines, rng)
    for start in range(0, len(logs), _BATCH):
        batch = logs[start : start + _BATCH]
        await session.execute(insert(ServiceLog), batch)
        await session.commit()
    log.info("Seed complete: %s machines, %s service logs.", len(machines), len(logs))
