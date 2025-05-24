"""
Static file serving routes for generated images
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["images"])

IMAGES_DIR = Path("generated_images")

@router.get("/{filename}")
async def serve_image(filename: str):
    """Serve generated images."""
    file_path = IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        path=file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"}
    )
