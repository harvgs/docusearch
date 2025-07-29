#!/usr/bin/env python3
"""
Script to copy embeddings file to main directory for Railway deployment
"""

import os
import shutil
import sys

def main():
    print("🔧 Copying embeddings file for Railway deployment")
    
    # Source file
    source_file = "embeddings/embeddings_light.json"
    target_file = "embeddings_light.json"
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        print("Please make sure the embeddings file exists in the embeddings/ directory")
        return False
    
    try:
        # Copy the file
        shutil.copy2(source_file, target_file)
        
        # Verify the copy
        if os.path.exists(target_file):
            source_size = os.path.getsize(source_file)
            target_size = os.path.getsize(target_file)
            
            print(f"✅ Successfully copied embeddings file")
            print(f"   Source: {source_file} ({source_size:,} bytes)")
            print(f"   Target: {target_file} ({target_size:,} bytes)")
            
            if source_size == target_size:
                print("✅ File sizes match - copy successful!")
                return True
            else:
                print("❌ File sizes don't match - copy may be incomplete")
                return False
        else:
            print("❌ Target file not found after copy")
            return False
            
    except Exception as e:
        print(f"❌ Error copying file: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for Railway deployment!")
        print("   The embeddings_light.json file is now in the main directory")
        print("   Commit and push to deploy with your embeddings")
    else:
        print("\n❌ Failed to copy embeddings file")
        sys.exit(1)