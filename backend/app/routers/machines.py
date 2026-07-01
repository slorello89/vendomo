"""Vending machine endpoints: list, map, detail, ingest."""
import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db import get_session
from ..models import ServiceLog, VendingMachine
from ..redis_client import redis_client
from ..schemas import (
    MachineCreate,
    MachineDetail,
    MachineList,
    MachineOut,
    MapMarker,
    ServiceLogOut,
)

log = logging.getLogger("vendomo.machines")
router = APIRouter(prefix="/api/machines", tags=["machines"])


@router.get("", response_model=MachineList)
async def list_machines(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: str | None = None,
    region: str | None = None,
    q: str | None = None,
):
    stmt = select(VendingMachine)
    count_stmt = select(func.count()).select_from(VendingMachine)
    if status:
        stmt = stmt.where(VendingMachine.status == status)
        count_stmt = count_stmt.where(VendingMachine.status == status)
    if region:
        stmt = stmt.where(VendingMachine.region == region)
        count_stmt = count_stmt.where(VendingMachine.region == region)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(VendingMachine.name.ilike(like))
        count_stmt = count_stmt.where(VendingMachine.name.ilike(like))

    total = await session.scalar(count_stmt)
    stmt = stmt.order_by(VendingMachine.asset_tag).limit(limit).offset(offset)
    rows = (await session.execute(stmt)).scalars().all()
    return MachineList(
        items=[MachineOut.model_validate(m) for m in rows],
        total=total or 0,
        limit=limit,
        offset=offset,
    )


def _serialize_marker(m: VendingMachine) -> dict:
    """Build the popup label + marker payload for a single machine."""
    # Human-friendly "last serviced" string for the map popup.
    last_serviced = m.last_serviced_at.strftime("%b %d, %Y")
    return {
        "id": str(m.id),
        "name": m.name,
        "lat": m.latitude,
        "lng": m.longitude,
        "status": m.status,
        "label": f"{m.name} — last serviced {last_serviced}",
    }


@router.get("/map", response_model=list[MapMarker])
async def machines_map(session: AsyncSession = Depends(get_session)):
    """All machines projected down to map markers (cached in Redis)."""
    cached = await redis_client.get(settings.map_cache_key)
    if cached is not None:
        return json.loads(cached)

    rows = (await session.execute(select(VendingMachine))).scalars().all()
    markers: list[dict] = []
    for m in rows:
        try:
            markers.append(_serialize_marker(m))
        except Exception as e:
            # Be defensive: one malformed record shouldn't blow up the whole map.
            continue

    await redis_client.set(settings.map_cache_key, json.dumps(markers), ex=settings.map_cache_ttl)
    return markers


@router.get("/{machine_id}", response_model=MachineDetail)
async def get_machine(machine_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    machine = await session.get(VendingMachine, machine_id)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    logs = (
        await session.execute(
            select(ServiceLog)
            .where(ServiceLog.machine_id == machine_id)
            .order_by(ServiceLog.created_at.desc())
            .limit(20)
        )
    ).scalars().all()
    detail = MachineDetail.model_validate(machine)
    detail.recent_service_logs = [ServiceLogOut.model_validate(log_) for log_ in logs]
    return detail


@router.post("", response_model=MachineOut, status_code=201)
async def create_machine(payload: MachineCreate, session: AsyncSession = Depends(get_session)):
    machine = VendingMachine(
        asset_tag=payload.asset_tag or f"VM-{uuid.uuid4().hex[:8].upper()}",
        name=payload.name,
        model=payload.model,
        manufacturer=payload.manufacturer,
        status=payload.status,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address=payload.address,
        location_description=payload.location_description,
        city=payload.city,
        region=payload.region,
        country=payload.country,
        capacity=payload.capacity,
        installed_at=func.now(),
        last_serviced_at=None,
    )
    session.add(machine)
    await session.commit()
    await session.refresh(machine)
    await redis_client.delete(settings.map_cache_key)  # invalidate map cache
    return MachineOut.model_validate(machine)


@router.post("/bulk", status_code=201)
async def create_machines_bulk(
    payload: list[MachineCreate], session: AsyncSession = Depends(get_session)
):
    created = 0
    for item in payload:
        session.add(
            VendingMachine(
                asset_tag=item.asset_tag or f"VM-{uuid.uuid4().hex[:8].upper()}",
                name=item.name,
                model=item.model,
                manufacturer=item.manufacturer,
                status=item.status,
                latitude=item.latitude,
                longitude=item.longitude,
                address=item.address,
                location_description=item.location_description,
                city=item.city,
                region=item.region,
                country=item.country,
                capacity=item.capacity,
                installed_at=func.now(),
                last_serviced_at=None,
            )
        )
        created += 1
    await session.commit()
    await redis_client.delete(settings.map_cache_key)
    return {"created": created}
