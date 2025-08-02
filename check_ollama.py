#!/usr/bin/env python3
"""
Quick script to test Ollama connection
"""
import requests
import json

def test_ollama():
    # Auto-detect WSL and use Windows host IP
    ollama_url = "http://localhost:11434"
    try:
        with open('/etc/resolv.conf', 'r') as f:
            for line in f:
                if 'nameserver' in line:
                    host_ip = line.split()[1]
                    ollama_url = f"http://{host_ip}:11434"
                    break
    except:
        pass
    
    print(f"🔍 Testing Ollama at {ollama_url}")
    
    try:
        # Test if Ollama is running
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama is running!")
            print("Available models:")
            for model in models:
                print(f"  - {model.get('name', 'Unknown')}")
            
            # Test a simple generation
            print("\n🧪 Testing generation with tohur:latest...")
            gen_response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": "tohur:latest",
                    "prompt": "Write one sentence about a knight in a medieval setting:",
                    "stream": False,
                    "options": {"num_predict": 50}
                },
                timeout=30
            )
            
            if gen_response.status_code == 200:
                result = gen_response.json()
                print(f"✅ Response: {result.get('response', 'No response')}")
            else:
                print(f"❌ Generation failed: {gen_response.status_code}")
                
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")

if __name__ == "__main__":
    test_ollama()