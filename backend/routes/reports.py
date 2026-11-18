"""
Reports routes – generate, retrieve and list inspection reports.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import uuid

from database.connection import get_collection
from ml.report_generator import ReportGenerator
from routes.detection import IN_MEMORY_INSPECTIONS

router = APIRouter(prefix="/api/reports", tags=["Reports"])

generator = ReportGenerator()
IN_MEMORY_REPORTS: dict = {}


from datetime import date
from bson import ObjectId


def _serialize(obj):
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k == "_id":
                result["id"] = str(v)
            else:
                result[k] = _serialize(v)
        return result
    elif isinstance(obj, list):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


@router.post("/generate/{detection_id}")
async def generate_report(detection_id: str):
    """Generate a full report for an existing inspection."""
    inspection = None

    # Check in-memory inspections first
    if detection_id in IN_MEMORY_INSPECTIONS:
        inspection = IN_MEMORY_INSPECTIONS[detection_id]

    # Otherwise check MongoDB
    if inspection is None:
        inspections = get_collection("inspections")
        if inspections is not None:
            from bson import ObjectId
            from bson.errors import InvalidId

            query = {"deleted": {"$ne": True}}
            try:
                query["_id"] = ObjectId(detection_id)
            except InvalidId:
                query["id"] = detection_id

            inspection = await inspections.find_one(query)
            if inspection:
                _serialize(inspection)

    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found.")

    # Reconstruct detection result object
    detection_res = {
        "total_count": inspection.get("detection_count", len(inspection.get("detections", []))),
        "damage_summary": inspection.get("damage_summary", {}),
        "detections": inspection.get("detections", []),
        "demo_mode": inspection.get("demo_mode", True),
        "image_dimensions": inspection.get("image_dimensions", {"width": 640, "height": 640}),
    }

    severity_res = inspection.get("severity", {"level": "Medium", "score": 0.5})
    risk_res = inspection.get("risk_prediction", {"level": "Moderate", "score": 0.5, "repair_priority": "Scheduled"})
    loc_data = inspection.get("location")

    report_data = generator.generate_report(detection_res, severity_res, risk_res, loc_data)

    rep_id = uuid.uuid4().hex
    report_doc = {
        "id": rep_id,
        "detection_id": detection_id,
        "inspection_summary": {
            "severity": severity_res.get("level", "Medium"),
            "risk_level": risk_res.get("level", "Moderate"),
            "damage_types": inspection.get("damage_types", []),
            "detection_count": inspection.get("detection_count", 0),
            "address": inspection.get("address", ""),
            "road_name": inspection.get("road_name", ""),
        },
        **report_data,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "deleted": False,
    }

    reports = get_collection("reports")
    if reports is not None:
        db_doc = dict(report_doc)
        result = await reports.insert_one(db_doc)
        report_doc["id"] = str(result.inserted_id)

    IN_MEMORY_REPORTS[report_doc["id"]] = report_doc

    return JSONResponse(content=report_doc, status_code=201)


@router.get("/")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List all reports with pagination."""
    items = []
    reports = get_collection("reports")

    if reports is not None:
        query = {"deleted": {"$ne": True}}
        total = await reports.count_documents(query)
        cursor = reports.find(query).skip(skip).limit(limit).sort("generated_at", -1)
        items = [_serialize(doc) async for doc in cursor]
    else:
        # Fall back to in-memory
        all_mem = [r for r in IN_MEMORY_REPORTS.values() if not r.get("deleted", False)]
        total = len(all_mem)
        items = all_mem[skip: skip + limit]

    return JSONResponse(content={"items": items, "total": total, "skip": skip, "limit": limit})


@router.get("/inspection/{detection_id}")
async def get_report_for_inspection(detection_id: str):
    """Find the report linked to a specific inspection."""
    for rep in IN_MEMORY_REPORTS.values():
        if rep.get("detection_id") == detection_id and not rep.get("deleted", False):
            return JSONResponse(content=rep)

    collection = get_collection("reports")
    if collection is not None:
        doc = await collection.find_one(
            {"detection_id": detection_id, "deleted": {"$ne": True}}
        )
        if doc is not None:
            return JSONResponse(content=_serialize(doc))

    raise HTTPException(status_code=404, detail="No report found for this inspection.")


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Return a report by its ID."""
    if report_id in IN_MEMORY_REPORTS:
        doc = IN_MEMORY_REPORTS[report_id]
        if not doc.get("deleted", False):
            return JSONResponse(content=doc)

    collection = get_collection("reports")
    if collection is not None:
        from bson import ObjectId
        from bson.errors import InvalidId

        query = {"deleted": {"$ne": True}}
        try:
            query["_id"] = ObjectId(report_id)
        except InvalidId:
            query["id"] = report_id

        doc = await collection.find_one(query)
        if doc is not None:
            return JSONResponse(content=_serialize(doc))

    raise HTTPException(status_code=404, detail="Report not found.")
