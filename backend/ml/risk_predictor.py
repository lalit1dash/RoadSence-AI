"""
Module C: Road Risk Prediction
Predicts road risk level and repair urgency from severity and detection data.
"""

import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

RISK_LEVELS = ["Low", "Moderate", "High", "Critical"]


class RiskPredictor:
    """
    Predicts road risk and repair priority based on damage analysis results.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.demo_mode = True
        self.model = None

        if model_path:
            try:
                import joblib
                from pathlib import Path
                if Path(model_path).exists():
                    self.model = joblib.load(model_path)
                    self.demo_mode = False
                    logger.info(f"Risk predictor loaded from {model_path}")
                else:
                    logger.info("Risk model path not found. Running in DEMO MODE.")
            except ImportError:
                logger.warning("joblib not installed. Running in DEMO MODE.")
            except Exception as e:
                logger.warning(f"Failed to load risk model: {e}. Running in DEMO MODE.")
        else:
            logger.info("No risk model provided. Running in DEMO MODE.")

    def predict(
        self,
        severity_result: dict,
        detections: list,
        location_data: Optional[dict] = None,
    ) -> dict:
        """
        Predict road risk level and repair priority.

        Score formula:
            risk_score = severity_score * 0.5
                       + detection_density * 0.3
                       + damage_diversity * 0.2

        Returns:
            dict with: level, score, factors, repair_priority,
                       estimated_repair_time, demo_mode
        """
        severity_score = float(severity_result.get("score", 0.5))
        severity_level = severity_result.get("level", "Medium")

        # Detection density: normalise count to 0-1 (cap at 10)
        detection_count = len(detections)
        detection_density = min(detection_count / 10.0, 1.0)

        # Damage diversity: fraction of unique damage classes present (5 total)
        unique_classes = {d["class_name"] for d in detections}
        damage_diversity = len(unique_classes) / 5.0

        risk_score = (
            severity_score * 0.5
            + detection_density * 0.3
            + damage_diversity * 0.2
        )
        risk_score = round(min(1.0, max(0.0, risk_score)), 4)

        # Map score to level
        if risk_score < 0.25:
            level = "Low"
        elif risk_score < 0.50:
            level = "Moderate"
        elif risk_score < 0.75:
            level = "High"
        else:
            level = "Critical"

        factors = self._get_factors(severity_level, detections, risk_score)
        repair_priority = self._get_repair_priority(level)
        estimated_repair_time = self._get_repair_time(severity_level, level)

        return {
            "level": level,
            "score": risk_score,
            "factors": factors,
            "repair_priority": repair_priority,
            "estimated_repair_time": estimated_repair_time,
            "demo_mode": self.demo_mode,
        }

    def _get_factors(self, severity: str, detections: list, score: float) -> list:
        """Generate human-readable risk factors based on actual data."""
        factors = []
        detection_count = len(detections)
        class_names = [d["class_name"] for d in detections]
        unique_classes = set(class_names)
        avg_conf = (
            sum(d["confidence"] for d in detections) / detection_count
            if detection_count else 0
        )

        # Severity factor
        factors.append(f"Damage severity assessed as {severity}")

        # Count factor
        if detection_count >= 5:
            factors.append(f"High damage density: {detection_count} distinct damage zones detected")
        elif detection_count >= 2:
            factors.append(f"{detection_count} damage areas identified across the road surface")
        else:
            factors.append(f"{detection_count} damage area detected")

        # Specific damage types
        if "pothole" in unique_classes:
            pothole_count = class_names.count("pothole")
            factors.append(
                f"{'Multiple potholes' if pothole_count > 1 else 'Pothole'} present "
                f"– poses immediate vehicle and safety risk"
            )
        if "alligator_crack" in unique_classes:
            factors.append(
                "Alligator cracking detected – indicates structural base failure"
            )
        if "longitudinal_crack" in unique_classes or "transverse_crack" in unique_classes:
            factors.append(
                "Cracking pattern suggests water infiltration risk during rain"
            )

        # Confidence factor
        if avg_conf > 0.85:
            factors.append(
                f"High detection confidence ({avg_conf:.0%}) supports reliable assessment"
            )
        elif avg_conf > 0.70:
            factors.append(
                f"Moderate detection confidence ({avg_conf:.0%})"
            )

        # Risk score
        factors.append(f"Composite risk score: {score:.2f} / 1.00")

        return factors[:6]  # cap at 6

    def _get_repair_priority(self, risk_level: str) -> str:
        """Map risk level to repair priority string."""
        priority_map = {
            "Critical": "Immediate (24-48 hours)",
            "High":     "Urgent (within 1 week)",
            "Moderate": "Scheduled (within 1 month)",
            "Low":      "Routine (within 3 months)",
        }
        return priority_map.get(risk_level, "Scheduled (within 1 month)")

    def _get_repair_time(self, severity: str, risk_level: str) -> str:
        """Estimate repair duration based on severity and risk level."""
        time_map = {
            ("Critical", "Critical"): "3-5 days (full section reconstruction)",
            ("Critical", "High"):     "2-4 days (major patching and resurfacing)",
            ("High",     "Critical"): "2-3 days (structural repair required)",
            ("High",     "High"):     "1-2 days (extensive patching)",
            ("High",     "Moderate"): "4-8 hours (patching)",
            ("Medium",   "High"):     "4-8 hours (crack sealing + patching)",
            ("Medium",   "Moderate"): "2-4 hours (crack sealing)",
            ("Medium",   "Low"):      "1-2 hours (surface treatment)",
            ("Low",      "Moderate"): "1-2 hours (preventive maintenance)",
            ("Low",      "Low"):      "< 1 hour (minor surface sealing)",
        }
        key = (severity, risk_level)
        if key in time_map:
            return time_map[key]
        # Fallback
        if risk_level == "Critical":
            return "2-5 days"
        if risk_level == "High":
            return "1-2 days"
        if risk_level == "Moderate":
            return "4-8 hours"
        return "1-2 hours"
