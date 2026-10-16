"""
ReCircle Backend - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.api.v1.router import api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await init_db()
    # Load ML model at startup (avoid cold starts)
    from app.services.vision.classifier import load_model
    load_model()
    if settings.DEMO_MODE and settings.DEMO_TRAFFIC:
        from app.services.twin.generator import demo_generator
        await demo_generator.start()
    yield
    from app.services.twin.generator import demo_generator
    await demo_generator.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReCircle API",
        description="Smart Recycling Assistant - Computer Vision × Digital Twin × Generative AI",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV == "dev" else None,
        redoc_url="/redoc" if settings.APP_ENV == "dev" else None,
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limited",
                    "message": "Too many requests. Wait a minute and retry.",
                }
            },
            headers={"Retry-After": "60"},
        )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security headers
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(self), geolocation=()")
        if settings.APP_ENV == "prod":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response
    
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