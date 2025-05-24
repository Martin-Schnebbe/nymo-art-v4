"""
Leonardo Phoenix Image Generation Engine
Framework-agnostic business logic for Leonardo AI Phoenix model.
"""

import logging
from typing import Dict, Any, List, Optional, cast
from pathlib import Path

from ...schemas import (
    LeonardoPhoenixRequest, 
    GenerationResult, 
    LeonardoEngineConfig,
    GenerationRequest
)
from ....services.leonardo_client import LeonardoClient, LeonardoAPIError
from ..base import ImageGenerationEngine


logger = logging.getLogger(__name__)


# Phoenix Model Constants
PHOENIX_MODEL_ID = "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3"

PHOENIX_STYLES = {
    "3D Render": "debdf72a-91a4-467b-bf61-cc02bdeb69c6",
    "Bokeh": "9fdc5e8c-4d13-49b4-9ce6-5a74cbb19177",
    "Cinematic": "a5632c7c-ddbb-4e2f-ba34-8456ab3ac436",
    "Cinematic Concept": "33abbb99-03b9-4dd7-9761-ee98650b2c88",
    "Creative": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
    "Dynamic": "111dc692-d470-4eec-b791-3475abac4c46",
    "Fashion": "594c4a08-a522-4e0e-b7ff-e4dac4b6b622",
    "Graphic Design Pop Art": "2e74ec31-f3a4-4825-b08b-2894f6d13941",
    "Graphic Design Vector": "1fbb6a68-9319-44d2-8d56-2957ca0ece6a",
    "HDR": "97c20e5c-1af6-4d42-b227-54d03d8f0727",
    "Illustration": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
    "Macro": "30c1d34f-e3a9-479a-b56f-c018bbc9c02a",
    "Minimalist": "cadc8cd6-7838-4c99-b645-df76be8ba8d8",
    "Moody": "621e1c9a-6319-4bee-a12d-ae40659162fa",
    "None": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
    "Portrait": "8e2bc543-6ee2-45f9-bcd9-594b6ce84dcd",
    "Pro B&W photography": "22a9a7d2-2166-4d86-80ff-22e2643adbcf",
    "Pro color photography": "7c3f932b-a572-47cb-9b9b-f20211e63b5b",
    "Pro film photography": "581ba6d6-5aac-4492-bebe-54c424a0d46e",
    "Portrait Fashion": "0d34f8e1-46d4-428f-8ddd-4b11811fa7c9",
    "Ray Traced": "b504f83c-3326-4947-82e1-7fe9e839ec0f",
    "Sketch (B&W)": "be8c6b58-739c-4d44-b9c1-b032ed308b61",
    "Sketch (Color)": "093accc3-7633-4ffd-82da-d34000dfc0d6",
    "Stock Photo": "5bdc3f2a-1be6-4d1c-8e77-992a30824a2c",
    "Vibrant": "dee282d3-891f-4f73-ba02-7f8131e5541b"
}


class PhoenixEngine(ImageGenerationEngine):
    """Leonardo AI Phoenix model generation engine."""
    
    def __init__(self, config: LeonardoEngineConfig):
        """Initialize Phoenix engine with Leonardo configuration."""
        super().__init__(config)
        
        # Create Leonardo client
        self.client = LeonardoClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            poll_interval=config.poll_interval
        )
        
        self.logger.info("Phoenix engine initialized successfully")
    
    def validate_request(self, request: GenerationRequest) -> None:
        """Validate Phoenix-specific request parameters."""
        if not isinstance(request, LeonardoPhoenixRequest):
            raise ValueError(f"Expected LeonardoPhoenixRequest, got {type(request)}")
        
        # Validate style
        if request.style and request.style not in PHOENIX_STYLES:
            available = list(PHOENIX_STYLES.keys())
            raise ValueError(f"Unknown style '{request.style}'. Available: {available}")
        
        # Validate dimensions for Phoenix
        valid_sizes = [512, 576, 640, 704, 768, 832, 896, 960, 1024, 1152, 1280, 1472, 1536, 1664, 1792, 1920, 2048]
        
        if request.width not in valid_sizes:
            raise ValueError(f"Invalid width {request.width}. Must be one of: {valid_sizes}")
        
        if request.height not in valid_sizes:
            raise ValueError(f"Invalid height {request.height}. Must be one of: {valid_sizes}")
        
        self.logger.debug(f"Request validation passed for Phoenix engine")
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate images using Phoenix model.
        
        Args:
            request: Phoenix generation request
            
        Returns:
            Generation result with images and metadata
        """
        self.validate_request(request)
        
        # Cast to Phoenix request after validation
        phoenix_request = cast(LeonardoPhoenixRequest, request)
        
        # Build payload
        payload = self._build_payload(phoenix_request)
        
        try:
            # Create generation
            generation_id = self.client.create_generation(payload)
            
            # Poll until complete
            generation_data = self.client.poll_generation(generation_id)
            
            # Download images
            images = self._download_images(generation_data)
            
            # Create metadata
            metadata = self.create_metadata(
                generation_id=generation_id,
                parameters=self._extract_parameters(phoenix_request),
                cost_estimate=self.estimate_cost(phoenix_request)
            )
            
            self.logger.info(f"Successfully generated {len(images)} images")
            
            return GenerationResult(
                outputs=images,
                metadata=metadata
            )
            
        except LeonardoAPIError as e:
            self.logger.error(f"Leonardo API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in Phoenix generation: {e}")
            raise
    
    def _build_payload(self, request: LeonardoPhoenixRequest) -> Dict[str, Any]:
        """Build Leonardo API payload from request."""
        payload = {
            "modelId": PHOENIX_MODEL_ID,
            "prompt": request.prompt,
            "num_images": request.num_outputs,  # Leonardo API expects 'num_images'
            "width": request.width,
            "height": request.height,
            "contrast": request.contrast,
            "alchemy": request.alchemy,
            "enhancePrompt": request.enhance_prompt  # Leonardo API expects 'enhancePrompt'
        }
        
        # Add optional parameters
        if request.style and request.style in PHOENIX_STYLES:
            payload["styleUUID"] = PHOENIX_STYLES[request.style]
        
        if request.negative_prompt:
            payload["negativePrompt"] = request.negative_prompt
        
        # Add ultra mode if enabled
        if request.ultra:
            payload["ultra"] = request.ultra
        
        # Only include upscale parameters if upscaling is enabled
        if request.upscale:
            payload["upscaleRatio"] = 2
            payload["upscaleStrength"] = request.upscale_strength
        
        return payload
    
    def _download_images(self, generation_data: Dict[str, Any]) -> List[bytes]:
        """Download all generated images."""
        images = []
        generated_images = generation_data.get("generated_images", [])
        
        self.logger.info(f"Downloading {len(generated_images)} images...")
        
        for img_data in generated_images:
            image_url = img_data.get("url")
            if image_url:
                try:
                    image_bytes = self.client.download_image(image_url)
                    images.append(image_bytes)
                except LeonardoAPIError as e:
                    self.logger.warning(f"Failed to download image: {e}")
                    continue
        
        if not images:
            raise LeonardoAPIError(0, "No images could be downloaded")
        
        return images
    
    def _extract_parameters(self, request: LeonardoPhoenixRequest) -> Dict[str, Any]:
        """Extract parameters for metadata."""
        return {
            "width": request.width,
            "height": request.height,
            "num_images": request.num_outputs,
            "contrast": request.contrast,
            "alchemy": request.alchemy,
            "enhance_prompt": request.enhance_prompt,
            "ultra": request.ultra,
            "upscale": request.upscale,
            "upscale_strength": request.upscale_strength,
            "style": request.style,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt
        }
    
    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate generation cost in USD."""
        # Ensure we have a Phoenix request
        if not isinstance(request, LeonardoPhoenixRequest):
            return 0.0
            
        # Leonardo Phoenix pricing (approximate)
        base_cost_per_image = 0.02  # $0.02 per image
        
        # Higher resolution increases cost
        pixel_count = request.width * request.height
        size_multiplier = pixel_count / (1024 * 1024)  # Normalize to 1MP
        
        # Alchemy mode adds cost
        alchemy_multiplier = 1.5 if request.alchemy else 1.0
        
        # Upscaling adds cost
        upscale_multiplier = 2.0 if request.upscale else 1.0
        
        total_cost = (
            base_cost_per_image * 
            request.num_outputs * 
            size_multiplier * 
            alchemy_multiplier * 
            upscale_multiplier
        )
        
        return round(total_cost, 4)
    
    @classmethod
    def get_available_styles(cls) -> List[str]:
        """Get list of available styles."""
        return list(PHOENIX_STYLES.keys())
    
    @classmethod
    def get_style_uuid(cls, style_name: str) -> Optional[str]:
        """Get UUID for a style name."""
        return PHOENIX_STYLES.get(style_name)
