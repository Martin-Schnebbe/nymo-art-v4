"""
Parameter Validation Module
Shared validation logic for image generation parameters across different engines.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class ParameterValidator:
    """Centralized parameter validation for image generation."""
    
    # Standard dimension options
    VALID_DIMENSIONS = [512, 768, 1024, 1344, 1536]
    
    # Valid image counts
    MIN_IMAGES = 1
    MAX_IMAGES = 10
    
    # Contrast ranges
    MIN_CONTRAST = 1.0
    MAX_CONTRAST = 4.5
    
    # Upscale strength ranges  
    MIN_UPSCALE_STRENGTH = 0.0
    MAX_UPSCALE_STRENGTH = 1.0
    
    @classmethod
    def validate_common_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate common parameters across all models."""
        validated = {}
        errors = []
        
        # Validate prompt
        prompt = params.get('prompt', '').strip()
        if not prompt:
            errors.append("Prompt is required and cannot be empty")
        elif len(prompt) > 1000:
            errors.append("Prompt must be 1000 characters or less")
        validated['prompt'] = prompt
        
        # Validate num_images/num_outputs
        num_images = params.get('num_images', params.get('num_outputs', 1))
        if not isinstance(num_images, int) or not (cls.MIN_IMAGES <= num_images <= cls.MAX_IMAGES):
            errors.append(f"Number of images must be between {cls.MIN_IMAGES} and {cls.MAX_IMAGES}")
        validated['num_outputs'] = num_images
        
        # Validate dimensions
        width = params.get('width', 1024)
        height = params.get('height', 1024)
        
        if width not in cls.VALID_DIMENSIONS:
            errors.append(f"Width must be one of: {cls.VALID_DIMENSIONS}")
        if height not in cls.VALID_DIMENSIONS:
            errors.append(f"Height must be one of: {cls.VALID_DIMENSIONS}")
            
        validated['width'] = width
        validated['height'] = height
        
        # Validate contrast
        contrast = params.get('contrast', 3.5)
        if not isinstance(contrast, (int, float)) or not (cls.MIN_CONTRAST <= contrast <= cls.MAX_CONTRAST):
            errors.append(f"Contrast must be between {cls.MIN_CONTRAST} and {cls.MAX_CONTRAST}")
        validated['contrast'] = float(contrast)
        
        # Validate negative prompt (optional)
        negative_prompt = params.get('negative_prompt', '')
        if negative_prompt and len(negative_prompt) > 500:
            errors.append("Negative prompt must be 500 characters or less")
        validated['negative_prompt'] = negative_prompt
        
        # Validate enhance_prompt (boolean)
        validated['enhance_prompt'] = bool(params.get('enhance_prompt', False))
        
        if errors:
            raise ValueError(f"Parameter validation failed: {'; '.join(errors)}")
            
        return validated
    
    @classmethod
    def validate_phoenix_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Phoenix-specific parameters."""
        validated = cls.validate_common_params(params)
        errors = []
        
        # Phoenix styles
        PHOENIX_STYLES = [
            "3D Render", "Bokeh", "Cinematic", "Cinematic Concept", "Creative", "Dynamic",
            "Fashion", "Graphic Design Pop Art", "Graphic Design Vector", "HDR", "Illustration",
            "Macro", "Minimalist", "Moody", "None", "Portrait", "Pro B&W photography",
            "Pro color photography", "Raytraced", "Stock Photo", "Vibrant"
        ]
        
        style = params.get('style')
        if style and style not in PHOENIX_STYLES:
            errors.append(f"Phoenix style must be one of: {PHOENIX_STYLES}")
        validated['style'] = style
        
        # Validate alchemy (boolean)
        validated['alchemy'] = bool(params.get('alchemy', True))
        
        # Validate upscale parameters
        validated['upscale'] = bool(params.get('upscale', False))
        
        upscale_strength = params.get('upscale_strength', 0.5)
        if not isinstance(upscale_strength, (int, float)) or not (cls.MIN_UPSCALE_STRENGTH <= upscale_strength <= cls.MAX_UPSCALE_STRENGTH):
            errors.append(f"Upscale strength must be between {cls.MIN_UPSCALE_STRENGTH} and {cls.MAX_UPSCALE_STRENGTH}")
        validated['upscale_strength'] = float(upscale_strength)
        
        if errors:
            raise ValueError(f"Phoenix parameter validation failed: {'; '.join(errors)}")
            
        return validated
    
    @classmethod 
    def validate_flux_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FLUX-specific parameters."""
        validated = cls.validate_common_params(params)
        errors = []
        
        # FLUX model types
        FLUX_MODELS = ["flux_precision", "flux_speed"]
        model_type = params.get('model_type', 'flux_precision')
        if model_type not in FLUX_MODELS:
            errors.append(f"FLUX model type must be one of: {FLUX_MODELS}")
        validated['model_type'] = model_type
        
        # FLUX styles (optional)
        style = params.get('style')
        validated['style'] = style  # FLUX styles are flexible
        
        # Validate ultra mode
        validated['ultra'] = bool(params.get('ultra', False))
        
        # Validate enhance_prompt_instruction (optional)
        enhance_instruction = params.get('enhance_prompt_instruction', '')
        if enhance_instruction and len(enhance_instruction) > 200:
            errors.append("Enhance prompt instruction must be 200 characters or less")
        validated['enhance_prompt_instruction'] = enhance_instruction
        
        # Validate seed (optional)
        seed = params.get('seed')
        if seed is not None:
            try:
                seed = int(seed)
                if not (0 <= seed <= 2**32 - 1):
                    errors.append("Seed must be between 0 and 2^32-1")
            except (ValueError, TypeError):
                errors.append("Seed must be a valid integer")
        validated['seed'] = seed
        
        if errors:
            raise ValueError(f"FLUX parameter validation failed: {'; '.join(errors)}")
            
        return validated
    
    @classmethod
    def validate_photoreal_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PhotoReal-specific parameters."""
        validated = cls.validate_common_params(params)
        errors = []
        
        # PhotoReal versions
        PHOTOREAL_VERSIONS = ["v1", "v2"]
        version = params.get('photoreal_version', 'v2')
        if version not in PHOTOREAL_VERSIONS:
            errors.append(f"PhotoReal version must be one of: {PHOTOREAL_VERSIONS}")
        validated['photoreal_version'] = version
        
        # PhotoReal styles
        PHOTOREAL_STYLES = ["CINEMATIC", "PHOTOGRAPHY", "PORTRAIT", "LIFESTYLE", "FASHION"]
        style = params.get('style', 'CINEMATIC')
        if style not in PHOTOREAL_STYLES:
            errors.append(f"PhotoReal style must be one of: {PHOTOREAL_STYLES}")
        validated['style'] = style
        
        # Validate model_id for v2
        model_id = params.get('model_id')
        if version == "v2" and not model_id:
            errors.append("model_id is required for PhotoReal v2")
        validated['model_id'] = model_id
        
        # Validate photoreal_strength (v1 only)
        photoreal_strength = params.get('photoreal_strength')
        if version == "v1":
            if photoreal_strength is None:
                photoreal_strength = 0.35
            elif not isinstance(photoreal_strength, (int, float)) or not (0.0 <= photoreal_strength <= 1.0):
                errors.append("PhotoReal strength must be between 0.0 and 1.0")
        elif version == "v2":
            photoreal_strength = None  # Not used in v2
        validated['photoreal_strength'] = photoreal_strength
        
        if errors:
            raise ValueError(f"PhotoReal parameter validation failed: {'; '.join(errors)}")
            
        return validated


class FileValidator:
    """Validation for file uploads and paths."""
    
    ALLOWED_CSV_EXTENSIONS = ['.csv']
    MAX_CSV_SIZE_MB = 10
    MAX_CSV_ROWS = 1000
    
    @classmethod
    def validate_csv_file(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate CSV file for batch processing."""
        file_path = Path(file_path)
        errors = []
        info = {}
        
        # Check if file exists
        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            
        # Check file extension
        if file_path.suffix.lower() not in cls.ALLOWED_CSV_EXTENSIONS:
            errors.append(f"File must have one of these extensions: {cls.ALLOWED_CSV_EXTENSIONS}")
            
        # Check file size
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            info['size_mb'] = round(size_mb, 2)
            
            if size_mb > cls.MAX_CSV_SIZE_MB:
                errors.append(f"File too large: {size_mb:.1f}MB (max: {cls.MAX_CSV_SIZE_MB}MB)")
        
        # Validate CSV content
        if file_path.exists() and file_path.suffix.lower() == '.csv':
            try:
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    # Check for required columns
                    fieldnames = reader.fieldnames or []
                    if 'prompt' not in fieldnames:
                        errors.append("CSV must contain a 'prompt' column")
                    
                    # Count rows and validate content
                    rows = list(reader)
                    info['num_rows'] = len(rows)
                    
                    if len(rows) > cls.MAX_CSV_ROWS:
                        errors.append(f"Too many rows: {len(rows)} (max: {cls.MAX_CSV_ROWS})")
                    
                    if len(rows) == 0:
                        errors.append("CSV file is empty")
                    
                    # Check for empty prompts
                    empty_prompts = sum(1 for row in rows if not row.get('prompt', '').strip())
                    if empty_prompts > 0:
                        errors.append(f"{empty_prompts} rows have empty prompts")
                        
                    info['empty_prompts'] = empty_prompts
                    
            except Exception as e:
                errors.append(f"Error reading CSV file: {str(e)}")
        
        if errors:
            raise ValueError(f"CSV validation failed: {'; '.join(errors)}")
            
        return info


# Convenience functions for easy import
def validate_phoenix_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for Phoenix parameter validation."""
    return ParameterValidator.validate_phoenix_params(params)

def validate_flux_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for FLUX parameter validation."""
    return ParameterValidator.validate_flux_params(params)

def validate_photoreal_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for PhotoReal parameter validation."""
    return ParameterValidator.validate_photoreal_params(params)

def validate_csv_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Convenience function for CSV file validation."""
    return FileValidator.validate_csv_file(file_path)
