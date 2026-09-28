from fastapi import APIRouter

from app import __version__
from app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__, "trading_mode": get_settings().trading_mode}
