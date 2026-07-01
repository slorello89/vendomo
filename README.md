# Vendomo

Fleet management for vending machines. Vendomo gives operations teams a single
place to see where every machine is, what state it's in, and what's been
serviced recently — plus tooling to onboard new machines into the fleet.

## Stack

| Layer      | Tech                                  |
| ---------- | ------------------------------------- |
| Frontend   | React + Vite + TypeScript + Leaflet   |
| API        | FastAPI (Python 3.12)                 |
| Database   | PostgreSQL 16                         |
| Cache/bus  | Redis 7 (map cache + revenue stream)  |
| Worker     | Async revenue-event generator         |

## Quick start

```bash
cp .env.example .env        # optional — sensible defaults are built in
docker compose up --build
```

Then open:

- **App:** http://localhost:5173
- **API docs (Swagger):** http://localhost:8000/docs

On first boot the API seeds the fleet with **1,000 vending machines** scattered
across ~30 US metros, plus historical service logs. Data persists in a Postgres
volume across restarts (the seed only runs when the table is empty).

### Reseeding / scaling the fleet

The fleet size is controlled by `SEED_COUNT`. To reseed from scratch, drop the
volume first:

```bash
docker compose down -v
SEED_COUNT=5000 docker compose up --build
```

## Services & ports

| Service    | Port  | Notes                                            |
| ---------- | ----- | ------------------------------------------------ |
| frontend   | 5173  | Vite dev server (proxies `/api` → backend)       |
| backend    | 8000  | FastAPI; `/docs` for Swagger                     |
| postgres   | 5432  | user/pass/db all `vendomo`                       |
| redis      | 6379  | cache + streams                                  |
| worker     | —     | pushes simulated sales to a Redis stream         |

## Project layout

```
vendomo/
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + lifespan (table create + seed)
│   │   ├── config.py          # env-driven settings
│   │   ├── db.py              # async SQLAlchemy engine/session
│   │   ├── redis_client.py    # shared async Redis client
│   │   ├── models.py          # VendingMachine, ServiceLog
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── seed.py            # idempotent startup seeding
│   │   ├── seed_data.py       # random fleet generator
│   │   └── routers/
│   │       ├── machines.py    # list / map / detail / ingest
│   │       ├── service.py     # service logs
│   │       └── stats.py       # fleet aggregates
│   └── worker/
│       └── revenue_worker.py  # simulated sales → Redis stream
└── frontend/
    └── src/                   # React app (map, list, detail, ingest, service)
```

## API reference

Base URL: `http://localhost:8000`

| Method | Path                       | Description                              |
| ------ | -------------------------- | ---------------------------------------- |
| GET    | `/api/health`              | Liveness check                           |
| GET    | `/api/machines`            | Paginated list (`limit/offset/status/region/q`) |
| GET    | `/api/machines/map`        | Lightweight markers for the map (cached) |
| GET    | `/api/machines/{id}`       | Machine detail + recent service logs     |
| POST   | `/api/machines`            | Create a single machine                  |
| POST   | `/api/machines/bulk`       | Create many machines (JSON array)        |
| GET    | `/api/service/logs`        | Service log feed (`machine_id/type`)     |
| POST   | `/api/service/logs`        | Record a service visit                   |
| GET    | `/api/stats`               | Counts by status / region, totals        |

## Fleet telemetry stream

The `worker` service simulates machines reporting sales. Each sale is appended
to the Redis stream **`vendomo:revenue:events`** with fields:

```
machine_id  region  item  amount  ts(epoch-ms)
```

Inspect it directly:

```bash
docker compose exec redis redis-cli XINFO STREAM vendomo:revenue:events
docker compose exec redis redis-cli XREVRANGE vendomo:revenue:events + - COUNT 5
```
