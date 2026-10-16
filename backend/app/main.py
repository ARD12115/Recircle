"""
ReCircle Backend - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    init_db()
    # Load ML model at startup (avoid cold starts)
    from app.services.vision.classifier import load_model
    load_model()
    yield
    # Shutdown
    pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReCircle API",
        description="Smart Recycling Assistant - Computer Vision × Digital Twin × Generative AI",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV == "dev" else None,
        redoc_url="/redoc" if settings.APP_ENV == "dev" else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files for uploaded images (if needed)
    # app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "1.0.0", "env": settings.APP_ENV}
    
    @app.get("/version")
    async def version():
        return {"version": "1.0.0"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)