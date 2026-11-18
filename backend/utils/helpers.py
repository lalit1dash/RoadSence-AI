"""
RoadSense – Shared utility / helper functions.
"""
from __future__ import annotations

import base64
import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile


# ──────────────────────────────────────────────────────────────────────────────
# File helpers
# ──────────────────────────────────────────────────────────────────────────────

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_upload(file: UploadFile, max_size_bytes: int) -> None:
    """
    Raise HTTP 400 if the uploaded file is not an allowed image type.
    Size validation happens after reading the file.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' is not supported. "
                   f"Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename preserving the original extension."""
    ext = Path(original_filename).suffix.lower() or ".jpg"
    return f"{uuid.uuid4().hex}{ext}"


async def save_upload_file(file: UploadFile, upload_dir: str, max_size_bytes: int) -> str:
    """
    Save an uploaded file to disk and return its path.
    Raises HTTP 413 if the file exceeds max_size_bytes.
    """
    os.makedirs(upload_dir, exist_ok=True)
    filename = generate_unique_filename(file.filename or "upload.jpg")
    file_path = os.path.join(upload_dir, filename)

    contents = await file.read()
    if len(contents) > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File size {len(contents) / 1_048_576:.1f} MB exceeds the "
                   f"{max_size_bytes / 1_048_576:.0f} MB limit.",
        )

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path


# ──────────────────────────────────────────────────────────────────────────────
# Image helpers
# ──────────────────────────────────────────────────────────────────────────────

def encode_image_base64(image_path: str) -> Optional[str]:
    """Read an image file and return its Base64-encoded string, or None on error."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except (FileNotFoundError, OSError):
        return None


def image_data_uri(image_path: str) -> Optional[str]:
    """Return a data-URI string for the image (suitable for embedding in HTML/JSON)."""
    b64 = encode_image_base64(image_path)
    if b64 is None:
        return None
    ext = Path(image_path).suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return f"data:image/{mime};base64,{b64}"


# ──────────────────────────────────────────────────────────────────────────────
# String / id helpers
# ──────────────────────────────────────────────────────────────────────────────

def utcnow_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.utcnow().isoformat() + "Z"


def sha256_hex(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# Severity / risk helpers
# ──────────────────────────────────────────────────────────────────────────────

SEVERITY_ORDER = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


def severity_to_int(level: str) -> int:
    """Convert a severity level string to an ordinal integer for sorting."""
    return SEVERITY_ORDER.get(level, 0)


def format_damage_class(class_name: str) -> str:
    """Convert snake_case damage class names to Title Case display names."""
    return class_name.replace("_", " ").title()
