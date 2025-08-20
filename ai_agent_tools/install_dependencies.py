#!/usr/bin/env python3
"""
Install Dependencies for AI Browser Agent

This script installs the required Python packages for the AI browser agent.
"""

import subprocess
import sys
import os

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

def check_package(package_name):
    """Check if a package is available."""
    try:
        __import__(package_name)
        print(f"✅ {package_name} is available")
        return True
    except ImportError:
        print(f"❌ {package_name} is not available")
        return False

def install_package(package_name):
    """Install a package using pip."""
    return run_command(f"pip install {package_name}", f"Installing {package_name}")

def main():
    """Main installation function."""
    print("🚀 Installing Dependencies for AI Browser Agent")
    print("=" * 50)
    
    # Check current Python environment
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Python executable: {sys.executable}")
    
    # Required packages
    required_packages = [
        "requests",
        "asyncio"
    ]
    
    # Optional packages (for different LLM providers)
    optional_packages = [
        "openai",
        "anthropic"
    ]
    
    print("\n📦 Checking required packages...")
    missing_required = []
    
    for package in required_packages:
        if not check_package(package):
            missing_required.append(package)
    
    print("\n📦 Checking optional packages...")
    missing_optional = []
    
    for package in optional_packages:
        if not check_package(package):
            missing_optional.append(package)
    
    # Install missing required packages
    if missing_required:
        print(f"\n🔧 Installing missing required packages: {missing_required}")
        for package in missing_required:
            if not install_package(package):
                print(f"❌ Failed to install {package}")
                return False
    else:
        print("✅ All required packages are available")
    
    # Install missing optional packages
    if missing_optional:
        print(f"\n🔧 Installing missing optional packages: {missing_optional}")
        for package in missing_optional:
            install_package(package)  # Don't fail if optional packages fail
    
    # Test the setup
    print("\n🧪 Testing AI agent setup...")
    
    try:
        # Test imports
        import requests
        print("✅ requests module imported successfully")
        
        import asyncio
        print("✅ asyncio module imported successfully")
        
        # Test Ollama connection
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama connection successful")
                
                # Check for DeepSeek model
                models = response.json().get("models", [])
                deepseek_found = any("deepseek-r1:14b" in model.get("name", "") for model in models)
                
                if deepseek_found:
                    print("✅ DeepSeek R1 14B model found")
                else:
                    print("⚠️  DeepSeek R1 14B model not found")
                    print("   Run: ollama pull deepseek-r1:14b")
            else:
                print("❌ Ollama connection failed")
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
        
        # Test AI agent imports
        try:
            from ai_browser_agent import AIBrowserAgent, AgentConfig
            print("✅ AI browser agent imported successfully")
        except Exception as e:
            print(f"❌ AI browser agent import error: {e}")
        
    except Exception as e:
        print(f"❌ Setup test error: {e}")
        return False
    
    print("\n🎉 Dependencies installation complete!")
    print("=" * 50)
    print("✅ Required packages installed")
    print("✅ Optional packages installed")
    print("✅ Setup tested successfully")
    
    print("\n🚀 Next steps:")
    print("1. In qutebrowser: :pyeval --file ai_agent_tools/load_ai_agent.py")
    print("2. Initialize agent: :ai-agent-init deepseek_assistant")
    print("3. Start using: :ai-agent-ask 'open github.com'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
