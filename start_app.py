#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles PORT environment variable properly
"""

import os
import subprocess
import sys

def get_port():
    """Get port from various possible sources"""
    # Try different environment variables
    port = os.getenv('PORT') or os.getenv('STREAMLIT_SERVER_PORT') or '8080'
    
    # Clean up the port value (remove any quotes or extra characters)
    port = str(port).strip().strip('"').strip("'")
    
    # Ensure it's a valid integer
    try:
        port_int = int(port)
        if port_int <= 0 or port_int > 65535:
            print(f"⚠️  Port {port_int} out of range, using 8080")
            return 8080
        return port_int
    except ValueError:
        print(f"⚠️  Invalid port value: '{port}', using 8080")
        return 8080

def main():
    # Get the port
    port = get_port()
    print(f"🚀 Starting DocuSearch Light on port {port}")
    print("💻 Using CPU-only PyTorch for minimal deployment size")
    
    # Debug: Print environment variables
    print(f"🔍 Environment: PORT={os.getenv('PORT')}, STREAMLIT_SERVER_PORT={os.getenv('STREAMLIT_SERVER_PORT')}")
    
    # Set cache directories to /tmp for Railway
    os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
    os.environ['TORCH_HOME'] = '/tmp/torch_cache'
    os.environ['HF_HOME'] = '/tmp/hf_cache'
    
    # Create cache directories
    os.makedirs('/tmp/transformers_cache', exist_ok=True)
    os.makedirs('/tmp/torch_cache', exist_ok=True)
    os.makedirs('/tmp/hf_cache', exist_ok=True)
    
    # Check if embeddings file exists
    if not os.path.exists('embeddings/embeddings_light.json'):
        print("⚠️  Warning: embeddings_light.json not found")
        print("   The app will need to generate embeddings.")
    
    # Start Streamlit
    try:
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'docusearch_light.py',
            '--server.port', str(port),
            '--server.address', '0.0.0.0'
        ]
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()