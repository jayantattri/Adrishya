#!/usr/bin/env python3
"""
Install AI Agent Integration for Qutebrowser

This script installs the AI browser agent directly into Qutebrowser's command system.
It copies the integration file to the correct location and updates the config.

Usage:
python3 install_qutebrowser_integration.py
"""

import os
import sys
import shutil
from pathlib import Path

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

def install_integration():
    """Install the AI agent integration into Qutebrowser."""
    print("🚀 Installing AI Agent Integration for Qutebrowser...")
    
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
    
    return True

def create_standalone_integration():
    """Create a standalone integration file that doesn't rely on external paths."""
    print("🔧 Creating standalone integration file...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qutebrowser_config_dir = get_qutebrowser_config_dir()
    
    # Read the original integration file
    source_file = os.path.join(current_dir, "qutebrowser_ai_agent.py")
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return False
    
    with open(source_file, 'r') as f:
        content = f.read()
    
    # Create a standalone version that includes all necessary code
    standalone_content = f'''#!/usr/bin/env python3
"""
Standalone Qutebrowser AI Agent Integration

This is a standalone version that includes all necessary components.
No external dependencies required.
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Any, Optional

# Add the ai_agent_tools directory to the path
# This file should be in ~/.config/qutebrowser/ai_agent.py
# and ai_agent_tools should be in ~/.config/qutebrowser/ai_agent_tools/
ai_agent_tools_path = os.path.join(os.path.dirname(__file__), 'ai_agent_tools')
if ai_agent_tools_path not in sys.path:
    sys.path.insert(0, ai_agent_tools_path)

# Also try parent directory
parent_tools_path = os.path.join(os.path.dirname(__file__), '..', 'ai_agent_tools')
if parent_tools_path not in sys.path:
    sys.path.insert(0, parent_tools_path)

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI agent not available: {e}")
    print("Please ensure ai_agent_tools directory is accessible")
    AGENT_AVAILABLE = False

# Global agent instance
ai_agent = None
current_profile = None

def load_config() -> Dict[str, Any]:
    """Load agent configuration."""
    try:
        # Try multiple possible config locations
        config_paths = [
            os.path.join(ai_agent_tools_path, "agent_config.json"),
            os.path.join(parent_tools_path, "agent_config.json"),
            os.path.join(os.path.dirname(__file__), "agent_config.json"),
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        
        # Return default config if no file found
        return {{
            "agent_profiles": {{
                "deepseek_assistant": {{
                    "llm_provider": "ollama",
                    "model": "deepseek-r1:14b",
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "timeout": 30,
                    "max_tool_calls": 10
                }}
            }}
        }}
    except Exception as e:
        print(f"Could not load agent config: {{e}}")
        return {{"agent_profiles": {{"default": {{}}}}}}

def initialize_agent(profile: str = "deepseek_assistant", api_key: str = None) -> bool:
    """Initialize the AI agent with specified profile."""
    global ai_agent, current_profile
    
    if not AGENT_AVAILABLE:
        print("❌ AI agent components not available")
        return False
    
    try:
        config = load_config()
        profile_config = config["agent_profiles"].get(profile, {{}})
        if not profile_config:
            print(f"❌ Unknown profile: {{profile}}")
            return False
        
        # Create agent config
        agent_config = AgentConfig(
            llm_provider=profile_config.get("llm_provider", "ollama"),
            model=profile_config.get("model", "deepseek-r1:14b"),
            api_key=api_key,
            api_base=profile_config.get("api_base"),
            temperature=profile_config.get("temperature", 0.1),
            max_tokens=profile_config.get("max_tokens", 1500),
            timeout=profile_config.get("timeout", 30),
            max_tool_calls=profile_config.get("max_tool_calls", 10),
            debug=False
        )
        
        ai_agent = AIBrowserAgent(agent_config)
        current_profile = profile
        
        print(f"✅ AI agent initialized with profile: {{profile}}")
        print(f"   Provider: {{agent_config.llm_provider}}")
        print(f"   Model: {{agent_config.model}}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {{e}}")
        return False

async def ask_agent(query: str) -> Dict[str, Any]:
    """Ask the AI agent to perform a browser task."""
    global ai_agent
    
    if not ai_agent:
        return {{"error": "Agent not initialized. Use :ai-agent-init first"}}
    
    try:
        response = await ai_agent.process_query(query)
        return {{
            "success": response.success,
            "message": response.message,
            "tool_calls": response.tool_calls,
            "execution_results": response.execution_results,
            "error": response.error
        }}
    except Exception as e:
        return {{"error": str(e)}}

# Qutebrowser command registration
@cmdutils.register(scope='global')
def ai_agent_init(profile: str = "deepseek_assistant", api_key: str = None):
    """Initialize AI browser agent.
    
    Args:
        profile: Agent profile to use (default: deepseek_assistant)
        api_key: API key for LLM provider (not needed for Ollama)
    """
    try:
        success = initialize_agent(profile, api_key)
        if success:
            message.info(f"✅ AI agent initialized with profile: {{profile}}")
            print(f"🤖 AI agent ready! Profile: {{profile}}")
            if profile == "deepseek_assistant":
                print("🧠 Using DeepSeek R1 14B model via Ollama")
        else:
            message.error("❌ Failed to initialize AI agent")
    except Exception as e:
        message.error(f"❌ AI agent initialization error: {{e}}")
        print(f"Error details: {{e}}")

@cmdutils.register(scope='global')
def ai_agent_ask(query: str):
    """Ask the AI agent to perform a browser task.
    
    Args:
        query: Natural language query (e.g., "open github.com")
    """
    global ai_agent
    
    if not ai_agent:
        message.error("❌ AI agent not initialized. Use :ai-agent-init first")
        print("💡 Try: :ai-agent-init deepseek_assistant")
        return
    
    try:
        print(f"🤖 Processing: {{query}}")
        message.info(f"🤖 AI agent processing: {{query}}")
        
        # Run async query in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(ask_agent(query))
        loop.close()
        
        if response.get("success"):
            message.info(f"✅ AI agent: {{response['message']}}")
            print(f"✅ Success: {{response['message']}}")
            
            # Show tool execution details
            tool_calls = response.get("tool_calls", [])
            if tool_calls:
                print(f"🔧 Tools used: {{len(tool_calls)}}")
                for tool_call in tool_calls:
                    print(f"   - {{tool_call.get('name', 'Unknown tool')}}")
        else:
            error_msg = response.get('error', 'Unknown error')
            message.error(f"❌ AI agent error: {{error_msg}}")
            print(f"❌ Error: {{error_msg}}")
            
    except Exception as e:
        error_msg = f"Error processing query: {{e}}"
        message.error(f"❌ {{error_msg}}")
        print(f"❌ {{error_msg}}")

@cmdutils.register(scope='global')
def ai_agent_status():
    """Show AI agent status."""
    global ai_agent, current_profile
    
    if ai_agent:
        profile = current_profile or "unknown"
        print(f"🤖 AI Agent Status:")
        print(f"   Profile: {{profile}}")
        print(f"   Status: Active")
        print(f"   Agent: {{type(ai_agent).__name__}}")
    else:
        print("🤖 AI Agent Status: Not initialized")
        print("💡 Use :ai-agent-init to initialize")

@cmdutils.register(scope='global')
def ai_agent_help():
    """Show AI agent help."""
    print("🤖 AI Browser Agent Help")
    print("=" * 40)
    print("Commands:")
    print("  :ai-agent-init [profile] - Initialize the AI agent")
    print("  :ai-agent-ask <query>    - Ask the AI agent to perform a task")
    print("  :ai-agent-status         - Show agent status")
    print("  :ai-agent-help           - Show this help")
    print()
    print("Profiles:")
    print("  deepseek_assistant - DeepSeek R1 14B via Ollama (recommended)")
    print("  default           - Default OpenAI GPT-4")
    print()
    print("Examples:")
    print("  :ai-agent-init deepseek_assistant")
    print("  :ai-agent-ask 'open google.com'")
    print("  :ai-agent-ask 'search for Python tutorials'")
    print("  :ai-agent-ask 'click the first result'")

# Auto-initialization message
print("🤖 AI Browser Agent Integration Loaded!")
print("📋 Available commands:")
print("   :ai-agent-init [profile] - Initialize the AI agent")
print("   :ai-agent-ask <query>    - Ask the AI agent to perform a task")
print("   :ai-agent-status         - Show agent status")
print("   :ai-agent-help           - Show help")
print()
print("🚀 To get started:")
print("   :ai-agent-init deepseek_assistant")
print("   :ai-agent-ask 'open google.com'")
'''
    
    # Write the standalone integration file
    target_file = os.path.join(qutebrowser_config_dir, "ai_agent.py")
    try:
        with open(target_file, 'w') as f:
            f.write(standalone_content)
        print(f"✅ Created standalone integration file: {target_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create standalone integration: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 AI Agent Qutebrowser Integration Installer")
    print("=" * 50)
    
    # Install the integration
    if install_integration():
        print("\n✅ Installation completed successfully!")
        
        # Create standalone version
        if create_standalone_integration():
            print("✅ Standalone integration created!")
        
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
        
    else:
        print("\n❌ Installation failed!")
        print("💡 Please check the error messages above")

if __name__ == "__main__":
    main()
