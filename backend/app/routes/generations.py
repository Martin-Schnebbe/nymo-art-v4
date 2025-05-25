"""
Image generation API routes
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, Any
import logging
import os
from pathlib import Path

from ..api import (
    GenerateImageRequest, 
    GenerateFluxImageRequest,
    GeneratePhotoRealImageRequest,
    ImageGenerationResponse, 
    ValidationError,
    EngineError
)
from core.schemas import LeonardoPhoenixRequest, LeonardoFluxRequest, LeonardoPhotoRealRequest, LeonardoEngineConfig
from core.engine.leonardo.phoenix import PhoenixEngine
from core.engine.leonardo.flux import FluxEngine
from core.engine.leonardo.photoreal import LeonardoPhotoRealEngine
from core.engine.base import engine_registry
from core.modules.image_generation_workflow import ImageGenerationWorkflow, ImageGenerationRequestFactory


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generations", tags=["generations"])


# Dependency to get Phoenix engine
def get_phoenix_engine() -> PhoenixEngine:
    """Get configured Phoenix engine."""
    try:
        engine = engine_registry.get("leonardo", "phoenix")
        if not isinstance(engine, PhoenixEngine):
            raise ValueError("Engine is not a PhoenixEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="phoenix",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = PhoenixEngine(config)
        engine_registry.register(engine)
        return engine


# Dependency to get FLUX engine
def get_flux_engine() -> FluxEngine:
    """Get configured FLUX engine."""
    try:
        engine = engine_registry.get("leonardo", "flux")
        if not isinstance(engine, FluxEngine):
            raise ValueError("Engine is not a FluxEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="flux",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = FluxEngine(config)
        engine_registry.register(engine)
        return engine


# Dependency to get PhotoReal engine
def get_photoreal_engine() -> LeonardoPhotoRealEngine:
    """Get configured PhotoReal engine."""
    try:
        engine = engine_registry.get("leonardo", "photoreal")
        if not isinstance(engine, LeonardoPhotoRealEngine):
            raise ValueError("Engine is not a LeonardoPhotoRealEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="photoreal",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = LeonardoPhotoRealEngine(config)
        engine_registry.register(engine)
        return engine


@router.post("/phoenix", response_model=ImageGenerationResponse)
async def generate_phoenix_images(
    request: GenerateImageRequest,
    background_tasks: BackgroundTasks,
    engine: PhoenixEngine = Depends(get_phoenix_engine)
):
    """Generate images using Leonardo Phoenix model."""
    
    try:
        # Create workflow
        workflow = ImageGenerationWorkflow(engine)
        
        # Convert API request to engine request using factory
        engine_request = ImageGenerationRequestFactory.from_api_request(request, "phoenix")
        
        # Use shared workflow
        result = await workflow.generate_and_save(engine_request)
        
        logger.info(f"Generated {result['num_images']} Phoenix images successfully")
        
        return ImageGenerationResponse(
            generation_id=result["generation_id"],
            status=result["status"],
            num_images=result["num_images"],
            image_urls=result["image_urls"],
            metadata=result["metadata"],
            cost_estimate=result["cost_estimate"]
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise EngineError(f"Image generation failed: {str(e)}")


@router.post("/flux", response_model=ImageGenerationResponse)
async def generate_flux_images(
    request: GenerateFluxImageRequest,
    background_tasks: BackgroundTasks,
    engine: FluxEngine = Depends(get_flux_engine)
):
    """Generate images using Leonardo FLUX model."""
    
    try:
        # Create workflow
        workflow = ImageGenerationWorkflow(engine)
        
        # Convert API request to engine request using factory
        engine_request = ImageGenerationRequestFactory.from_api_request(request, "flux")
        
        # Use shared workflow
        result = await workflow.generate_and_save(engine_request)
        
        logger.info(f"Generated {result['num_images']} FLUX images successfully")
        
        return ImageGenerationResponse(
            generation_id=result["generation_id"],
            status=result["status"],
            num_images=result["num_images"],
            image_urls=result["image_urls"],
            metadata=result["metadata"],
            cost_estimate=result["cost_estimate"]
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise EngineError(f"Image generation failed: {str(e)}")


@router.post("/photoreal", response_model=ImageGenerationResponse)
async def generate_photoreal_images(
    request: GeneratePhotoRealImageRequest,
    background_tasks: BackgroundTasks,
    engine: LeonardoPhotoRealEngine = Depends(get_photoreal_engine)
):
    """Generate images using Leonardo PhotoReal model."""
    
    try:
        # Create workflow
        workflow = ImageGenerationWorkflow(engine)
        
        # Convert API request to engine request using factory
        engine_request = ImageGenerationRequestFactory.from_api_request(request, "photoreal")
        
        # Use shared workflow
        result = await workflow.generate_and_save(engine_request)
        
        logger.info(f"Generated {result['num_images']} PhotoReal images successfully")
        
        return ImageGenerationResponse(
            generation_id=result["generation_id"],
            status=result["status"],
            num_images=result["num_images"],
            image_urls=result["image_urls"],
            metadata=result["metadata"],
            cost_estimate=result["cost_estimate"]
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise EngineError(f"Image generation failed: {str(e)}")


@router.get("/status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get status of a generation job."""
    # In a real implementation, you'd track job status
    return {
        "generation_id": generation_id,
        "status": "complete",
        "message": "Generation completed successfully"
    }


@router.get("/")
async def list_generations():
    """List recent generations."""
    # In a real implementation, you'd return paginated results
    return {
        "generations": [],
        "total": 0,
        "page": 1,
        "per_page": 20
    }
