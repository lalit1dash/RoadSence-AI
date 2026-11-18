"""
Module D: Report Generation
Generates structured inspection reports from ML analysis results.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Text templates keyed by severity / risk level
# ---------------------------------------------------------------------------

_SEVERITY_DESCRIPTIONS = {
    "Critical": (
        "The road surface exhibits critical structural damage requiring immediate intervention. "
        "Multiple severe damage types have been identified that pose significant safety risks "
        "to all road users."
    ),
    "High": (
        "Significant road damage has been detected across the inspected area. "
        "The damage pattern indicates accelerated deterioration that will worsen without prompt action."
    ),
    "Medium": (
        "Moderate road damage is present. While the road remains passable, the detected issues "
        "should be addressed within the scheduled maintenance window to prevent further degradation."
    ),
    "Low": (
        "Minor surface imperfections have been observed. The road is in generally acceptable condition "
        "and requires only routine preventive maintenance."
    ),
}

_RISK_DESCRIPTIONS = {
    "Critical": (
        "Risk assessment indicates a critical safety hazard. Immediate closure or traffic restriction "
        "should be considered pending emergency repair works."
    ),
    "High": (
        "High risk to vehicle safety and road integrity. Urgent repair scheduling is strongly recommended "
        "to prevent accidents and further structural deterioration."
    ),
    "Moderate": (
        "Moderate risk level identified. Standard repair procedures should be planned and executed "
        "within the near-term maintenance schedule."
    ),
    "Low": (
        "Low overall risk. Routine monitoring and preventive maintenance are sufficient at this stage."
    ),
}

_RECOMMENDATIONS = {
    "Critical": [
        "Deploy emergency repair crew within 24-48 hours.",
        "Install warning signs and barriers around high-risk damage zones immediately.",
        "Notify traffic management authority for potential road closure assessment.",
        "Conduct full structural inspection before repair to assess base layer integrity.",
        "Use cold-mix asphalt for emergency pothole filling as interim measure.",
        "Schedule full-depth reclamation or resurfacing after emergency stabilisation.",
    ],
    "High": [
        "Schedule urgent repair works within 1 week.",
        "Apply temporary crack sealant to prevent water infiltration.",
        "Post advisory speed limit signage near damaged sections.",
        "Inspect drainage channels adjacent to cracked areas for blockages.",
        "Prioritise alligator-cracked zones for milling and overlay.",
        "Document and report damage extent to road authority for budget allocation.",
    ],
    "Moderate": [
        "Plan crack sealing and patching within the next maintenance cycle (1 month).",
        "Apply surface treatment to slow crack propagation.",
        "Monitor damage progression with monthly visual inspections.",
        "Ensure proper drainage to reduce water-related deterioration.",
        "Consider micro-surfacing for widespread surface damage areas.",
    ],
    "Low": [
        "Include in routine maintenance schedule (within 3 months).",
        "Apply preventive surface sealant during next maintenance round.",
        "Continue periodic monitoring with quarterly inspections.",
        "Document current condition as baseline for future comparisons.",
    ],
}

_SAFETY_WARNINGS = {
    "Critical": [
        "⚠ IMMEDIATE SAFETY RISK: Critical potholes or structural damage detected.",
        "⚠ Vehicles may sustain tyre or suspension damage in affected zones.",
        "⚠ Motorcyclists and cyclists are at elevated risk of accident.",
        "⚠ Road may be unsafe for heavy vehicles until repaired.",
    ],
    "High": [
        "⚠ Elevated safety risk for high-speed traffic.",
        "⚠ Wet weather significantly increases accident likelihood in damaged sections.",
        "⚠ Recommend advisory speed reduction near identified damage zones.",
    ],
}

_INSPECTOR_NOTES = {
    "Critical": (
        "Automated inspection flagged critical damage levels. Manual on-site verification by a "
        "certified road inspector is strongly advised before finalising repair scope."
    ),
    "High": (
        "Automated analysis detected high-severity damage. Field verification is recommended to "
        "confirm extents and determine appropriate repair methodology."
    ),
    "Medium": (
        "Analysis indicates moderate deterioration. Standard inspection procedures apply. "
        "Review annotated imagery for precise damage locations."
    ),
    "Low": (
        "Minor damage only. Standard monitoring protocols are sufficient. "
        "No immediate field visit required."
    ),
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _damage_display_name(key: str) -> str:
    names = {
        "pothole": "Pothole",
        "longitudinal_crack": "Longitudinal Crack",
        "transverse_crack": "Transverse Crack",
        "alligator_crack": "Alligator Crack",
        "surface_damage": "Surface Damage",
    }
    return names.get(key, key.replace("_", " ").title())


def _build_executive_summary(
    detection_result: dict,
    severity_result: dict,
    risk_result: dict,
) -> str:
    total = detection_result.get("total_count", 0)
    severity = severity_result.get("level", "Unknown")
    risk = risk_result.get("level", "Unknown")
    priority = risk_result.get("repair_priority", "N/A")
    damage_types = list(detection_result.get("damage_summary", {}).keys())
    types_str = (
        ", ".join(_damage_display_name(d) for d in damage_types)
        if damage_types else "no specific damage types"
    )

    return (
        f"Road inspection identified {total} damage instance(s) including {types_str}. "
        f"Overall damage severity is rated {severity} with a {risk} risk level. "
        f"Recommended repair action: {priority}."
    )


def _build_damage_analysis(detection_result: dict) -> dict:
    summary = detection_result.get("damage_summary", {})
    detections = detection_result.get("detections", [])
    analysis = {}

    for cls, count in summary.items():
        cls_dets = [d for d in detections if d["class_name"] == cls]
        avg_conf = (
            sum(d["confidence"] for d in cls_dets) / len(cls_dets) if cls_dets else 0.0
        )
        avg_area = (
            sum(d.get("area_ratio", 0) for d in cls_dets) / len(cls_dets) if cls_dets else 0.0
        )
        analysis[cls] = {
            "display_name": _damage_display_name(cls),
            "count": count,
            "avg_confidence": round(avg_conf, 3),
            "avg_area_ratio": round(avg_area, 4),
        }

    return analysis


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class ReportGenerator:
    """
    Generates comprehensive, structured inspection reports.
    """

    def generate_report(
        self,
        detection_result: dict,
        severity_result: dict,
        risk_result: dict,
        location_data: Optional[dict] = None,
    ) -> dict:
        """
        Generate a full structured inspection report.

        Args:
            detection_result: Output from RoadDamageDetector.detect()
            severity_result:  Output from SeverityClassifier.classify()
            risk_result:      Output from RiskPredictor.predict()
            location_data:    Optional location dict with lat, lng, address, road_name

        Returns:
            Structured report dict.
        """
        severity_level = severity_result.get("level", "Medium")
        risk_level = risk_result.get("level", "Moderate")
        demo_mode = (
            detection_result.get("demo_mode", True)
            or severity_result.get("demo_mode", True)
            or risk_result.get("demo_mode", True)
        )

        executive_summary = _build_executive_summary(
            detection_result, severity_result, risk_result
        )
        damage_analysis = _build_damage_analysis(detection_result)

        severity_assessment = _SEVERITY_DESCRIPTIONS.get(
            severity_level, _SEVERITY_DESCRIPTIONS["Medium"]
        )
        risk_assessment = _RISK_DESCRIPTIONS.get(
            risk_level, _RISK_DESCRIPTIONS["Moderate"]
        )
        recommendations = _RECOMMENDATIONS.get(
            risk_level, _RECOMMENDATIONS["Moderate"]
        )
        safety_warnings = _SAFETY_WARNINGS.get(risk_level, [])
        inspector_notes = _INSPECTOR_NOTES.get(
            severity_level, _INSPECTOR_NOTES["Medium"]
        )

        if demo_mode:
            inspector_notes += (
                " NOTE: This report was generated in DEMO MODE using simulated detections. "
                "Results are illustrative and do not represent real road conditions."
            )

        repair_timeline = risk_result.get("estimated_repair_time", "To be determined")

        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "executive_summary": executive_summary,
            "location": location_data or {},
            "damage_analysis": damage_analysis,
            "severity_assessment": {
                "level": severity_level,
                "score": severity_result.get("score", 0.0),
                "explanation": severity_assessment,
                "features": severity_result.get("features_dict", {}),
            },
            "risk_assessment": {
                "level": risk_level,
                "score": risk_result.get("score", 0.0),
                "explanation": risk_assessment,
                "factors": risk_result.get("factors", []),
            },
            "recommendations": recommendations,
            "safety_warnings": safety_warnings,
            "repair_timeline": repair_timeline,
            "repair_priority": risk_result.get("repair_priority", "Scheduled"),
            "inspector_notes": inspector_notes,
            "detection_summary": {
                "total_count": detection_result.get("total_count", 0),
                "damage_summary": detection_result.get("damage_summary", {}),
                "image_dimensions": detection_result.get("image_dimensions", {}),
            },
            "demo_mode": demo_mode,
        }

        return report
