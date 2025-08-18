"""
Interactive Agent Interface for Qutebrowser

This module provides an easy-to-use interface for interacting with the AI browser agent
from within qutebrowser. It includes both programmatic and command-line interfaces.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/agent_interface.py
"""

import json
import os
import asyncio
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig, create_ai_agent
    from browser_control_tools import BrowserControlTools
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI agent not available: {e}")
    AGENT_AVAILABLE = False

try:
    from qutebrowser.utils import message, objreg
    from qutebrowser.api import cmdutils
    QUTEBROWSER_AVAILABLE = True
except ImportError:
    QUTEBROWSER_AVAILABLE = False


class AgentInterface:
    """Interactive interface for the AI browser agent."""
    
    def __init__(self):
        """Initialize the agent interface."""
        self.agent = None
        self.config = self._load_config()
        self.current_profile = "default"
        self.conversation_log = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "agent_config.json")
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Could not load agent config: {e}")
            return {"agent_profiles": {"default": {}}}
    
    def initialize_agent(self, profile: str = "default", 
                        api_key: str = None, window_id: int = 0) -> bool:
        """Initialize the AI agent with specified profile.
        
        Args:
            profile: Agent profile name from config
            api_key: API key for LLM provider (optional)
            window_id: Qutebrowser window ID
            
        Returns:
            True if successful, False otherwise
        """
        if not AGENT_AVAILABLE:
            print("❌ AI agent components not available")
            return False
        
        try:
            profile_config = self.config["agent_profiles"].get(profile, {})
            if not profile_config:
                print(f"❌ Unknown profile: {profile}")
                return False
            
            # Create agent config
            agent_config = AgentConfig(
                llm_provider=profile_config.get("llm_provider", "openai"),
                model=profile_config.get("model", "gpt-4"),
                api_key=api_key,
                api_base=profile_config.get("api_base"),
                temperature=profile_config.get("temperature", 0.1),
                max_tokens=profile_config.get("max_tokens", 1500),
                timeout=profile_config.get("timeout", 30),
                max_tool_calls=profile_config.get("max_tool_calls", 10),
                debug=False
            )
            
            self.agent = AIBrowserAgent(agent_config, window_id)
            self.current_profile = profile
            
            print(f"✅ AI agent initialized with profile: {profile}")
            print(f"   Provider: {agent_config.llm_provider}")
            print(f"   Model: {agent_config.model}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    async def ask(self, query: str) -> Dict[str, Any]:
        """Ask the AI agent a question and get a response.
        
        Args:
            query: Natural language query
            
        Returns:
            Response dictionary with results
        """
        if not self.agent:
            return {"error": "Agent not initialized. Call initialize_agent() first."}
        
        try:
            print(f"\n🤖 Processing: {query}")
            
            # Get response from agent
            response = await self.agent.process_query(query)
            
            # Log conversation
            self.conversation_log.append({
                "timestamp": response.timestamp,
                "query": query,
                "response": response.message,
                "tool_calls": len(response.tool_calls),
                "success": response.success
            })
            
            # Print response
            if response.success:
                print(f"✅ Response: {response.message}")
                if response.tool_calls:
                    print(f"🔧 Executed {len(response.tool_calls)} tool(s):")
                    for i, tool_call in enumerate(response.tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        print(f"   {i}. {tool_name}: {params}")
                    
                    # Show execution results
                    successful = sum(1 for r in response.execution_results if r.success)
                    total = len(response.execution_results)
                    print(f"📊 Results: {successful}/{total} successful")
            else:
                print(f"❌ Error: {response.error}")
            
            return {
                "success": response.success,
                "message": response.message,
                "tool_calls": response.tool_calls,
                "execution_results": [r.__dict__ for r in response.execution_results],
                "error": response.error
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def list_profiles(self) -> List[str]:
        """List available agent profiles."""
        profiles = list(self.config["agent_profiles"].keys())
        print("📋 Available profiles:")
        for profile in profiles:
            profile_info = self.config["agent_profiles"][profile]
            current = " (current)" if profile == self.current_profile else ""
            print(f"   • {profile}: {profile_info.get('description', 'No description')}{current}")
        return profiles
    
    def get_profile_info(self, profile: str) -> Dict[str, Any]:
        """Get detailed information about a profile."""
        profile_info = self.config["agent_profiles"].get(profile, {})
        if profile_info:
            print(f"📝 Profile: {profile}")
            print(f"   Name: {profile_info.get('name', 'Unknown')}")
            print(f"   Description: {profile_info.get('description', 'No description')}")
            print(f"   Provider: {profile_info.get('llm_provider', 'Unknown')}")
            print(f"   Model: {profile_info.get('model', 'Unknown')}")
            print(f"   Capabilities: {', '.join(profile_info.get('capabilities', []))}")
        else:
            print(f"❌ Profile '{profile}' not found")
        return profile_info
    
    def list_providers(self) -> List[str]:
        """List available LLM providers."""
        providers = list(self.config["llm_providers"].keys())
        print("🤖 Available LLM providers:")
        for provider in providers:
            provider_info = self.config["llm_providers"][provider]
            print(f"   • {provider}: {provider_info.get('description', 'No description')}")
            print(f"     Models: {', '.join(provider_info.get('supported_models', []))}")
            print(f"     API Key required: {provider_info.get('requires_api_key', 'Unknown')}")
        return providers
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        print(f"💬 Conversation history ({len(self.conversation_log)} entries):")
        for i, entry in enumerate(self.conversation_log[-10:], 1):  # Show last 10
            status = "✅" if entry["success"] else "❌"
            print(f"   {i}. {status} {entry['query'][:50]}...")
            print(f"      Response: {entry['response'][:50]}...")
            print(f"      Tools used: {entry['tool_calls']}")
        return self.conversation_log
    
    def clear_history(self):
        """Clear conversation history."""
        if self.agent:
            self.agent.clear_history()
        self.conversation_log = []
        print("🗑️ Conversation history cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        status = {
            "agent_initialized": self.agent is not None,
            "current_profile": self.current_profile,
            "conversation_entries": len(self.conversation_log),
            "available_profiles": len(self.config["agent_profiles"]),
            "available_providers": len(self.config["llm_providers"])
        }
        
        if self.agent:
            status.update({
                "llm_provider": self.agent.config.llm_provider,
                "model": self.agent.config.model,
                "available_tools": len(self.agent.get_available_tools())
            })
        
        print("📊 Agent Status:")
        for key, value in status.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        return status
    
    def help(self):
        """Show help information."""
        print("""
🤖 AI Browser Agent Interface Help

=== Quick Start ===
1. agent.initialize_agent(profile="default", api_key="your-key")
2. await agent.ask("your question here")

=== Main Commands ===
• initialize_agent(profile, api_key, window_id) - Initialize AI agent
• ask(query) - Ask the agent to perform a task
• list_profiles() - Show available agent profiles  
• list_providers() - Show available LLM providers
• get_status() - Show current agent status
• get_conversation_history() - View conversation log
• clear_history() - Clear conversation history
• help() - Show this help

=== Example Usage ===
# Initialize with OpenAI GPT-4
agent.initialize_agent("default", api_key="sk-...")

# Basic navigation
await agent.ask("Open https://example.com")
await agent.ask("Go back to the previous page")

# Tab management  
await agent.ask("Open GitHub in a new tab")
await agent.ask("Close the current tab")

# Page interaction
await agent.ask("Scroll down to see more content")
await agent.ask("Search for 'documentation' on this page")

# Complex tasks
await agent.ask("Fill out the login form with my credentials")
await agent.ask("Find the pricing section and take a screenshot")

=== Available Profiles ===
• default - General-purpose assistant (GPT-4)
• research_assistant - Research and analysis (Claude)
• automation_expert - Workflow automation (GPT-4)
• local_assistant - Privacy-focused (Ollama)
• quick_helper - Fast responses (GPT-3.5)

=== LLM Providers ===
• openai - OpenAI GPT models (requires API key)
• anthropic - Claude models (requires API key)  
• ollama - Local models (requires Ollama server)

=== Tips ===
• Set API keys as environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY)
• Use specific, clear requests for best results
• The agent can handle complex multi-step tasks
• Check conversation history to review past interactions
        """)


# Global interface instance
agent_interface = AgentInterface()

# Convenience functions for easy access
def init_agent(profile: str = "default", api_key: str = None, window_id: int = 0) -> bool:
    """Initialize the AI agent (convenience function)."""
    return agent_interface.initialize_agent(profile, api_key, window_id)

async def ask_agent(query: str) -> Dict[str, Any]:
    """Ask the AI agent a question (convenience function)."""
    return await agent_interface.ask(query)

def agent_status() -> Dict[str, Any]:
    """Get agent status (convenience function)."""
    return agent_interface.get_status()

def agent_help():
    """Show agent help (convenience function)."""
    agent_interface.help()

def list_agent_profiles() -> List[str]:
    """List available profiles (convenience function)."""
    return agent_interface.list_profiles()


# Qutebrowser command integration
if QUTEBROWSER_AVAILABLE:
    
    @cmdutils.register(instance='ai-agent', scope='global')
    def ai_agent_init(profile: str = "default", api_key: str = None):
        """Initialize AI browser agent.
        
        Args:
            profile: Agent profile to use
            api_key: API key for LLM provider
        """
        try:
            success = agent_interface.initialize_agent(profile, api_key)
            if success:
                message.info(f"AI agent initialized with profile: {profile}")
            else:
                message.error("Failed to initialize AI agent")
        except Exception as e:
            message.error(f"AI agent initialization error: {e}")
    
    @cmdutils.register(instance='ai-agent', scope='global')
    def ai_agent_ask(query: str):
        """Ask the AI agent to perform a browser task.
        
        Args:
            query: Natural language query
        """
        if not agent_interface.agent:
            message.error("AI agent not initialized. Use :ai-agent-init first")
            return
        
        try:
            # Run async query in event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(agent_interface.ask(query))
            loop.close()
            
            if response.get("success"):
                message.info(f"AI agent: {response['message']}")
            else:
                message.error(f"AI agent error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            message.error(f"AI agent query error: {e}")
    
    @cmdutils.register(instance='ai-agent', scope='global')
    def ai_agent_status():
        """Show AI agent status."""
        try:
            agent_interface.get_status()
            message.info("AI agent status displayed in console")
        except Exception as e:
            message.error(f"AI agent status error: {e}")


# Main interface setup for qutebrowser
if __name__ == "__main__" or True:  # Always run when imported
    print("🤖 AI Browser Agent Interface Loaded!")
    print("=" * 50)
    
    if AGENT_AVAILABLE:
        print("✅ AI agent components available")
    else:
        print("❌ AI agent components not available")
        print("   Install required packages: pip install openai anthropic requests")
    
    if QUTEBROWSER_AVAILABLE:
        print("✅ Qutebrowser integration available")
        print("   Commands: :ai-agent-init, :ai-agent-ask, :ai-agent-status")
    else:
        print("⚠️  Not running in qutebrowser")
    
    print("\n📖 Quick Start:")
    print("1. agent = agent_interface")
    print("2. agent.initialize_agent('default', api_key='your-key')")
    print("3. await agent.ask('your question')")
    print("\n💡 Type agent.help() for full documentation")
    print("=" * 50)
    
    # Make interface available globally
    globals()['agent'] = agent_interface
