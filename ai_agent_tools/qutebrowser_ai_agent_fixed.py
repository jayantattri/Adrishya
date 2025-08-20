#!/usr/bin/env python3
"""
Qutebrowser AI Agent Integration (Fixed Version)

This module integrates the AI browser agent directly into Qutebrowser's command system.
It should be placed in Qutebrowser's config directory and loaded automatically.

Installation:
1. Copy this file to ~/.config/qutebrowser/ai_agent.py
2. Add 'config-source ai_agent.py' to your config.py
3. Restart Qutebrowser

Usage:
:ai-agent-init deepseek_assistant
:ai-agent-ask "open google.com"
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Any, Optional

# Add the ai_agent_tools directory to the path
# Handle the case where __file__ might not be defined
try:
    current_file = __file__
except NameError:
    # Fallback for when __file__ is not available
    current_file = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "qutebrowser", "ai_agent.py")

# Try multiple possible paths for ai_agent_tools
possible_paths = [
    os.path.join(os.path.dirname(current_file), 'ai_agent_tools'),
    os.path.join(os.path.dirname(current_file), '..', 'ai_agent_tools'),
    os.path.join(os.path.expanduser("~"), "Documents", "Adrishya", "ai_agent_tools"),
]

ai_agent_tools_path = None
for path in possible_paths:
    if os.path.exists(path):
        ai_agent_tools_path = path
        break

if ai_agent_tools_path and ai_agent_tools_path not in sys.path:
    sys.path.insert(0, ai_agent_tools_path)

# Try to import Qutebrowser-specific modules
try:
    from qutebrowser.api import cmdutils
    from qutebrowser.utils import message
    QUTEBROWSER_AVAILABLE = True
except ImportError:
    print("Warning: Could not import qutebrowser modules: No module named 'PyQt6.QtCore'")
    print("This module should be run from within qutebrowser or with proper imports")
    QUTEBROWSER_AVAILABLE = False

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI agent not available: {e}")
    print(f"Tried paths: {possible_paths}")
    AGENT_AVAILABLE = False

# Global agent instance
ai_agent = None
current_profile = None

def load_config() -> Dict[str, Any]:
    """Load agent configuration."""
    try:
        # Try multiple possible config locations
        config_paths = []
        if ai_agent_tools_path:
            config_paths.append(os.path.join(ai_agent_tools_path, "agent_config.json"))
        
        config_paths.extend([
            os.path.join(os.path.expanduser("~"), "Documents", "Adrishya", "ai_agent_tools", "agent_config.json"),
            os.path.join(os.path.dirname(current_file), "agent_config.json"),
        ])
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        
        # Return default config if no file found
        return {
            "agent_profiles": {
                "deepseek_assistant": {
                    "llm_provider": "ollama",
                    "model": "deepseek-r1:14b",
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "timeout": 30,
                    "max_tool_calls": 10
                }
            }
        }
    except Exception as e:
        print(f"Could not load agent config: {e}")
        return {"agent_profiles": {"default": {}}}

def initialize_agent(profile: str = "deepseek_assistant", api_key: str = None) -> bool:
    """Initialize the AI agent with specified profile."""
    global ai_agent, current_profile
    
    if not AGENT_AVAILABLE:
        print("❌ AI agent components not available")
        return False
    
    try:
        config = load_config()
        profile_config = config["agent_profiles"].get(profile, {})
        if not profile_config:
            print(f"❌ Unknown profile: {profile}")
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
        
        print(f"✅ AI agent initialized with profile: {profile}")
        print(f"   Provider: {agent_config.llm_provider}")
        print(f"   Model: {agent_config.model}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False

async def ask_agent(query: str) -> Dict[str, Any]:
    """Ask the AI agent to perform a browser task."""
    global ai_agent
    
    if not ai_agent:
        return {"error": "Agent not initialized. Use :ai-agent-init first"}
    
    try:
        response = await ai_agent.process_query(query)
        return {
            "success": response.success,
            "message": response.message,
            "tool_calls": response.tool_calls,
            "execution_results": response.execution_results,
            "error": response.error
        }
    except Exception as e:
        return {"error": str(e)}

# Only register commands if we're in Qutebrowser
if QUTEBROWSER_AVAILABLE:
    class AIAgentCommandDispatcher:
        """Command dispatcher for AI agent commands.
        
        This follows the same pattern as the main CommandDispatcher in qutebrowser.
        """
        
        def __init__(self):
            pass
        
        @cmdutils.register(instance='ai-agent-dispatcher', scope='global')
        def ai_agent_init(self, profile: str = "deepseek_assistant", api_key: str = None):
            """Initialize AI browser agent.
            
            Args:
                profile: Agent profile to use (default: deepseek_assistant)
                api_key: API key for LLM provider (not needed for Ollama)
            """
            try:
                success = initialize_agent(profile, api_key)
                if success:
                    message.info(f"✅ AI agent initialized with profile: {profile}")
                    print(f"🤖 AI agent ready! Profile: {profile}")
                    if profile == "deepseek_assistant":
                        print("🧠 Using DeepSeek R1 14B model via Ollama")
                else:
                    message.error("❌ Failed to initialize AI agent")
            except Exception as e:
                message.error(f"❌ AI agent initialization error: {e}")
                print(f"Error details: {e}")

        @cmdutils.register(instance='ai-agent-dispatcher', scope='global')
        def ai_agent_ask(self, query: str):
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
                print(f"🤖 Processing: {query}")
                message.info(f"🤖 AI agent processing: {query}")
                
                # Run async query in event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(ask_agent(query))
                loop.close()
                
                if response.get("success"):
                    message.info(f"✅ AI agent: {response['message']}")
                    print(f"✅ Success: {response['message']}")
                    
                    # Show tool execution details
                    tool_calls = response.get("tool_calls", [])
                    if tool_calls:
                        print(f"🔧 Tools used: {len(tool_calls)}")
                        for tool_call in tool_calls:
                            print(f"   - {tool_call.get('name', 'Unknown tool')}")
                else:
                    error_msg = response.get('error', 'Unknown error')
                    message.error(f"❌ AI agent error: {error_msg}")
                    print(f"❌ Error: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Error processing query: {e}"
                message.error(f"❌ {error_msg}")
                print(f"❌ {error_msg}")

        @cmdutils.register(instance='ai-agent-dispatcher', scope='global')
        def ai_agent_status(self):
            """Show AI agent status."""
            global ai_agent, current_profile
            
            if ai_agent:
                profile = current_profile or "unknown"
                print(f"🤖 AI Agent Status:")
                print(f"   Profile: {profile}")
                print(f"   Status: Active")
                print(f"   Agent: {type(ai_agent).__name__}")
            else:
                print("🤖 AI Agent Status: Not initialized")
                print("💡 Use :ai-agent-init to initialize")

        @cmdutils.register(instance='ai-agent-dispatcher', scope='global')
        def ai_agent_help(self):
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

    # Create and register the command dispatcher instance
    try:
        from qutebrowser.utils import objreg
        ai_agent_dispatcher = AIAgentCommandDispatcher()
        objreg.register('ai-agent-dispatcher', ai_agent_dispatcher, scope='global')
        print("✅ AI Agent Command Dispatcher registered successfully")
    except Exception as e:
        print(f"❌ Failed to register AI Agent Command Dispatcher: {e}")

# Auto-initialization message
print("🤖 AI Browser Agent Integration Loaded!")
if QUTEBROWSER_AVAILABLE:
    print("📋 Available commands:")
    print("   :ai-agent-init [profile] - Initialize the AI agent")
    print("   :ai-agent-ask <query>    - Ask the AI agent to perform a task")
    print("   :ai-agent-status         - Show agent status")
    print("   :ai-agent-help           - Show help")
    print()
    print("🚀 To get started:")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open google.com'")
else:
    print("⚠️  Qutebrowser modules not available - commands not registered")
    print("   This file should be loaded from within Qutebrowser")
