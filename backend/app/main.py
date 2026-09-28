from fastapi import FastAPI

from app import __version__
from app.api.health import router as health_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    # Fail fast: an invalid config must stop the process before uvicorn ever binds a port.
    get_settings()
    application = FastAPI(title="AI Stock Decision", version=__version__)
    application.include_router(health_router)
    return application


app = create_app()
