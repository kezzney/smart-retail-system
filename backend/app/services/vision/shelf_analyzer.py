"""Shelf Monitoring & Stock Occupancy Analysis Service.

Analyzes raw bounding boxes from product detection to infer:
- Shelf row/tier grouping
- Horizontal shelf fill ratio and occupancy percentage
- Out-of-stock gaps between adjacent products
- Estimated missing front-facing units and overall shelf status

Note: All metrics are explicitly calculated as computer vision estimates
based on visible front facings and do not replace ground-truth ERP inventory.
"""

import logging
from typing import List, Dict, Any, Tuple

from app.schemas.vision import BoundingBox, ShelfGap, ShelfAnalysisResponse
from app.services.vision.detector import get_detector

logger = logging.getLogger(__name__)


def cluster_shelf_rows(boxes: List[Dict[str, Any]], y_tolerance: float = 0.08) -> List[List[Dict[str, Any]]]:
    """Group normalized bounding boxes into horizontal shelf tiers based on vertical alignment.

    Parameters:
        boxes: List of bounding box dictionaries with normalized coordinates.
        y_tolerance: Maximum vertical center difference to consider items on the same tier.

    Returns:
        List of shelf rows, where each row is a list of bounding boxes sorted left-to-right.
    """
    if not boxes:
        return []

    # Calculate vertical center for each box
    boxes_with_y = []
    for b in boxes:
        y_center = (b["y_min"] + b["y_max"]) / 2.0
        boxes_with_y.append((y_center, b))

    # Sort boxes from top to bottom
    boxes_with_y.sort(key=lambda item: item[0])

    rows: List[List[Dict[str, Any]]] = []
    current_row: List[Dict[str, Any]] = []
    current_y_anchor: float = -1.0

    for y_center, box in boxes_with_y:
        if current_y_anchor < 0:
            current_row.append(box)
            current_y_anchor = y_center
        elif abs(y_center - current_y_anchor) <= y_tolerance:
            current_row.append(box)
            # Update running average of y_anchor
            current_y_anchor = (current_y_anchor * (len(current_row) - 1) + y_center) / len(current_row)
        else:
            # Sort previous row left-to-right by x_min
            current_row.sort(key=lambda b: b["x_min"])
            rows.append(current_row)
            current_row = [box]
            current_y_anchor = y_center

    if current_row:
        current_row.sort(key=lambda b: b["x_min"])
        rows.append(current_row)

    return rows


def analyze_shelf_gaps(
    rows: List[List[Dict[str, Any]]],
    min_gap_multiplier: float = 1.3,
) -> Tuple[List[Dict[str, Any]], int]:
    """Identify spatial gaps between adjacent products along each shelf tier.

    Parameters:
        rows: Shelf tiers containing bounding boxes sorted left-to-right.
        min_gap_multiplier: Multiplier of average product width to qualify as a gap.

    Returns:
        Tuple of (list of detected ShelfGap dicts, total estimated missing units).
    """
    detected_gaps: List[Dict[str, Any]] = []
    total_missing_units = 0

    for row_idx, row_boxes in enumerate(rows):
        if len(row_boxes) < 2:
            continue

        # Calculate average width of items on this shelf tier
        widths = [b["x_max"] - b["x_min"] for b in row_boxes if (b["x_max"] - b["x_min"]) > 0.01]
        if not widths:
            continue
        avg_width = sum(widths) / len(widths)

        # Check spacing between consecutive bounding boxes
        for i in range(len(row_boxes) - 1):
            left_box = row_boxes[i]
            right_box = row_boxes[i + 1]

            gap_start = left_box["x_max"]
            gap_end = right_box["x_min"]
            gap_w = gap_end - gap_start

            # Check if spacing exceeds threshold for an empty product slot
            if gap_w >= (avg_width * min_gap_multiplier):
                missing_units = max(1, round(gap_w / avg_width))
                total_missing_units += missing_units

                if missing_units == 1:
                    severity = "LOW"
                elif missing_units <= 3:
                    severity = "MEDIUM"
                else:
                    severity = "HIGH"

                detected_gaps.append({
                    "shelf_row": row_idx + 1,  # 1-indexed for display
                    "gap_x_start": round(gap_start, 4),
                    "gap_x_end": round(gap_end, 4),
                    "gap_width": round(gap_w, 4),
                    "estimated_missing_units": missing_units,
                    "severity": severity,
                })

    return detected_gaps, total_missing_units


def determine_stock_status(occupancy_pct: float, gaps: List[Dict[str, Any]]) -> str:
    """Classify overall shelf health status based on occupancy and gap severity."""
    high_severity_gaps = sum(1 for g in gaps if g["severity"] == "HIGH")

    if occupancy_pct >= 85.0 and high_severity_gaps == 0:
        return "OPTIMAL"
    elif occupancy_pct >= 65.0 and high_severity_gaps <= 1:
        return "MODERATE"
    elif occupancy_pct >= 40.0:
        return "LOW_STOCK"
    else:
        return "CRITICAL_STOCKOUT"


def analyze_shelf_image(
    image_input: Any,
    conf: float = 0.20,
    iou: float = 0.45,
) -> ShelfAnalysisResponse:
    """Run end-to-end shelf monitoring pipeline on an image input.

    Flow:
    1. Runs YOLO detector to extract product bounding boxes.
    2. Clusters bounding boxes into shelf tiers.
    3. Analyzes inter-product spacing for empty shelf gaps.
    4. Computes estimated capacity, occupancy percentage, and status.
    5. Returns structured ShelfAnalysisResponse.
    """
    detector = get_detector()
    det_result = detector.detect(image_input=image_input, conf=conf, iou=iou)

    detections = det_result["detections"]
    total_detected = len(detections)

    # Cluster into rows and detect gaps
    rows = cluster_shelf_rows(detections)
    gaps, missing_units = analyze_shelf_gaps(rows)

    # Estimate capacity & occupancy
    estimated_capacity = total_detected + missing_units
    if estimated_capacity == 0:
        occupancy_pct = 0.0
    else:
        occupancy_pct = round((total_detected / estimated_capacity) * 100.0, 1)

    stock_status = determine_stock_status(occupancy_pct, gaps)

    return ShelfAnalysisResponse(
        total_detected_products=total_detected,
        estimated_shelf_capacity=estimated_capacity,
        estimated_occupancy_pct=occupancy_pct,
        stock_status=stock_status,
        detected_gaps=[ShelfGap(**g) for g in gaps],
        detections=[BoundingBox(**d) for d in detections],
        inference_time_ms=det_result["inference_time_ms"],
        image_width=det_result["image_width"],
        image_height=det_result["image_height"],
    )
