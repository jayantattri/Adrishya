#!/usr/bin/env python3
"""
Simple AI Agent Integration Installer

This script installs the AI browser agent directly into Qutebrowser's command system.
It copies the integration file to the correct location and updates the config.

Usage:
python3 install_simple.py
"""

import os
import sys
import shutil

def get_qutebrowser_config_dir():
    """Get the Qutebrowser config directory."""
    # Try to find qutebrowser config directory
    possible_paths = [
        os.path.expanduser("~/.config/qutebrowser"),
        os.path.expanduser("~/Library/Application Support/qutebrowser"),
        os.path.expanduser("~/.qutebrowser"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Default to ~/.config/qutebrowser
    return os.path.expanduser("~/.config/qutebrowser")

def main():
    """Main installation function."""
    print("🚀 Simple AI Agent Qutebrowser Integration Installer")
    print("=" * 50)
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qutebrowser_config_dir = get_qutebrowser_config_dir()
    
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 Qutebrowser config directory: {qutebrowser_config_dir}")
    
    # Create qutebrowser config directory if it doesn't exist
    os.makedirs(qutebrowser_config_dir, exist_ok=True)
    
    # Copy the integration file
    source_file = os.path.join(current_dir, "qutebrowser_ai_agent.py")
    target_file = os.path.join(qutebrowser_config_dir, "ai_agent.py")
    
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
    
    try:
        shutil.copy2(source_file, target_file)
        print(f"✅ Copied integration file to: {target_file}")
    except Exception as e:
        print(f"❌ Failed to copy integration file: {e}")
        return False
    
    # Create or update config.py
    config_file = os.path.join(qutebrowser_config_dir, "config.py")
    
    # Check if config.py exists and if it already has our integration
    config_content = ""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_content = f.read()
    
    # Check if our integration is already loaded
    if "config-source ai_agent.py" in config_content:
        print("✅ Integration already configured in config.py")
    else:
        # Add our integration to config.py
        integration_line = "\n# AI Browser Agent Integration\nconfig-source ai_agent.py\n"
        
        try:
            with open(config_file, 'a') as f:
                f.write(integration_line)
            print(f"✅ Added integration to config.py")
        except Exception as e:
            print(f"❌ Failed to update config.py: {e}")
            print(f"💡 Please manually add 'config-source ai_agent.py' to {config_file}")
    
    # Create a symlink to the ai_agent_tools directory
    tools_link = os.path.join(qutebrowser_config_dir, "ai_agent_tools")
    if not os.path.exists(tools_link):
        try:
            os.symlink(current_dir, tools_link)
            print(f"✅ Created symlink to ai_agent_tools: {tools_link}")
        except Exception as e:
            print(f"⚠️  Could not create symlink: {e}")
            print(f"💡 The integration will look for ai_agent_tools in the parent directory")
    
    print("\n✅ Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Restart Qutebrowser")
    print("2. Try the commands:")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open google.com'")
    print("   :ai-agent-help")
    
    print("\n💡 If you encounter issues:")
    print("- Check that Ollama is running: ollama list")
    print("- Verify the DeepSeek model is installed: ollama list | grep deepseek")
    print("- Check the console for error messages")
    
    return True

if __name__ == "__main__":
    main()
