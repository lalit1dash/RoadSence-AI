"""
Module B: Damage Severity Classification
Classifies road damage severity using extracted image features.

DEMO MODE: When a trained model is unavailable, uses rule-based heuristics.
Works seamlessly with PIL and numpy, using cv2 optionally when present.
"""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageFilter
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False

logger = logging.getLogger(__name__)

SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]


class SeverityClassifier:
    """
    Classifies road damage severity based on detection results and image features.
    Falls back to rule-based DEMO MODE if no trained model is available.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.demo_mode = True
        self.model = None

        if model_path and Path(model_path).exists():
            try:
                import joblib
                self.model = joblib.load(model_path)
                self.demo_mode = False
                logger.info(f"Severity classifier loaded from {model_path}")
            except ImportError:
                logger.warning("joblib not installed. Running in DEMO MODE.")
            except Exception as e:
                logger.warning(f"Failed to load severity model: {e}. Running in DEMO MODE.")
        else:
            logger.info("No severity model provided. Running in DEMO MODE.")

    def extract_features(self, image_path: str, detections: list) -> np.ndarray:
        """
        Extract a feature vector from image and detections.
        Features:
            [0] detection_count      - total number of detections
            [1] avg_confidence       - mean confidence of all detections
            [2] max_confidence       - maximum confidence score
            [3] has_pothole          - binary: 1 if pothole detected
            [4] has_long_crack       - binary: 1 if longitudinal_crack detected
            [5] has_trans_crack      - binary: 1 if transverse_crack detected
            [6] has_alligator        - binary: 1 if alligator_crack detected
            [7] has_surface          - binary: 1 if surface_damage detected
            [8] edge_density         - fraction of edge pixels
            [9] dark_ratio           - fraction of pixels below brightness threshold 50
        """
        try:
            pil_img = Image.open(image_path).convert("L")
            w, h = pil_img.size
            gray_arr = np.array(pil_img, dtype=np.uint8)

            if HAS_CV2 and cv2 is not None:
                edges = cv2.Canny(gray_arr, 50, 150)
                edge_density = float(np.count_nonzero(edges)) / (h * w)
            else:
                edge_img = pil_img.filter(ImageFilter.FIND_EDGES)
                edge_arr = np.array(edge_img)
                edge_density = float(np.count_nonzero(edge_arr > 35)) / (h * w)

            dark_ratio = float(np.sum(gray_arr < 50)) / (h * w)
        except Exception as e:
            logger.warning(f"Feature extraction image read failed: {e}. Using defaults.")
            edge_density = 0.05
            dark_ratio = 0.10

        # Detection-based features
        detection_count = len(detections)
        confidences = [d["confidence"] for d in detections] if detections else [0.0]
        avg_confidence = float(np.mean(confidences))
        max_confidence = float(np.max(confidences))

        class_names = {d["class_name"] for d in detections}
        has_pothole = 1.0 if "pothole" in class_names else 0.0
        has_long_crack = 1.0 if "longitudinal_crack" in class_names else 0.0
        has_trans_crack = 1.0 if "transverse_crack" in class_names else 0.0
        has_alligator = 1.0 if "alligator_crack" in class_names else 0.0
        has_surface = 1.0 if "surface_damage" in class_names else 0.0

        return np.array([
            detection_count,
            avg_confidence,
            max_confidence,
            has_pothole,
            has_long_crack,
            has_trans_crack,
            has_alligator,
            has_surface,
            edge_density,
            dark_ratio,
        ], dtype=np.float32)

    def classify(self, image_path: str, detections: list) -> dict:
        """
        Classify damage severity.
        Returns:
            dict with keys: level, score, features_dict, demo_mode
        """
        features = self.extract_features(image_path, detections)

        feature_names = [
            "detection_count", "avg_confidence", "max_confidence",
            "has_pothole", "has_long_crack", "has_trans_crack",
            "has_alligator", "has_surface", "edge_density", "dark_ratio",
        ]
        features_dict = {name: round(float(val), 4) for name, val in zip(feature_names, features)}

        if self.demo_mode:
            level, score = self._rule_based(features)
        else:
            proba = self.model.predict_proba(features.reshape(1, -1))[0]
            level_idx = int(np.argmax(proba))
            level = SEVERITY_LEVELS[level_idx]
            score = float(proba[level_idx])

        return {
            "level": level,
            "score": round(score, 3),
            "features": features.tolist(),
            "features_dict": features_dict,
            "demo_mode": self.demo_mode,
        }

    def _rule_based(self, features: np.ndarray) -> tuple[str, float]:
        """
        Rule-based severity estimation for DEMO MODE.
        """
        count = features[0]
        avg_conf = features[1]
        has_pothole = features[3] == 1.0
        has_alligator = features[6] == 1.0
        edge_density = features[8]

        jitter = random.uniform(-0.04, 0.04)

        if count >= 4 or (has_pothole and has_alligator) or edge_density > 0.15:
            level = "Critical"
            base_score = 0.88 + (count * 0.02)
        elif count >= 3 or (has_pothole and avg_conf > 0.80):
            level = "High"
            base_score = 0.68 + (count * 0.03)
        elif count >= 1:
            level = "Medium"
            base_score = 0.45 + (count * 0.04)
        else:
            level = "Low"
            base_score = 0.20

        score = float(np.clip(base_score + jitter, 0.05, 0.98))
        return level, round(score, 3)
