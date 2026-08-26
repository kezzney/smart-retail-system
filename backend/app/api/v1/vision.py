"""Computer Vision & Shelf Monitoring API Endpoints."""

import os
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, Response

from app.config import settings
from app.schemas.vision import (
    DetectionResponse,
    ShelfAnalysisResponse,
    SampleImagesResponse,
    SampleImageItem,
)
from app.services.vision.detector import get_detector
from app.services.vision.shelf_analyzer import analyze_shelf_image

router = APIRouter(prefix="/vision", tags=["Computer Vision"])

# Pre-configured demo sample scenes from SKU-110K validation set
PRECONFIGURED_SAMPLES: List[dict] = [
    {
        "sample_id": "sample_01",
        "filename": "val_0.jpg",
        "split": "val",
        "title": "Beverage & Bottled Goods Shelf",
        "description": "High-density multi-tier display of refrigerated and shelf beverages.",
    },
    {
        "sample_id": "sample_02",
        "filename": "val_1.jpg",
        "split": "val",
        "title": "Snack & Packaged Foods Rack",
        "description": "Horizontal snack display with mixed packaging sizes and spacings.",
    },
    {
        "sample_id": "sample_03",
        "filename": "val_10.jpg",
        "split": "val",
        "title": "Grocery Aisle Shelf with Empty Slots",
        "description": "Retail shelf display exhibiting multiple out-of-stock gaps.",
    },
    {
        "sample_id": "sample_04",
        "filename": "val_100.jpg",
        "split": "val",
        "title": "Cosmetics & Health Care Tier",
        "description": "Densely packed compact packages on narrow shelf rows.",
    },
]


def _download_demo_image(filename: str, dest_path: str) -> None:
    """Download a demo image from the configured Hugging Face URL into dest_path atomically."""
    import urllib.request
    import tempfile

    url = f"{settings.DEMO_IMAGES_BASE_URL}/{filename}"
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(dest_path), suffix=".tmp")
    try:
        os.close(tmp_fd)
        urllib.request.urlretrieve(url, tmp_path)
        os.replace(tmp_path, dest_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _resolve_sample_path(sample_id: str) -> str:
    """Find (or download) the filesystem path for a preconfigured sample ID.

    Resolution order:
    1. Local demo image cache  (DEMO_IMAGES_DIR / filename)
    2. Full SKU-110K dataset   (SMART_RETAIL_DATA_ROOT / … / images / split / filename)
    3. Download from Hugging Face and store in DEMO_IMAGES_DIR
    """
    sample = next((s for s in PRECONFIGURED_SAMPLES if s["sample_id"] == sample_id), None)
    if not sample:
        raise HTTPException(
            status_code=404,
            detail=f"Sample '{sample_id}' not found. Available samples: {[s['sample_id'] for s in PRECONFIGURED_SAMPLES]}",
        )

    filename = sample["filename"]

    # 1. Check local demo image cache
    cached_path = os.path.join(settings.DEMO_IMAGES_DIR, filename)
    if os.path.exists(cached_path):
        return cached_path

    # 2. Check full local SKU-110K dataset
    val_dir = os.path.join(
        settings.SMART_RETAIL_DATA_ROOT,
        "01_SKU110K",
        "raw",
        "SKU110K_fixed",
        "images",
        sample["split"],
    )
    local_path = os.path.join(val_dir, filename)
    if os.path.exists(local_path):
        return local_path

    # 3. Download from Hugging Face and cache
    try:
        _download_demo_image(filename, cached_path)
        return cached_path
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Demo image '{filename}' is not available locally and could not be downloaded: {exc}",
        )


@router.get(
    "/samples",
    response_model=SampleImagesResponse,
    summary="List Pre-configured Shelf Demo Images",
    description="Returns metadata for preset SKU-110K sample shelf images available for instant demo detection.",
)
def list_samples():
    """List preset sample shelf images for demo evaluation."""
    items = [SampleImageItem(**s) for s in PRECONFIGURED_SAMPLES]
    return SampleImagesResponse(total=len(items), samples=items)


@router.get(
    "/samples/{sample_id}/image",
    summary="Fetch Sample Image File",
    description="Streams the raw JPEG image for the specified sample ID for browser rendering.",
)
def get_sample_image(sample_id: str):
    """Serve the raw sample shelf image."""
    img_path = _resolve_sample_path(sample_id)
    return FileResponse(img_path, media_type="image/jpeg")


@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Detect Products on Shelf Image",
    description="Runs YOLO object detection on an uploaded shelf image or a pre-configured sample ID.",
)
async def detect_products(
    file: Optional[UploadFile] = File(None, description="Uploaded shelf image file (JPEG/PNG)"),
    sample_id: Optional[str] = Query(None, description="Pre-configured sample ID (e.g. 'sample_01')"),
    conf: float = Query(0.25, ge=0.01, le=1.0, description="Detection confidence threshold"),
    iou: float = Query(0.45, ge=0.01, le=1.0, description="NMS IOU overlap threshold"),
):
    """Run product detection and return raw bounding boxes."""
    detector = get_detector()

    if file is not None:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        image_input = image_bytes
    elif sample_id is not None:
        image_input = _resolve_sample_path(sample_id)
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either an uploaded image file or a 'sample_id' parameter.",
        )

    try:
        result = detector.detect(image_input=image_input, conf=conf, iou=iou)
        return DetectionResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detection inference failed: {str(exc)}")


@router.post(
    "/shelf-analysis",
    response_model=ShelfAnalysisResponse,
    summary="Analyze Shelf Occupancy & Out-of-Stock Gaps",
    description="Runs detection, clusters shelf tiers, computes occupancy %, and identifies out-of-stock gaps.",
)
async def analyze_shelf(
    file: Optional[UploadFile] = File(None, description="Uploaded shelf image file (JPEG/PNG)"),
    sample_id: Optional[str] = Query(None, description="Pre-configured sample ID (e.g. 'sample_01')"),
    conf: float = Query(0.25, ge=0.01, le=1.0, description="Detection confidence threshold"),
    iou: float = Query(0.45, ge=0.01, le=1.0, description="NMS IOU overlap threshold"),
):
    """Perform full shelf monitoring and stock gap analysis."""
    if file is not None:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        image_input = image_bytes
    elif sample_id is not None:
        image_input = _resolve_sample_path(sample_id)
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either an uploaded image file or a 'sample_id' parameter.",
        )

    try:
        analysis = analyze_shelf_image(image_input=image_input, conf=conf, iou=iou)
        return analysis
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Shelf analysis failed: {str(exc)}")
