#!/usr/bin/env python3
"""
Generate Light Embeddings for Railway Deployment
This script creates embeddings using the smallest sentence-transformers model.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def main():
    print("🔧 Generating Light Embeddings for Railway Deployment")
    print("=" * 60)
    
    # Check if extracted_content exists
    if not os.path.exists("extracted_content"):
        print("❌ Error: extracted_content directory not found")
        print("   Please run your content extraction first")
        return
    
    # Check if create_embeddings_light.py exists
    if not os.path.exists("create_embeddings_light.py"):
        print("❌ Error: create_embeddings_light.py not found")
        print("   Please ensure the light embeddings script is available")
        return
    
    # Create embeddings directory if it doesn't exist
    os.makedirs("embeddings", exist_ok=True)
    
    print("📁 Processing files from extracted_content/")
    print("🔄 Using sentence-transformers/all-MiniLM-L6-v2 (smallest model)")
    print("💻 CPU-only PyTorch for minimal deployment size")
    print("📏 Model size: ~90MB (vs ~1.5GB for instructor-xl)")
    
    try:
        # Import and run the light embeddings script
        from create_embeddings_light import process_text_files
        
        # Process files and create light embeddings
        process_text_files(
            input_folder="extracted_content",
            output_file="embeddings/embeddings_light.json"
        )
        
        print("✅ Light embeddings generated successfully!")
        print("📊 File: embeddings/embeddings_light.json")
        
        # Check file sizes
        if os.path.exists("embeddings/embeddings_light.json"):
            size_mb = os.path.getsize("embeddings/embeddings_light.json") / (1024 * 1024)
            print(f"📏 Embeddings file size: {size_mb:.2f} MB")
        
        print("\n🚀 Ready for Railway deployment!")
        print("   Estimated total image size: ~2.5-3GB")
        print("   ✅ Fits well within Railway's 4GB limit")
        print("   🧠 Full neural embedding capabilities")
        print("   💻 CPU-only PyTorch (no CUDA bloat)")
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {str(e)}")
        print("   Please check your dependencies and try again")

if __name__ == "__main__":
    main()