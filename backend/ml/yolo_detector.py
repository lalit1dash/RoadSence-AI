"""
Module A: Road Damage Detection
YOLO-based road damage object detection.

DEMO MODE: When YOLO weights are not available, the system runs in DEMO MODE.
Demo detections are clearly labeled and NOT real ML predictions.
Uses OpenCV when available, with a full PIL fallback.
"""

from __future__ import annotations

import base64
import io
import logging
import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    cv2 = None
    np = None
    HAS_CV2 = False

logger = logging.getLogger(__name__)

DAMAGE_CLASSES = [
    "pothole",
    "longitudinal_crack",
    "transverse_crack",
    "alligator_crack",
    "surface_damage",
]

# RGB colors for PIL
CLASS_COLORS_RGB = {
    "pothole": (239, 68, 68),            # Red
    "longitudinal_crack": (249, 115, 22), # Orange
    "transverse_crack": (234, 179, 8),   # Yellow
    "alligator_crack": (168, 85, 247),   # Purple
    "surface_damage": (6, 182, 212),     # Cyan
}

CLASS_DISPLAY_NAMES = {
    "pothole": "Pothole",
    "longitudinal_crack": "Longitudinal Crack",
    "transverse_crack": "Transverse Crack",
    "alligator_crack": "Alligator Crack",
    "surface_damage": "Surface Damage",
}


class RoadDamageDetector:
    """
    Road damage detector using YOLO model.
    Falls back to DEMO MODE if weights are unavailable.
    """

    def __init__(self, weights_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.demo_mode = True
        self.model = None

        if weights_path and Path(weights_path).exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(weights_path)
                self.demo_mode = False
                logger.info(f"YOLO model loaded from {weights_path}")
            except ImportError:
                logger.warning("ultralytics not installed. Running in DEMO MODE.")
            except Exception as e:
                logger.warning(f"Failed to load YOLO weights: {e}. Running in DEMO MODE.")
        else:
            logger.info("No YOLO weights provided. Running in DEMO MODE.")

    def detect(self, image_path: str) -> dict:
        """
        Detect road damage in an image.
        Returns detections, annotated image (base64), and metadata.
        """
        # Always open via PIL for cross-platform reliability
        try:
            pil_image = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Could not load image from {image_path}: {e}")

        w, h = pil_image.size

        if self.demo_mode:
            detections = self._demo_detect(w, h)
        else:
            detections = self._yolo_detect(image_path, w, h)

        # Draw detections
        annotated_pil = self._draw_detections_pil(pil_image.copy(), detections)
        annotated_b64 = self._pil_to_base64(annotated_pil)

        damage_summary = {}
        for d in detections:
            cls = d["class_name"]
            damage_summary[cls] = damage_summary.get(cls, 0) + 1

        return {
            "detections": detections,
            "annotated_image": annotated_b64,
            "annotated_image_base64": annotated_b64,
            "demo_mode": self.demo_mode,
            "total_count": len(detections),
            "total_detections": len(detections),
            "damage_summary": damage_summary,
            "image_dimensions": {"width": w, "height": h},
        }

    def _yolo_detect(self, image_path: str, w: int, h: int) -> list:
        """Run actual YOLO inference if ultralytics loaded."""
        results = self.model(image_path, conf=self.confidence_threshold)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class_name": DAMAGE_CLASSES[cls_id] if cls_id < len(DAMAGE_CLASSES) else "unknown",
                    "confidence": round(conf, 3),
                    "bbox": {"x1": x1 / w, "y1": y1 / h, "x2": x2 / w, "y2": y2 / h},
                    "area_ratio": round(((x2 - x1) * (y2 - y1)) / (w * h), 4),
                })
        return detections

    def _demo_detect(self, w: int, h: int) -> list:
        """
        DEMO MODE: Generate realistic simulated detections.
        These are NOT real ML predictions.
        """
        num_detections = random.randint(2, 5)
        detections = []

        weights = [0.35, 0.25, 0.20, 0.12, 0.08]
        selected_classes = random.choices(DAMAGE_CLASSES, weights=weights, k=num_detections)

        used_areas = []
        for cls in selected_classes:
            for _ in range(25):
                box_w = random.uniform(0.10, 0.28)
                box_h = random.uniform(0.08, 0.22)
                x1 = random.uniform(0.05, 0.95 - box_w)
                y1 = random.uniform(0.15, 0.90 - box_h)
                x2 = x1 + box_w
                y2 = y1 + box_h

                overlap = False
                for ua in used_areas:
                    if x1 < ua[2] and x2 > ua[0] and y1 < ua[3] and y2 > ua[1]:
                        overlap = True
                        break

                if not overlap:
                    used_areas.append((x1, y1, x2, y2))
                    confidence = round(random.uniform(0.72, 0.96), 3)
                    detections.append({
                        "class_name": cls,
                        "confidence": confidence,
                        "bbox": {"x1": round(x1, 4), "y1": round(y1, 4), "x2": round(x2, 4), "y2": round(y2, 4)},
                        "area_ratio": round(box_w * box_h, 4),
                    })
                    break

        return detections

    def _draw_detections_pil(self, img: Image.Image, detections: list) -> Image.Image:
        """Draw bounding boxes and labels using PIL."""
        w, h = img.size
        draw = ImageDraw.Draw(img)

        # Draw DEMO MODE watermark banner at the top
        if self.demo_mode:
            banner_h = max(28, int(h * 0.045))
            draw.rectangle([(0, 0), (w, banner_h)], fill=(15, 23, 42, 220))
            draw.text((12, int(banner_h * 0.2)), "DEMO MODE — Simulated Detections (RoadSense AI)", fill=(245, 158, 11))

        for det in detections:
            cls = det["class_name"]
            conf = det["confidence"]
            bbox = det["bbox"]

            x1 = int(bbox["x1"] * w)
            y1 = int(bbox["y1"] * h)
            x2 = int(bbox["x2"] * w)
            y2 = int(bbox["y2"] * h)

            color = CLASS_COLORS_RGB.get(cls, (239, 68, 68))

            # Bounding box border (thickness 3)
            for offset in range(3):
                draw.rectangle([(x1 - offset, y1 - offset), (x2 + offset, y2 + offset)], outline=color)

            # Label badge
            label = f"{CLASS_DISPLAY_NAMES.get(cls, cls)}: {conf:.0%}"
            label_w = len(label) * 8 + 12
            label_h = 20
            draw.rectangle([(x1, max(0, y1 - label_h)), (x1 + label_w, y1)], fill=color)
            draw.text((x1 + 4, max(2, y1 - label_h + 2)), label, fill=(255, 255, 255))

        return img

    def _pil_to_base64(self, img: Image.Image) -> str:
        """Convert PIL image to JPEG base64 string."""
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
