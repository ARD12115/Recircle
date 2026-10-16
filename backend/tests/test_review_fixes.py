import asyncio
import io

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.requests import Request as StarletteRequest
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import Settings
from app.core.request_limits import ScanRequestBodyLimitMiddleware
from app.core.security import create_access_token, get_user_for_stream
from app.db.session import _async_url
from app.services.vision.preprocess import process_image


def test_cors_origins_accepts_csv_and_lists():
    assert Settings(
        _env_file=None,
        CORS_ORIGINS=" https://one.example, https://two.example ",
    ).CORS_ORIGINS == ["https://one.example", "https://two.example"]
    assert Settings(
        _env_file=None,
        CORS_ORIGINS=[" https://one.example ", "", "https://two.example"],
    ).CORS_ORIGINS == ["https://one.example", "https://two.example"]


def test_postgres_sslmode_is_converted_for_asyncpg():
    url = _async_url(
        "postgres://user:password@db:5432/recircle"
        "?sslmode=verify-full&prepared_statement_cache_size=100"
    )
    engine = create_async_engine(url)
    try:
        args, kwargs = engine.sync_engine.dialect.create_connect_args(make_url(url))
        assert kwargs["ssl"] == "verify-full"
        assert kwargs["prepared_statement_cache_size"] == 100
    finally:
        asyncio.run(engine.dispose())


def test_invalid_sse_query_token_falls_back_to_bearer():
    token = create_access_token({"sub": "42", "role": "resident"})
    request = StarletteRequest({
        "type": "http",
        "method": "GET",
        "path": "/api/v1/twin/stream",
        "query_string": b"token=invalid",
        "headers": [],
        "scheme": "http",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
        "http_version": "1.1",
    })
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user = asyncio.run(get_user_for_stream(request, credentials))

    assert user["sub"] == "42"


def test_scan_body_limit_rejects_before_route_parsing():
    app = FastAPI()
    app.add_middleware(ScanRequestBodyLimitMiddleware, max_bytes=16)

    @app.post("/api/v1/scan")
    async def scan(request: Request):
        return {"size": len(await request.body())}

    response = TestClient(app).post(
        "/api/v1/scan",
        content=b"x" * 17,
        headers={"Content-Type": "multipart/form-data; boundary=test"},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}


def test_image_preprocessing_applies_exif_orientation_and_strips_metadata():
    source = Image.new("RGB", (16, 8), color="green")
    exif = Image.Exif()
    exif[274] = 6
    encoded = io.BytesIO()
    source.save(encoded, format="JPEG", exif=exif)

    processed = process_image(encoded.getvalue())

    assert processed.size == (8, 16)
    assert not processed.getexif()
