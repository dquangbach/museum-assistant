from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from starlette.responses import JSONResponse

from app.api.catalog import router as catalog_router
from app.api.exhibits import admin_router, router as exhibit_router
from app.core.config import Settings, get_settings
from app.db.session import make_engine

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app):
        engine = make_engine(settings.database_url)
        app.state.engine = engine
        app.state.session_factory = sessionmaker(engine, expire_on_commit=False)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Da Nang Museum API", version="0.1.0", lifespan=lifespan,
                  description="Catalog and media from the field dataset; verified exhibits are published separately.")
    app.state.settings = settings
    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                           allow_credentials=False, allow_methods=["GET", "POST", "PATCH"],
                           allow_headers=["Content-Type", "X-Admin-Key"])

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request, error):
        logger.warning("Database constraint rejected a write")
        return JSONResponse(status_code=409, content={"detail": "Data conflicts with an existing record or relation"})

    @app.get("/health/live", tags=["Health"])
    def live():
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Health"])
    def ready():
        try:
            with app.state.engine.connect() as connection:
                revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        except SQLAlchemyError:
            raise HTTPException(503, "Database is unavailable or migrations have not been applied")
        return {"status": "ok", "database": "ok", "migration": revision}

    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(exhibit_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")
    return app


app = create_app()
