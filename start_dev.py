#!/usr/bin/env python3
"""
Development startup script for Mythic Bastionlands
Starts the backend server with automatic reload
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🏰 Starting Mythic Bastionlands Development Server")
    print("=" * 50)
    
    # Get the backend directory
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if virtual environment exists
    venv_dir = Path(__file__).parent / "venv"
    python_executable = sys.executable
    
    if not venv_dir.exists():
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        
    # Use virtual environment python
    if os.name == 'nt':  # Windows
        python_executable = str(venv_dir / "Scripts" / "python.exe")
        pip_executable = str(venv_dir / "Scripts" / "pip.exe")
    else:  # Unix/Linux/Mac
        python_executable = str(venv_dir / "bin" / "python")
        pip_executable = str(venv_dir / "bin" / "pip")
    
    # Install requirements
    print("📦 Installing dependencies...")
    subprocess.run([pip_executable, "install", "-r", str(backend_dir / "requirements.txt")])
    
    # Check if Ollama is running (WSL-aware)
    ollama_url = "http://localhost:11434"
    try:
        # Try to detect WSL and use Windows host IP
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if 'nameserver' in line:
                    host_ip = line.split()[1]
                    ollama_url = f"http://{host_ip}:11434"
                    break
    except:
        pass
    
    try:
        import requests
        print(f"🔍 Checking Ollama at {ollama_url}...")
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            print(f"✅ Ollama is running with models: {', '.join(model_names)}")
        else:
            print("⚠️  Ollama may not be properly configured")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print(f"   Tried connecting to: {ollama_url}")
        print("   Make sure Ollama is running on Windows")
        print("\nContinuing anyway...")
    
    # Start the server
    print("\n🚀 Starting server...")
    print("Frontend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("API Status: http://localhost:8000/api/status")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    # Change to backend directory and start server
    os.chdir(backend_dir)
    subprocess.run([
        python_executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

if __name__ == "__main__":
    main()