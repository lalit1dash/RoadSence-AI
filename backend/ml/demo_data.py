"""
RoadSense – Demo Mode Data Generators
======================================
⚠️  DEMO MODE – No real ML models are loaded here.
     All functions return realistic synthetic data for development and testing.

Replace these implementations with real model inference when YOLO weights,
severity classifiers, and risk models are available.
"""
from __future__ import annotations

import random
from typing import Dict, List, Any

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

DAMAGE_CLASSES: List[str] = [
    "alligator_crack",
    "longitudinal_crack",
    "transverse_crack",
    "pothole",
    "rutting",
    "raveling",
    "edge_crack",
    "patching",
    "depression",
    "bleeding",
]

# BGR color codes for OpenCV annotation
CLASS_COLORS: Dict[str, tuple] = {
    "alligator_crack":    (0,   0,   255),   # Red
    "longitudinal_crack": (0,   165, 255),   # Orange
    "transverse_crack":   (0,   255, 255),   # Yellow
    "pothole":            (128, 0,   128),   # Purple
    "rutting":            (255, 0,   0),     # Blue
    "raveling":           (0,   128, 255),   # Light orange
    "edge_crack":         (255, 0,   255),   # Magenta
    "patching":           (0,   255, 0),     # Green
    "depression":         (128, 128, 0),     # Teal
    "bleeding":           (0,   0,   128),   # Dark red
}

# Severity weights per damage class (higher = more severe)
_SEVERITY_WEIGHTS: Dict[str, float] = {
    "pothole":            1.0,
    "alligator_crack":    0.9,
    "rutting":            0.85,
    "depression":         0.8,
    "longitudinal_crack": 0.65,
    "transverse_crack":   0.6,
    "edge_crack":         0.55,
    "raveling":           0.5,
    "bleeding":           0.4,
    "patching":           0.2,
}


# ──────────────────────────────────────────────────────────────────────────────
# Module A – Detection (DEMO)
# ──────────────────────────────────────────────────────────────────────────────

def generate_demo_detections(image_width: int, image_height: int) -> List[Dict[str, Any]]:
    """
    ⚠️  DEMO MODE – Generate realistic synthetic detection results.

    Simulates YOLO model output with bounding boxes spread across different
    image regions to mimic real road damage patterns.

    Args:
        image_width:  Width of the uploaded image in pixels.
        image_height: Height of the uploaded image in pixels.

    Returns:
        List of detection dicts compatible with the Detection schema.
    """
    num_detections = random.randint(2, 6)
    # Divide image into a 3×2 grid; pick unique cells for more natural spread
    grid_cells = [(col, row) for row in range(2) for col in range(3)]
    random.shuffle(grid_cells)
    selected_cells = grid_cells[:num_detections]

    detections: List[Dict[str, Any]] = []

    for col, row in selected_cells:
        damage_class = random.choice(DAMAGE_CLASSES)
        confidence = round(random.uniform(0.55, 0.97), 4)

        # Cell boundaries
        cell_w = image_width / 3
        cell_h = image_height / 2
        cell_x = col * cell_w
        cell_y = row * cell_h

        # Random bbox within cell with some margin
        margin_x = cell_w * 0.1
        margin_y = cell_h * 0.1
        x1 = random.uniform(cell_x + margin_x, cell_x + cell_w * 0.5)
        y1 = random.uniform(cell_y + margin_y, cell_y + cell_h * 0.5)
        x2 = random.uniform(x1 + cell_w * 0.2, cell_x + cell_w - margin_x)
        y2 = random.uniform(y1 + cell_h * 0.2, cell_y + cell_h - margin_y)

        # Clamp to image bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2 = min(image_width, x2)
        y2 = min(image_height, y2)

        area = (x2 - x1) * (y2 - y1)
        area_ratio = round(area / (image_width * image_height), 4)

        detections.append({
            "class_name": damage_class,
            "confidence": confidence,
            "bbox": {"x1": round(x1, 2), "y1": round(y1, 2), "x2": round(x2, 2), "y2": round(y2, 2)},
            "area_ratio": area_ratio,
        })

    return detections


# ──────────────────────────────────────────────────────────────────────────────
# Module B – Severity Classification (DEMO)
# ──────────────────────────────────────────────────────────────────────────────

def classify_severity_demo(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ⚠️  DEMO MODE – Compute severity from detection metadata.

    Combines damage type weights, confidence scores, and total covered area
    to produce a 0–100 severity score, then maps to a level bucket.

    Args:
        detections: List of detection dicts (from generate_demo_detections).

    Returns:
        Dict matching the SeverityResult schema.
    """
    if not detections:
        return {
            "level": "Low",
            "score": 5.0,
            "features": {"detection_count": 0, "total_area_ratio": 0.0, "weighted_damage_score": 0.0},
            "demo_mode": True,
        }

    total_area = sum(d.get("area_ratio", 0) for d in detections)
    detection_count = len(detections)

    weighted_score = sum(
        _SEVERITY_WEIGHTS.get(d["class_name"], 0.5) * d["confidence"]
        for d in detections
    ) / detection_count

    # Composite score (0–100)
    score = min(100.0, (
        weighted_score * 50 +
        min(total_area * 200, 30) +
        min(detection_count * 3, 20)
    ))
    score = round(score, 2)

    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "score": score,
        "features": {
            "detection_count": detection_count,
            "total_area_ratio": round(total_area, 4),
            "weighted_damage_score": round(weighted_score, 4),
            "avg_confidence": round(
                sum(d["confidence"] for d in detections) / detection_count, 4
            ),
        },
        "demo_mode": True,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Module C – Risk Prediction (DEMO)
# ──────────────────────────────────────────────────────────────────────────────

def predict_risk_demo(
    severity_result: Dict[str, Any],
    detections: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    ⚠️  DEMO MODE – Predict repair risk from severity and detection data.

    Uses rule-based logic that mirrors what a trained classifier would output,
    with contextual risk factor generation for realistic reporting.

    Args:
        severity_result: Output dict from classify_severity_demo.
        detections:      List of detection dicts.

    Returns:
        Dict matching the RiskPrediction schema.
    """
    severity_score = severity_result.get("score", 0.0)
    severity_level = severity_result.get("level", "Low")
    damage_classes = {d["class_name"] for d in detections}

    # Risk score is derived from severity with some jitter
    jitter = random.uniform(-5, 10)
    risk_score = round(min(100.0, max(0.0, severity_score + jitter)), 2)

    if risk_score >= 75:
        risk_level = "Critical"
        repair_priority = "Immediate"
        estimated_repair_time = "Within 24 hours"
    elif risk_score >= 50:
        risk_level = "High"
        repair_priority = "High"
        estimated_repair_time = "Within 1 week"
    elif risk_score >= 25:
        risk_level = "Medium"
        repair_priority = "Medium"
        estimated_repair_time = "Within 1 month"
    else:
        risk_level = "Low"
        repair_priority = "Low"
        estimated_repair_time = "Within 3 months"

    # Build contextual risk factors
    factors: List[str] = []
    if "pothole" in damage_classes:
        factors.append("Active pothole detected – high vehicle damage risk")
    if "alligator_crack" in damage_classes:
        factors.append("Alligator cracking indicates structural base failure")
    if "rutting" in damage_classes:
        factors.append("Rutting presents hydroplaning hazard in wet conditions")
    if severity_level in ("High", "Critical"):
        factors.append(f"Severity classified as {severity_level} – urgent attention required")
    if len(detections) >= 4:
        factors.append(f"Multiple damage zones detected ({len(detections)}) indicating widespread deterioration")
    if severity_result.get("features", {}).get("total_area_ratio", 0) > 0.15:
        factors.append("Damage covers more than 15% of visible road surface")

    # Ensure at least one generic factor
    if not factors:
        factors.append("Minor surface degradation detected – routine monitoring recommended")

    return {
        "level": risk_level,
        "score": risk_score,
        "factors": factors,
        "repair_priority": repair_priority,
        "estimated_repair_time": estimated_repair_time,
        "demo_mode": True,
    }
