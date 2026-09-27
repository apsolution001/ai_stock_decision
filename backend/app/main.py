from fastapi import FastAPI

from app import __version__
from app.api.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(title="AI Stock Decision", version=__version__)
    application.include_router(health_router)
    return application


app = create_app()
