"""
Core schemas for AI generation parameters and responses.
Framework-agnostic Pydantic models for domain logic.
"""

from typing import Optional, List, Literal, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path


class GenerationRequest(BaseModel):
    """Base request schema for all AI generation engines."""
    
    prompt: str = Field(..., min_length=1, description="Text prompt for generation")
    num_outputs: int = Field(1, ge=1, le=10, description="Number of outputs to generate")
    
    class Config:
        extra = "forbid"


class ImageGenerationRequest(GenerationRequest):
    """Request schema for image generation engines."""
    
    width: int = Field(1024, ge=512, le=2048, description="Image width")
    height: int = Field(1024, ge=512, le=2048, description="Image height")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt")
    
    @field_validator('width', 'height')
    @classmethod
    def validate_dimensions(cls, v):
        """Ensure dimensions are multiples of 64."""
        if v % 64 != 0:
            raise ValueError(f"Dimension must be multiple of 64, got {v}")
        return v


class LeonardoPhoenixRequest(ImageGenerationRequest):
    """Request schema specific to Leonardo Phoenix model."""
    
    style: Optional[str] = Field(None, description="Art style name")
    contrast: float = Field(3.5, description="Contrast level - valid values: [1.0, 1.3, 1.8, 2.5, 3, 3.5, 4, 4.5]")
    alchemy: bool = Field(True, description="Enable Alchemy mode")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    ultra: bool = Field(False, description="Enable Ultra mode")
    upscale: bool = Field(False, description="Enable image upscaling")
    upscale_strength: float = Field(0.5, ge=0.0, le=1.0, description="Upscaling strength")
    
    @field_validator('contrast')
    @classmethod
    def validate_contrast(cls, v, values=None):
        """Validate contrast values according to Leonardo API."""
        valid_values = [1.0, 1.3, 1.8, 2.5, 3.0, 3.5, 4.0, 4.5]
        if v not in valid_values:
            raise ValueError(f"Contrast must be one of {valid_values}, got {v}")
        return v
    
    @model_validator(mode='after')
    def validate_alchemy_contrast(self):
        """If alchemy is true, contrast must be >= 2.5"""
        if self.alchemy and self.contrast < 2.5:
            raise ValueError("When alchemy is true, contrast must be >= 2.5")
        return self


class LeonardoFluxRequest(ImageGenerationRequest):
    """Request schema specific to Leonardo FLUX model."""
    
    model_type: Literal["flux_speed", "flux_precision"] = Field("flux_precision", description="FLUX model variant")
    style: Optional[str] = Field(None, description="Art style name")
    contrast: float = Field(3.5, description="Contrast level - valid values: [1.0, 1.3, 1.8, 2.5, 3, 3.5, 4, 4.5]")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    enhance_prompt_instruction: Optional[str] = Field(None, description="Custom instruction for prompt enhancement")
    ultra: bool = Field(False, description="Enable Ultra generation mode")
    seed: Optional[int] = Field(None, ge=0, le=2147483638, description="Seed for reproducible generation")
    
    @field_validator('contrast')
    @classmethod
    def validate_contrast(cls, v, values=None):
        """Validate contrast values according to Leonardo API."""
        valid_values = [1.0, 1.3, 1.8, 2.5, 3.0, 3.5, 4.0, 4.5]
        if v not in valid_values:
            raise ValueError(f"Contrast must be one of {valid_values}, got {v}")
        return v
    
    @model_validator(mode='after')
    def validate_enhance_prompt(self):
        """If enhance_prompt is true, ensure instruction is provided when needed."""
        if self.enhance_prompt and self.enhance_prompt_instruction:
            # If instruction is provided, it should be reasonable length
            if len(self.enhance_prompt_instruction.strip()) < 3:
                raise ValueError("Enhancement instruction must be at least 3 characters long")
        return self


class LeonardoPhotoRealRequest(ImageGenerationRequest):
    """Request schema specific to Leonardo PhotoReal model."""
    
    photoreal_version: Literal["v1", "v2"] = Field("v2", description="PhotoReal version - v1 or v2")
    model_id: Optional[str] = Field(None, description="Model ID for PhotoReal v2 (required for v2)")
    style: str = Field("CINEMATIC", description="PhotoReal style")
    contrast: float = Field(3.5, description="Contrast level")
    photoreal_strength: Optional[float] = Field(None, ge=0.1, le=1.0, description="PhotoReal strength (v1 only)")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    
    @field_validator('contrast')
    @classmethod
    def validate_contrast(cls, v, values=None):
        """Validate contrast values according to Leonardo API."""
        if not 1.0 <= v <= 4.5:
            raise ValueError(f"Contrast must be between 1.0 and 4.5, got {v}")
        return v
    
    @model_validator(mode='after')
    def validate_photoreal_version(self):
        """Validate PhotoReal version-specific parameters."""
        if self.photoreal_version == "v2" and not self.model_id:
            raise ValueError("PhotoReal v2 requires a model_id")
        
        if self.photoreal_version == "v2" and self.photoreal_strength is not None:
            raise ValueError("photoreal_strength is only supported in PhotoReal v1")
        
        return self


class ChatCompletionRequest(GenerationRequest):
    """Request schema for chat completion engines."""
    
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens")
    system_prompt: Optional[str] = Field(None, description="System prompt")


# Response Schemas

class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""
    
    generation_id: str = Field(..., description="Unique generation ID")
    engine_name: str = Field(..., description="Engine that performed generation")
    vendor: str = Field(..., description="AI vendor")
    parameters: Dict[str, Any] = Field(..., description="Generation parameters used")
    timestamp: str = Field(..., description="Generation timestamp")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")


class GenerationResult(BaseModel):
    """Base result from any generation engine."""
    
    outputs: List[bytes] = Field(..., description="Generated outputs (images as bytes)")
    metadata: GenerationMetadata = Field(..., description="Generation metadata")
    
    def save_outputs(self, output_dir: Path, prefix: str = "output") -> List[Path]:
        """Save all outputs to files and return paths."""
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        
        for i, output_data in enumerate(self.outputs):
            filename = output_dir / f"{prefix}_{i+1}.png"
            filename.write_bytes(output_data)
            saved_paths.append(filename)
            
        return saved_paths


class ChatCompletionResult(BaseModel):
    """Result from chat completion engines."""
    
    text: str = Field(..., description="Generated text")
    metadata: GenerationMetadata = Field(..., description="Generation metadata")


# Engine Configuration Schemas

class EngineConfig(BaseModel):
    """Base configuration for engines."""
    
    name: str = Field(..., description="Engine name")
    vendor: str = Field(..., description="Vendor name")
    enabled: bool = Field(True, description="Whether engine is enabled")


class LeonardoEngineConfig(EngineConfig):
    """Configuration for Leonardo AI engines."""
    
    api_key: str = Field(..., description="Leonardo API key")
    base_url: str = Field("https://cloud.leonardo.ai/api/rest/v1", description="API base URL")
    timeout: int = Field(300, description="Request timeout in seconds")
    poll_interval: int = Field(2, description="Polling interval in seconds")


class OpenAIEngineConfig(EngineConfig):
    """Configuration for OpenAI engines."""
    
    api_key: str = Field(..., description="OpenAI API key")
    base_url: str = Field("https://api.openai.com/v1", description="API base URL")
    timeout: int = Field(60, description="Request timeout in seconds")
