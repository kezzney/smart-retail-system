"""Unit & Integration Tests for Computer Vision & Shelf Monitoring."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi import status

from app.schemas.vision import (
    BoundingBox,
    DetectionResponse,
    ShelfGap,
    ShelfAnalysisResponse,
    SampleImagesResponse,
)
from app.services.vision.shelf_analyzer import (
    cluster_shelf_rows,
    analyze_shelf_gaps,
    determine_stock_status,
    analyze_shelf_image,
)
from app.services.vision.detector import YOLODetector


# ─── Schema Tests ─────────────────────────────────────────────────────────────

def test_bounding_box_schema():
    """Verify BoundingBox schema instantiation and constraints."""
    box = BoundingBox(
        x_min=0.1,
        y_min=0.2,
        x_max=0.3,
        y_max=0.5,
        confidence=0.88,
        class_id=0,
        class_name="product",
    )
    assert box.x_min == 0.1
    assert box.confidence == 0.88
    assert box.class_name == "product"


def test_shelf_analysis_response_schema():
    """Verify ShelfAnalysisResponse schema defaults and structure."""
    res = ShelfAnalysisResponse(
        total_detected_products=42,
        estimated_shelf_capacity=50,
        estimated_occupancy_pct=84.0,
        stock_status="MODERATE",
        detected_gaps=[],
        detections=[],
        inference_time_ms=120.5,
        image_width=1920,
        image_height=1080,
    )
    assert res.total_detected_products == 42
    assert res.estimated_occupancy_pct == 84.0
    assert "estimate" in res.disclaimer.lower()


# ─── Shelf Analyzer Algorithm Tests ───────────────────────────────────────────

def test_cluster_shelf_rows_empty():
    """Empty bounding boxes list should return an empty list of rows."""
    assert cluster_shelf_rows([]) == []


def test_cluster_shelf_rows_single_tier():
    """Boxes with similar vertical centers should be clustered into a single row."""
    boxes = [
        {"x_min": 0.5, "y_min": 0.10, "x_max": 0.6, "y_max": 0.30},
        {"x_min": 0.1, "y_min": 0.11, "x_max": 0.2, "y_max": 0.31},
        {"x_min": 0.3, "y_min": 0.09, "x_max": 0.4, "y_max": 0.29},
    ]
    rows = cluster_shelf_rows(boxes, y_tolerance=0.08)
    assert len(rows) == 1
    assert len(rows[0]) == 3
    # Verify row is sorted left-to-right by x_min
    assert rows[0][0]["x_min"] == 0.1
    assert rows[0][1]["x_min"] == 0.3
    assert rows[0][2]["x_min"] == 0.5


def test_cluster_shelf_rows_multi_tier():
    """Boxes at different vertical levels should split into multiple rows."""
    boxes = [
        # Top row (y ~ 0.2)
        {"x_min": 0.1, "y_min": 0.1, "x_max": 0.2, "y_max": 0.3},
        {"x_min": 0.3, "y_min": 0.1, "x_max": 0.4, "y_max": 0.3},
        # Bottom row (y ~ 0.7)
        {"x_min": 0.1, "y_min": 0.6, "x_max": 0.2, "y_max": 0.8},
        {"x_min": 0.3, "y_min": 0.6, "x_max": 0.4, "y_max": 0.8},
    ]
    rows = cluster_shelf_rows(boxes, y_tolerance=0.10)
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert len(rows[1]) == 2


def test_analyze_shelf_gaps_none():
    """Uniformly packed products with normal spacing should report zero gaps."""
    # Average product width = 0.10, gap = 0.02 (much less than 1.3 * 0.10)
    rows = [[
        {"x_min": 0.0, "x_max": 0.10},
        {"x_min": 0.12, "x_max": 0.22},
        {"x_min": 0.24, "x_max": 0.34},
    ]]
    gaps, missing_units = analyze_shelf_gaps(rows, min_gap_multiplier=1.3)
    assert len(gaps) == 0
    assert missing_units == 0


def test_analyze_shelf_gaps_detected():
    """A wide empty gap between products should be detected with correct missing units."""
    # Product width = 0.10, gap from 0.10 to 0.40 (width 0.30 -> ~3 missing units)
    rows = [[
        {"x_min": 0.0, "x_max": 0.10},
        {"x_min": 0.40, "x_max": 0.50},
    ]]
    gaps, missing_units = analyze_shelf_gaps(rows, min_gap_multiplier=1.3)
    assert len(gaps) == 1
    assert gaps[0]["gap_width"] == 0.30
    assert gaps[0]["estimated_missing_units"] == 3
    assert gaps[0]["severity"] == "MEDIUM"
    assert missing_units == 3


def test_determine_stock_status_optimal():
    """Occupancy >= 85% with no high gaps should be OPTIMAL."""
    status_label = determine_stock_status(occupancy_pct=92.0, gaps=[])
    assert status_label == "OPTIMAL"


def test_determine_stock_status_critical():
    """Low occupancy (<40%) should trigger CRITICAL_STOCKOUT."""
    status_label = determine_stock_status(occupancy_pct=35.0, gaps=[])
    assert status_label == "CRITICAL_STOCKOUT"


# ─── Detector Error Handling Tests ────────────────────────────────────────────

def test_detector_missing_model_handling():
    """Detector should raise RuntimeError if model cannot be loaded."""
    detector = YOLODetector(model_path="non_existent_weights_xyz123.pt")
    assert not detector.is_available
    with pytest.raises(RuntimeError) as exc_info:
        detector.detect("dummy_path.jpg")
    assert "not available" in str(exc_info.value).lower()


# ─── API Endpoints Tests ──────────────────────────────────────────────────────

def test_get_samples_endpoint(client):
    """GET /api/v1/vision/samples should return pre-configured sample list."""
    response = client.get("/api/v1/vision/samples")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "samples" in data
    assert data["total"] > 0
    assert data["samples"][0]["sample_id"] == "sample_01"


def test_detect_endpoint_missing_input(client):
    """POST /api/v1/vision/detect without file or sample_id should return 400."""
    response = client.post("/api/v1/vision/detect")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_shelf_analysis_endpoint_missing_input(client):
    """POST /api/v1/vision/shelf-analysis without file or sample_id should return 400."""
    response = client.post("/api/v1/vision/shelf-analysis")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_detect_endpoint_with_mocked_inference(client):
    """POST /api/v1/vision/detect should return DetectionResponse when detector executes."""
    mock_detection_result = {
        "total_detections": 2,
        "inference_time_ms": 45.2,
        "image_width": 1000,
        "image_height": 800,
        "confidence_threshold": 0.25,
        "detections": [
            {
                "x_min": 0.1,
                "y_min": 0.2,
                "x_max": 0.2,
                "y_max": 0.4,
                "confidence": 0.91,
                "class_id": 0,
                "class_name": "product",
            },
            {
                "x_min": 0.25,
                "y_min": 0.2,
                "x_max": 0.35,
                "y_max": 0.4,
                "confidence": 0.85,
                "class_id": 0,
                "class_name": "product",
            },
        ],
    }

    with patch("app.api.v1.vision.get_detector") as mock_get_detector:
        mock_detector = MagicMock()
        mock_detector.detect.return_value = mock_detection_result
        mock_get_detector.return_value = mock_detector

        # Dummy fake image upload
        fake_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
        files = {"file": ("test.jpg", fake_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/vision/detect?conf=0.25", files=files)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_detections"] == 2
        assert len(data["detections"]) == 2
        assert data["confidence_threshold"] == 0.25


def test_shelf_analysis_endpoint_with_mock(client):
    """POST /api/v1/vision/shelf-analysis should return full ShelfAnalysisResponse."""
    mock_detection_result = {
        "total_detections": 3,
        "inference_time_ms": 62.0,
        "image_width": 1200,
        "image_height": 800,
        "confidence_threshold": 0.20,
        "detections": [
            {"x_min": 0.1, "y_min": 0.3, "x_max": 0.2, "y_max": 0.5, "confidence": 0.9, "class_id": 0, "class_name": "product"},
            {"x_min": 0.22, "y_min": 0.3, "x_max": 0.32, "y_max": 0.5, "confidence": 0.88, "class_id": 0, "class_name": "product"},
            {"x_min": 0.65, "y_min": 0.3, "x_max": 0.75, "y_max": 0.5, "confidence": 0.85, "class_id": 0, "class_name": "product"},
        ],
    }

    with patch("app.services.vision.shelf_analyzer.get_detector") as mock_get_det:
        mock_detector = MagicMock()
        mock_detector.detect.return_value = mock_detection_result
        mock_get_det.return_value = mock_detector

        fake_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
        files = {"file": ("shelf.jpg", fake_image_bytes, "image/jpeg")}
        response = client.post("/api/v1/vision/shelf-analysis", files=files)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_detected_products"] == 3
        assert data["estimated_shelf_capacity"] > 3
        assert len(data["detected_gaps"]) >= 1
        assert "disclaimer" in data
