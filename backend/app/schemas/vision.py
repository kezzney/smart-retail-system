"""Computer Vision & Shelf Monitoring Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized bounding box coordinates with class prediction."""

    x_min: float = Field(..., description="Normalized left coordinate (0.0 to 1.0)")
    y_min: float = Field(..., description="Normalized top coordinate (0.0 to 1.0)")
    x_max: float = Field(..., description="Normalized right coordinate (0.0 to 1.0)")
    y_max: float = Field(..., description="Normalized bottom coordinate (0.0 to 1.0)")
    confidence: float = Field(..., description="Detection confidence score (0.0 to 1.0)")
    class_id: int = Field(..., description="YOLO class identifier")
    class_name: str = Field(..., description="Detected class label (e.g. 'product', 'bottle')")


class DetectionResponse(BaseModel):
    """Response schema for object detection requests."""

    total_detections: int = Field(..., description="Total bounding boxes detected")
    inference_time_ms: float = Field(..., description="Inference latency in milliseconds")
    image_width: int = Field(..., description="Input image width in pixels")
    image_height: int = Field(..., description="Input image height in pixels")
    confidence_threshold: float = Field(..., description="Confidence threshold used for filtering")
    detections: List[BoundingBox] = Field(default_factory=list, description="List of detected bounding boxes")


class ShelfGap(BaseModel):
    """Estimated gap / potential out-of-stock region on a shelf tier."""

    shelf_row: int = Field(..., description="Shelf tier index (0 = top shelf, 1 = second, etc.)")
    gap_x_start: float = Field(..., description="Normalized left boundary of detected gap")
    gap_x_end: float = Field(..., description="Normalized right boundary of detected gap")
    gap_width: float = Field(..., description="Normalized width of the gap space")
    estimated_missing_units: int = Field(..., description="Estimated product units missing in this gap")
    severity: str = Field(..., description="Gap severity level: 'LOW', 'MEDIUM', 'HIGH'")


class ShelfAnalysisResponse(BaseModel):
    """Comprehensive shelf monitoring and occupancy analysis response."""

    total_detected_products: int = Field(..., description="Total visible facing products detected")
    estimated_shelf_capacity: int = Field(..., description="Estimated full shelf unit capacity")
    estimated_occupancy_pct: float = Field(..., description="Estimated percentage of shelf occupied (0.0 - 100.0)")
    stock_status: str = Field(..., description="Overall shelf status: 'OPTIMAL', 'MODERATE', 'LOW_STOCK', 'CRITICAL_STOCKOUT'")
    detected_gaps: List[ShelfGap] = Field(default_factory=list, description="List of detected empty shelf spaces")
    detections: List[BoundingBox] = Field(default_factory=list, description="Raw bounding boxes detected")
    inference_time_ms: float = Field(..., description="Total processing & inference time in ms")
    image_width: int = Field(..., description="Image width in pixels")
    image_height: int = Field(..., description="Image height in pixels")
    disclaimer: str = Field(
        default="Values are computer vision estimates based on visible shelf front-facings, not ground-truth inventory counts.",
        description="Business intelligence estimation disclaimer",
    )


class SampleImageItem(BaseModel):
    """Metadata for pre-configured demo shelf image samples."""

    sample_id: str = Field(..., description="Unique sample identifier (e.g. 'sample_01')")
    filename: str = Field(..., description="Image filename in dataset")
    split: str = Field(..., description="Dataset split: 'val' or 'test'")
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Short scene description")


class SampleImagesResponse(BaseModel):
    """List of available sample shelf images for demo evaluation."""

    total: int
    samples: List[SampleImageItem]
