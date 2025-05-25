"""
Batch Processing System for Leonardo AI Image Generation
Processes CSV files with prompts while respecting concurrent request limits.
"""

import asyncio
import csv
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .schemas import GenerationRequest, GenerationResult
from .engine.base import ImageGenerationEngine
from .modules.image_generation_workflow import BatchImageGenerationWorkflow, ImageGenerationRequestFactory


logger = logging.getLogger(__name__)


@dataclass
class BatchJob:
    """Represents a single batch job."""
    id: str
    prompt: str
    status: str = "pending"  # pending, processing, completed, failed
    generation_id: Optional[str] = None
    image_urls: Optional[List[str]] = None  # 🔥 FIX: Make it Optional
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_concurrent_requests: int = 10
    wait_timeout: int = 300  # 5 minutes timeout per request
    retry_attempts: int = 2
    output_dir: str = "batch_output"
    save_images: bool = True
    progress_callback: Optional[Callable[[int, int, str], None]] = None


class BatchProcessor:
    """Processes CSV files with prompts in batches."""
    
    def __init__(self, engine: ImageGenerationEngine, config: BatchConfig):
        """Initialize the batch processor."""
        self.engine = engine
        self.config = config
        self.jobs: List[BatchJob] = []
        self.current_batch: List[BatchJob] = []
        self.completed_jobs: List[BatchJob] = []
        self.failed_jobs: List[BatchJob] = []
        self.current_progress_callback: Optional[Callable[[int, int, str], None]] = None  # 🔥 FIX: Add progress callback
        
        # Create output directory
        self.output_path = Path(config.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BatchProcessor initialized with max {config.max_concurrent_requests} concurrent requests")
    
    def load_csv(self, csv_path: str) -> int:
        """
        Load prompts from CSV file.
        
        Args:
            csv_path: Path to CSV file with prompts
            
        Returns:
            Number of jobs loaded
        """
        jobs_loaded = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # 🔥 FIX: Check fieldnames exist and contain 'prompt'
                fieldnames = reader.fieldnames or []
                if 'prompt' not in fieldnames:
                    raise ValueError("CSV must contain 'prompt' column")
                
                for i, row in enumerate(reader):
                    prompt = row['prompt'].strip().strip('"')
                    if prompt:
                        job = BatchJob(
                            id=f"job_{i+1:03d}",
                            prompt=prompt
                        )
                        self.jobs.append(job)
                        jobs_loaded += 1
                        
                logger.info(f"Loaded {jobs_loaded} jobs from {csv_path}")
                        
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise
            
        return jobs_loaded
    
    async def process_batch(self, 
                          generation_params: Dict[str, Any],
                          progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Dict[str, Any]:
        """
        Process all jobs in batches.
        
        Args:
            generation_params: Parameters for image generation (model, size, style, etc.)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Summary of batch processing results
        """
        if not self.jobs:
            raise ValueError("No jobs loaded. Use load_csv() first.")
        
        logger.info(f"Starting batch processing of {len(self.jobs)} jobs")
        start_time = datetime.now()
        
        # Reset counters
        self.completed_jobs = []
        self.failed_jobs = []
        
        total_jobs = len(self.jobs)
        
        # Store progress callback for use in job processing
        self.current_progress_callback = progress_callback or self.config.progress_callback
        
        # Process jobs in batches of max_concurrent_requests
        for i in range(0, len(self.jobs), self.config.max_concurrent_requests):
            batch = self.jobs[i:i + self.config.max_concurrent_requests]
            
            logger.info(f"Processing batch {i//self.config.max_concurrent_requests + 1}: jobs {i+1}-{min(i+len(batch), total_jobs)}")
            
            # Process current batch concurrently
            await self._process_batch_concurrent(batch, generation_params)
            
            # Wait for all images to be downloaded before proceeding
            await self._wait_for_downloads(batch)
            
            logger.info(f"Batch completed. {len([j for j in batch if j.status == 'completed'])} successful, {len([j for j in batch if j.status == 'failed'])} failed")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = {
            "total_jobs": total_jobs,
            "completed": len(self.completed_jobs),
            "failed": len(self.failed_jobs),
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "output_directory": str(self.output_path),
            "failed_jobs": [{"id": job.id, "prompt": job.prompt, "error": job.error} for job in self.failed_jobs]
        }
        
        logger.info(f"Batch processing completed: {summary['completed']}/{summary['total_jobs']} successful in {duration:.1f}s")
        
        # Save summary to file
        await self._save_summary(summary)
        
        return summary
    
    async def _process_batch_concurrent(self, batch: List[BatchJob], generation_params: Dict[str, Any]):
        """Process a batch of jobs concurrently."""
        tasks = []
        
        for job in batch:
            task = asyncio.create_task(self._process_single_job(job, generation_params))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_job(self, job: BatchJob, generation_params: Dict[str, Any]):
        """Process a single job with retry logic."""
        job.status = "processing"
        job.start_time = datetime.now()
        
        for attempt in range(self.config.retry_attempts + 1):
            try:
                logger.info(f"Processing {job.id}: {job.prompt[:50]}... (attempt {attempt + 1})")
                
                # Create generation request with the prompt and user's settings
                request = self._create_generation_request(job.prompt, generation_params)
                
                # Generate images
                result = await self.engine.generate(request)
                
                # Extract image URLs or save images
                if self.config.save_images:
                    job.image_urls = await self._save_job_images(job, result)
                else:
                    job.image_urls = getattr(result, 'image_urls', [])
                
                job.generation_id = result.metadata.generation_id
                job.status = "completed"
                job.end_time = datetime.now()
                
                self.completed_jobs.append(job)
                logger.info(f"✅ {job.id} completed: {len(job.image_urls or [])} images generated")  # 🔥 FIX: Handle None case
                
                # 🔥 FIX: Update progress for each completed job
                if hasattr(self, 'current_progress_callback') and self.current_progress_callback:
                    total_completed = len(self.completed_jobs) + len(self.failed_jobs)
                    total_jobs = len(self.jobs)
                    progress_message = f"Completed {job.id} ({total_completed}/{total_jobs})"
                    self.current_progress_callback(total_completed, total_jobs, progress_message)
                
                return
                
            except Exception as e:
                logger.warning(f"❌ {job.id} attempt {attempt + 1} failed: {e}")
                
                if attempt == self.config.retry_attempts:
                    # Final attempt failed
                    job.status = "failed"
                    job.error = str(e)
                    job.end_time = datetime.now()
                    self.failed_jobs.append(job)
                    logger.error(f"❌ {job.id} failed after {self.config.retry_attempts + 1} attempts")
                    
                    # 🔥 FIX: Update progress for each failed job
                    if hasattr(self, 'current_progress_callback') and self.current_progress_callback:
                        total_completed = len(self.completed_jobs) + len(self.failed_jobs)
                        total_jobs = len(self.jobs)
                        progress_message = f"Failed {job.id} ({total_completed}/{total_jobs})"
                        self.current_progress_callback(total_completed, total_jobs, progress_message)
                    
                else:
                    # Wait before retry
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def _create_generation_request(self, prompt: str, params: Dict[str, Any]) -> GenerationRequest:
        """Create a generation request from prompt and parameters using factory."""
        # Use the shared factory instead of duplicated logic
        engine_type = str(type(self.engine)).lower()
        return ImageGenerationRequestFactory.from_batch_params(prompt, params, engine_type)
    
    async def _save_job_images(self, job: BatchJob, result: GenerationResult) -> List[str]:
        """Save images from generation result and return file paths."""
        image_paths = []
        
        job_dir = self.output_path / job.id
        job_dir.mkdir(exist_ok=True)
        
        for i, image_data in enumerate(result.outputs):
            filename = f"{job.id}_image_{i+1:02d}.png"
            filepath = job_dir / filename
            
            # Write image data to file
            filepath.write_bytes(image_data)
            image_paths.append(str(filepath))
            
        return image_paths
    
    async def _wait_for_downloads(self, batch: List[BatchJob]):
        """Wait for all downloads in batch to complete."""
        # Since we're processing synchronously in _save_job_images, 
        # this is mainly for API rate limiting compliance
        await asyncio.sleep(1)  # Small delay between batches
    
    async def _save_summary(self, summary: Dict[str, Any]):
        """Save batch processing summary to file."""
        summary_file = self.output_path / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary saved to {summary_file}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processing status."""
        return {
            "total_jobs": len(self.jobs),
            "pending": len([j for j in self.jobs if j.status == "pending"]),
            "processing": len([j for j in self.jobs if j.status == "processing"]),
            "completed": len(self.completed_jobs),
            "failed": len(self.failed_jobs),
            "current_batch_size": len(self.current_batch)
        }
