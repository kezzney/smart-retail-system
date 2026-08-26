"""YOLO Object Detection Service for Retail Shelf Monitoring.

Provides CPU-compatible inference with configurable confidence/IOU thresholds,
graceful handling of missing weights, and normalized bounding box outputs.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any, Union
from io import BytesIO

from PIL import Image
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Lazy global detector instance
_detector_instance: Optional["YOLODetector"] = None


class YOLODetector:
    """Ultralytics YOLO wrapper for retail shelf product detection."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize the detector with weights from model_path."""
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load YOLO model weights cleanly with fallback."""
        try:
            from ultralytics import YOLO

            logger.info("Loading YOLO model from %s...", self.model_path)
            self._model = YOLO(self.model_path)
            logger.info("YOLO model loaded successfully: task=%s", getattr(self._model, "task", "detect"))
        except Exception as exc:
            logger.error("Failed to load YOLO model from %s: %s", self.model_path, exc)
            self._model = None

    @property
    def is_available(self) -> bool:
        """Return True if model is loaded and ready for inference."""
        return self._model is not None

    def detect(
        self,
        image_input: Union[str, bytes, Image.Image, np.ndarray],
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        imgsz: int = 640,
    ) -> Dict[str, Any]:
        """Perform object detection on the provided image input.

        Parameters:
            image_input: File path (str), raw image bytes, PIL Image, or numpy array.
            conf: Confidence threshold (default from settings).
            iou: NMS IOU threshold (default from settings).
            imgsz: Inference input resolution.

        Returns:
            Structured dictionary matching DetectionResponse schema.
        """
        if not self.is_available:
            # Try reloading once in case weights were downloaded later
            self._load_model()
            if not self.is_available:
                raise RuntimeError(
                    f"YOLO model is not available at '{self.model_path}'. "
                    "Ensure weights are downloaded or configure YOLO_MODEL_PATH."
                )

        confidence_threshold = conf if conf is not None else settings.DEFAULT_CONFIDENCE_THRESHOLD
        iou_threshold = iou if iou is not None else settings.DEFAULT_IOU_THRESHOLD

        # Load and convert image to PIL Image for dimension checking
        pil_image = self._prepare_pil_image(image_input)
        img_w, img_h = pil_image.size

        # Run inference and measure latency
        t_start = time.perf_counter()
        results = self._model.predict(
            source=pil_image,
            conf=confidence_threshold,
            iou=iou_threshold,
            imgsz=imgsz,
            verbose=False,
            device="cpu",
        )
        inference_time_ms = round((time.perf_counter() - t_start) * 1000, 2)

        detections: List[Dict[str, Any]] = []

        if results and len(results) > 0:
            result_item = results[0]
            boxes = result_item.boxes

            if boxes is not None and len(boxes) > 0:
                xyxy = boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2] in pixels
                confs = boxes.conf.cpu().numpy()
                classes = boxes.cls.cpu().numpy().astype(int)

                for i in range(len(xyxy)):
                    x1, y1, x2, y2 = xyxy[i]
                    cls_id = int(classes[i])
                    class_name = self._model.names.get(cls_id, "product") if hasattr(self._model, "names") else "product"

                    # Normalize coordinates to [0.0, 1.0]
                    norm_x_min = max(0.0, min(1.0, float(x1 / img_w)))
                    norm_y_min = max(0.0, min(1.0, float(y1 / img_h)))
                    norm_x_max = max(0.0, min(1.0, float(x2 / img_w)))
                    norm_y_max = max(0.0, min(1.0, float(y2 / img_h)))

                    detections.append({
                        "x_min": round(norm_x_min, 4),
                        "y_min": round(norm_y_min, 4),
                        "x_max": round(norm_x_max, 4),
                        "y_max": round(norm_y_max, 4),
                        "confidence": round(float(confs[i]), 4),
                        "class_id": cls_id,
                        "class_name": class_name,
                    })

        return {
            "total_detections": len(detections),
            "inference_time_ms": inference_time_ms,
            "image_width": img_w,
            "image_height": img_h,
            "confidence_threshold": confidence_threshold,
            "detections": detections,
        }

    @staticmethod
    def _prepare_pil_image(image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Image.Image:
        """Convert various input types into a standard RGB PIL Image."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        elif isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise FileNotFoundError(f"Image file not found: {image_input}")
            return Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            return Image.open(BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input).convert("RGB")
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")


def get_detector(model_path: Optional[str] = None) -> YOLODetector:
    """Return singleton or initialized YOLODetector instance."""
    global _detector_instance
    if _detector_instance is None or (model_path and _detector_instance.model_path != model_path):
        _detector_instance = YOLODetector(model_path=model_path)
    return _detector_instance
