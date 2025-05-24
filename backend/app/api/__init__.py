"""
FastAPI Request/Response schemas and exception handlers
"""

from typing import Optional, List, Any, Dict
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


# Request/Response DTOs for FastAPI

class GenerateImageRequest(BaseModel):
    """API request schema for image generation."""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt")
    num_images: int = Field(1, ge=1, le=10, description="Number of images")
    width: int = Field(1024, ge=512, le=2048, description="Image width") 
    height: int = Field(1024, ge=512, le=2048, description="Image height")
    style: Optional[str] = Field(None, description="Art style")
    contrast: float = Field(3.5, ge=1.0, le=5.0, description="Contrast level")
    alchemy: bool = Field(True, description="Enable Alchemy mode")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    upscale: bool = Field(False, description="Enable upscaling")
    upscale_strength: float = Field(0.35, ge=0.0, le=1.0, description="Upscale strength")


class ImageGenerationResponse(BaseModel):
    """API response schema for image generation."""
    
    generation_id: str = Field(..., description="Generation ID")
    status: str = Field(..., description="Generation status")
    num_images: int = Field(..., description="Number of images generated")
    image_urls: List[str] = Field(..., description="URLs to download images")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")
    cost_estimate: Optional[float] = Field(None, description="Cost estimate in USD")


class ModelInfo(BaseModel):
    """Information about available models."""
    
    vendor: str = Field(..., description="AI vendor")
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type (image, text)")
    available: bool = Field(..., description="Whether model is available")
    styles: Optional[List[str]] = Field(None, description="Available styles")


class ModelsResponse(BaseModel):
    """Response for available models."""
    
    models: List[ModelInfo] = Field(..., description="Available models")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")


# Exception Handlers

class APIError(Exception):
    """Base API error."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(APIError):
    """Validation error."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, 400, details)


class EngineError(APIError):
    """Engine processing error."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, 500, details)


def setup_exception_handlers(app):
    """Setup exception handlers for FastAPI app."""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle custom API errors."""
        logger.error(f"API error: {exc.message}", exc_info=exc)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "timestamp": "2025-05-24T00:00:00Z"
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP exception: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "timestamp": "2025-05-24T00:00:00Z"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=exc)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": "2025-05-24T00:00:00Z"
            }
        )
