#!/usr/bin/env python3
"""
Test PyTorch Installation
This script checks if PyTorch is installed correctly without CUDA dependencies.
"""

import sys
import subprocess
import os

def check_pytorch_installation():
    """Check PyTorch installation and CUDA availability"""
    print("🔍 Testing PyTorch Installation")
    print("=" * 40)
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"🔍 CUDA available: {cuda_available}")
        
        if cuda_available:
            print("⚠️  CUDA is available - this might cause size issues")
            print(f"   CUDA version: {torch.version.cuda}")
        else:
            print("✅ CUDA not available - CPU-only installation")
        
        # Check if CUDA is being used
        if hasattr(torch, 'cuda') and torch.cuda.is_available():
            print("⚠️  PyTorch can use CUDA")
        else:
            print("✅ PyTorch is CPU-only")
        
        # Check torch installation path
        torch_path = torch.__file__
        print(f"📁 PyTorch installed at: {torch_path}")
        
        # Check for CUDA-related files
        torch_dir = os.path.dirname(torch_path)
        cuda_files = []
        for root, dirs, files in os.walk(torch_dir):
            for file in files:
                if 'cuda' in file.lower():
                    cuda_files.append(os.path.join(root, file))
        
        if cuda_files:
            print(f"⚠️  Found {len(cuda_files)} CUDA-related files:")
            for file in cuda_files[:5]:  # Show first 5
                print(f"   - {file}")
            if len(cuda_files) > 5:
                print(f"   ... and {len(cuda_files) - 5} more")
        else:
            print("✅ No CUDA-related files found")
        
        return True
        
    except ImportError as e:
        print(f"❌ PyTorch not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking PyTorch: {e}")
        return False

def check_installed_packages():
    """Check what packages are installed"""
    print("\n📦 Checking Installed Packages")
    print("=" * 40)
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        
        packages = result.stdout.split('\n')
        cuda_packages = [pkg for pkg in packages if 'cuda' in pkg.lower() or 'nvidia' in pkg.lower()]
        
        if cuda_packages:
            print("⚠️  Found CUDA/NVIDIA packages:")
            for pkg in cuda_packages:
                print(f"   - {pkg}")
        else:
            print("✅ No CUDA/NVIDIA packages found")
            
    except Exception as e:
        print(f"❌ Error checking packages: {e}")

def main():
    print("🧪 PyTorch CPU-Only Installation Test")
    print("=" * 50)
    
    # Check PyTorch installation
    pytorch_ok = check_pytorch_installation()
    
    # Check installed packages
    check_installed_packages()
    
    # Summary
    print("\n" + "=" * 50)
    if pytorch_ok:
        print("✅ PyTorch is installed")
        print("💡 If CUDA is available, consider using a different installation method")
    else:
        print("❌ PyTorch installation issues detected")
    
    print("\n🔧 Recommendations:")
    print("1. Use --extra-index-url https://download.pytorch.org/whl/cpu")
    print("2. Set environment variables: CUDA_VISIBLE_DEVICES=''")
    print("3. Use specific PyTorch CPU version: torch==2.1.0+cpu")

if __name__ == "__main__":
    main()