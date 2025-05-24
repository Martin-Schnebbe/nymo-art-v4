"""
Leonardo FLUX Image Generation Engine
Framework-agnostic business logic for Leonardo AI FLUX model.
"""

import logging
from typing import Dict, Any, List, Optional, cast
from pathlib import Path

from ...schemas import (
    LeonardoFluxRequest, 
    GenerationResult, 
    LeonardoEngineConfig,
    GenerationRequest
)
from services.leonardo_client import LeonardoClient, LeonardoAPIError
from ..base import ImageGenerationEngine


logger = logging.getLogger(__name__)


# FLUX Model Constants
FLUX_MODELS = {
    "flux_speed": "1dd50843-d653-4516-a8e3-f0238ee453ff",  # Flux Schnell
    "flux_precision": "b2614463-296c-462a-9586-aafdb8f00e36"  # Flux Dev
}

FLUX_STYLES = {
    "3D Render": "debdf72a-91a4-467b-bf61-cc02bdeb69c6",
    "Acrylic": "3cbb655a-7ca4-463f-b697-8a03ad67327c",
    "Anime General": "b2a54a51-230b-4d4f-ad4e-8409bf58645f",
    "Creative": "6fedbf1f-4a17-45ec-84fb-92fe524a29ef",
    "Dynamic": "111dc692-d470-4eec-b791-3475abac4c46",
    "Fashion": "594c4a08-a522-4e0e-b7ff-e4dac4b6b622",
    "Game Concept": "09d2b5b5-d7c5-4c02-905d-9f84051640f4",
    "Graphic Design 3D": "7d7c2bc5-4b12-4ac3-81a9-630057e9e89f",
    "Illustration": "645e4195-f63d-4715-a3f2-3fb1e6eb8c70",
    "None": "556c1ee5-ec38-42e8-955a-1e82dad0ffa1",
    "Portrait": "8e2bc543-6ee2-45f9-bcd9-594b6ce84dcd",
    "Portrait Cinematic": "4edb03c9-8a26-4041-9d01-f85b5d4abd71",
    "Ray Traced": "b504f83c-3326-4947-82e1-7fe9e839ec0f",
    "Stock Photo": "5bdc3f2a-1be6-4d1c-8e77-992a30824a2c",
    "Watercolor": "1db308ce-c7ad-4d10-96fd-592fa6b75cc4"
}


class FluxEngine(ImageGenerationEngine):
    """Leonardo AI FLUX model generation engine."""
    
    @classmethod
    def get_available_styles(cls) -> list[str]:
        """Get list of available FLUX styles."""
        return list(FLUX_STYLES.keys())
    
    def __init__(self, config: LeonardoEngineConfig):
        """Initialize FLUX engine with Leonardo configuration."""
        super().__init__(config)
        
        # Create Leonardo client
        self.client = LeonardoClient(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            poll_interval=config.poll_interval
        )
        
        self.logger.info("FLUX engine initialized successfully")
    
    def validate_request(self, request: GenerationRequest) -> None:
        """Validate FLUX-specific request parameters."""
        if not isinstance(request, LeonardoFluxRequest):
            raise ValueError(f"Expected LeonardoFluxRequest, got {type(request)}")
        
        # Validate model type
        if request.model_type not in FLUX_MODELS:
            available = list(FLUX_MODELS.keys())
            raise ValueError(f"Unknown model type '{request.model_type}'. Available: {available}")
        
        # Validate style
        if request.style and request.style not in FLUX_STYLES:
            available = list(FLUX_STYLES.keys())
            raise ValueError(f"Unknown style '{request.style}'. Available: {available}")
        
        # Validate dimensions for FLUX
        valid_sizes = [512, 576, 640, 704, 768, 832, 896, 960, 1024, 1152, 1280, 1472, 1536, 1664, 1792, 1920, 2048]
        
        if request.width not in valid_sizes:
            raise ValueError(f"Invalid width {request.width}. Must be one of: {valid_sizes}")
        
        if request.height not in valid_sizes:
            raise ValueError(f"Invalid height {request.height}. Must be one of: {valid_sizes}")
        
        self.logger.debug(f"Request validation passed for FLUX engine")
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate images using FLUX model.
        
        Args:
            request: FLUX generation request
            
        Returns:
            Generation result with images and metadata
        """
        self.validate_request(request)
        flux_request = cast(LeonardoFluxRequest, request)
        
        try:
            # Prepare Leonardo API request
            leonardo_request = self._prepare_leonardo_request(flux_request)
            
            self.logger.info(f"Generating {flux_request.num_outputs} images with FLUX {flux_request.model_type}")
            self.logger.debug(f"Request parameters: {leonardo_request}")
            
            # Create generation
            generation_id = self.client.create_generation(leonardo_request)
            
            # Poll until complete
            generation_data = self.client.poll_generation(generation_id)
            
            # Download images
            images = self._download_images(generation_data)
            
            # Create metadata
            metadata = self.create_metadata(
                generation_id=generation_id,
                parameters=self._extract_parameters(flux_request),
                cost_estimate=self.estimate_cost(flux_request)
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
            self.logger.error(f"Unexpected error in FLUX generation: {e}")
            raise
    
    def _prepare_leonardo_request(self, request: LeonardoFluxRequest) -> Dict[str, Any]:
        """Convert domain request to Leonardo API format."""
        
        leonardo_request = {
            "modelId": FLUX_MODELS[request.model_type],
            "prompt": request.prompt,
            "num_images": request.num_outputs,
            "width": request.width,
            "height": request.height,
            "contrast": request.contrast,
            "enhancePrompt": request.enhance_prompt,
            "ultra": request.ultra
        }
        
        # Add optional parameters
        if request.negative_prompt:
            leonardo_request["negative_prompt"] = request.negative_prompt
        
        if request.style and request.style != "None":
            leonardo_request["styleUUID"] = FLUX_STYLES[request.style]
        
        if request.enhance_prompt and request.enhance_prompt_instruction:
            leonardo_request["enhancePromptInstruction"] = request.enhance_prompt_instruction
        
        if request.seed is not None:
            leonardo_request["seed"] = request.seed
        
        return leonardo_request
    
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
    
    def _extract_parameters(self, request: LeonardoFluxRequest) -> Dict[str, Any]:
        """Extract parameters for metadata."""
        return {
            "model_type": request.model_type,
            "style": request.style,
            "contrast": request.contrast,
            "enhance_prompt": request.enhance_prompt,
            "ultra": request.ultra,
            "width": request.width,
            "height": request.height,
            "num_outputs": request.num_outputs,
            "seed": request.seed,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "enhance_prompt_instruction": request.enhance_prompt_instruction
        }
    
    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate generation cost in USD."""
        # Ensure we have a FLUX request
        if not isinstance(request, LeonardoFluxRequest):
            return 0.0
            
        # Leonardo FLUX pricing (approximate)
        base_cost_per_image = 0.015  # $0.015 per image for FLUX (cheaper than Phoenix)
        
        # Higher resolution increases cost
        pixel_count = request.width * request.height
        size_multiplier = pixel_count / (1024 * 1024)  # Normalize to 1MP
        
        # Ultra mode adds cost
        ultra_multiplier = 1.5 if request.ultra else 1.0
        
        # Precision model costs more than speed
        model_multiplier = 1.2 if request.model_type == "flux_precision" else 1.0
        
        total_cost = (
            base_cost_per_image * 
            request.num_outputs * 
            size_multiplier * 
            ultra_multiplier * 
            model_multiplier
        )
        
        return round(total_cost, 4)
