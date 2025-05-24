"""
Leonardo AI HTTP Service Client
Thin wrapper around Leonardo.ai REST API.
"""

import time
import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class LeonardoAPIError(Exception):
    """Leonardo AI API specific errors."""
    
    def __init__(self, status_code: int, message: str, response_data: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"Leonardo API error {status_code}: {message}")


class LeonardoClient:
    """HTTP client for Leonardo AI API."""
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://cloud.leonardo.ai/api/rest/v1",
        timeout: int = 300,
        poll_interval: int = 2
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.poll_interval = poll_interval
        
        if not self.api_key:
            raise ValueError("Leonardo API key is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        
        logger.info(f"Leonardo client initialized with base URL: {base_url}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            response = self.session.request(method, url, timeout=timeout, **kwargs)
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                
                raise LeonardoAPIError(
                    status_code=response.status_code,
                    message=error_data.get("error", "Unknown error"),
                    response_data=error_data
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise LeonardoAPIError(
                status_code=0,
                message=f"Network error: {str(e)}"
            )
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST request."""
        return self._make_request("POST", endpoint, json=data, **kwargs)
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def create_generation(self, payload: Dict[str, Any]) -> str:
        """
        Create a new image generation job.
        
        Args:
            payload: Generation parameters
            
        Returns:
            generation_id: The ID of the created generation job
        """
        logger.info("Creating generation job...")
        logger.debug(f"Payload: {payload}")
        
        response = self.post("/generations", data=payload)
        
        try:
            generation_id = response["sdGenerationJob"]["generationId"]
            logger.info(f"Generation job created: {generation_id}")
            return generation_id
        except KeyError:
            raise LeonardoAPIError(
                status_code=0,
                message="Unexpected response format",
                response_data=response
            )
    
    def poll_generation(self, generation_id: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Poll generation status until complete.
        
        Args:
            generation_id: ID of the generation to poll
            timeout: Override default timeout
            
        Returns:
            Generation data when complete
        """
        logger.info(f"Polling generation {generation_id}...")
        start_time = time.time()
        poll_timeout = timeout or self.timeout
        
        while True:
            if time.time() - start_time > poll_timeout:
                raise LeonardoAPIError(
                    status_code=408,
                    message=f"Polling timeout after {poll_timeout}s"
                )
            
            response = self.get(f"/generations/{generation_id}")
            generation = response.get("generations_by_pk", {})
            status = generation.get("status", "PENDING")
            
            logger.debug(f"Generation status: {status}")
            
            if status == "COMPLETE":
                logger.info("Generation completed successfully")
                return generation
            elif status == "FAILED":
                raise LeonardoAPIError(
                    status_code=0,
                    message="Generation failed",
                    response_data=generation
                )
            
            time.sleep(self.poll_interval)
    
    def download_image(self, url: str) -> bytes:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            Image data as bytes
        """
        logger.debug(f"Downloading image: {url}")
        
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.warning(f"Failed to download image {url}: {e}")
            raise LeonardoAPIError(
                status_code=0,
                message=f"Image download failed: {e}"
            )
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user account information."""
        return self.get("/me")
    
    def upscale_image(self, image_id: str, upscale_strength: float = 0.35) -> str:
        """
        Upscale an existing image.
        
        Args:
            image_id: ID of the image to upscale
            upscale_strength: Upscaling strength (0.0-1.0)
            
        Returns:
            upscale_id: ID of the upscaling job
        """
        payload = {
            "imageId": image_id,
            "upscalerStyle": "GENERAL",
            "creativity": upscale_strength
        }
        
        response = self.post("/generations-upscale", data=payload)
        return response["sdUpscaleJob"]["id"]
    
    async def generate_photoreal_images(self, photoreal_request) -> Any:
        """
        Generate images using Leonardo PhotoReal.
        
        Args:
            photoreal_request: PhotoReal generation request
            
        Returns:
            Generation result with images and metadata
        """
        # Build payload for PhotoReal
        payload = {
            "height": photoreal_request.height,
            "width": photoreal_request.width,
            "prompt": photoreal_request.prompt,
            "num_images": photoreal_request.num_outputs,
            "alchemy": True,  # PhotoReal requires alchemy
            "photoReal": True,
            "photoRealVersion": photoreal_request.photoreal_version
        }
        
        # Add negative prompt if provided
        if photoreal_request.negative_prompt:
            payload["negative_prompt"] = photoreal_request.negative_prompt
        
        # Version-specific parameters
        if photoreal_request.photoreal_version == "v1":
            # v1 specific parameters
            if photoreal_request.photoreal_strength is not None:
                payload["photoRealStrength"] = photoreal_request.photoreal_strength
            
            # v1 uses presetStyle instead of styleUUID
            payload["presetStyle"] = photoreal_request.style
            
        else:  # v2
            # v2 requires modelId
            payload["modelId"] = photoreal_request.model_id
            
            # v2 uses presetStyle 
            payload["presetStyle"] = photoreal_request.style
        
        # Add enhance prompt if enabled
        if photoreal_request.enhance_prompt:
            payload["enhancePrompt"] = True
        
        logger.info(f"Creating PhotoReal {photoreal_request.photoreal_version} generation...")
        logger.debug(f"Payload: {payload}")
        
        # Create generation
        generation_id = self.create_generation(payload)
        
        # Poll until complete
        generation_data = self.poll_generation(generation_id)
        
        # Extract image URLs
        image_urls = []
        for img_data in generation_data.get("generated_images", []):
            if img_data.get("url"):
                image_urls.append(img_data["url"])
        
        # Calculate rough cost estimate for PhotoReal
        base_cost = 0.025 if photoreal_request.photoreal_version == "v2" else 0.02  # v2 costs slightly more
        pixel_multiplier = (photoreal_request.width * photoreal_request.height) / (1024 * 1024)
        cost_estimate = base_cost * photoreal_request.num_outputs * pixel_multiplier
        
        # Return result in expected format
        class PhotoRealResult:
            def __init__(self, generation_id, image_urls, metadata, cost_estimate):
                self.generation_id = generation_id
                self.status = "complete"
                self.image_urls = image_urls
                self.metadata = metadata
                self.cost_estimate = cost_estimate
        
        return PhotoRealResult(
            generation_id=generation_id,
            image_urls=image_urls,
            metadata={
                "photoreal_version": photoreal_request.photoreal_version,
                "model_id": photoreal_request.model_id,
                "style": photoreal_request.style,
                "parameters": payload
            },
            cost_estimate=round(cost_estimate, 4)
        )
