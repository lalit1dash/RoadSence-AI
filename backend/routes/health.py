"""
RoadSense – Health check route.
GET /health  →  system status overview.
"""
from __future__ import annotations

import platform
import sys
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database.connection import check_connection

router = APIRouter(tags=["Health"])


@router.get("/health", summary="System health check")
@router.get("/api/health", summary="System health check")
async def health_check():
    """
    Returns the current health status of all system components.

    - **status**: overall health (ok | degraded)
    - **database**: MongoDB connectivity
    - **python_version**: running Python version
    - **timestamp**: UTC time of this check
    """
    db_status = "ok"
    db_error: str | None = None

    try:
        await check_connection()
    except Exception as exc:
        db_status = "error"
        db_error = str(exc)

    overall = "ok" if db_status == "ok" else "degraded"

    payload = {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "database": {
                "status": db_status,
                "error": db_error,
            },
            "api": {"status": "ok"},
        },
        "python_version": sys.version,
        "platform": platform.system(),
    }

    status_code = 200 if overall == "ok" else 503
    return JSONResponse(content=payload, status_code=status_code)
