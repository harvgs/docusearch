#!/usr/bin/env python3
"""
Validate Light Deployment Setup
This script checks that all required files and configurations are in place.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_requirements_file():
    """Check requirements file for CPU-only PyTorch"""
    requirements_file = "requirements_ultra_minimal.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file missing: {requirements_file}")
        return False
    
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    if "torch>=2.0.0+cpu" in content:
        print("✅ CPU-only PyTorch configured correctly")
        return True
    elif "torch" in content:
        print("⚠️  PyTorch found but not CPU-only version")
        return False
    else:
        print("❌ PyTorch not found in requirements")
        return False

def main():
    print("🔍 Validating Light Deployment Setup")
    print("=" * 50)
    
    all_good = True
    
    # Check required files
    required_files = [
        ("docusearch_light.py", "Main application file"),
        ("create_embeddings_light.py", "Light embedding processor"),
        ("generate_light_embeddings.py", "Embedding generation script"),
        ("requirements_ultra_minimal.txt", "CPU-only requirements"),
        ("Dockerfile", "Docker configuration"),
        ("start.sh", "Startup script"),
        ("RAILWAY_LIGHT_DEPLOYMENT.md", "Deployment guide")
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Check requirements configuration
    if not check_requirements_file():
        all_good = False
    
    # Check for embeddings
    embeddings_file = "embeddings/embeddings_light.json"
    if os.path.exists(embeddings_file):
        size_mb = os.path.getsize(embeddings_file) / (1024 * 1024)
        print(f"✅ Light embeddings found: {embeddings_file} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Light embeddings not found: {embeddings_file}")
        print("   Run: python generate_light_embeddings.py")
    
    # Check for extracted content
    if os.path.exists("extracted_content"):
        print("✅ Extracted content directory found")
    else:
        print("⚠️  Extracted content directory not found")
        print("   Ensure your document data is available")
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 Light deployment setup is ready!")
        print("📊 Estimated deployment size: ~2.5-3GB")
        print("✅ Should fit within Railway's 4GB limit")
        print("\n🚀 Next steps:")
        print("   1. Generate embeddings: python generate_light_embeddings.py")
        print("   2. Deploy to Railway")
        print("   3. Set OPENAI_API_KEY environment variable")
    else:
        print("❌ Some issues found. Please fix them before deployment.")
        print("\n🔧 Common fixes:")
        print("   - Run: python generate_light_embeddings.py")
        print("   - Check file paths and permissions")
        print("   - Verify requirements_ultra_minimal.txt contains torch>=2.0.0+cpu")

if __name__ == "__main__":
    main()