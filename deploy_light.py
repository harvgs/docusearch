#!/usr/bin/env python3
"""
Light Deployment Validator for Railway
This script validates the light version setup before deployment.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and return status"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def main():
    print("🔧 Light Version Deployment Validator")
    print("=" * 50)
    
    # Check required files for light deployment
    required_files = [
        ("docusearch_light.py", "Light main application"),
        ("create_embeddings_light.py", "Light embeddings script"),
        ("requirements_minimal.txt", "Minimal requirements"),
        ("Dockerfile", "Docker configuration"),
        ("Procfile", "Railway configuration"),
        ("start.sh", "Startup script"),
        (".dockerignore", "Docker ignore file")
    ]
    
    all_exist = True
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            all_exist = False
    
    print("\n📦 Checking dependencies...")
    
    # Check if minimal requirements file has correct packages
    if os.path.exists("requirements_minimal.txt"):
        with open("requirements_minimal.txt", "r") as f:
            content = f.read()
        
        required_packages = [
            "streamlit",
            "openai", 
            "torch",
            "transformers",
            "sentence-transformers"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            all_exist = False
        else:
            print("✅ All required packages found")
    
    print("\n📁 Checking data files...")
    
    # Check for embeddings (either light or original)
    embeddings_files = [
        ("embeddings/embeddings_light.json", "Light embeddings"),
        ("embeddings/embeddings.json", "Original embeddings")
    ]
    
    embeddings_found = False
    for filepath, description in embeddings_files:
        if check_file_exists(filepath, description):
            embeddings_found = True
            # Check file size
            if os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"   📏 Size: {size_mb:.2f} MB")
    
    if not embeddings_found:
        print("⚠️  No embeddings file found")
        print("   Run: python generate_light_embeddings.py")
    
    print("\n🔐 Checking environment...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OPENAI_API_KEY environment variable is set")
    else:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Set this in Railway dashboard")
    
    print("\n" + "=" * 50)
    
    if all_exist:
        print("✅ Light version is ready for deployment!")
        print("\n🚀 Next steps:")
        print("1. Generate light embeddings: python generate_light_embeddings.py")
        print("2. Push code to GitHub")
        print("3. Deploy on Railway")
        print("4. Set OPENAI_API_KEY environment variable")
    else:
        print("❌ Light version needs fixes before deployment")
        print("\nPlease fix the issues above before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()