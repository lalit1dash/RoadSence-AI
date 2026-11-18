"""
RoadSense – Pydantic v2 request / response schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _str_object_id(v: Any) -> str:
    """Convert ObjectId to str if needed."""
    if isinstance(v, ObjectId):
        return str(v)
    return str(v)


# ──────────────────────────────────────────────────────────────────────────────
# Detection primitives
# ──────────────────────────────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    """Pixel-space bounding box returned by the detector."""
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    """Single damage detection from Module A."""
    class_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    area_ratio: float = Field(0.0, ge=0.0, le=1.0)


# ──────────────────────────────────────────────────────────────────────────────
# ML pipeline outputs
# ──────────────────────────────────────────────────────────────────────────────

class SeverityResult(BaseModel):
    """Output of Module B – severity classification."""
    level: str  # Low | Medium | High | Critical
    score: float = Field(..., ge=0.0, le=100.0)
    features: Dict[str, Any] = Field(default_factory=dict)
    demo_mode: bool = True


class RiskPrediction(BaseModel):
    """Output of Module C – risk prediction."""
    level: str  # Low | Medium | High | Critical
    score: float = Field(..., ge=0.0, le=100.0)
    factors: List[str] = Field(default_factory=list)
    repair_priority: str  # Immediate | High | Medium | Low
    estimated_repair_time: str  # e.g. "Within 24 hours"
    demo_mode: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# Location
# ──────────────────────────────────────────────────────────────────────────────

class LocationData(BaseModel):
    """Optional geolocation metadata attached to an inspection."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = ""
    road_name: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Inspection documents
# ──────────────────────────────────────────────────────────────────────────────

class DamageInspection(BaseModel):
    """Full inspection document as stored in MongoDB."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    id: Optional[str] = Field(default=None, alias="_id")

    # Image info
    original_image_path: str = ""
    annotated_image_path: str = ""
    annotated_image_base64: Optional[str] = None
    image_width: int = 0
    image_height: int = 0

    # Pipeline results
    detections: List[Dict[str, Any]] = Field(default_factory=list)
    detection_count: int = 0
    damage_classes: List[str] = Field(default_factory=list)
    severity: Optional[Dict[str, Any]] = None
    risk: Optional[Dict[str, Any]] = None

    # Location
    location: Optional[LocationData] = None

    # Meta
    processing_time_ms: float = 0.0
    demo_mode: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return _str_object_id(v) if v is not None else None


class InspectionSummary(BaseModel):
    """Abbreviated inspection info used in list endpoints."""
    id: str
    detection_count: int
    damage_classes: List[str]
    severity_level: Optional[str] = None
    risk_level: Optional[str] = None
    demo_mode: bool = True
    created_at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# Reports
# ──────────────────────────────────────────────────────────────────────────────

class InspectionReport(BaseModel):
    """AI-generated inspection report stored in MongoDB."""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    id: Optional[str] = Field(default=None, alias="_id")
    detection_id: str

    executive_summary: str = ""
    damage_analysis: str = ""
    severity_assessment: str = ""
    risk_assessment: str = ""
    recommendations: List[str] = Field(default_factory=list)
    safety_warnings: List[str] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_object_id(cls, v):
        return _str_object_id(v) if v is not None else None


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    """Aggregated metrics returned by the dashboard endpoint."""
    total_inspections: int = 0
    total_detections: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    avg_severity_score: float = 0.0
    avg_risk_score: float = 0.0
    most_common_damage: Optional[str] = None
    inspections_last_7_days: int = 0
    inspections_last_30_days: int = 0
    severity_distribution: Dict[str, int] = Field(default_factory=dict)
    risk_distribution: Dict[str, int] = Field(default_factory=dict)
    damage_type_counts: Dict[str, int] = Field(default_factory=dict)
    daily_trend: List[Dict[str, Any]] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# Map
# ──────────────────────────────────────────────────────────────────────────────

class MapPoint(BaseModel):
    """Lightweight inspection record for map rendering."""
    id: str
    lat: float
    lng: float
    severity: str
    risk_level: str
    damage_types: List[str] = Field(default_factory=list)
    timestamp: datetime
