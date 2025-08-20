#!/usr/bin/env python3
"""
Qutebrowser AI Agent Integration

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
# Assuming this file is in ~/.config/qutebrowser/ and ai_agent_tools is in the parent directory
ai_agent_tools_path = os.path.join(os.path.dirname(__file__), '..', 'ai_agent_tools')
if ai_agent_tools_path not in sys.path:
    sys.path.insert(0, ai_agent_tools_path)

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig
    from agent_interface import AgentInterface
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI agent not available: {e}")
    AGENT_AVAILABLE = False

# Global agent instance
ai_agent = None
current_profile = None

def load_config() -> Dict[str, Any]:
    """Load agent configuration."""
    try:
        config_path = os.path.join(ai_agent_tools_path, "agent_config.json")
        with open(config_path, 'r') as f:
            return json.load(f)
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
            message.info(f"✅ AI agent initialized with profile: {profile}")
            print(f"🤖 AI agent ready! Profile: {profile}")
            if profile == "deepseek_assistant":
                print("🧠 Using DeepSeek R1 14B model via Ollama")
        else:
            message.error("❌ Failed to initialize AI agent")
    except Exception as e:
        message.error(f"❌ AI agent initialization error: {e}")
        print(f"Error details: {e}")

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
        print(f"🤖 Processing: {query}")
        message.info(f"🤖 AI agent processing: {query}")
        
        # Create a streaming callback to show real-time progress
        def streaming_callback(update_type: str, content: str, **kwargs):
            """Callback to handle streaming updates from the AI agent."""
            if update_type == "thinking":
                print(f"\n🧠 REASONING:")
                print(f"   {content}")
                print()  # Add spacing
            elif update_type == "tool_call":
                tool_name = kwargs.get('tool_name', 'unknown')
                params = kwargs.get('parameters', {})
                print(f"🔧 Executing: {tool_name}")
                if params:
                    print(f"   Parameters: {params}")
            elif update_type == "tool_result":
                tool_name = kwargs.get('tool_name', 'unknown')
                success = kwargs.get('success', False)
                result = kwargs.get('result', '')
                status = "✅" if success else "❌"
                print(f"{status} {tool_name}: {result}")
            elif update_type == "progress":
                print(f"📊 {content}")
            elif update_type == "error":
                print(f"❌ Error: {content}")
        
        # Run async query with streaming
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create a task that can be monitored
        async def process_with_streaming():
            try:
                # Import and use the streaming wrapper
                from .streaming_agent import create_streaming_agent
                
                # Create streaming wrapper
                streaming_agent = create_streaming_agent(ai_agent)
                streaming_agent.set_streaming_callback(streaming_callback)
                
                # Process with streaming
                response = await streaming_agent.process_query_with_streaming(query)
                
                return response
                
            except Exception as e:
                print(f"❌ Processing error: {e}")
                raise
        
        response = loop.run_until_complete(process_with_streaming())
        loop.close()
        
        # Final status message
        if response.get("success"):
            message.info(f"✅ AI agent: {response['message']}")
            print(f"\n🎉 Task completed successfully!")
        else:
            error_msg = response.get('error', 'Unknown error')
            message.error(f"❌ AI agent error: {error_msg}")
            print(f"\n💥 Task failed: {error_msg}")
            
    except Exception as e:
        error_msg = f"Error processing query: {e}"
        message.error(f"❌ {error_msg}")
        print(f"❌ {error_msg}")

@cmdutils.register(scope='global')
def ai_agent_status():
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
