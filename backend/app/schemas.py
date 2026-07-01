"""Pydantic request/response schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Vending machines
# ---------------------------------------------------------------------------
class MachineCreate(BaseModel):
    name: str
    model: str = "VendoMax 3000"
    manufacturer: str = "Vendomo"
    status: str = "operational"
    latitude: float
    longitude: float
    address: str = ""
    location_description: str | None = None
    city: str
    region: str
    country: str = "USA"
    capacity: int = 40
    asset_tag: str | None = None


class MachineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_tag: str
    name: str
    model: str
    manufacturer: str
    status: str
    latitude: float
    longitude: float
    address: str
    location_description: str | None
    city: str
    region: str
    country: str
    capacity: int
    installed_at: datetime
    last_serviced_at: datetime | None
    created_at: datetime


class MachineList(BaseModel):
    items: list[MachineOut]
    total: int
    limit: int
    offset: int


class MapMarker(BaseModel):
    """Lightweight projection of a machine for the map layer."""
    id: uuid.UUID
    name: str
    lat: float
    lng: float
    status: str
    label: str


# ---------------------------------------------------------------------------
# Service logs
# ---------------------------------------------------------------------------
class ServiceLogCreate(BaseModel):
    machine_id: uuid.UUID
    type: str = Field(default="inspection", description="refill | repair | inspection")
    technician: str
    notes: str = ""


class ServiceLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    machine_id: uuid.UUID
    type: str
    technician: str
    notes: str
    created_at: datetime


class InventoryItem(BaseModel):
    product: str
    quantity: int = 0


class MachineDetail(MachineOut):
    products: list[InventoryItem] = []
    recent_service_logs: list[ServiceLogOut] = []


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
class StatsOut(BaseModel):
    total_machines: int
    by_status: dict[str, int]
    by_region: dict[str, int]
    needs_service: int
    never_serviced: int
