"""
Image processing utilities for RoadSense.
Handles validation, saving, metadata extraction, and thumbnail generation using PIL.
"""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import Tuple

from PIL import Image

logger = logging.getLogger(__name__)


def validate_image(file_bytes: bytes) -> bool:
    """
    Check whether bytes represent a valid, decodable image.
    """
    if not file_bytes:
        return False
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
        return True
    except Exception as e:
        logger.debug(f"Image validation failed: {e}")
        return False


def save_uploaded_image(file_bytes: bytes, filename: str, upload_dir: str) -> str:
    """
    Save image bytes to the upload directory.
    """
    if not validate_image(file_bytes):
        raise ValueError("Provided bytes do not represent a valid image.")

    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    safe_name = Path(filename).name.replace(" ", "_")
    dest = upload_path / safe_name

    counter = 1
    while dest.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        dest = upload_path / f"{stem}_{counter}{suffix}"
        counter += 1

    dest.write_bytes(file_bytes)
    logger.info(f"Saved uploaded image to {dest}")
    return str(dest)


def extract_metadata(image_path: str) -> dict:
    """
    Extract basic metadata from an image file.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with Image.open(image_path) as img:
        w, h = img.size
        channels = len(img.getbands())
        fmt = img.format or "UNKNOWN"

    return {
        "width": w,
        "height": h,
        "channels": channels,
        "file_size_bytes": path.stat().st_size,
        "format": fmt,
    }


def generate_thumbnail_b64(image_path: str, size: Tuple[int, int] = (200, 200)) -> str:
    """
    Generate a base64-encoded JPEG thumbnail of the given image.
    """
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail(size)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
