"""
Abstract base classes for AI generation engines.
Framework-agnostic domain logic with clear interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
import logging
from datetime import datetime

from ..schemas import (
    GenerationRequest, 
    GenerationResult, 
    GenerationMetadata,
    EngineConfig
)


logger = logging.getLogger(__name__)


class BaseEngine(ABC):
    """Abstract base class for all AI generation engines."""
    
    def __init__(self, config: EngineConfig):
        """Initialize engine with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if not config.enabled:
            raise ValueError(f"Engine {config.name} is disabled")
            
        self.logger.info(f"Initialized {config.vendor} {config.name} engine")
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate content based on request."""
        pass
    
    @abstractmethod
    def validate_request(self, request: GenerationRequest) -> None:
        """Validate that request is compatible with this engine."""
        pass
    
    def create_metadata(
        self, 
        generation_id: str, 
        parameters: Dict[str, Any],
        cost_estimate: Optional[float] = None
    ) -> GenerationMetadata:
        """Create standardized metadata for generation results."""
        return GenerationMetadata(
            generation_id=generation_id,
            engine_name=self.config.name,
            vendor=self.config.vendor,
            parameters=parameters,
            timestamp=datetime.utcnow().isoformat(),
            cost_estimate=cost_estimate
        )
    
    def __str__(self) -> str:
        return f"{self.config.vendor}.{self.config.name}"


class ImageGenerationEngine(BaseEngine):
    """Abstract base for image generation engines."""
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate images based on request."""
        pass
    
    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate generation cost in USD. Override in subclasses."""
        return 0.0


class TextGenerationEngine(BaseEngine):
    """Abstract base for text generation engines."""
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate text based on request."""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count. Simple approximation, override for accuracy."""
        return int(len(text.split()) * 1.3)  # Rough approximation


class EngineRegistry:
    """Registry for managing available engines."""
    
    def __init__(self):
        self._engines: Dict[str, BaseEngine] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register(self, engine: BaseEngine) -> None:
        """Register an engine."""
        key = f"{engine.config.vendor}.{engine.config.name}"
        self._engines[key] = engine
        self.logger.info(f"Registered engine: {key}")
    
    def get(self, vendor: str, name: str) -> BaseEngine:
        """Get an engine by vendor and name."""
        key = f"{vendor}.{name}"
        if key not in self._engines:
            available = list(self._engines.keys())
            raise ValueError(f"Engine {key} not found. Available: {available}")
        return self._engines[key]
    
    def list_engines(self) -> Dict[str, str]:
        """List all registered engines."""
        return {key: str(engine) for key, engine in self._engines.items()}
    
    def is_available(self, vendor: str, name: str) -> bool:
        """Check if an engine is available."""
        key = f"{vendor}.{name}"
        return key in self._engines


# Global registry instance
engine_registry = EngineRegistry()
