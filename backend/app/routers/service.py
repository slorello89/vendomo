"""Service log endpoints powering the service dashboard."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from ..models import ServiceLog, VendingMachine
from ..redis_client import redis_client
from ..schemas import ServiceLogCreate, ServiceLogOut

router = APIRouter(prefix="/api/service", tags=["service"])


@router.get("/logs", response_model=list[ServiceLogOut])
async def list_service_logs(
    session: AsyncSession = Depends(get_session),
    machine_id: uuid.UUID | None = None,
    type: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    stmt = select(ServiceLog).order_by(ServiceLog.created_at.desc())
    if machine_id:
        stmt = stmt.where(ServiceLog.machine_id == machine_id)
    if type:
        stmt = stmt.where(ServiceLog.type == type)
    stmt = stmt.limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return [ServiceLogOut.model_validate(r) for r in rows]


@router.post("/logs", response_model=ServiceLogOut, status_code=201)
async def create_service_log(payload: ServiceLogCreate, session: AsyncSession = Depends(get_session)):
    machine = await session.get(VendingMachine, payload.machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    entry = ServiceLog(
        machine_id=payload.machine_id,
        type=payload.type,
        technician=payload.technician,
        notes=payload.notes,
    )
    session.add(entry)

    # Servicing a machine updates its last-serviced timestamp and clears the
    # "needs service" flag.
    machine.last_serviced_at = func.now()
    if machine.status == "needs_service":
        machine.status = "operational"

    await session.commit()
    await session.refresh(entry)
    await redis_client.delete(settings.map_cache_key)  # map label/visibility changed
    return ServiceLogOut.model_validate(entry)
