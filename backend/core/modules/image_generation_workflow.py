"""
Image Generation Workflow Module
Shared logic for image generation processes across the application.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from datetime import datetime

from ..schemas import GenerationRequest, GenerationResult, LeonardoEngineConfig
from ..engine.base import ImageGenerationEngine
from .file_manager import EnhancedFileManager


logger = logging.getLogger(__name__)


class ImageGenerationWorkflow:
    """Encapsulates common image generation workflow patterns."""
    
    def __init__(self, engine: ImageGenerationEngine, output_base_dir: str = "generated_images", use_enhanced_naming: bool = True):
        self.engine = engine
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        self.use_enhanced_naming = use_enhanced_naming
        if use_enhanced_naming:
            self.file_manager = EnhancedFileManager(str(self.output_base_dir))
        
    async def generate_and_save(
        self, 
        request: GenerationRequest,
        engine_type: str = "phoenix",
        output_subdir: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Standard workflow: generate -> save -> return metadata.
        
        Args:
            request: Generation request
            engine_type: Type of engine being used (e.g., "phoenix", "flux", "photoreal")
            output_subdir: Optional subdirectory for output
            filename_prefix: Optional prefix for filenames (only used with legacy naming)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with generation metadata and file paths
        """
        if progress_callback:
            progress_callback("Starting image generation...")
        
        # Generate images
        logger.info(f"Starting generation: {request.prompt[:50]}...")
        result = await self.engine.generate(request)
        
        if progress_callback:
            progress_callback("Images generated, saving to disk...")
        
        # Save images with enhanced or legacy naming
        if self.use_enhanced_naming:
            save_result = self.file_manager.save_normal_generation(
                request, result, engine_type, result.outputs, output_subdir
            )
            
            if progress_callback:
                progress_callback(f"Saved {save_result['num_images']} images with metadata")
            
            return {
                "generation_id": result.metadata.generation_id,
                "status": "complete",
                "num_images": save_result['num_images'],
                "image_urls": [self._path_to_url(path) for path in save_result['image_paths']],
                "local_paths": save_result['image_paths'],
                "metadata_path": save_result['metadata_path'],
                "metadata": result.metadata.parameters,
                "cost_estimate": result.metadata.cost_estimate,
                "enhanced_metadata": save_result['metadata']
            }
        else:
            # Legacy saving method
            image_paths = self._save_images(
                result, 
                output_subdir=output_subdir,
                filename_prefix=filename_prefix
            )
            
            if progress_callback:
                progress_callback(f"Saved {len(image_paths)} images successfully")
            
            return {
                "generation_id": result.metadata.generation_id,
                "status": "complete",
                "num_images": len(result.outputs),
                "image_urls": [self._path_to_url(path) for path in image_paths],
                "local_paths": image_paths,
                "metadata": result.metadata.parameters,
                "cost_estimate": result.metadata.cost_estimate
            }
    
    def _save_images(
        self, 
        result: GenerationResult, 
        output_subdir: Optional[str] = None,
        filename_prefix: Optional[str] = None
    ) -> List[str]:
        """Save images to disk and return file paths."""
        # Determine output directory
        if output_subdir:
            output_dir = self.output_base_dir / output_subdir
        else:
            output_dir = self.output_base_dir
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename prefix if not provided
        if not filename_prefix:
            filename_prefix = result.metadata.generation_id
        
        # Save each image
        image_paths = []
        for i, image_data in enumerate(result.outputs):
            filename = f"{filename_prefix}_{i+1}.png"
            filepath = output_dir / filename
            filepath.write_bytes(image_data)
            image_paths.append(str(filepath))
            
        logger.info(f"Saved {len(image_paths)} images to {output_dir}")
        return image_paths
    
    def _path_to_url(self, file_path: str) -> str:
        """Convert file path to URL for API responses."""
        # Always return /images/{filename} for frontend compatibility
        filename = Path(file_path).name
        return f"/images/{filename}"
    
    def estimate_cost(self, request: GenerationRequest) -> float:
        """Estimate generation cost."""
        return self.engine.estimate_cost(request)
    
    def validate_request(self, request: GenerationRequest) -> None:
        """Validate generation request."""
        self.engine.validate_request(request)


class BatchImageGenerationWorkflow:
    """Specialized workflow for batch image generation."""
    
    def __init__(self, engine: ImageGenerationEngine, batch_id: str, output_base_dir: str = "batch_output", use_enhanced_naming: bool = True):
        self.engine = engine
        self.batch_id = batch_id
        self.output_base_dir = Path(output_base_dir)
        self.use_enhanced_naming = use_enhanced_naming
        
        if use_enhanced_naming:
            self.file_manager = EnhancedFileManager(str(self.output_base_dir))
            # Create batch structure will be called separately
            self.batch_dir = None
            self.batch_metadata = None
            self.batch_metadata_path = None
        else:
            # Legacy approach
            self.batch_dir = self.output_base_dir / f"batch_{batch_id}"
            self.batch_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize_batch(self, total_jobs: int, engine_type: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Initialize batch with enhanced structure (only for enhanced naming)."""
        if not self.use_enhanced_naming:
            return {"batch_dir": str(self.batch_dir)}
        
        batch_structure = self.file_manager.create_batch_structure(
            self.batch_id, total_jobs, engine_type, description
        )
        
        self.batch_dir = Path(batch_structure["batch_dir"])
        self.batch_metadata = batch_structure["batch_metadata"]
        self.batch_metadata_path = Path(batch_structure["metadata_path"])
        
        return batch_structure
        
    async def process_single_job(
        self, 
        job_id: str,
        request: GenerationRequest,
        engine_type: str = "phoenix",
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """Process a single batch job."""
        if progress_callback:
            progress_callback(f"Processing job {job_id}")
        
        start_time = datetime.now()
        
        try:
            # Generate images
            result = await self.engine.generate(request)
            
            if self.use_enhanced_naming and self.batch_dir and self.batch_metadata:
                # Use enhanced file management
                job_result = self.file_manager.save_batch_job(
                    self.batch_dir, job_id, request, result, engine_type,
                    result.outputs, self.batch_metadata
                )
                
                # Save updated batch metadata
                if self.batch_metadata_path:
                    self.file_manager.metadata.save_metadata(
                        self.batch_metadata, self.batch_metadata_path
                    )
                
                end_time = datetime.now()
                job_result.update({
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "processing_time": (end_time - start_time).total_seconds()
                })
                
                return job_result
            else:
                # Legacy approach
                if self.batch_dir is None:
                    raise ValueError("Batch directory not initialized")
                
                # Save images in job-specific directory
                job_dir = self.batch_dir / job_id
                job_dir.mkdir(exist_ok=True)
                
                image_paths = []
                for i, image_data in enumerate(result.outputs):
                    filename = f"{job_id}_image_{i+1:02d}.png"
                    filepath = job_dir / filename
                    filepath.write_bytes(image_data)
                    image_paths.append(str(filepath))
                
                end_time = datetime.now()
                
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "generation_id": result.metadata.generation_id,
                    "image_paths": image_paths,
                    "num_images": len(image_paths),
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "processing_time": (end_time - start_time).total_seconds(),
                    "cost_estimate": result.metadata.cost_estimate
                }
            
        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Job {job_id} failed: {e}")
            
            job_result = {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "processing_time": (end_time - start_time).total_seconds()
            }
            
            # Update batch metadata for failed job if using enhanced naming
            if self.use_enhanced_naming and self.batch_metadata and self.batch_metadata_path:
                self.file_manager.metadata.update_batch_job_metadata(
                    self.batch_metadata, job_id, job_result
                )
                self.file_manager.metadata.save_metadata(
                    self.batch_metadata, self.batch_metadata_path
                )
            
            return job_result
    
    def finalize_batch(self) -> None:
        """Finalize batch processing."""
        if self.use_enhanced_naming and self.batch_metadata and self.batch_metadata_path:
            self.file_manager.finalize_batch(self.batch_metadata_path, self.batch_metadata)


class ImageGenerationRequestFactory:
    """Factory for creating generation requests from different sources."""
    
    @staticmethod
    def from_api_request(api_request: Any, request_type: str) -> GenerationRequest:
        """Create engine request from API request."""
        if request_type.lower() == 'phoenix':
            from ..schemas import LeonardoPhoenixRequest
            return LeonardoPhoenixRequest(
                prompt=api_request.prompt,
                num_outputs=api_request.num_images,
                width=api_request.width,
                height=api_request.height,
                style=api_request.style,
                contrast=api_request.contrast,
                alchemy=api_request.alchemy,
                enhance_prompt=api_request.enhance_prompt,
                negative_prompt=api_request.negative_prompt,
                upscale=getattr(api_request, 'upscale', False),
                upscale_strength=getattr(api_request, 'upscale_strength', 0.5)
            )
        elif request_type.lower() == 'flux':
            from ..schemas import LeonardoFluxRequest
            return LeonardoFluxRequest(
                prompt=api_request.prompt,
                num_outputs=api_request.num_images,
                width=api_request.width,
                height=api_request.height,
                model_type=api_request.model_type,
                style=api_request.style,
                contrast=api_request.contrast,
                enhance_prompt=api_request.enhance_prompt,
                enhance_prompt_instruction=getattr(api_request, 'enhance_prompt_instruction', None),
                negative_prompt=api_request.negative_prompt,
                ultra=getattr(api_request, 'ultra', False),
                seed=getattr(api_request, 'seed', None)
            )
        elif request_type.lower() == 'photoreal':
            from ..schemas import LeonardoPhotoRealRequest
            return LeonardoPhotoRealRequest(
                prompt=api_request.prompt,
                num_outputs=api_request.num_images,
                width=api_request.width,
                height=api_request.height,
                photoreal_version=api_request.photoreal_version,
                model_id=getattr(api_request, 'model_id', None),
                style=api_request.style,
                contrast=api_request.contrast,
                photoreal_strength=getattr(api_request, 'photoreal_strength', None),
                enhance_prompt=api_request.enhance_prompt,
                negative_prompt=api_request.negative_prompt
            )
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    @staticmethod
    def from_batch_params(prompt: str, params: Dict[str, Any], engine_type: str) -> GenerationRequest:
        """Create engine request from batch parameters."""
        if 'phoenix' in engine_type.lower():
            from ..schemas import LeonardoPhoenixRequest
            return LeonardoPhoenixRequest(
                prompt=prompt,
                num_outputs=params.get('num_outputs', 1),
                width=params.get('width', 1024),
                height=params.get('height', 1024),
                style=params.get('style'),
                contrast=params.get('contrast', 3.5),
                alchemy=params.get('alchemy', True),
                enhance_prompt=params.get('enhance_prompt', False),
                negative_prompt=params.get('negative_prompt', ''),
                upscale=params.get('upscale', False),
                upscale_strength=params.get('upscale_strength', 0.5)
            )
        elif 'flux' in engine_type.lower():
            from ..schemas import LeonardoFluxRequest
            return LeonardoFluxRequest(
                prompt=prompt,
                num_outputs=params.get('num_outputs', 1),
                width=params.get('width', 1024),
                height=params.get('height', 1024),
                model_type=params.get('model_type', 'flux_precision'),
                style=params.get('style'),
                contrast=params.get('contrast', 3.5),
                enhance_prompt=params.get('enhance_prompt', False),
                enhance_prompt_instruction=params.get('enhance_prompt_instruction'),
                negative_prompt=params.get('negative_prompt', ''),
                ultra=params.get('ultra', False),
                seed=params.get('seed')
            )
        elif 'photoreal' in engine_type.lower():
            from ..schemas import LeonardoPhotoRealRequest
            return LeonardoPhotoRealRequest(
                prompt=prompt,
                num_outputs=params.get('num_outputs', 1),
                width=params.get('width', 1024),
                height=params.get('height', 1024),
                photoreal_version=params.get('photoreal_version', 'v2'),
                model_id=params.get('model_id'),
                style=params.get('style', 'CINEMATIC'),
                contrast=params.get('contrast', 3.5),
                photoreal_strength=params.get('photoreal_strength'),
                enhance_prompt=params.get('enhance_prompt', False),
                negative_prompt=params.get('negative_prompt', '')
            )
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
