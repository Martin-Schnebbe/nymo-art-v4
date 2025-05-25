"""
Enhanced File Management Module
Handles improved naming conventions and metadata storage for generated images.
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..schemas import GenerationRequest, GenerationResult


class FileNamingManager:
    """Manages enhanced file naming conventions with timestamps and metadata."""
    
    @staticmethod
    def sanitize_prompt(prompt: str, max_length: int = 50) -> str:
        """Sanitize prompt for use in filename."""
        # Remove special characters and replace with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', prompt.lower())
        # Replace spaces and multiple hyphens with single hyphens
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-')
        return sanitized
    
    @staticmethod
    def generate_generation_folder_name(
        request: GenerationRequest,
        engine_type: str,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate folder name for single generation.
        Format: 2025-05-25_14-30-15_phoenix_dynamic_a-beautiful-sunset
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format timestamp
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Get engine type (e.g., "phoenix", "flux", "photoreal")
        engine_name = engine_type.lower().split('_')[0]
        
        # Get style or model type
        style_part = ""
        style_attr = getattr(request, 'style', None)
        model_type_attr = getattr(request, 'model_type', None)
        
        if style_attr:
            style_part = FileNamingManager.sanitize_prompt(style_attr, 15)
        elif model_type_attr:
            style_part = FileNamingManager.sanitize_prompt(model_type_attr, 15)
        
        # Sanitize prompt
        prompt_part = FileNamingManager.sanitize_prompt(request.prompt, 40)
        
        # Combine parts
        parts = [timestamp_str, engine_name]
        if style_part:
            parts.append(style_part)
        parts.append(prompt_part)
        
        return "_".join(parts)

    @staticmethod
    def generate_normal_filename(
        request: GenerationRequest,
        engine_type: str,
        image_index: int = 1,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate filename for normal generation (inside generation folder).
        Format: phoenix_dynamic_a-beautiful-sunset_001.png
        """
        # Get engine type (e.g., "phoenix", "flux", "photoreal")
        engine_name = engine_type.lower().split('_')[0]
        
        # Get style or model type
        style_part = ""
        style_attr = getattr(request, 'style', None)
        model_type_attr = getattr(request, 'model_type', None)
        
        if style_attr:
            style_part = FileNamingManager.sanitize_prompt(style_attr, 15)
        elif model_type_attr:
            style_part = FileNamingManager.sanitize_prompt(model_type_attr, 15)
        
        # Sanitize prompt
        prompt_part = FileNamingManager.sanitize_prompt(request.prompt, 40)
        
        # Format image index
        index_str = f"{image_index:03d}"
        
        # Combine parts
        parts = [engine_name]
        if style_part:
            parts.append(style_part)
        parts.extend([prompt_part, index_str])
        
        return "_".join(parts) + ".png"
    
    @staticmethod
    def generate_batch_folder_name(
        batch_id: str,
        timestamp: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Generate folder name for batch generation.
        Format: batch_2025-05-25_14-30-15_landscape-scenes_8c3fe95c
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
        batch_short = batch_id[:8]  # Short batch ID
        
        parts = ["batch", timestamp_str]
        if description:
            desc_part = FileNamingManager.sanitize_prompt(description, 20)
            parts.append(desc_part)
        parts.append(batch_short)
        
        return "_".join(parts)
    
    @staticmethod
    def generate_batch_filename(
        job_id: str,
        request: GenerationRequest,
        engine_type: str,
        image_index: int = 1
    ) -> str:
        """
        Generate filename for batch job.
        Format: job_003_phoenix_cinematic_mountain-sunset_001.png
        """
        # Get engine type
        engine_name = engine_type.lower().split('_')[0]
        
        # Get style or model type
        style_part = ""
        style_attr = getattr(request, 'style', None)
        model_type_attr = getattr(request, 'model_type', None)
        
        if style_attr:
            style_part = FileNamingManager.sanitize_prompt(style_attr, 15)
        elif model_type_attr:
            style_part = FileNamingManager.sanitize_prompt(model_type_attr, 15)
        
        # Sanitize prompt
        prompt_part = FileNamingManager.sanitize_prompt(request.prompt, 30)
        
        # Format image index
        index_str = f"{image_index:03d}"
        
        # Combine parts
        parts = [job_id, engine_name]
        if style_part:
            parts.append(style_part)
        parts.extend([prompt_part, index_str])
        
        return "_".join(parts) + ".png"


class MetadataManager:
    """Manages metadata storage for generated images."""
    
    @staticmethod
    def create_generation_metadata(
        request: GenerationRequest,
        result: GenerationResult,
        engine_type: str,
        image_paths: List[str],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create comprehensive metadata for a generation."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Base metadata
        metadata = {
            "generation_info": {
                "generation_id": result.metadata.generation_id,
                "timestamp": timestamp.isoformat(),
                "engine_type": engine_type,
                "engine_parameters": result.metadata.parameters,
                "cost_estimate": result.metadata.cost_estimate,
                "processing_time": getattr(result.metadata, 'processing_time', None)
            },
            "request_parameters": {
                "prompt": request.prompt,
                "num_outputs": request.num_outputs,
                "width": getattr(request, 'width', None),
                "height": getattr(request, 'height', None),
            },
            "images": [
                {
                    "index": i + 1,
                    "filename": Path(path).name,
                    "filepath": path,
                    "size_bytes": Path(path).stat().st_size if Path(path).exists() else 0
                }
                for i, path in enumerate(image_paths)
            ],
            "metadata_version": "1.0"
        }
        
        # Add engine-specific parameters using getattr to avoid type issues
        style = getattr(request, 'style', None)
        if style is not None:
            metadata["request_parameters"]["style"] = style
            
        contrast = getattr(request, 'contrast', None)
        if contrast is not None:
            metadata["request_parameters"]["contrast"] = contrast
            
        negative_prompt = getattr(request, 'negative_prompt', None)
        if negative_prompt is not None:
            metadata["request_parameters"]["negative_prompt"] = negative_prompt
            
        alchemy = getattr(request, 'alchemy', None)
        if alchemy is not None:
            metadata["request_parameters"]["alchemy"] = alchemy
            
        enhance_prompt = getattr(request, 'enhance_prompt', None)
        if enhance_prompt is not None:
            metadata["request_parameters"]["enhance_prompt"] = enhance_prompt
            
        model_type = getattr(request, 'model_type', None)
        if model_type is not None:
            metadata["request_parameters"]["model_type"] = model_type
            
        photoreal_version = getattr(request, 'photoreal_version', None)
        if photoreal_version is not None:
            metadata["request_parameters"]["photoreal_version"] = photoreal_version
            
        upscale = getattr(request, 'upscale', None)
        if upscale is not None:
            metadata["request_parameters"]["upscale"] = upscale
            
        upscale_strength = getattr(request, 'upscale_strength', None)
        if upscale_strength is not None:
            metadata["request_parameters"]["upscale_strength"] = upscale_strength
            
        ultra = getattr(request, 'ultra', None)
        if ultra is not None:
            metadata["request_parameters"]["ultra"] = ultra
            
        seed = getattr(request, 'seed', None)
        if seed is not None:
            metadata["request_parameters"]["seed"] = seed
        
        return metadata
    
    @staticmethod
    def save_metadata(metadata: Dict[str, Any], filepath: Path) -> None:
        """Save metadata to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_metadata(filepath: Path) -> Optional[Dict[str, Any]]:
        """Load metadata from JSON file."""
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata from {filepath}: {e}")
            return None
    
    @staticmethod
    def create_batch_metadata(
        batch_id: str,
        total_jobs: int,
        engine_type: str,
        timestamp: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create metadata for batch processing."""
        if timestamp is None:
            timestamp = datetime.now()
        
        return {
            "batch_info": {
                "batch_id": batch_id,
                "timestamp": timestamp.isoformat(),
                "description": description,
                "total_jobs": total_jobs,
                "engine_type": engine_type,
                "status": "started"
            },
            "jobs": {},
            "summary": {
                "completed": 0,
                "failed": 0,
                "total_images": 0,
                "total_cost": 0.0
            },
            "metadata_version": "1.0"
        }
    
    @staticmethod
    def update_batch_job_metadata(
        batch_metadata: Dict[str, Any],
        job_id: str,
        job_result: Dict[str, Any]
    ) -> None:
        """Update batch metadata with job result."""
        batch_metadata["jobs"][job_id] = job_result
        
        # Update summary
        if job_result["status"] == "completed":
            batch_metadata["summary"]["completed"] += 1
            batch_metadata["summary"]["total_images"] += job_result.get("num_images", 0)
            batch_metadata["summary"]["total_cost"] += job_result.get("cost_estimate", 0.0)
        elif job_result["status"] == "failed":
            batch_metadata["summary"]["failed"] += 1
    
    @staticmethod
    def finalize_batch_metadata(batch_metadata: Dict[str, Any]) -> None:
        """Finalize batch metadata when processing is complete."""
        batch_metadata["batch_info"]["status"] = "completed"
        batch_metadata["batch_info"]["completed_timestamp"] = datetime.now().isoformat()


class EnhancedFileManager:
    """Main class that combines naming and metadata management."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.naming = FileNamingManager()
        self.metadata = MetadataManager()
    
    def save_normal_generation(
        self,
        request: GenerationRequest,
        result: GenerationResult,
        engine_type: str,
        image_data_list: List[bytes],
        output_subdir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save normal generation with enhanced naming and metadata in its own folder."""
        timestamp = datetime.now()
        
        # Create generation-specific folder
        generation_folder_name = self.naming.generate_generation_folder_name(
            request, engine_type, timestamp
        )
        
        # Determine output directory
        if output_subdir:
            generation_dir = self.base_dir / output_subdir / generation_folder_name
        else:
            generation_dir = self.base_dir / generation_folder_name
        generation_dir.mkdir(parents=True, exist_ok=True)
        
        # Save images with enhanced names
        image_paths = []
        for i, image_data in enumerate(image_data_list):
            filename = self.naming.generate_normal_filename(
                request, engine_type, i + 1, timestamp
            )
            filepath = generation_dir / filename
            filepath.write_bytes(image_data)
            image_paths.append(str(filepath))
        
        # Create and save metadata
        metadata = self.metadata.create_generation_metadata(
            request, result, engine_type, image_paths, timestamp
        )
        
        # Save metadata file
        metadata_filename = f"metadata_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        metadata_filepath = generation_dir / metadata_filename
        self.metadata.save_metadata(metadata, metadata_filepath)
        
        return {
            "generation_id": result.metadata.generation_id,
            "status": "complete",
            "num_images": len(image_paths),
            "image_paths": image_paths,
            "metadata_path": str(metadata_filepath),
            "timestamp": timestamp.isoformat(),
            "generation_folder": str(generation_dir),
            "folder_name": generation_folder_name,
            "metadata": metadata
        }
    
    def create_batch_structure(
        self,
        batch_id: str,
        total_jobs: int,
        engine_type: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create enhanced batch folder structure."""
        timestamp = datetime.now()
        
        # Create batch folder with enhanced name
        folder_name = self.naming.generate_batch_folder_name(
            batch_id, timestamp, description
        )
        batch_dir = self.base_dir / folder_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Create batch metadata
        batch_metadata = self.metadata.create_batch_metadata(
            batch_id, total_jobs, engine_type, timestamp, description
        )
        
        # Save initial batch metadata
        metadata_filepath = batch_dir / "batch_metadata.json"
        self.metadata.save_metadata(batch_metadata, metadata_filepath)
        
        return {
            "batch_dir": str(batch_dir),
            "metadata_path": str(metadata_filepath),
            "batch_metadata": batch_metadata,
            "folder_name": folder_name
        }
    
    def save_batch_job(
        self,
        batch_dir: Path,
        job_id: str,
        request: GenerationRequest,
        result: GenerationResult,
        engine_type: str,
        image_data_list: List[bytes],
        batch_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save batch job with enhanced naming and metadata."""
        # Create job subdirectory
        job_dir = batch_dir / job_id
        job_dir.mkdir(exist_ok=True)
        
        # Save images with enhanced names
        image_paths = []
        for i, image_data in enumerate(image_data_list):
            filename = self.naming.generate_batch_filename(
                job_id, request, engine_type, i + 1
            )
            filepath = job_dir / filename
            filepath.write_bytes(image_data)
            image_paths.append(str(filepath))
        
        # Create job metadata
        job_metadata = self.metadata.create_generation_metadata(
            request, result, engine_type, image_paths
        )
        
        # Save job metadata
        job_metadata_filepath = job_dir / f"{job_id}_metadata.json"
        self.metadata.save_metadata(job_metadata, job_metadata_filepath)
        
        # Create job result for batch tracking
        job_result = {
            "job_id": job_id,
            "status": "completed",
            "generation_id": result.metadata.generation_id,
            "image_paths": image_paths,
            "num_images": len(image_paths),
            "cost_estimate": result.metadata.cost_estimate,
            "metadata_path": str(job_metadata_filepath),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update batch metadata
        self.metadata.update_batch_job_metadata(batch_metadata, job_id, job_result)
        
        return job_result
    
    def finalize_batch(
        self,
        batch_metadata_path: Path,
        batch_metadata: Dict[str, Any]
    ) -> None:
        """Finalize batch processing and save final metadata."""
        self.metadata.finalize_batch_metadata(batch_metadata)
        self.metadata.save_metadata(batch_metadata, batch_metadata_path)
