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
    port_sources = ['PORT', 'STREAMLIT_SERVER_PORT', 'RAILWAY_STATIC_URL']
    
    for source in port_sources:
        port = os.getenv(source)
        if port:
            print(f"Found {source}={port}")
            # Clean up the port value
            port = str(port).strip().strip('"').strip("'")
            try:
                port_int = int(port)
                if 1 <= port_int <= 65535:
                    return port_int
                else:
                    print(f"Port {port_int} out of range, trying next source")
            except ValueError:
                print(f"Invalid port value '{port}', trying next source")
    
    # Default fallback
    print("Using default port 8080")
    return 8080

def main():
    # Get the port
    port = get_port()
    print(f"🚀 Starting DocuSearch Light on port {port}")
    print("💻 Using CPU-only PyTorch for minimal deployment size")
    
    # Debug: Print all environment variables
    print("🔍 Environment variables:")
    for key, value in os.environ.items():
        if 'PORT' in key.upper():
            print(f"  {key}={value}")
    
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