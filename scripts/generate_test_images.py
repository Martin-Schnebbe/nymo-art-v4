#!/usr/bin/env python3
"""
Generate real test images using Leonardo Phoenix API for validation.
Tests different parameter combinations to ensure end-to-end functionality.
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from core.engine.leonardo.phoenix import PhoenixEngine
from core.schemas import LeonardoPhoenixRequest, LeonardoEngineConfig


async def generate_test_images():
    """Generate a variety of test images with different parameters."""
    
    # Check for API key
    api_key = os.getenv("LEONARDO_API_KEY")
    if not api_key:
        print("❌ LEONARDO_API_KEY environment variable not set!")
        print("Please set your Leonardo API key:")
        print("export LEONARDO_API_KEY='your_api_key_here'")
        return
    
    print("🎨 Starting Leonardo Phoenix image generation test...")
    print(f"📅 Timestamp: {datetime.now().isoformat()}")
    
    # Initialize engine with config
    config = LeonardoEngineConfig(
        name="phoenix",
        vendor="leonardo",
        enabled=True,
        api_key=api_key
    )
    engine = PhoenixEngine(config)
    
    # Test configurations
    test_configs = [
        {
            "name": "Basic Portrait",
            "request": LeonardoPhoenixRequest(
                prompt="A professional portrait of a confident businesswoman in a modern office",
                num_outputs=1,
                width=1024,
                height=1024,
                style="Cinematic",
                contrast=3.5,
                alchemy=True,
                enhance_prompt=False
            )
        },
        {
            "name": "Artistic Landscape",
            "request": LeonardoPhoenixRequest(
                prompt="A serene mountain landscape at sunset with golden light",
                num_outputs=1,
                width=1344,
                height=768,
                style="Pro color photography",
                contrast=4.0,
                alchemy=True,
                enhance_prompt=True
            )
        },
        {
            "name": "Fantasy Character",
            "request": LeonardoPhoenixRequest(
                prompt="A mystical elven warrior with glowing blue eyes in an enchanted forest",
                num_outputs=2,
                width=832,
                height=1216,
                style="Illustration",
                contrast=2.5,
                alchemy=True,
                enhance_prompt=False
            )
        },
        {
            "name": "No Alchemy Test",
            "request": LeonardoPhoenixRequest(
                prompt="A simple geometric abstract pattern in bright colors",
                num_outputs=1,
                width=1024,
                height=1024,
                style=None,
                contrast=1.8,
                alchemy=False,
                enhance_prompt=False
            )
        }
    ]
    
    # Create output directory
    output_dir = Path("generated_images")
    output_dir.mkdir(exist_ok=True)
    
    total_images = 0
    successful_generations = 0
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n🖼️  Test {i}/{len(test_configs)}: {config['name']}")
        print(f"   Prompt: {config['request'].prompt[:60]}...")
        print(f"   Style: {config['request'].style}")
        print(f"   Dimensions: {config['request'].width}x{config['request'].height}")
        print(f"   Alchemy: {config['request'].alchemy}")
        print(f"   Contrast: {config['request'].contrast}")
        
        try:
            # Generate images
            result = await engine.generate(config['request'])
            
            # Save images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"test_{i}_{config['name'].lower().replace(' ', '_')}_{timestamp}"
            
            saved_paths = result.save_outputs(output_dir, prefix)
            
            print(f"   ✅ Generated {len(saved_paths)} image(s)")
            for path in saved_paths:
                print(f"      📁 {path.name}")
            
            # Print metadata
            print(f"   🔖 Generation ID: {result.metadata.generation_id}")
            print(f"   💰 Cost Estimate: ${result.metadata.cost_estimate:.4f}")
            
            total_images += len(saved_paths)
            successful_generations += 1
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            continue
    
    print(f"\n📊 Generation Summary:")
    print(f"   Total tests: {len(test_configs)}")
    print(f"   Successful: {successful_generations}")
    print(f"   Failed: {len(test_configs) - successful_generations}")
    print(f"   Total images: {total_images}")
    print(f"   Output directory: {output_dir.absolute()}")
    
    if successful_generations > 0:
        print(f"\n🎉 Leonardo Phoenix API integration is working correctly!")
        print(f"   Check the generated images in: {output_dir.absolute()}")
    else:
        print(f"\n❌ All generations failed. Please check your API key and network connection.")


if __name__ == "__main__":
    asyncio.run(generate_test_images())
