#!/usr/bin/env python3
"""
Debug script to check file structure on Railway
"""

import os
import sys
from pathlib import Path

def main():
    print("🔍 Railway File Structure Debug")
    print("=" * 50)
    
    # Current working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).resolve()}")
    
    # Check for embeddings directory
    embeddings_paths = [
        "embeddings",
        "/app/embeddings", 
        "./embeddings",
        "../embeddings"
    ]
    
    print("\n📁 Checking embeddings directories:")
    for path in embeddings_paths:
        if os.path.exists(path):
            print(f"✅ {path} exists")
            try:
                files = os.listdir(path)
                print(f"   Files: {files}")
            except Exception as e:
                print(f"   Error listing: {e}")
        else:
            print(f"❌ {path} does not exist")
    
    # Check for embeddings files directly
    embeddings_files = [
        "embeddings/embeddings_light.json",
        "embeddings/embeddings.json",
        "/app/embeddings/embeddings_light.json",
        "/app/embeddings/embeddings.json"
    ]
    
    print("\n📄 Checking embeddings files:")
    for file_path in embeddings_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} exists ({size} bytes)")
        else:
            print(f"❌ {file_path} does not exist")
    
    # List all files in current directory
    print("\n📂 Current directory contents:")
    try:
        files = os.listdir(".")
        for file in files:
            if os.path.isdir(file):
                print(f"📁 {file}/")
            else:
                size = os.path.getsize(file)
                print(f"📄 {file} ({size} bytes)")
    except Exception as e:
        print(f"Error listing current directory: {e}")

if __name__ == "__main__":
    main()