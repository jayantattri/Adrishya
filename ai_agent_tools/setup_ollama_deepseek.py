#!/usr/bin/env python3
"""
Ollama DeepSeek Setup Script for AI Browser Agent

This script helps you set up the AI browser agent to use Ollama with the DeepSeek R1 14B model.
It handles installation, model downloading, and configuration.

Usage:
    python setup_ollama_deepseek.py
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and return success status."""
    print(f"🔄 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def check_ollama_installed():
    """Check if Ollama is installed and running."""
    print("🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    if not run_command("which ollama", "Checking if Ollama is installed"):
        return False
    
    # Check if Ollama service is running
    if not run_command("ollama list", "Checking if Ollama service is running"):
        return False
    
    return True

def install_ollama():
    """Install Ollama if not already installed."""
    print("📦 Installing Ollama...")
    
    system = sys.platform
    if system == "darwin":  # macOS
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama on macOS")
    elif system == "linux":
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama on Linux")
    else:
        print("❌ Unsupported operating system. Please install Ollama manually from https://ollama.ai")
        return False

def download_deepseek_model():
    """Download the DeepSeek R1 14B model."""
    print("📥 Downloading DeepSeek R1 14B model...")
    print("   This may take several minutes depending on your internet connection.")
    
    return run_command("ollama pull deepseek-r1:14b", "Downloading DeepSeek R1 14B model")

def test_model():
    """Test the DeepSeek model with a simple query."""
    print("🧪 Testing DeepSeek model...")
    
    test_prompt = "Hello! Can you help me with browser automation tasks?"
    
    # Create a simple test script
    test_script = f'''import requests
import json

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={{
            "model": "deepseek-r1:14b",
            "prompt": "{test_prompt}",
            "stream": False
        }},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Model test successful!")
        print(f"Response: {{result.get('response', 'No response')[:100]}}...")
        return True
    else:
        print(f"❌ Model test failed: {{response.status_code}}")
        return False
        
except Exception as e:
    print(f"❌ Model test error: {{e}}")
    return False
'''
    
    # Write test script to temporary file
    test_file = "test_deepseek_model.py"
    with open(test_file, "w") as f:
        f.write(test_script)
    
    # Run test
    success = run_command(f"python {test_file}", "Testing DeepSeek model")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    
    return success

def setup_ai_agent():
    """Set up the AI browser agent with DeepSeek configuration."""
    print("🤖 Setting up AI Browser Agent...")
    
    # Check if agent interface exists
    agent_file = Path("agent_interface.py")
    if not agent_file.exists():
        print("❌ agent_interface.py not found. Please ensure you're in the ai_agent_tools directory.")
        return False
    
    # Create a setup script for qutebrowser
    setup_script = '''
# AI Browser Agent Setup for DeepSeek R1 14B
# Run this in qutebrowser's Python console

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from agent_interface import AgentInterface
    
    # Create agent instance
    agent = AgentInterface()
    
    # Initialize with DeepSeek profile
    success = agent.initialize_agent("deepseek_assistant")
    
    if success:
        print("✅ AI Browser Agent initialized with DeepSeek R1 14B!")
        print("🎯 You can now use commands like:")
        print("   await agent.ask('open github.com')")
        print("   await agent.ask('help me research Python frameworks')")
        print("   await agent.ask('fill out the contact form')")
    else:
        print("❌ Failed to initialize AI agent")
        
except Exception as e:
    print(f"❌ Setup error: {e}")
'''
    
    # Write setup script
    with open("setup_deepseek_agent.py", "w") as f:
        f.write(setup_script)
    
    print("✅ Setup script created: setup_deepseek_agent.py")
    return True

def main():
    """Main setup function."""
    print("🚀 Ollama DeepSeek R1 14B Setup for AI Browser Agent")
    print("=" * 60)
    
    # Step 1: Check/Install Ollama
    if not check_ollama_installed():
        print("\n📦 Ollama not found. Installing...")
        if not install_ollama():
            print("❌ Failed to install Ollama. Please install manually from https://ollama.ai")
            return False
        
        # Wait a moment for installation
        time.sleep(3)
        
        # Check again
        if not check_ollama_installed():
            print("❌ Ollama installation verification failed")
            return False
    
    print("✅ Ollama is installed and running")
    
    # Step 2: Download DeepSeek model
    print("\n📥 Checking if DeepSeek R1 14B model is available...")
    if not run_command("ollama list | grep deepseek-r1:14b", "Checking for DeepSeek model"):
        print("\n📥 Model not found. Downloading...")
        if not download_deepseek_model():
            print("❌ Failed to download DeepSeek model")
            return False
    
    print("✅ DeepSeek R1 14B model is ready")
    
    # Step 3: Test the model
    print("\n🧪 Testing model functionality...")
    if not test_model():
        print("⚠️  Model test failed, but continuing with setup...")
    
    # Step 4: Set up AI agent
    print("\n🤖 Setting up AI Browser Agent...")
    if not setup_ai_agent():
        print("❌ Failed to set up AI agent")
        return False
    
    # Success!
    print("\n🎉 Setup Complete!")
    print("=" * 60)
    print("✅ Ollama is installed and running")
    print("✅ DeepSeek R1 14B model is downloaded")
    print("✅ AI Browser Agent is configured")
    print("\n🚀 Next Steps:")
    print("1. In qutebrowser, run: :pyeval --file ai_agent_tools/setup_deepseek_agent.py")
    print("2. Or use the command: :ai-agent-init deepseek_assistant")
    print("3. Start giving commands: :ai-agent-ask 'open github.com'")
    print("\n💡 Example commands to try:")
    print("   :ai-agent-ask 'open reddit.com in a new tab'")
    print("   :ai-agent-ask 'help me research AI tools'")
    print("   :ai-agent-ask 'find the search box and search for Python'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
