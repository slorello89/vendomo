"""SQLAlchemy ORM models for the Vendomo fleet."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class VendingMachine(Base):
    __tablename__ = "vending_machines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    model: Mapped[str] = mapped_column(String(64))
    manufacturer: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), index=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str] = mapped_column(String(256))
    # Free-text "where inside the venue", e.g. "In the back by the pinball machines".
    location_description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    city: Mapped[str] = mapped_column(String(128), index=True)
    region: Mapped[str] = mapped_column(String(64), index=True)  # US state
    country: Mapped[str] = mapped_column(String(64), default="USA")

    capacity: Mapped[int] = mapped_column(Integer, default=40)
    # What this machine stocks: [{"product": "Cola", "quantity": 7}, ...]
    products: Mapped[list] = mapped_column(JSONB, default=list)
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Nullable on purpose: a freshly installed machine has never been serviced.
    last_serviced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    service_logs: Mapped[list["ServiceLog"]] = relationship(
        back_populates="machine", cascade="all, delete-orphan", order_by="ServiceLog.created_at.desc()"
    )


class ServiceLog(Base):
    __tablename__ = "service_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vending_machines.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(32))  # refill | repair | inspection
    technician: Mapped[str] = mapped_column(String(128))
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    machine: Mapped["VendingMachine"] = relationship(back_populates="service_logs")
