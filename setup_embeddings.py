#!/usr/bin/env python3
"""
Setup script to ensure embeddings file is available
"""

import os
import shutil
import json
from pathlib import Path

def main():
    print("🔧 Setting up embeddings for Railway deployment")
    
    # Check if embeddings file exists locally
    local_embeddings = "embeddings/embeddings_light.json"
    
    if os.path.exists(local_embeddings):
        print(f"✅ Found local embeddings: {local_embeddings}")
        
        # Ensure embeddings directory exists
        os.makedirs("embeddings", exist_ok=True)
        
        # Copy to current directory if needed
        if not os.path.exists("embeddings/embeddings_light.json"):
            shutil.copy2(local_embeddings, "embeddings/embeddings_light.json")
            print("📋 Copied embeddings file to current directory")
        
        # Also copy to /app/embeddings for Docker compatibility
        os.makedirs("/app/embeddings", exist_ok=True)
        shutil.copy2(local_embeddings, "/app/embeddings/embeddings_light.json")
        print("📋 Copied embeddings file to /app/embeddings")
        
        # Verify the file
        file_size = os.path.getsize("embeddings/embeddings_light.json")
        print(f"✅ Embeddings file size: {file_size} bytes")
        
    else:
        print("❌ Local embeddings file not found")
        print("Available files in embeddings/ directory:")
        if os.path.exists("embeddings"):
            files = os.listdir("embeddings")
            for file in files:
                size = os.path.getsize(f"embeddings/{file}")
                print(f"  - {file} ({size} bytes)")
        else:
            print("  embeddings/ directory does not exist")

if __name__ == "__main__":
    main()