"""
Leonardo PhotoReal Image Generation Engine
Framework-agnostic business logic for Leonardo AI PhotoReal model.
"""

import logging
from typing import Dict, Any, List, Optional, cast

from ...schemas import (
    LeonardoPhotoRealRequest,
    GenerationResult, 
    LeonardoEngineConfig,
    GenerationRequest
)
from services.leonardo_client import LeonardoClient, LeonardoAPIError
from ..base import ImageGenerationEngine


logger = logging.getLogger(__name__)


# PhotoReal Model Constants
LEONARDO_KINO_XL_MODEL_ID = "aa77f04e-3eec-4034-9c07-d0f619684628"
LEONARDO_DIFFUSION_XL_MODEL_ID = "b24e16ff-06e3-43eb-8d33-4416c2d75876"
LEONARDO_VISION_XL_MODEL_ID = "5c232a9e-9061-4777-980a-ddc8e65647c6"

# PhotoReal v1 Styles (limited set)
PHOTOREAL_V1_STYLES = {
    "Cinematic": "CINEMATIC",
    "Creative": "CREATIVE",
    "Vibrant": "VIBRANT"
}

# PhotoReal v2 Styles (full set)
PHOTOREAL_V2_STYLES = {
    "Bokeh": "BOKEH",
    "Cinematic": "CINEMATIC", 
    "Cinematic (Closeup)": "CINEMATIC_CLOSEUP",
    "Creative": "CREATIVE",
    "Fashion": "FASHION",
    "Film": "FILM",
    "Food": "FOOD",
    "HDR": "HDR",
    "Long Exposure": "LONG_EXPOSURE",
    "Macro": "MACRO",
    "Minimalistic": "MINIMALISTIC",
    "Monochrome": "MONOCHROME",
    "Moody": "MOODY",
    "Neutral": "NEUTRAL",
    "Portrait": "PORTRAIT",
    "Retro": "RETRO",
    "Stock Photo": "STOCK_PHOTO",
    "Vibrant": "VIBRANT",
    "Unprocessed": "UNPROCESSED"
}


class LeonardoPhotoRealEngine(ImageGenerationEngine):
    """Leonardo PhotoReal image generation engine implementation."""
    
    def __init__(self, config: LeonardoEngineConfig):
        """Initialize the PhotoReal engine with configuration."""
        super().__init__(config)
        self.client = LeonardoClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            poll_interval=config.poll_interval
        )
        logger.info(f"PhotoReal engine initialized with model support for v1 and v2")
    
    def validate_request(self, request: GenerationRequest) -> None:
        """Validate PhotoReal-specific request parameters."""
        if not isinstance(request, LeonardoPhotoRealRequest):
            raise ValueError(f"Expected LeonardoPhotoRealRequest, got {type(request)}")
        
        if not request.prompt or not request.prompt.strip():
            raise ValueError("Prompt is required")
        
        if request.width not in [512, 768, 1024, 1536]:
            raise ValueError("Width must be one of: 512, 768, 1024, 1536")
        
        if request.height not in [512, 768, 1024, 1536]:
            raise ValueError("Height must be one of: 512, 768, 1024, 1536")
        
        if not 1 <= request.num_outputs <= 10:
            raise ValueError("Number of images must be between 1 and 10")
        
        if request.photoreal_version not in ['v1', 'v2']:
            raise ValueError("PhotoReal version must be 'v1' or 'v2'")
        
        # v2 requires model_id
        if request.photoreal_version == 'v2' and not request.model_id:
            raise ValueError("PhotoReal v2 requires a model_id")
        
        # v1 can use photoreal_strength, v2 cannot
        if request.photoreal_version == 'v2' and request.photoreal_strength is not None:
            logger.warning("photoreal_strength is not used in PhotoReal v2")
        
        # PhotoReal v1 only works reliably with strength 0.5
        if request.photoreal_version == 'v1' and request.photoreal_strength is not None:
            if request.photoreal_strength != 0.5:
                raise ValueError("PhotoReal v1 only supports strength value of 0.5")
        
        # General strength validation for backwards compatibility
        if request.photoreal_strength is not None and not 0.1 <= request.photoreal_strength <= 1.0:
            raise ValueError("PhotoReal strength must be between 0.1 and 1.0")
        
        if request.contrast and not 1.0 <= request.contrast <= 4.5:
            raise ValueError("Contrast must be between 1.0 and 4.5")
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate images using Leonardo PhotoReal.
        
        Args:
            request: PhotoReal generation request
            
        Returns:
            Generation result with images and metadata
        """
        self.validate_request(request)
        photoreal_request = cast(LeonardoPhotoRealRequest, request)
        
        try:
            # Generate images
            logger.info(f"Starting PhotoReal {photoreal_request.photoreal_version} generation: {photoreal_request.prompt[:50]}...")
            
            result = await self.client.generate_photoreal_images(
                photoreal_request=photoreal_request
            )
            
            # Download images
            images = []
            for url in result.image_urls:
                try:
                    image_bytes = self.client.download_image(url)
                    images.append(image_bytes)
                except Exception as e:
                    logger.warning(f"Failed to download image: {e}")
                    continue
            
            if not images:
                raise LeonardoAPIError(0, "No images could be downloaded")
            
            # Create metadata
            metadata = self.create_metadata(
                generation_id=result.generation_id,
                parameters=self._extract_parameters(photoreal_request),
                cost_estimate=self.estimate_cost(photoreal_request)
            )
            
            logger.info(f"Successfully generated {len(images)} images")
            
            return GenerationResult(
                outputs=images,
                metadata=metadata
            )
            
        except LeonardoAPIError as e:
            logger.error(f"Leonardo API error: {e}")
            raise
        except Exception as e:
            logger.error(f"PhotoReal generation failed: {e}")
            raise
    
    def _extract_parameters(self, request: LeonardoPhotoRealRequest) -> Dict[str, Any]:
        """Extract parameters for metadata."""
        return {
            "photoreal_version": request.photoreal_version,
            "model_id": request.model_id,
            "style": request.style,
            "contrast": request.contrast,
            "photoreal_strength": request.photoreal_strength,
            "enhance_prompt": request.enhance_prompt,
            "width": request.width,
            "height": request.height,
            "num_outputs": request.num_outputs,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt
        }
    
    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate generation cost in USD."""
        if not isinstance(request, LeonardoPhotoRealRequest):
            return 0.0
            
        # PhotoReal pricing (approximate)
        base_cost = 0.025 if request.photoreal_version == "v2" else 0.02  # v2 costs slightly more
        
        # Higher resolution increases cost
        pixel_count = request.width * request.height
        size_multiplier = pixel_count / (1024 * 1024)  # Normalize to 1MP
        
        # Calculate total cost
        total_cost = base_cost * request.num_outputs * size_multiplier
        
        return round(total_cost, 4)
    
    def get_supported_dimensions(self) -> List[tuple[int, int]]:
        """Get list of supported image dimensions."""
        return [(512, 512), (768, 768), (1024, 1024), (1536, 1536)]
    
    def get_supported_styles(self, version: str = 'v2') -> Dict[str, str]:
        """Get supported styles for PhotoReal version."""
        if version == 'v1':
            return PHOTOREAL_V1_STYLES.copy()
        else:
            return PHOTOREAL_V2_STYLES.copy()
    
    def get_available_models(self) -> Dict[str, str]:
        """Get available model IDs for PhotoReal v2."""
        return {
            "Leonardo Kino XL": LEONARDO_KINO_XL_MODEL_ID,
            "Leonardo Diffusion XL": LEONARDO_DIFFUSION_XL_MODEL_ID,
            "Leonardo Vision XL": LEONARDO_VISION_XL_MODEL_ID
        }
    
    @classmethod
    def get_available_styles(cls, version: str = "v2") -> List[str]:
        """Get list of available styles for PhotoReal version."""
        if version == "v1":
            return list(PHOTOREAL_V1_STYLES.keys())
        else:
            return list(PHOTOREAL_V2_STYLES.keys())
