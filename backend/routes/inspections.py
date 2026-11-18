"""
Inspections routes – dynamic listing, filtering, and aggregate statistics directly from MongoDB.
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from database.connection import get_collection
from routes.detection import IN_MEMORY_INSPECTIONS

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])


from datetime import datetime, date
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


@router.get("/")
async def list_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
):
    """Return paginated list of real inspections with optional filters."""
    items = []
    total = 0

    collection = get_collection("inspections")
    if collection is not None:
        query: dict = {"deleted": {"$ne": True}}
        if severity and severity != "All":
            query["severity.level"] = severity
        if risk_level and risk_level != "All":
            query["risk_prediction.level"] = risk_level

        total = await collection.count_documents(query)
        if total > 0:
            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            items = [_serialize(doc) async for doc in cursor]

    # If MongoDB is empty or unavailable, pull from in-memory cache
    if not items:
        mem_items = [i for i in IN_MEMORY_INSPECTIONS.values() if not i.get("deleted", False)]
        if severity and severity != "All":
            mem_items = [i for i in mem_items if i.get("severity", {}).get("level") == severity]
        if risk_level and risk_level != "All":
            mem_items = [i for i in mem_items if i.get("risk_prediction", {}).get("level") == risk_level]

        total = len(mem_items)
        items = mem_items[skip: skip + limit]

    return JSONResponse(
        content={"items": items, "total": total, "skip": skip, "limit": limit}
    )


@router.get("/stats")
async def inspection_stats():
    """Return real aggregate statistics across all stored inspections."""
    collection = get_collection("inspections")
    if collection is None:
        return JSONResponse(content={
            "total": len(IN_MEMORY_INSPECTIONS),
            "by_severity": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
            "by_risk_level": {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0},
            "by_damage_type": {},
            "avg_confidence": 0.0,
        })

    total = await collection.count_documents({"deleted": {"$ne": True}})
    if total == 0:
        return JSONResponse(content={
            "total": 0,
            "by_severity": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
            "by_risk_level": {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0},
            "by_damage_type": {},
            "avg_confidence": 0.0,
        })

    # 1. Severity counts
    by_severity: dict = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$group": {"_id": "$severity.level", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            by_severity[row["_id"]] = row["count"]

    # 2. Risk counts
    by_risk: dict = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$group": {"_id": "$risk_prediction.level", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            by_risk[row["_id"]] = row["count"]

    # 3. Damage type counts
    by_damage: dict = {}
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$unwind": "$damage_types"},
        {"$group": {"_id": "$damage_types", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            by_damage[row["_id"]] = row["count"]

    # 4. Average confidence
    avg_conf = 0.0
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}, "detections": {"$exists": True}}},
        {"$unwind": "$detections"},
        {"$group": {"_id": None, "avg": {"$avg": "$detections.confidence"}}},
    ]):
        avg_conf = round(row.get("avg", 0.0), 3)

    return JSONResponse(
        content={
            "total": total,
            "by_severity": by_severity,
            "by_risk_level": by_risk,
            "by_damage_type": by_damage,
            "avg_confidence": avg_conf,
        }
    )


@router.get("/{inspection_id}")
async def get_inspection(inspection_id: str):
    """Return a single real inspection by ID."""
    if inspection_id in IN_MEMORY_INSPECTIONS:
        doc = IN_MEMORY_INSPECTIONS[inspection_id]
        if not doc.get("deleted", False):
            return JSONResponse(content=doc)

    collection = get_collection("inspections")
    if collection is not None:
        from bson import ObjectId
        from bson.errors import InvalidId

        query = {"deleted": {"$ne": True}}
        try:
            query["_id"] = ObjectId(inspection_id)
        except InvalidId:
            query["id"] = inspection_id

        doc = await collection.find_one(query)
        if doc is not None:
            return JSONResponse(content=_serialize(doc))

    raise HTTPException(status_code=404, detail="Inspection not found.")
