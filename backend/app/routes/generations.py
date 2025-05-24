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
        # Convert API request to engine request
        engine_request = LeonardoPhoenixRequest(
            prompt=request.prompt,
            num_outputs=request.num_images,
            width=request.width,
            height=request.height,
            style=request.style,
            contrast=request.contrast,
            alchemy=request.alchemy,
            enhance_prompt=request.enhance_prompt,
            negative_prompt=request.negative_prompt,
            upscale=request.upscale,
            upscale_strength=request.upscale_strength
        )
        
        # Generate images
        logger.info(f"Starting Phoenix generation: {request.prompt[:50]}...")
        result = await engine.generate(engine_request)
        
        # Save images and create URLs
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        image_urls = []
        for i, image_data in enumerate(result.outputs):
            filename = f"{result.metadata.generation_id}_{i+1}.png"
            filepath = output_dir / filename
            filepath.write_bytes(image_data)
            
            # In production, use proper URL construction
            image_urls.append(f"/images/{filename}")
        
        logger.info(f"Generated {len(result.outputs)} images successfully")
        
        return ImageGenerationResponse(
            generation_id=result.metadata.generation_id,
            status="complete",
            num_images=len(result.outputs),
            image_urls=image_urls,
            metadata=result.metadata.parameters,
            cost_estimate=result.metadata.cost_estimate
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
        # Convert API request to engine request
        engine_request = LeonardoFluxRequest(
            prompt=request.prompt,
            num_outputs=request.num_images,
            width=request.width,
            height=request.height,
            model_type=request.model_type,
            style=request.style,
            contrast=request.contrast,
            enhance_prompt=request.enhance_prompt,
            enhance_prompt_instruction=request.enhance_prompt_instruction,
            negative_prompt=request.negative_prompt,
            ultra=request.ultra,
            seed=request.seed
        )
        
        # Generate images
        logger.info(f"Starting FLUX generation: {request.prompt[:50]}...")
        result = await engine.generate(engine_request)
        
        # Save images and create URLs
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        image_urls = []
        for i, image_data in enumerate(result.outputs):
            filename = f"{result.metadata.generation_id}_{i+1}.png"
            filepath = output_dir / filename
            filepath.write_bytes(image_data)
            
            # In production, use proper URL construction
            image_urls.append(f"/images/{filename}")
        
        logger.info(f"Generated {len(result.outputs)} images successfully")
        
        return ImageGenerationResponse(
            generation_id=result.metadata.generation_id,
            status="complete",
            num_images=len(result.outputs),
            image_urls=image_urls,
            metadata=result.metadata.parameters,
            cost_estimate=result.metadata.cost_estimate
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
        # Convert API request to engine request
        engine_request = LeonardoPhotoRealRequest(
            prompt=request.prompt,
            num_outputs=request.num_images,
            width=request.width,
            height=request.height,
            photoreal_version=request.photoreal_version,
            model_id=request.model_id,
            style=request.style,
            contrast=request.contrast,
            photoreal_strength=request.photoreal_strength,
            enhance_prompt=request.enhance_prompt,
            negative_prompt=request.negative_prompt
        )
        
        # Generate images
        logger.info(f"Starting PhotoReal {request.photoreal_version} generation: {request.prompt[:50]}...")
        result = await engine.generate(engine_request)
        
        # Save images and create URLs
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        image_urls = []
        for i, image_data in enumerate(result.outputs):
            filename = f"{result.metadata.generation_id}_{i+1}.png"
            filepath = output_dir / filename
            filepath.write_bytes(image_data)
            
            # In production, use proper URL construction
            image_urls.append(f"/images/{filename}")
        
        logger.info(f"Generated {len(result.outputs)} images successfully")
        
        return ImageGenerationResponse(
            generation_id=result.metadata.generation_id,
            status="complete",
            num_images=len(result.outputs),
            image_urls=image_urls,
            metadata=result.metadata.parameters,
            cost_estimate=result.metadata.cost_estimate
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
