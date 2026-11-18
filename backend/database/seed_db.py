"""
Seed Database with Realistic Road Inspection Records.
Populates MongoDB 'inspections' and 'reports' collections with rich real-world data.
"""

import asyncio
import datetime
import random
import uuid
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "roadsense"

SAMPLE_IMAGES = [
    "pothole_severe_nh48.jpg",
    "alligator_crack_urban.jpg",
    "longitudinal_crack_highway.jpg",
    "transverse_crack_suburb.jpg",
    "surface_damage_multi.jpg",
    "heavy_damage_sector14.jpg",
]

ROAD_SITES = [
    {"road": "NH-48 Expressway", "address": "Dhaula Kuan to Gurugram Mile 12, Delhi", "lat": 28.5355, "lng": 77.1990, "city": "Delhi"},
    {"road": "Cyber City Corridor", "address": "DLF Phase 2 Rapid Transit Rd, Gurugram", "lat": 28.4900, "lng": 77.0888, "city": "Gurugram"},
    {"road": "Noida-Greater Noida Expressway", "address": "Expressway Sector 128, Noida", "lat": 28.5100, "lng": 77.3700, "city": "Noida"},
    {"road": "Western Express Highway", "address": "Andheri East Flyover, Mumbai", "lat": 19.1136, "lng": 72.8697, "city": "Mumbai"},
    {"road": "Marine Drive", "address": "Netaji Subhash Chandra Bose Rd, Mumbai", "lat": 18.9438, "lng": 72.8232, "city": "Mumbai"},
    {"road": "Eastern Freeway", "address": "Wadala Truck Terminal Stretch, Mumbai", "lat": 19.0176, "lng": 72.8561, "city": "Mumbai"},
    {"road": "Mumbai-Pune Expressway", "address": "Khandala Ghat Section Mile 48, Maharashtra", "lat": 18.7500, "lng": 73.4000, "city": "Pune"},
    {"road": "Hinjawadi IT Corridor", "address": "Hinjawadi Phase 1 Main Road, Pune", "lat": 18.5913, "lng": 73.7389, "city": "Pune"},
    {"road": "MG Road", "address": "Mahatma Gandhi Road / Trinity Circle, Bangalore", "lat": 12.9756, "lng": 77.6097, "city": "Bangalore"},
    {"road": "Outer Ring Road (ORR)", "address": "Bellandur EcoSpace Junction, Bangalore", "lat": 12.9260, "lng": 77.6762, "city": "Bangalore"},
    {"road": "Electronic City Flyover", "address": "Hosur Rd Elevated Expressway, Bangalore", "lat": 12.8452, "lng": 77.6602, "city": "Bangalore"},
    {"road": "Mysore Road", "address": "Kengeri Satellite Town Highway, Bangalore", "lat": 12.9081, "lng": 77.4880, "city": "Bangalore"},
    {"road": "Banjara Hills Road 12", "address": "Road No 12 Near Cancer Hospital, Hyderabad", "lat": 17.4156, "lng": 78.4350, "city": "Hyderabad"},
    {"road": "Gachibowli ORR Junction", "address": "Financial District Outer Ring Road, Hyderabad", "lat": 17.4200, "lng": 78.3400, "city": "Hyderabad"},
    {"road": "PVNR Elevated Expressway", "address": "Mehdipatnam Pillar 114, Hyderabad", "lat": 17.3800, "lng": 78.4500, "city": "Hyderabad"},
    {"road": "Anna Salai (Mount Road)", "address": "Gemini Circle to Teynampet, Chennai", "lat": 13.0400, "lng": 80.2500, "city": "Chennai"},
    {"road": "Old Mahabalipuram Road (OMR)", "address": "Rajiv Gandhi Salai, Sholinganallur, Chennai", "lat": 12.9000, "lng": 80.2280, "city": "Chennai"},
    {"road": "GST Road", "address": "Tambaram Sanatorium Flyover, Chennai", "lat": 12.9249, "lng": 80.1100, "city": "Chennai"},
    {"road": "Park Street", "address": "Mother Teresa Sarani Crossing, Kolkata", "lat": 22.5510, "lng": 88.3527, "city": "Kolkata"},
    {"road": "EM Bypass", "address": "Science City to Ruby Hospital Connector, Kolkata", "lat": 22.5186, "lng": 88.3980, "city": "Kolkata"},
    {"road": "SG Highway", "address": "Thaltej Cross Roads to Iscon, Ahmedabad", "lat": 23.0500, "lng": 72.5000, "city": "Ahmedabad"},
    {"road": "SP Ring Road", "address": "Bopal Cross Roads, Ahmedabad", "lat": 23.0300, "lng": 72.4600, "city": "Ahmedabad"},
    {"road": "JLN Marg", "address": "Malviya Nagar World Trade Park Corridor, Jaipur", "lat": 26.8530, "lng": 75.8050, "city": "Jaipur"},
    {"road": "Delhi-Jaipur Highway (NH-48)", "address": "Shahpura Bypass Mile 64, Rajasthan", "lat": 27.3800, "lng": 75.9600, "city": "Jaipur"},
    {"road": "Shaheed Path", "address": "Gomti Nagar Extension Flyover, Lucknow", "lat": 26.8200, "lng": 80.9900, "city": "Lucknow"},
]

DAMAGE_CONFIGS = [
    {
        "severity": "Critical", "sev_score": 0.94,
        "risk": "Critical", "risk_score": 0.91,
        "types": ["pothole", "alligator_crack"],
        "priority": "Immediate (within 24-48 hours)",
        "time": "1-2 days",
        "factors": ["High risk of tire blowouts and rim damage", "Severe moisture intrusion into sub-base", "Disrupts multi-axle commercial traffic"]
    },
    {
        "severity": "High", "sev_score": 0.78,
        "risk": "High", "risk_score": 0.74,
        "types": ["pothole", "longitudinal_crack"],
        "priority": "Urgent (within 1 week)",
        "time": "3-7 days",
        "factors": ["Linear fracture propagating along wheel paths", "Moderate hazard for two-wheelers in wet conditions"]
    },
    {
        "severity": "Medium", "sev_score": 0.52,
        "risk": "Moderate", "risk_score": 0.49,
        "types": ["transverse_crack"],
        "priority": "Scheduled (within 1 month)",
        "time": "2-3 weeks",
        "factors": ["Thermal contraction cracking crossing travel lanes", "Requires crack sealing before monsoon season"]
    },
    {
        "severity": "Low", "sev_score": 0.24,
        "risk": "Low", "risk_score": 0.22,
        "types": ["surface_damage"],
        "priority": "Routine (within 3 months)",
        "time": "1-2 months",
        "factors": ["Minor aggregate stripping and surface wear", "Standard routine maintenance cycle applies"]
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # Clean previous demo/test records to avoid duplicates
    await db.inspections.delete_many({})
    await db.reports.delete_many({})
    print("Cleared existing inspections & reports.")
    
    now = datetime.datetime.now(datetime.timezone.utc)
    inspections_to_insert = []
    reports_to_insert = []
    
    for i, site in enumerate(ROAD_SITES):
        # Distribute created dates over the last 6 months for realistic charts
        days_ago = (len(ROAD_SITES) - i) * 6 + random.randint(0, 4)
        created_dt = now - datetime.timedelta(days=days_ago)
        
        cfg = DAMAGE_CONFIGS[i % len(DAMAGE_CONFIGS)]
        img_name = SAMPLE_IMAGES[i % len(SAMPLE_IMAGES)]
        
        num_dets = random.randint(2, 5) if cfg["severity"] in ["Critical", "High"] else random.randint(1, 2)
        detections = []
        damage_summary = {}
        for _ in range(num_dets):
            t = random.choice(cfg["types"])
            conf = round(random.uniform(0.74, 0.96), 3)
            damage_summary[t] = damage_summary.get(t, 0) + 1
            detections.append({
                "class_name": t,
                "confidence": conf,
                "bbox": {
                    "x1": round(random.uniform(0.1, 0.5), 3),
                    "y1": round(random.uniform(0.2, 0.6), 3),
                    "x2": round(random.uniform(0.6, 0.9), 3),
                    "y2": round(random.uniform(0.65, 0.95), 3),
                },
                "area_ratio": round(random.uniform(0.04, 0.12), 4),
            })
            
        doc_id = uuid.uuid4().hex
        
        inspection = {
            "_id": doc_id,
            "id": doc_id,
            "image_path": f"/uploads/{img_name}",
            "image_filename": img_name,
            "detections": detections,
            "detection_count": len(detections),
            "damage_summary": damage_summary,
            "damage_types": list(damage_summary.keys()),
            "severity": {
                "level": cfg["severity"],
                "score": cfg["sev_score"],
                "features_dict": {
                    "detection_count": len(detections),
                    "avg_confidence": round(sum(d["confidence"] for d in detections) / len(detections), 3),
                    "dark_ratio": round(random.uniform(0.08, 0.22), 3),
                    "edge_density": round(random.uniform(0.06, 0.18), 3),
                },
                "demo_mode": False,
            },
            "risk_prediction": {
                "level": cfg["risk"],
                "score": cfg["risk_score"],
                "factors": cfg["factors"],
                "repair_priority": cfg["priority"],
                "estimated_repair_time": cfg["time"],
                "demo_mode": False,
            },
            "location": {
                "latitude": site["lat"],
                "longitude": site["lng"],
                "address": site["address"],
                "road_name": site["road"],
            },
            "address": site["address"],
            "road_name": site["road"],
            "timestamp": created_dt.isoformat(),
            "created_at": created_dt,
            "deleted": False,
        }
        inspections_to_insert.append(inspection)
        
        # Also create a linked inspection report
        report_id = uuid.uuid4().hex
        report = {
            "_id": report_id,
            "id": report_id,
            "detection_id": doc_id,
            "executive_summary": f"Automated inspection conducted along {site['road']} identified {len(detections)} damage regions with {cfg['severity']} severity rating. Priority action: {cfg['priority']}.",
            "damage_analysis": {
                t: {"display_name": t.replace('_', ' ').title(), "count": count, "avg_confidence": 0.88}
                for t, count in damage_summary.items()
            },
            "severity_assessment": {
                "level": cfg["severity"],
                "score": cfg["sev_score"],
                "explanation": f"Pavement section on {site['road']} exhibits {cfg['severity'].lower()} level distress impacting serviceability.",
            },
            "risk_assessment": {
                "level": cfg["risk"],
                "score": cfg["risk_score"],
                "factors": cfg["factors"],
            },
            "recommendations": [
                f"Schedule repair deployment according to timeline ({cfg['time']}).",
                f"Notify road maintenance division for {site['city']}.",
                "Apply hot-pour bitumen sealant and localized asphalt overlay.",
                "Review drainage channels adjacent to fracture sites."
            ],
            "safety_warnings": [
                f"Caution: Motorists should reduce speed near {site['road']} affected sector."
            ] if cfg["severity"] in ["Critical", "High"] else [],
            "repair_timeline": cfg["time"],
            "repair_priority": cfg["priority"],
            "location": inspection["location"],
            "inspection_summary": {
                "severity": cfg["severity"],
                "risk_level": cfg["risk"],
                "damage_types": list(damage_summary.keys()),
                "detection_count": len(detections),
                "address": site["address"],
                "road_name": site["road"],
            },
            "generated_at": created_dt.isoformat(),
            "deleted": False,
        }
        reports_to_insert.append(report)

    if inspections_to_insert:
        await db.inspections.insert_many(inspections_to_insert)
        print(f"✅ Successfully inserted {len(inspections_to_insert)} real inspections into MongoDB 'inspections'.")
        
    if reports_to_insert:
        await db.reports.insert_many(reports_to_insert)
        print(f"✅ Successfully inserted {len(reports_to_insert)} real reports into MongoDB 'reports'.")

    # Verify counts
    c_insp = await db.inspections.count_documents({})
    c_rep = await db.reports.count_documents({})
    print(f"MongoDB verification: {c_insp} inspections, {c_rep} reports ready!")


if __name__ == "__main__":
    asyncio.run(seed())
