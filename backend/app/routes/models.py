"""
Models information API routes
"""

from fastapi import APIRouter
import logging

from ..api import ModelsResponse, ModelInfo
from ...core.engine.leonardo.phoenix import PhoenixEngine


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=ModelsResponse)
async def list_models():
    """List all available AI models."""
    
    models = [
        ModelInfo(
            vendor="leonardo",
            name="phoenix",
            type="image",
            available=True,
            styles=PhoenixEngine.get_available_styles()
        ),
        # Future models can be added here
        ModelInfo(
            vendor="leonardo",
            name="flux",
            type="image", 
            available=False,
            styles=None
        ),
        ModelInfo(
            vendor="openai",
            name="chat_completion",
            type="text",
            available=False,
            styles=None
        )
    ]
    
    return ModelsResponse(models=models)


@router.get("/leonardo/phoenix/styles")
async def get_phoenix_styles():
    """Get available styles for Phoenix model."""
    return {
        "model": "leonardo.phoenix",
        "styles": PhoenixEngine.get_available_styles(),
        "total": len(PhoenixEngine.get_available_styles())
    }


@router.get("/{vendor}/{model}")
async def get_model_info(vendor: str, model: str):
    """Get detailed information about a specific model."""
    
    if vendor == "leonardo" and model == "phoenix":
        return {
            "vendor": vendor,
            "name": model,
            "type": "image",
            "available": True,
            "description": "Leonardo AI Phoenix model for high-quality image generation",
            "capabilities": {
                "styles": True,
                "negative_prompts": True,
                "upscaling": True,
                "alchemy": True,
                "prompt_enhancement": True
            },
            "parameters": {
                "width": {"min": 512, "max": 2048, "step": 64},
                "height": {"min": 512, "max": 2048, "step": 64},
                "contrast": {"min": 1.0, "max": 5.0, "default": 3.5},
                "num_images": {"min": 1, "max": 10, "default": 1}
            },
            "styles": PhoenixEngine.get_available_styles(),
            "cost": {
                "base_cost_per_image": 0.02,
                "currency": "USD",
                "factors": ["resolution", "alchemy", "upscaling"]
            }
        }
    
    return {
        "error": f"Model {vendor}.{model} not found",
        "available_models": ["leonardo.phoenix"]
    }
