"""Deterministic-ish random data generation for the Vendomo fleet.

Machines are scattered around real US metro centroids with a little jitter so
the map looks plausible and so geospatial clustering (Phase 3) is meaningful.
Intentionally dependency-free and fast so a 100k seed stays snappy.
"""
import random
import uuid
from collections import namedtuple
from datetime import datetime, timedelta, timezone

# A metro centroid plus an (optionally asymmetric) jitter box in degrees:
# dlat_s/dlat_n = how far south/north a pin may fall, dlng_w/dlng_e = west/east.
Metro = namedtuple("Metro", "city state lat lng dlat_s dlat_n dlng_w dlng_e")

# Default half-spread (~5 km) — keeps a metro's pins clustered tightly downtown.
_D = 0.05


def _m(city, state, lat, lng, *, dlat_s=_D, dlat_n=_D, dlng_w=_D, dlng_e=_D) -> Metro:
    """Build a metro. Coastal/riverfront cities bias the box away from the water
    (and the next state over) so pins don't land in a lake, bay, or river."""
    return Metro(city, state, lat, lng, dlat_s, dlat_n, dlng_w, dlng_e)


METROS: list[Metro] = [
    # --- water/border-constrained metros (box biased onto land) ---
    _m("New York", "NY", 40.7128, -74.0060, dlat_s=0.05, dlat_n=0.09, dlng_w=0.00, dlng_e=0.10),   # Hudson W -> NJ
    _m("Chicago", "IL", 41.8781, -87.6298, dlat_s=0.11, dlat_n=0.11, dlng_w=0.14, dlng_e=0.00),     # Lake Michigan E
    _m("Philadelphia", "PA", 39.9526, -75.1652, dlng_w=0.10, dlng_e=0.02),                          # Delaware R E -> NJ
    _m("Boston", "MA", 42.3601, -71.0589, dlng_w=0.09, dlng_e=0.01),                                # harbor E
    _m("Miami", "FL", 25.7617, -80.1918, dlng_w=0.11, dlng_e=0.00),                                 # Biscayne Bay E
    _m("San Diego", "CA", 32.7157, -117.1611, dlng_w=0.01, dlng_e=0.11),                            # bay/ocean W
    _m("Seattle", "WA", 47.6062, -122.3321, dlat_s=0.09, dlat_n=0.09, dlng_w=0.01, dlng_e=0.05),    # Sound W / Lk WA E
    _m("Detroit", "MI", 42.3314, -83.0458, dlat_s=0.01, dlat_n=0.11, dlng_w=0.10, dlng_e=0.02),     # Detroit R S/E
    _m("Memphis", "TN", 35.1495, -90.0490, dlng_w=0.00, dlng_e=0.11),                               # Mississippi W
    _m("St. Louis", "MO", 38.6270, -90.1994, dlng_w=0.10, dlng_e=0.01),                             # Mississippi E
    _m("New Orleans", "LA", 29.9511, -90.0715, dlat_s=0.05, dlat_n=0.01, dlng_w=0.06, dlng_e=0.05), # Lk Pontchartrain N
    _m("Jacksonville", "FL", 30.3322, -81.6557, dlng_w=0.08, dlng_e=0.02),                          # river/ocean E
    _m("Salt Lake City", "UT", 40.7608, -111.8910, dlng_w=0.03, dlng_e=0.07),                       # Great Salt Lake NW
    # --- sprawling inland metros (a little wider looks natural) ---
    _m("Los Angeles", "CA", 34.0522, -118.2437, dlat_s=0.10, dlat_n=0.10, dlng_w=0.12, dlng_e=0.06),
    _m("Houston", "TX", 29.7604, -95.3698, dlat_s=0.10, dlat_n=0.10, dlng_w=0.10, dlng_e=0.10),
    _m("Phoenix", "AZ", 33.4484, -112.0740, dlat_s=0.10, dlat_n=0.10, dlng_w=0.12, dlng_e=0.12),
    _m("Dallas", "TX", 32.7767, -96.7970, dlat_s=0.09, dlat_n=0.09, dlng_w=0.10, dlng_e=0.10),
    _m("Atlanta", "GA", 33.7490, -84.3880, dlat_s=0.10, dlat_n=0.10, dlng_w=0.10, dlng_e=0.10),
    _m("Las Vegas", "NV", 36.1699, -115.1398, dlat_s=0.08, dlat_n=0.08, dlng_w=0.08, dlng_e=0.06),
    # --- compact inland metros (tight default-ish clusters) ---
    _m("San Antonio", "TX", 29.4241, -98.4936, dlat_s=0.07, dlat_n=0.07, dlng_w=0.07, dlng_e=0.07),
    _m("San Jose", "CA", 37.3382, -121.8863, dlat_s=0.05, dlat_n=0.07, dlng_w=0.06, dlng_e=0.04),
    _m("Austin", "TX", 30.2672, -97.7431, dlat_s=0.07, dlat_n=0.07, dlng_w=0.06, dlng_e=0.06),
    _m("Columbus", "OH", 39.9612, -82.9988, dlat_s=0.07, dlat_n=0.07, dlng_w=0.07, dlng_e=0.07),
    _m("Charlotte", "NC", 35.2271, -80.8431, dlat_s=0.07, dlat_n=0.07, dlng_w=0.07, dlng_e=0.07),
    _m("Indianapolis", "IN", 39.7684, -86.1581, dlat_s=0.08, dlat_n=0.08, dlng_w=0.08, dlng_e=0.08),
    _m("Denver", "CO", 39.7392, -104.9903, dlat_s=0.08, dlat_n=0.08, dlng_w=0.08, dlng_e=0.08),
    _m("Nashville", "TN", 36.1627, -86.7816, dlat_s=0.07, dlat_n=0.07, dlng_w=0.07, dlng_e=0.07),
    _m("Portland", "OR", 45.5152, -122.6784, dlat_s=0.06, dlat_n=0.06, dlng_w=0.05, dlng_e=0.06),
    _m("Minneapolis", "MN", 44.9778, -93.2650, dlat_s=0.06, dlat_n=0.06, dlng_w=0.06, dlng_e=0.06),
    _m("Kansas City", "MO", 39.0997, -94.5786, dlat_s=0.08, dlat_n=0.08, dlng_w=0.08, dlng_e=0.08),
]

VENUE_TYPES = [
    "Airport Terminal", "Office Tower", "University Hall", "Hospital Lobby",
    "Train Station", "Shopping Mall", "Convention Center", "Gym", "Hotel Lobby",
    "Transit Hub", "Tech Campus", "Stadium Concourse", "Library", "Parking Garage",
]

# Granular "where inside the venue" descriptions, composed from a position + a
# nearby landmark, e.g. "In the back by the pinball machines".
LOCATION_POSITIONS = [
    "In the back", "Near the main entrance", "By the restrooms", "On the second floor",
    "In the lobby", "Next to the elevators", "By the food court", "In the break room",
    "Down the north corridor", "By the ticket counter", "In the waiting area",
    "Just past the security checkpoint",
]
LOCATION_LANDMARKS = [
    "by the pinball machines", "next to the ATM", "beside the seating area",
    "across from the info desk", "by the escalators", "near the water fountain",
    "beside the arcade", "by the checkout lanes", "next to the coffee kiosk",
    "by the lockers", "under the departures board", "next to the help desk",
]

STREET_NAMES = [
    "Main", "Oak", "Maple", "Market", "Broadway", "Park", "Elm", "Washington",
    "Lincoln", "Cedar", "Pine", "Lake", "Hill", "Sunset", "Union", "Commerce",
]
STREET_SUFFIXES = ["St", "Ave", "Blvd", "Rd", "Way", "Ln", "Dr"]

MODELS = ["VendoMax 3000", "VendoMax 5000", "SnackPro X", "ChillVend 2", "FreshServe 400"]
MANUFACTURERS = ["Vendomo", "AcmeVend", "Crane", "Royal", "Seaga"]
STATUSES = ["operational", "operational", "operational", "needs_service", "offline"]

# Canonical product catalog. Note the canonical names ("Cola", not "Coke") — a
# natural-language query for "coke" has to be normalized to match.
PRODUCTS = [
    "Cola", "Diet Cola", "Lemon-Lime Soda", "Root Beer", "Ginger Ale",
    "Spring Water", "Sparkling Water", "Orange Juice", "Apple Juice",
    "Energy Drink", "Iced Coffee", "Green Tea", "Lemonade",
    "Potato Chips", "Pretzels", "Tortilla Chips", "Popcorn",
    "Chocolate Bar", "Peanut M&Ms", "Granola Bar", "Trail Mix",
    "Gum", "Mints", "Fruit Snacks", "Cookies", "Protein Bar", "Beef Jerky",
]

TECHNICIANS = [
    "Alex Rivera", "Sam Chen", "Jordan Patel", "Taylor Kim", "Casey Morgan",
    "Drew Nguyen", "Robin Diaz", "Jamie Flores", "Morgan Lee", "Quinn Ortiz",
]
SERVICE_TYPES = ["refill", "refill", "refill", "inspection", "repair"]

# Roughly this fraction of machines are brand-new and have never been serviced
# (last_serviced_at = NULL). Keep it noticeable but not dominant.
NEVER_SERVICED_FRACTION = 0.10


def _now() -> datetime:
    return datetime.now(timezone.utc)


def generate_machines(count: int, rng: random.Random) -> list[dict]:
    now = _now()
    machines: list[dict] = []
    for i in range(count):
        metro = rng.choice(METROS)
        city, state = metro.city, metro.state
        # Jitter within the metro's (possibly asymmetric) box — biased away from
        # water and state lines for coastal/riverfront cities.
        lat = metro.lat + rng.uniform(-metro.dlat_s, metro.dlat_n)
        lng = metro.lng + rng.uniform(-metro.dlng_w, metro.dlng_e)

        installed_days_ago = rng.randint(1, 1500)
        installed_at = now - timedelta(days=installed_days_ago)

        never_serviced = rng.random() < NEVER_SERVICED_FRACTION
        if never_serviced:
            last_serviced_at = None
            status = "needs_service" if rng.random() < 0.4 else "operational"
        else:
            serviced_days_ago = rng.randint(0, min(installed_days_ago, 120))
            last_serviced_at = now - timedelta(days=serviced_days_ago)
            status = rng.choice(STATUSES)

        venue = rng.choice(VENUE_TYPES)
        stocked = rng.sample(PRODUCTS, k=rng.randint(8, 14))
        products = [{"product": p, "quantity": rng.randint(0, 12)} for p in stocked]
        machines.append(
            {
                "id": uuid.uuid4(),
                "asset_tag": f"VM-{i + 1:06d}",
                "name": f"{venue} #{rng.randint(1, 9)} — {city}",
                "location_description": f"{rng.choice(LOCATION_POSITIONS)} {rng.choice(LOCATION_LANDMARKS)}",
                "model": rng.choice(MODELS),
                "manufacturer": rng.choice(MANUFACTURERS),
                "status": status,
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
                "address": f"{rng.randint(1, 9999)} {rng.choice(STREET_NAMES)} {rng.choice(STREET_SUFFIXES)}",
                "city": city,
                "region": state,
                "country": "USA",
                "capacity": rng.choice([30, 36, 40, 45, 50]),
                "products": products,
                "installed_at": installed_at,
                "last_serviced_at": last_serviced_at,
            }
        )
    return machines


def generate_service_logs(machines: list[dict], rng: random.Random, max_machines: int = 3000) -> list[dict]:
    """Generate a handful of historical service logs for serviced machines.

    Capped so that a large fleet seed doesn't explode the log table.
    """
    logs: list[dict] = []
    serviced = [m for m in machines if m["last_serviced_at"] is not None]
    rng.shuffle(serviced)
    for m in serviced[:max_machines]:
        for _ in range(rng.randint(1, 3)):
            created = m["last_serviced_at"] - timedelta(days=rng.randint(0, 90))
            logs.append(
                {
                    "id": uuid.uuid4(),
                    "machine_id": m["id"],
                    "type": rng.choice(SERVICE_TYPES),
                    "technician": rng.choice(TECHNICIANS),
                    "notes": rng.choice(
                        ["Routine refill", "Replaced coin mechanism", "Cleaned coils",
                         "Firmware update", "Cleared jam", "Restocked top rows", ""]
                    ),
                    "created_at": created,
                }
            )
    return logs
