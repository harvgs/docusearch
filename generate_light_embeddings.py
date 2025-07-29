#!/usr/bin/env python3
"""
Generate Light Embeddings for Railway Deployment
This script creates embeddings using a smaller, more efficient model.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def main():
    print("🔧 Generating Light Embeddings for Railway Deployment")
    print("=" * 50)
    
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
    print("🔄 Using all-MiniLM-L6-v2 model (much smaller than instructor-xl)")
    
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
        
        # Check file size
        if os.path.exists("embeddings/embeddings_light.json"):
            size_mb = os.path.getsize("embeddings/embeddings_light.json") / (1024 * 1024)
            print(f"📏 File size: {size_mb:.2f} MB")
        
        print("\n🚀 Ready for Railway deployment!")
        print("   The light version should fit within the 4GB limit.")
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {str(e)}")
        print("   Please check your dependencies and try again")

if __name__ == "__main__":
    main()