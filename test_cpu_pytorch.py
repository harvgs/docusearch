#!/usr/bin/env python3
"""
Test CPU-Only PyTorch Installation
This script tests if PyTorch can be installed without CUDA dependencies.
"""

import subprocess
import sys
import os

def test_current_pytorch():
    """Test current PyTorch installation"""
    print("🔍 Testing Current PyTorch Installation")
    print("=" * 50)
    
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
        
        return True
        
    except ImportError as e:
        print(f"❌ PyTorch not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking PyTorch: {e}")
        return False

def test_pytorch_installation():
    """Test PyTorch CPU-only installation"""
    print("\n🧪 Testing CPU-Only PyTorch Installation")
    print("=" * 50)
    
    # Create a test requirements file
    test_requirements = """--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.7.1+cpu
numpy>=1.24.0
"""
    
    with open("test_requirements.txt", "w") as f:
        f.write(test_requirements)
    
    print("📝 Created test requirements file")
    
    try:
        # Install PyTorch CPU-only with --no-deps to avoid conflicts
        print("📦 Installing PyTorch CPU-only...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--no-cache-dir", "--force-reinstall", "--no-deps",
            "torch==2.7.1+cpu", "--extra-index-url", "https://download.pytorch.org/whl/cpu"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyTorch CPU-only installation successful")
            
            # Check what was installed
            print("\n📋 Installed packages:")
            pip_list = subprocess.run([
                sys.executable, "-m", "pip", "list"
            ], capture_output=True, text=True)
            
            lines = pip_list.stdout.split('\n')
            torch_line = [line for line in lines if 'torch' in line.lower()]
            cuda_lines = [line for line in lines if 'cuda' in line.lower() or 'nvidia' in line.lower()]
            
            if torch_line:
                print(f"   {torch_line[0]}")
            
            if cuda_lines:
                print("⚠️  CUDA packages found:")
                for line in cuda_lines:
                    print(f"   {line}")
            else:
                print("✅ No CUDA packages found")
                
        else:
            print("❌ PyTorch installation failed")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        if os.path.exists("test_requirements.txt"):
            os.remove("test_requirements.txt")

def main():
    # First test current installation
    current_ok = test_current_pytorch()
    
    # Then test new installation
    test_pytorch_installation()
    
    print("\n" + "=" * 50)
    if current_ok:
        print("✅ Current PyTorch installation looks good")
        print("💡 If CUDA is not available, you're ready for Railway deployment")
    else:
        print("❌ PyTorch installation issues detected")
    
    print("\n🔧 Recommendations:")
    print("1. Current setup should work for Railway if CUDA is not available")
    print("2. The hash error is likely due to existing PyTorch installation")
    print("3. Railway will do a fresh install, so this shouldn't be an issue")

if __name__ == "__main__":
    main()