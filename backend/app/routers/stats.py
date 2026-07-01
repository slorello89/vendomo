"""Fleet-wide aggregate stats for the dashboards/header."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import VendingMachine
from ..schemas import StatsOut

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
async def get_stats(session: AsyncSession = Depends(get_session)):
    total = await session.scalar(select(func.count()).select_from(VendingMachine)) or 0

    status_rows = await session.execute(
        select(VendingMachine.status, func.count()).group_by(VendingMachine.status)
    )
    by_status = {status: count for status, count in status_rows.all()}

    region_rows = await session.execute(
        select(VendingMachine.region, func.count())
        .group_by(VendingMachine.region)
        .order_by(func.count().desc())
    )
    by_region = {region: count for region, count in region_rows.all()}

    never_serviced = await session.scalar(
        select(func.count())
        .select_from(VendingMachine)
        .where(VendingMachine.last_serviced_at.is_(None))
    ) or 0

    return StatsOut(
        total_machines=total,
        by_status=by_status,
        by_region=by_region,
        needs_service=by_status.get("needs_service", 0),
        never_serviced=never_serviced,
    )
