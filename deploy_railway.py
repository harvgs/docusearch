#!/usr/bin/env python3
"""
Railway Deployment Helper Script
This script validates your project setup and provides guidance for Railway deployment.
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and return status"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_requirements():
    """Check if all required files exist"""
    print("🔍 Checking project files for Railway deployment...\n")
    
    required_files = [
        ("docusearch_new.py", "Main Streamlit application"),
        ("requirements.txt", "Python dependencies"),
        ("Procfile", "Railway deployment configuration"),
        ("railway.json", "Railway settings"),
        (".dockerignore", "Build optimization")
    ]
    
    all_exist = True
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            all_exist = False
    
    print()
    return all_exist

def check_requirements_content():
    """Check if requirements.txt has necessary dependencies"""
    print("📦 Checking requirements.txt content...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_packages = [
        "streamlit",
        "openai", 
        "torch",
        "transformers",
        "langchain"
    ]
    
    missing_packages = []
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages in requirements.txt: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages found in requirements.txt")
        return True

def check_data_files():
    """Check if data files exist"""
    print("\n📁 Checking data files...")
    
    data_files = [
        ("embeddings/embeddings.json", "Embeddings data"),
        ("extracted_content/", "Extracted content directory")
    ]
    
    for filepath, description in data_files:
        check_file_exists(filepath, description)

def check_environment_setup():
    """Check environment variable setup"""
    print("\n🔐 Checking environment setup...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OPENAI_API_KEY environment variable is set")
        print(f"   Key starts with: {api_key[:8]}...")
    else:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   You'll need to set this in Railway dashboard")

def generate_deployment_commands():
    """Generate deployment commands"""
    print("\n🚀 Railway Deployment Commands:")
    print("=" * 50)
    
    print("\n1. Install Railway CLI:")
    print("   npm install -g @railway/cli")
    
    print("\n2. Login to Railway:")
    print("   railway login")
    
    print("\n3. Initialize project:")
    print("   railway init")
    
    print("\n4. Deploy to Railway:")
    print("   railway up")
    
    print("\n5. Set environment variable:")
    print("   railway variables set OPENAI_API_KEY=your-api-key-here")

def main():
    """Main validation function"""
    print("DocuSearch Railway Deployment Validator")
    print("=" * 40)
    
    # Check all requirements
    files_ok = check_requirements()
    requirements_ok = check_requirements_content()
    check_data_files()
    check_environment_setup()
    
    print("\n" + "=" * 40)
    
    if files_ok and requirements_ok:
        print("✅ Project is ready for Railway deployment!")
        generate_deployment_commands()
    else:
        print("❌ Project needs fixes before deployment")
        print("\nPlease fix the issues above before deploying to Railway")
        sys.exit(1)

if __name__ == "__main__":
    main()