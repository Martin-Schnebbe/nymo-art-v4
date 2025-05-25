"""
Batch processing API routes
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import csv
import io
from pathlib import Path
from datetime import datetime
import asyncio
import uuid

from ..api import ValidationError, EngineError
from core.batch_processor import BatchProcessor, BatchConfig, BatchJob
from core.schemas import GenerationRequest, LeonardoEngineConfig
from core.engine.leonardo.phoenix import PhoenixEngine
from core.engine.leonardo.flux import FluxEngine  
from core.engine.leonardo.photoreal import LeonardoPhotoRealEngine
from core.engine.base import engine_registry
from core.naming import NamingConfig
import os


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/batch", tags=["batch"])


# In-memory storage for batch jobs (in production, use Redis or database)
active_batches: Dict[str, Dict[str, Any]] = {}


# Dependency to get engines
def get_phoenix_engine() -> PhoenixEngine:
    """Get configured Phoenix engine."""
    try:
        engine = engine_registry.get("leonardo", "phoenix")
        if not isinstance(engine, PhoenixEngine):
            raise ValueError("Engine is not a PhoenixEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="phoenix",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = PhoenixEngine(config)
        engine_registry.register(engine)
        return engine

def get_flux_engine() -> FluxEngine:
    """Get configured FLUX engine."""
    try:
        engine = engine_registry.get("leonardo", "flux")
        if not isinstance(engine, FluxEngine):
            raise ValueError("Engine is not a FluxEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="flux",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = FluxEngine(config)
        engine_registry.register(engine)
        return engine

def get_photoreal_engine() -> LeonardoPhotoRealEngine:
    """Get configured PhotoReal engine."""
    try:
        engine = engine_registry.get("leonardo", "photoreal")
        if not isinstance(engine, LeonardoPhotoRealEngine):
            raise ValueError("Engine is not a LeonardoPhotoRealEngine instance")
        return engine
    except ValueError:
        # Create and register engine if not exists
        api_key = os.getenv("LEONARDO_API_KEY")
        if not api_key:
            raise ValidationError("Leonardo API key not configured")
        
        config = LeonardoEngineConfig(
            name="photoreal",
            vendor="leonardo",
            enabled=True,
            api_key=api_key,
            base_url="https://cloud.leonardo.ai/api/rest/v1",
            timeout=300,
            poll_interval=2
        )
        
        engine = LeonardoPhotoRealEngine(config)
        engine_registry.register(engine)
        return engine


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and validate CSV file with prompts.
    
    Returns:
        List of prompts extracted from the CSV
    """
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV content
        content = await file.read()
        
        # Handle BOM and decode
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]  # Remove UTF-8 BOM
        
        try:
            csv_text = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_text = content.decode('utf-8-sig')  # Handle BOM
            except UnicodeDecodeError:
                csv_text = content.decode('latin-1')  # Fallback encoding
        
        # Normalize line endings
        csv_text = csv_text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Try to parse as CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        # Check for 'prompt' column (case insensitive)
        fieldnames = [name.lower().strip() for name in (csv_reader.fieldnames or [])]
        prompt_column = None
        
        for original_name, lower_name in zip(csv_reader.fieldnames or [], fieldnames):
            if lower_name in ['prompt', 'prompts', 'text', 'description']:
                prompt_column = original_name
                break
        
        if not prompt_column:
            raise HTTPException(status_code=400, detail="CSV must contain a 'prompt' column (or similar: prompts, text, description)")
        
        prompts = []
        for i, row in enumerate(csv_reader):
            if prompt_column in row:
                # Clean up the prompt text
                prompt = row[prompt_column].strip()
                
                # Remove various quote patterns
                if prompt.startswith('"""') and prompt.endswith('"""'):
                    prompt = prompt[3:-3].strip()
                elif prompt.startswith('"') and prompt.endswith('"'):
                    prompt = prompt[1:-1].strip()
                elif prompt.startswith("'") and prompt.endswith("'"):
                    prompt = prompt[1:-1].strip()
                
                # Skip empty prompts
                if prompt:
                    prompts.append({
                        "id": f"job_{i+1:03d}",
                        "prompt": prompt
                    })
        
        if not prompts:
            raise HTTPException(status_code=400, detail="No valid prompts found in CSV")
        
        logger.info(f"Successfully parsed CSV with {len(prompts)} prompts")
        
        return {
            "success": True,
            "prompts": prompts,
            "count": len(prompts)
        }
        
    except Exception as e:
        logger.error(f"CSV parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")


@router.post("/start")
async def start_batch_processing(
    background_tasks: BackgroundTasks,
    batch_request: Dict[str, Any]
):
    """
    Start batch processing of prompts.
    
    Expected format:
    {
        "prompts": [{"id": "job_001", "prompt": "..."}],
        "config": {
            "model": "phoenix|flux|photoreal",
            "num_images": 1-10,
            "width": 512-1536,
            "height": 512-1536,
            "style": "...",
            "contrast": 1.0-4.5,
            ... other model-specific settings
        }
    }
    """
    try:
        prompts = batch_request.get('prompts', [])
        config_data = batch_request.get('config', {})
        
        if not prompts:
            raise HTTPException(status_code=400, detail="No prompts provided")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Create batch configuration with unified output directory
        batch_config = BatchConfig(
            max_concurrent_requests=min(10, len(prompts)),  # Respect 10 concurrent limit
            output_dir=NamingConfig.BASE_OUTPUT_DIR,  # Use unified directory structure
            save_images=True,
            retry_attempts=2
        )
        
        # Select engine based on model
        model = config_data.get('model', 'phoenix').lower()
        if model == 'phoenix':
            engine = get_phoenix_engine()
        elif model == 'flux':
            engine = get_flux_engine()
        elif model == 'photoreal':
            engine = get_photoreal_engine()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported model: {model}")
        
        # Create batch processor
        processor = BatchProcessor(engine, batch_config)
        
        # Create temporary CSV for the processor
        csv_path = f"/tmp/batch_{batch_id}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['prompt'])
            for item in prompts:
                writer.writerow([item['prompt']])
        
        # Load CSV into processor
        processor.load_csv(csv_path)
        
        # Store batch info
        active_batches[batch_id] = {
            "id": batch_id,
            "status": "starting",
            "total_jobs": len(prompts),
            "completed": 0,
            "failed": 0,
            "start_time": datetime.now().isoformat(),
            "processor": processor,
            "config": config_data
        }
        
        # Start processing in background
        background_tasks.add_task(
            process_batch_async, 
            batch_id, 
            processor, 
            config_data
        )
        
        return {
            "success": True,
            "batch_id": batch_id,
            "message": "Batch processing started",
            "total_jobs": len(prompts)
        }
        
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_batch_async(batch_id: str, processor: BatchProcessor, config: Dict[str, Any]):
    """Process batch in background."""
    try:
        active_batches[batch_id]["status"] = "processing"
        
        # Progress callback to update status
        def progress_callback(completed: int, total: int, message: str):
            if batch_id in active_batches:
                progress_percentage = (completed / total) * 100 if total > 0 else 0
                logger.info(f"🔄 Progress callback: {completed}/{total} ({progress_percentage:.1f}%) - {message}")
                active_batches[batch_id].update({
                    "completed": completed,
                    "progress": progress_percentage,
                    "message": message
                })
        
        # Determine engine type from config
        model = config.get('model', 'phoenix').lower()
        engine_type = model  # Use the model name as engine type
        
        # Process the batch
        result = await processor.process_batch(config, engine_type, progress_callback)
        
        # Update final status
        active_batches[batch_id].update({
            "status": "completed",
            "completed": result["completed"],
            "failed": result["failed"],
            "end_time": result["end_time"],
            "duration": result["duration_seconds"],
            "output_directory": result["output_directory"]
        })
        
        logger.info(f"Batch {batch_id} completed: {result['completed']}/{result['total_jobs']} successful")
        
    except Exception as e:
        logger.error(f"Batch processing error for {batch_id}: {e}")
        if batch_id in active_batches:
            active_batches[batch_id].update({
                "status": "failed",
                "error": str(e),
                "end_time": datetime.now().isoformat()
            })


@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch processing job."""
    if batch_id not in active_batches:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    batch_info = active_batches[batch_id].copy()
    
    # Don't return the processor object
    if "processor" in batch_info:
        del batch_info["processor"]
    
    # Get detailed job status if processor is available
    if batch_id in active_batches and "processor" in active_batches[batch_id]:
        processor = active_batches[batch_id]["processor"]
        status = processor.get_status()
        batch_info.update({
            "completed_jobs": status["completed"],
            "failed_jobs": status["failed"],
            "jobs": {
                "pending": status["pending"],
                "processing": status["processing"],
                "completed": status["completed"],
                "failed": status["failed"]
            }
        })
        
        # Fortschritt berechnen
        total = batch_info.get("total_jobs") or 1
        progress = int(100 * (status["completed"] + status["failed"]) / total)
        batch_info["progress"] = progress
    
    return batch_info


@router.get("/")
async def list_active_batches():
    """List all active batch processing jobs."""
    batches = []
    for batch_id, info in active_batches.items():
        batch_summary = {
            "id": batch_id,
            "status": info["status"],
            "total_jobs": info["total_jobs"],
            "completed": info.get("completed", 0),
            "failed": info.get("failed", 0),
            "start_time": info["start_time"],
            "progress": info.get("progress", 0)
        }
        batches.append(batch_summary)
    
    return {"batches": batches}


@router.delete("/{batch_id}")
async def cancel_batch(batch_id: str):
    """Cancel a running batch processing job."""
    if batch_id not in active_batches:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    batch_info = active_batches[batch_id]
    
    if batch_info["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Batch is not running")
    
    # Update status to cancelled
    active_batches[batch_id]["status"] = "cancelled"
    active_batches[batch_id]["end_time"] = datetime.now().isoformat()
    
    return {"success": True, "message": "Batch cancelled"}


@router.get("/{batch_id}/download")
async def download_batch_results(batch_id: str):
    """Download batch processing results."""
    if batch_id not in active_batches:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    batch_info = active_batches[batch_id]
    
    if batch_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Batch is not completed")
    
    output_dir = batch_info.get("output_directory")
    if not output_dir or not Path(output_dir).exists():
        raise HTTPException(status_code=404, detail="Batch output not found")
    
    # TODO: Implement zip file creation and download
    # For now, return the directory path
    return {
        "success": True,
        "output_directory": output_dir,
        "message": "Download functionality will be implemented"
    }
