"""
Detection routes – image upload, analysis, retrieval, deletion.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import os
import shutil
from datetime import datetime, timezone

from database.connection import get_collection
from ml.yolo_detector import RoadDamageDetector
from ml.severity_classifier import SeverityClassifier
from ml.risk_predictor import RiskPredictor
from utils.auth import get_optional_current_user

router = APIRouter(prefix="/api/detection", tags=["Detection"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Singletons for ML components
detector = RoadDamageDetector()
classifier = SeverityClassifier()
predictor = RiskPredictor()

# In-memory storage fallback when MongoDB is unavailable
IN_MEMORY_INSPECTIONS: dict = {}


def get_db():
    """Return the inspections collection (or None when DB is unavailable)."""
    return get_collection("inspections")


def _ext_ok(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    road_name: Optional[str] = Form(None),
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """Upload a road image and run full ML pipeline."""

    # --- Validate extension ---
    if not _ext_ok(file.filename or ""):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, JPEG and PNG are accepted.",
        )

    # --- Save to uploads/ ---
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    ext = (file.filename or "image.jpg").rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    image_path = os.path.join(upload_dir, unique_name)

    try:
        with open(image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # --- ML pipeline ---
        detection_result = detector.detect(image_path)
        detections = detection_result.get("detections", [])
        annotated_image_base64 = detection_result.get("annotated_image_base64", "")
        demo_mode = detection_result.get("demo_mode", True)

        location = None
        if latitude is not None and longitude is not None:
            location = {
                "latitude": latitude,
                "longitude": longitude,
                "address": address or "",
                "road_name": road_name or "",
            }

        # Severity Classification
        severity_result = classifier.classify(image_path, detections)

        # Risk Prediction
        risk_result = predictor.predict(severity_result, detections, location)

        # --- Build inspection document ---
        now = datetime.now(timezone.utc)
        damage_types = list(detection_result.get("damage_summary", {}).keys())
        if not damage_types:
            damage_types = list({d.get("class_name", "unknown") for d in detections})

        doc_id = uuid.uuid4().hex

        inspection = {
            "id": doc_id,
            "image_path": f"/uploads/{unique_name}",
            "image_filename": unique_name,
            "detections": detections,
            "detection_count": len(detections),
            "damage_summary": detection_result.get("damage_summary", {}),
            "damage_types": damage_types,
            "severity": severity_result,
            "risk_prediction": risk_result,
            "location": location,
            "address": address or (location.get("address") if location else ""),
            "road_name": road_name or (location.get("road_name") if location else ""),
            "annotated_image_base64": annotated_image_base64,
            "demo_mode": demo_mode,
            "user": {
                "id": current_user.get("id"),
                "name": current_user.get("name"),
                "email": current_user.get("email"),
                "role": current_user.get("role"),
            } if current_user else None,
            "timestamp": now.isoformat(),
            "created_at": now.isoformat(),
            "deleted": False,
        }

        # --- Persist to MongoDB or in-memory fallback ---
        collection = get_db()
        if collection is not None:
            db_doc = dict(inspection)
            result = await collection.insert_one(db_doc)
            inspection["id"] = str(result.inserted_id)

        # Always save copy in memory cache for instant lookup
        IN_MEMORY_INSPECTIONS[inspection["id"]] = inspection

        return JSONResponse(content=inspection, status_code=200)

    except HTTPException:
        raise
    except Exception as exc:
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        )


@router.get("/{detection_id}")
async def get_detection(detection_id: str):
    """Retrieve a single inspection by ID."""
    # Check in-memory first
    if detection_id in IN_MEMORY_INSPECTIONS:
        doc = IN_MEMORY_INSPECTIONS[detection_id]
        if not doc.get("deleted", False):
            return JSONResponse(content=doc)

    collection = get_db()
    if collection is not None:
        from bson import ObjectId
        from bson.errors import InvalidId

        query = {"deleted": {"$ne": True}}
        try:
            query["_id"] = ObjectId(detection_id)
        except InvalidId:
            query["id"] = detection_id

        doc = await collection.find_one(query)
        if doc is not None:
            doc["id"] = str(doc.pop("_id", doc.get("id", detection_id)))
            return JSONResponse(content=doc)

    raise HTTPException(status_code=404, detail="Detection not found.")


@router.delete("/{detection_id}", status_code=204)
async def delete_detection(detection_id: str):
    """Soft-delete a detection record."""
    deleted_any = False
    if detection_id in IN_MEMORY_INSPECTIONS:
        IN_MEMORY_INSPECTIONS[detection_id]["deleted"] = True
        deleted_any = True

    collection = get_db()
    if collection is not None:
        from bson import ObjectId
        from bson.errors import InvalidId

        query = {}
        try:
            query["_id"] = ObjectId(detection_id)
        except InvalidId:
            query["id"] = detection_id

        result = await collection.update_one(
            query,
            {
                "$set": {
                    "deleted": True,
                    "deleted_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )
        if result.matched_count > 0:
            deleted_any = True

    if not deleted_any:
        raise HTTPException(status_code=404, detail="Detection not found.")
