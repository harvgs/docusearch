#!/usr/bin/env python3
"""
Verification script to check if embeddings files are present
Run this during Docker build or deployment to verify file presence
"""

import os
import json
import sys

def check_embeddings_files():
    """Check for embeddings files and verify they're valid JSON"""
    print("🔍 Checking for embeddings files...")
    
    # Possible locations for embeddings files
    embeddings_locations = [
        "embeddings_light.json",
        "embeddings.json", 
        "embeddings/embeddings_light.json",
        "embeddings/embeddings.json",
        "/app/embeddings_light.json",
        "/app/embeddings.json",
        "/app/embeddings/embeddings_light.json",
        "/app/embeddings/embeddings.json"
    ]
    
    found_files = []
    
    for location in embeddings_locations:
        if os.path.exists(location):
            try:
                # Try to load as JSON to verify it's valid
                with open(location, 'r') as f:
                    data = json.load(f)
                
                file_size = os.path.getsize(location) / (1024 * 1024)  # Size in MB
                print(f"✅ Found valid embeddings file: {location} ({file_size:.1f} MB)")
                found_files.append(location)
                
                # Check if it has the expected structure
                if isinstance(data, list) and len(data) > 0:
                    print(f"   - Contains {len(data)} embeddings")
                    if 'text' in data[0] and 'embedding' in data[0]:
                        print(f"   - Valid structure with text and embedding fields")
                    else:
                        print(f"   ⚠️  Warning: Unexpected structure")
                else:
                    print(f"   ⚠️  Warning: Unexpected data format")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in {location}: {e}")
            except Exception as e:
                print(f"❌ Error reading {location}: {e}")
        else:
            print(f"❌ Not found: {location}")
    
    # Check directories
    print("\n📁 Checking directories:")
    for dir_path in ["embeddings", "/app/embeddings", "./embeddings"]:
        if os.path.exists(dir_path):
            try:
                files = os.listdir(dir_path)
                print(f"✅ Directory exists: {dir_path}")
                print(f"   Files: {files}")
            except Exception as e:
                print(f"❌ Error listing {dir_path}: {e}")
        else:
            print(f"❌ Directory not found: {dir_path}")
    
    # Summary
    print(f"\n📊 Summary:")
    if found_files:
        print(f"✅ Found {len(found_files)} valid embeddings file(s)")
        print(f"   Primary file: {found_files[0]}")
        return True
    else:
        print(f"❌ No valid embeddings files found!")
        print(f"   The app will not function without embeddings data.")
        return False

if __name__ == "__main__":
    success = check_embeddings_files()
    if not success:
        print("\n🚨 CRITICAL: No embeddings files found!")
        print("   Please ensure embeddings_light.json is included in the deployment.")
        sys.exit(1)
    else:
        print("\n🎉 Embeddings verification successful!")
        sys.exit(0)