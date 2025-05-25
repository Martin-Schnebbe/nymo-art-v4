"""
Static file serving routes for generated images
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from core.naming import NamingConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["images"])

# Use unified directory structure
UNIFIED_IMAGES_DIR = Path(NamingConfig.BASE_OUTPUT_DIR)
LEGACY_BATCH_DIR = Path(NamingConfig.LEGACY_BATCH_DIR)

@router.get("/{image_path:path}")
async def serve_image(image_path: str):
    """Serve generated images from unified directory structure with legacy fallback."""
    # Try unified directory first (primary location for new images)
    file_path = UNIFIED_IMAGES_DIR / image_path
    source_dir = UNIFIED_IMAGES_DIR
    
    # If not found, try legacy batch output directory for backward compatibility
    if not file_path.exists():
        file_path = LEGACY_BATCH_DIR / image_path
        source_dir = LEGACY_BATCH_DIR
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Ensure the path is within one of the allowed directories (security check)
    try:
        file_path.resolve().relative_to(source_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"}
    )
