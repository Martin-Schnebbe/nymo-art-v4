"""
Unified Naming Module for Nymo Art v4

This module centralizes all file and directory naming logic for consistent
naming across single image generation, batch processing, and other features.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import uuid


class NamingConfig:
    """Configuration for naming conventions."""
    
    # Directory settings
    BASE_OUTPUT_DIR = "generated_images"
    LEGACY_BATCH_DIR = "batch_output"
    
    # File naming settings
    MAX_PROMPT_LENGTH = 45
    MAX_FILENAME_LENGTH = 100
    TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
    
    # URL prefix for serving images
    IMAGE_URL_PREFIX = "/images"


class NamingUtils:
    """Utility functions for text processing in names."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 50) -> str:
        """Sanitize text for use in filenames."""
        if not text or not isinstance(text, str):
            return "untitled"
        
        # Convert to lowercase and replace special characters
        sanitized = re.sub(r'[^\w\s-]', '', text.lower())
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        sanitized = sanitized.strip('-')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-')
        
        return sanitized or "untitled"
    
    @staticmethod
    def create_timestamp() -> str:
        """Create a timestamp string for naming."""
        return datetime.now().strftime(NamingConfig.TIMESTAMP_FORMAT)
    
    @staticmethod
    def create_unique_id(length: int = 8) -> str:
        """Create a unique identifier."""
        return str(uuid.uuid4()).replace('-', '')[:length]


class DirectoryNaming:
    """Handles directory naming for different generation types."""
    
    @staticmethod
    def create_base_directory() -> Path:
        """Create and return the base output directory."""
        base_dir = Path(NamingConfig.BASE_OUTPUT_DIR)
        base_dir.mkdir(exist_ok=True)
        return base_dir
    
    @staticmethod
    def create_single_generation_directory(
        engine_type: str,
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> str:
        """Create directory name for single image generation."""
        timestamp = timestamp or NamingUtils.create_timestamp()
        engine = NamingUtils.sanitize_text(engine_type, 15)
        style_part = NamingUtils.sanitize_text(style, 15) if style else "default"
        prompt_part = NamingUtils.sanitize_text(prompt, NamingConfig.MAX_PROMPT_LENGTH) if prompt else "generation"
        
        return f"{timestamp}_{engine}_{style_part}_{prompt_part}"
    
    @staticmethod
    def create_batch_directory(
        batch_id: str,
        total_jobs: int,
        engine_type: str,
        description: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> str:
        """Create directory name for batch processing."""
        timestamp = timestamp or NamingUtils.create_timestamp()
        engine = NamingUtils.sanitize_text(engine_type, 15)
        desc = NamingUtils.sanitize_text(description, 25) if description else f"batch-{total_jobs}-prompts"
        short_id = batch_id.replace('-', '')[:8]
        
        return f"batch_{timestamp}_{desc}_{engine}_{short_id}"


class FileNaming:
    """Handles file naming for images and metadata."""
    
    @staticmethod
    def create_image_filename(
        job_id: Optional[str] = None,
        engine_type: str = "phoenix",
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        image_index: int = 1,
        timestamp: Optional[str] = None,
        unique_id: Optional[str] = None
    ) -> str:
        """Create standardized image filename."""
        parts = []
        
        # Add job ID if provided (for batch processing)
        if job_id:
            parts.append(NamingUtils.sanitize_text(job_id, 15))
        
        # Add engine type
        parts.append(NamingUtils.sanitize_text(engine_type, 15))
        
        # Add style if provided
        if style:
            parts.append(NamingUtils.sanitize_text(style, 15))
        
        # Add prompt snippet
        if prompt:
            parts.append(NamingUtils.sanitize_text(prompt, NamingConfig.MAX_PROMPT_LENGTH))
        
        # Add unique identifier if no timestamp
        if not timestamp and not unique_id:
            unique_id = NamingUtils.create_unique_id(8)
        
        if unique_id:
            parts.append(unique_id)
        
        # Join parts and add image index
        base_name = "_".join(parts)
        filename = f"{base_name}_{image_index:03d}.png"
        
        # Ensure filename is not too long
        if len(filename) > NamingConfig.MAX_FILENAME_LENGTH:
            # Truncate the base name to fit
            max_base_length = NamingConfig.MAX_FILENAME_LENGTH - 8  # 8 for "_001.png"
            base_name = base_name[:max_base_length]
            filename = f"{base_name}_{image_index:03d}.png"
        
        return filename
    
    @staticmethod
    def create_metadata_filename(base_name: str, timestamp: Optional[str] = None) -> str:
        """Create standardized metadata filename."""
        if not timestamp:
            timestamp = NamingUtils.create_timestamp()
        return f"metadata_{NamingUtils.sanitize_text(base_name, 30)}_{timestamp}.json"
    
    @staticmethod
    def create_batch_summary_filename(timestamp: Optional[str] = None) -> str:
        """Create standardized batch summary filename."""
        if not timestamp:
            timestamp = NamingUtils.create_timestamp()
        return f"batch_summary_{timestamp}.json"


class URLGeneration:
    """Handles URL generation for serving images."""
    
    @staticmethod
    def path_to_url(file_path: Union[str, Path], base_dir: Union[str, Path] = None) -> str:
        """Convert a file path to a servable URL."""
        file_path = Path(file_path)
        base_dir = Path(base_dir or NamingConfig.BASE_OUTPUT_DIR)
        
        try:
            # Get relative path from base directory
            relative_path = file_path.relative_to(base_dir)
            # Convert to URL format with forward slashes
            url_path = str(relative_path).replace('\\', '/')
            return f"{NamingConfig.IMAGE_URL_PREFIX}/{url_path}"
        except ValueError:
            # If file is not under base directory, use filename only
            return f"{NamingConfig.IMAGE_URL_PREFIX}/{file_path.name}"
    
    @staticmethod
    def url_to_path(url: str, base_dir: Union[str, Path] = None) -> Path:
        """Convert a URL back to a file path."""
        base_dir = Path(base_dir or NamingConfig.BASE_OUTPUT_DIR)
        
        # Remove URL prefix
        if url.startswith(NamingConfig.IMAGE_URL_PREFIX):
            relative_path = url[len(NamingConfig.IMAGE_URL_PREFIX):].lstrip('/')
        else:
            relative_path = url.lstrip('/')
        
        return base_dir / relative_path


class GenerationNaming:
    """High-level naming interface for different generation types."""
    
    @staticmethod
    def create_single_generation_structure(
        engine_type: str,
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        num_images: int = 1,
        base_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Create complete naming structure for single image generation."""
        base_dir = base_dir or DirectoryNaming.create_base_directory()
        timestamp = NamingUtils.create_timestamp()
        
        # Create directory
        dir_name = DirectoryNaming.create_single_generation_directory(
            engine_type, style, prompt, timestamp
        )
        output_dir = base_dir / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create image filenames
        image_files = []
        for i in range(1, num_images + 1):
            filename = FileNaming.create_image_filename(
                engine_type=engine_type,
                style=style,
                prompt=prompt,
                image_index=i,
                timestamp=timestamp
            )
            image_files.append({
                "filename": filename,
                "path": output_dir / filename,
                "url": URLGeneration.path_to_url(output_dir / filename)
            })
        
        return {
            "generation_id": NamingUtils.create_unique_id(),
            "generation_directory": str(output_dir),
            "directory_name": dir_name,
            "images": image_files,
            "metadata_file": output_dir / FileNaming.create_metadata_filename(dir_name),
            "timestamp": timestamp
        }
    
    @staticmethod
    def create_batch_generation_structure(
        batch_id: str,
        total_jobs: int,
        engine_type: str,
        description: Optional[str] = None,
        base_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Create complete naming structure for batch processing."""
        base_dir = base_dir or DirectoryNaming.create_base_directory()
        timestamp = NamingUtils.create_timestamp()
        
        # Create batch directory
        batch_dir_name = DirectoryNaming.create_batch_directory(
            batch_id, total_jobs, engine_type, description, timestamp
        )
        batch_dir = base_dir / batch_dir_name
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        return {
            "batch_id": batch_id,
            "batch_directory": str(batch_dir),
            "batch_directory_name": batch_dir_name,
            "timestamp": timestamp,
            "metadata_file": batch_dir / FileNaming.create_batch_summary_filename(timestamp)
        }
    
    @staticmethod
    def create_batch_job_structure(
        batch_directory: Path,
        job_id: str,
        engine_type: str,
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        num_images: int = 1
    ) -> Dict[str, Any]:
        """Create naming structure for a single batch job."""
        timestamp = NamingUtils.create_timestamp()
        
        # Create job directory within batch
        job_dir = batch_directory / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        # Create image filenames for the job
        image_files = []
        for i in range(1, num_images + 1):
            filename = FileNaming.create_image_filename(
                job_id=job_id,
                engine_type=engine_type,
                style=style,
                prompt=prompt,
                image_index=i,
                timestamp=timestamp
            )
            image_path = job_dir / filename
            image_files.append({
                "filename": filename,
                "path": str(image_path),
                "url": URLGeneration.path_to_url(image_path)
            })
        
        return {
            "job_id": job_id,
            "job_directory": str(job_dir),
            "images": image_files,
            "metadata_file": job_dir / FileNaming.create_metadata_filename(job_id),
            "timestamp": timestamp
        }


# Convenience functions for backward compatibility
def sanitize_filename(text: str) -> str:
    """Legacy function for filename sanitization."""
    return NamingUtils.sanitize_text(text)

def create_timestamp() -> str:
    """Legacy function for timestamp creation."""
    return NamingUtils.create_timestamp()

def path_to_url(file_path: Union[str, Path]) -> str:
    """Legacy function for URL generation."""
    return URLGeneration.path_to_url(file_path)
