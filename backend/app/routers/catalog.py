"""Product catalog — the canonical set of products machines can stock."""
from fastapi import APIRouter

from ..seed_data import PRODUCTS

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/products")
async def list_products() -> list[str]:
    """The canonical product vocabulary (e.g. 'Cola', not 'Coke')."""
    return sorted(PRODUCTS)
