"""
Dashboard routes – dynamic summary stats and geographic map points.
All metrics and map points are computed live from MongoDB with in-memory upload support.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from database.connection import get_collection
from routes.detection import IN_MEMORY_INSPECTIONS

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _serialize(doc: dict) -> dict:
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.get("/stats")
async def dashboard_stats():
    """
    Return dynamic dashboard statistics computed directly from the database.
    """
    collection = get_collection("inspections")
    
    # Base defaults if database is completely empty
    empty_response = {
        "total_inspections": 0,
        "critical_count": 0,
        "high_risk_count": 0,
        "pending_repairs": 0,
        "severity_distribution": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
        "damage_type_distribution": {
            "pothole": 0,
            "longitudinal_crack": 0,
            "transverse_crack": 0,
            "alligator_crack": 0,
            "surface_damage": 0,
        },
        "risk_distribution": {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0},
        "monthly_trend": [],
        "recent_inspections": [],
    }

    if collection is None:
        # Fall back to in-memory uploads count if DB is offline
        mem_items = [d for d in IN_MEMORY_INSPECTIONS.values() if not d.get("deleted", False)]
        if not mem_items:
            return JSONResponse(content=empty_response)
        
        total = len(mem_items)
        sev_dist = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        risk_dist = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
        dtype_dist = {"pothole": 0, "longitudinal_crack": 0, "transverse_crack": 0, "alligator_crack": 0, "surface_damage": 0}
        
        for item in mem_items:
            sev = item.get("severity", {}).get("level", "Medium") if isinstance(item.get("severity"), dict) else item.get("severity", "Medium")
            sev_dist[sev] = sev_dist.get(sev, 0) + 1
            risk = item.get("risk_prediction", {}).get("level", "Moderate") if isinstance(item.get("risk_prediction"), dict) else item.get("risk_prediction", "Moderate")
            risk_dist[risk] = risk_dist.get(risk, 0) + 1
            for dt in item.get("damage_types", []):
                dtype_dist[dt] = dtype_dist.get(dt, 0) + 1

        recent = [
            {
                "id": str(d.get("id")),
                "timestamp": d.get("timestamp", ""),
                "severity": d.get("severity", {}).get("level", "Medium") if isinstance(d.get("severity"), dict) else d.get("severity", "Medium"),
                "risk_level": d.get("risk_prediction", {}).get("level", "Moderate") if isinstance(d.get("risk_prediction"), dict) else d.get("risk_prediction", "Moderate"),
                "damage_types": d.get("damage_types", []),
                "road_name": d.get("road_name") or d.get("address") or "Inspected Road",
            }
            for d in list(mem_items)[-5:]
        ]
        
        return JSONResponse(content={
            "total_inspections": total,
            "critical_count": sev_dist.get("Critical", 0),
            "high_risk_count": risk_dist.get("High", 0) + risk_dist.get("Critical", 0),
            "pending_repairs": sev_dist.get("High", 0) + sev_dist.get("Critical", 0),
            "severity_distribution": sev_dist,
            "damage_type_distribution": dtype_dist,
            "risk_distribution": risk_dist,
            "monthly_trend": [{"month": "Current", "count": total}],
            "recent_inspections": recent,
        })

    total = await collection.count_documents({"deleted": {"$ne": True}})
    if total == 0:
        return JSONResponse(content=empty_response)

    # 1. Severity distribution aggregation
    sev_dist = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$group": {"_id": "$severity.level", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            sev_dist[row["_id"]] = row["count"]

    critical_count = sev_dist.get("Critical", 0)

    # 2. Risk distribution aggregation
    risk_dist = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$group": {"_id": "$risk_prediction.level", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            risk_dist[row["_id"]] = row["count"]

    high_risk_count = risk_dist.get("High", 0) + risk_dist.get("Critical", 0)

    # 3. Damage type distribution aggregation
    dtype_dist = {
        "pothole": 0,
        "longitudinal_crack": 0,
        "transverse_crack": 0,
        "alligator_crack": 0,
        "surface_damage": 0,
    }
    async for row in collection.aggregate([
        {"$match": {"deleted": {"$ne": True}}},
        {"$unwind": "$damage_types"},
        {"$group": {"_id": "$damage_types", "count": {"$sum": 1}}},
    ]):
        if row["_id"]:
            dtype_dist[row["_id"]] = row["count"]

    # 4. Monthly trend aggregation (last 6 months from created_at)
    monthly_pipeline = [
        {"$match": {"deleted": {"$ne": True}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {"$limit": 6},
    ]
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    monthly_trend = []
    async for row in collection.aggregate(monthly_pipeline):
        m = row["_id"].get("month", 1)
        monthly_trend.append({"month": month_names[m - 1], "count": row["count"]})

    # If monthly_trend is empty or short, summarize recent
    if not monthly_trend:
        monthly_trend = [{"month": "Nov", "count": total}]

    # 5. Recent inspections from DB (last 5)
    recent_cursor = (
        collection.find({"deleted": {"$ne": True}})
        .sort("created_at", -1)
        .limit(5)
    )
    recent = []
    async for doc in recent_cursor:
        recent.append(
            {
                "id": str(doc.get("_id", doc.get("id"))),
                "timestamp": doc.get("timestamp", ""),
                "severity": doc.get("severity", {}).get("level", "Medium") if isinstance(doc.get("severity"), dict) else doc.get("severity", "Medium"),
                "risk_level": doc.get("risk_prediction", {}).get("level", "Moderate") if isinstance(doc.get("risk_prediction"), dict) else doc.get("risk_prediction", "Moderate"),
                "damage_types": doc.get("damage_types", []),
                "road_name": doc.get("road_name") or doc.get("address") or "Inspected Road",
            }
        )

    # Pending repairs = High + Critical severity
    pending = sev_dist.get("High", 0) + sev_dist.get("Critical", 0)

    return JSONResponse(
        content={
            "total_inspections": total,
            "critical_count": critical_count,
            "high_risk_count": high_risk_count,
            "pending_repairs": pending,
            "severity_distribution": sev_dist,
            "damage_type_distribution": dtype_dist,
            "risk_distribution": risk_dist,
            "monthly_trend": monthly_trend,
            "recent_inspections": recent,
        }
    )


@router.get("/map-data")
async def map_data():
    """
    Return all real road inspections with valid GPS coordinates from MongoDB.
    100% computed from stored database records.
    """
    points = []
    seen_ids = set()

    collection = get_collection("inspections")
    if collection is not None:
        query = {
            "deleted": {"$ne": True},
            "location.latitude": {"$ne": None},
            "location.longitude": {"$ne": None},
        }
        cursor = collection.find(query).sort("created_at", -1)
        async for doc in cursor:
            loc = doc.get("location") or {}
            doc_id = str(doc.get("_id", doc.get("id")))
            if doc_id not in seen_ids and loc.get("latitude") is not None and loc.get("longitude") is not None:
                seen_ids.add(doc_id)
                points.append({
                    "id": doc_id,
                    "latitude": float(loc["latitude"]),
                    "longitude": float(loc["longitude"]),
                    "severity": doc.get("severity", {}).get("level", "Medium") if isinstance(doc.get("severity"), dict) else (doc.get("severity") or "Medium"),
                    "risk_level": doc.get("risk_prediction", {}).get("level", "Moderate") if isinstance(doc.get("risk_prediction"), dict) else (doc.get("risk_prediction") or "Moderate"),
                    "damage_types": doc.get("damage_types", []),
                    "timestamp": doc.get("timestamp", ""),
                    "address": loc.get("address") or doc.get("address") or doc.get("road_name") or "Inspected Road Section",
                    "road_name": doc.get("road_name") or loc.get("road_name") or "",
                })

    # Also include in-memory uploads that haven't been synced to disk
    for doc in IN_MEMORY_INSPECTIONS.values():
        if doc.get("deleted", False):
            continue
        doc_id = str(doc.get("id"))
        if doc_id in seen_ids:
            continue
        loc = doc.get("location") or {}
        if loc.get("latitude") is not None and loc.get("longitude") is not None:
            seen_ids.add(doc_id)
            points.append({
                "id": doc_id,
                "latitude": float(loc["latitude"]),
                "longitude": float(loc["longitude"]),
                "severity": doc.get("severity", {}).get("level", "Medium") if isinstance(doc.get("severity"), dict) else "Medium",
                "risk_level": doc.get("risk_prediction", {}).get("level", "Moderate") if isinstance(doc.get("risk_prediction"), dict) else "Moderate",
                "damage_types": doc.get("damage_types", []),
                "timestamp": doc.get("timestamp", ""),
                "address": loc.get("address") or doc.get("address") or doc.get("road_name") or "Inspected Road Section",
                "road_name": doc.get("road_name") or loc.get("road_name") or "",
            })

    return JSONResponse(content=points)
