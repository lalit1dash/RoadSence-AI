"""
RoadSense – FastAPI application entry point.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database.connection import connect_to_mongo, close_mongo_connection
from routes.health import router as health_router

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
)
logger = logging.getLogger("roadsense")


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────
    logger.info("🚀 RoadSense API starting up …")

    # Connect to MongoDB
    await connect_to_mongo()

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Upload directory ready: %s", settings.UPLOAD_DIR)

    logger.info("✅ Startup complete. API is ready.")
    yield

    # ── Shutdown ───────────────────────────────────────────────────────────
    logger.info("🛑 RoadSense API shutting down …")
    await close_mongo_connection()
    logger.info("Shutdown complete.")


# ──────────────────────────────────────────────────────────────────────────────
# Application factory
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="RoadSense API",
    description=(
        "AI-Powered Road Damage Detection & Risk Prediction REST API. "
        "Upload road images to detect damage, classify severity, predict risk, "
        "and generate inspection reports."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
# Static files
# ──────────────────────────────────────────────────────────────────────────────

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads",
)


# ──────────────────────────────────────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────────────────────────────────────

# Health check (no prefix – accessible at /health)
app.include_router(health_router)

# Authentication & JWT security
try:
    from routes.auth import router as auth_router
    app.include_router(auth_router)
except ImportError as e:
    logger.warning("routes.auth not found: %s", e)

# Feature routers
try:
    from routes.detection import router as detection_router
    app.include_router(detection_router)
except ImportError:
    logger.warning("routes.detection not found – stub placeholder active")

# Inspections
try:
    from routes.inspections import router as inspections_router
    app.include_router(inspections_router)
except ImportError:
    logger.warning("routes.inspections not found – stub placeholder active")

# Dashboard
try:
    from routes.dashboard import router as dashboard_router
    app.include_router(dashboard_router)
except ImportError:
    logger.warning("routes.dashboard not found – stub placeholder active")

# Reports
try:
    from routes.reports import router as reports_router
    app.include_router(reports_router)
except ImportError:
    logger.warning("routes.reports not found – stub placeholder active")


# ──────────────────────────────────────────────────────────────────────────────
# Root endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], summary="API welcome message")
async def root():
    """Welcome endpoint – confirms the API is reachable."""
    return {
        "message": "Welcome to the RoadSense API 🛣️",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
