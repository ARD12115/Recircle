"""
Vision Preprocess - Validate, strip EXIF, resize
"""
import io
from PIL import Image, ImageOps
from fastapi import HTTPException, status
from app.core.config import settings


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_PIXELS = 25_000_000  # 25 megapixels decompression bomb guard


def validate_upload(content_type: str, file_size: int) -> None:
    """Validate uploaded file."""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {content_type}. Allowed: JPEG, PNG, WebP",
        )
    
    if file_size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum {settings.MAX_UPLOAD_MB} MB",
        )


def process_image(image_bytes: bytes) -> Image.Image:
    """
    Process uploaded image: validate, strip EXIF, resize, re-encode.
    Returns PIL Image ready for inference.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image: {str(e)}",
        )
    
    # Verify format
    if image.format not in ("JPEG", "PNG", "WEBP"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image format: {image.format}",
        )
    
    # Decompression bomb guard
    if image.width * image.height > MAX_PIXELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large ({image.width}x{image.height}). Max {MAX_PIXELS} pixels",
        )
    
    # Orient and downscale before re-encoding to avoid copying full-resolution pixels.
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    image_without_exif = image
    
    # Re-encode as JPEG (quality 0.85) to normalize
    buffer = io.BytesIO()
    image_without_exif.save(buffer, format="JPEG", quality=85, optimize=True)
    buffer.seek(0)
    
    return Image.open(buffer)


def image_to_bytes(image: Image.Image, format: str = "JPEG", quality: int = 85) -> bytes:
    """Convert PIL image to bytes."""
    buffer = io.BytesIO()
    image.save(buffer, format=format, quality=quality, optimize=True)
    return buffer.getvalue()