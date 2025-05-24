#!/usr/bin/env python3
"""
Batch Processing CLI for Leonardo AI Image Generation
Processes CSV files with prompts using manual UI settings.
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from core.batch_processor import BatchProcessor, BatchConfig
from core.engine.leonardo.phoenix import PhoenixEngine
from core.engine.leonardo.flux import FluxEngine
from core.engine.leonardo.photoreal import LeonardoPhotoRealEngine
from core.schemas import LeonardoEngineConfig


def get_engine(model_type: str, api_key: str):
    """Get the appropriate engine based on model type."""
    config = LeonardoEngineConfig(
        name=model_type,
        vendor="leonardo",
        enabled=True,
        api_key=api_key,
        base_url="https://cloud.leonardo.ai/api/rest/v1",
        timeout=300,
        poll_interval=2
    )
    
    if model_type == "phoenix":
        return PhoenixEngine(config)
    elif model_type == "flux":
        return FluxEngine(config)
    elif model_type == "photoreal":
        return LeonardoPhotoRealEngine(config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def progress_callback(completed: int, total: int, status: str):
    """Progress callback for batch processing."""
    percentage = (completed / total) * 100 if total > 0 else 0
    print(f"\r🔄 Progress: {completed}/{total} ({percentage:.1f}%) - {status}", end="", flush=True)
    if completed == total:
        print()  # New line when complete


def interactive_setup() -> Dict[str, Any]:
    """Interactive setup for generation parameters."""
    print("\n🎨 Leonardo AI Batch Processing Setup")
    print("=" * 50)
    
    # Model selection
    print("\n1. Select AI Model:")
    print("   [1] Phoenix - Premium Quality")
    print("   [2] FLUX - Speed & Precision") 
    print("   [3] PhotoReal - Photorealistic")
    
    while True:
        choice = input("\nChoose model (1-3): ").strip()
        if choice == "1":
            model_type = "phoenix"
            break
        elif choice == "2":
            model_type = "flux"
            break
        elif choice == "3":
            model_type = "photoreal"
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    print(f"✅ Selected: {model_type.title()}")
    
    # Basic parameters
    print("\n2. Generation Settings:")
    
    num_images = int(input("Number of images per prompt (1-10): ") or "1")
    width = int(input("Width (512, 768, 1024, 1536): ") or "1024")
    height = int(input("Height (512, 768, 1024, 1536): ") or "1024")
    
    params = {
        "model_type": model_type,
        "num_outputs": min(max(num_images, 1), 10),
        "width": width,
        "height": height,
        "enhance_prompt": input("Enhance prompts? (y/N): ").lower().startswith('y'),
        "negative_prompt": input("Negative prompt (optional): ").strip()
    }
    
    # Model-specific parameters
    if model_type == "phoenix":
        params.update({
            "style": input("Style (Dynamic, Cinematic, etc. - optional): ").strip() or None,
            "contrast": float(input("Contrast (1.0-4.5, default 3.5): ") or "3.5"),
            "alchemy": input("Use Alchemy? (Y/n): ").lower() != 'n',
            "ultra": input("Use Ultra mode? (y/N): ").lower().startswith('y'),
            "upscale": input("Upscale images? (y/N): ").lower().startswith('y')
        })
        
    elif model_type == "flux":
        params.update({
            "style": input("Style (Cyberpunk, Portrait, etc. - optional): ").strip() or None,
            "contrast": float(input("Contrast (1.0-4.5, default 3.5): ") or "3.5"),
            "ultra": input("Use Ultra mode? (y/N): ").lower().startswith('y')
        })
        
    elif model_type == "photoreal":
        version = input("PhotoReal version (v1/v2, default v2): ").strip() or "v2"
        params.update({
            "photoreal_version": version,
            "contrast": float(input("Contrast (1.0-4.5, default 3.5): ") or "3.5")
        })
        
        if version == "v2":
            print("\nAvailable models:")
            print("   [1] Leonardo Kino XL")
            print("   [2] Leonardo Diffusion XL") 
            print("   [3] Leonardo Vision XL")
            model_choice = input("Choose model (1-3): ").strip()
            model_ids = {
                "1": "aa77f04e-3eec-4034-9c07-d0f619684628",
                "2": "b24e16ff-06e3-43eb-8d33-4416c2d75876", 
                "3": "5c232a9e-9061-4777-980a-ddc8e65647c6"
            }
            params["model_id"] = model_ids.get(model_choice, model_ids["1"])
            params["style"] = input("Style (HDR, PORTRAIT, CINEMATIC, etc. - optional): ").strip() or None
        else:
            params["style"] = input("Style (CINEMATIC, CREATIVE, VIBRANT - optional): ").strip() or None
            strength = input("PhotoReal strength (0.1-1.0, default 0.5): ").strip()
            if strength:
                params["photoreal_strength"] = float(strength)
    
    return params


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch process CSV prompts with Leonardo AI")
    parser.add_argument("csv_file", help="Path to CSV file with prompts")
    parser.add_argument("--config", help="JSON config file with generation parameters")
    parser.add_argument("--output", default="batch_output", help="Output directory")
    parser.add_argument("--concurrent", type=int, default=10, help="Max concurrent requests")
    parser.add_argument("--retry", type=int, default=2, help="Retry attempts")
    parser.add_argument("--api-key", help="Leonardo API key (or set LEONARDO_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Check CSV file exists
    if not Path(args.csv_file).exists():
        print(f"❌ CSV file not found: {args.csv_file}")
        return 1
    
    # Get API key
    api_key = args.api_key or os.getenv("LEONARDO_API_KEY")
    if not api_key:
        print("❌ Leonardo API key required. Set LEONARDO_API_KEY env var or use --api-key")
        return 1
    
    try:
        # Load or create generation parameters
        if args.config and Path(args.config).exists():
            with open(args.config) as f:
                params = json.load(f)
            print(f"✅ Loaded config from {args.config}")
        else:
            params = interactive_setup()
            
            # Save config for reuse
            config_file = f"batch_config_{params['model_type']}.json"
            with open(config_file, 'w') as f:
                json.dump(params, f, indent=2)
            print(f"✅ Config saved to {config_file}")
        
        # Create engine
        model_type = params.pop("model_type")
        engine = get_engine(model_type, api_key)
        
        # Create batch processor
        batch_config = BatchConfig(
            max_concurrent_requests=args.concurrent,
            retry_attempts=args.retry,
            output_dir=args.output,
            save_images=True,
            progress_callback=progress_callback
        )
        
        processor = BatchProcessor(engine, batch_config)
        
        # Load CSV
        job_count = processor.load_csv(args.csv_file)
        print(f"✅ Loaded {job_count} prompts from {args.csv_file}")
        
        # Show summary
        print(f"\n📋 Batch Processing Summary:")
        print(f"   Model: {model_type.title()}")
        print(f"   Prompts: {job_count}")
        print(f"   Images per prompt: {params.get('num_outputs', 1)}")
        print(f"   Total images: {job_count * params.get('num_outputs', 1)}")
        print(f"   Max concurrent: {args.concurrent}")
        print(f"   Output directory: {args.output}")
        
        # Confirm before starting
        if input("\n🚀 Start batch processing? (Y/n): ").lower() != 'n':
            print("\n🎨 Starting batch processing...")
            
            # Process batch
            summary = await processor.process_batch(params)
            
            # Show results
            print(f"\n✅ Batch processing completed!")
            print(f"   Successful: {summary['completed']}/{summary['total_jobs']}")
            print(f"   Failed: {summary['failed']}")
            print(f"   Duration: {summary['duration_seconds']:.1f}s")
            print(f"   Output: {summary['output_directory']}")
            
            if summary['failed'] > 0:
                print(f"\n❌ Failed jobs:")
                for job in summary['failed_jobs']:
                    print(f"   {job['id']}: {job['error']}")
            
            return 0 if summary['failed'] == 0 else 1
        else:
            print("❌ Batch processing cancelled.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(1)
