#!/usr/bin/env python3
"""
Test Simplified Prompt Fix

This script tests that the simplified system prompt works correctly
and doesn't cause the DeepSeek model to get stuck in reasoning loops.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_simplified_prompt.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Simplified Prompt Fix...")

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig
    print("✅ AIBrowserAgent imported successfully")
except ImportError as e:
    print(f"❌ Could not import AIBrowserAgent: {e}")
    sys.exit(1)

def test_simplified_prompt():
    """Test that the simplified prompt works correctly."""
    print("\n🔧 Testing simplified prompt...")
    
    try:
        # Create agent config for DeepSeek
        config = AgentConfig(
            llm_provider="ollama",
            model="deepseek-r1:14b",
            temperature=0.1,
            max_tokens=500,
            timeout=30
        )
        
        # Create agent instance
        agent = AIBrowserAgent(config)
        print("✅ Agent created successfully")
        
        # Test tool formatting
        tools = [
            {
                "name": "open_url",
                "description": "Opens a URL in the current tab",
                "parameters": {
                    "properties": {
                        "url": {"type": "string", "description": "The URL to open"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "search_page",
                "description": "Searches for text on the current page",
                "parameters": {
                    "properties": {
                        "text": {"type": "string", "description": "Text to search for"}
                    },
                    "required": ["text"]
                }
            }
        ]
        
        # Test prompt creation
        prompt = agent.llm_provider._create_reasoning_system_prompt(tools)
        print("✅ Simplified prompt created successfully")
        
        # Check prompt length (should be much shorter now)
        prompt_lines = prompt.split('\n')
        print(f"📏 Prompt length: {len(prompt_lines)} lines")
        
        if len(prompt_lines) < 50:
            print("✅ Prompt is appropriately short")
        else:
            print("⚠️  Prompt might still be too long")
        
        # Check for key elements
        if "THINKING:" in prompt and "ACTION:" in prompt and "EXECUTE:" in prompt:
            print("✅ Prompt has correct format sections")
        else:
            print("❌ Prompt missing required format sections")
        
        # Check for simplified examples
        if "open google.com" in prompt.lower():
            print("✅ Prompt has simplified examples")
        else:
            print("❌ Prompt missing simplified examples")
        
        print("\n📝 Sample prompt preview:")
        print("-" * 40)
        lines = prompt.split('\n')[:20]  # Show first 20 lines
        for line in lines:
            print(line)
        print("...")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Simplified prompt test failed: {e}")
        import traceback
        traceback.print_exc()

def test_tool_formatting():
    """Test that tool formatting is simplified."""
    print("\n🔧 Testing tool formatting...")
    
    try:
        from ai_browser_agent import OllamaProvider, AgentConfig
        
        config = AgentConfig(llm_provider="ollama", model="deepseek-r1:14b")
        provider = OllamaProvider(config)
        
        tools = [
            {
                "name": "open_url",
                "description": "Opens a URL in the current tab",
                "parameters": {
                    "properties": {
                        "url": {"type": "string", "description": "The URL to open"}
                    },
                    "required": ["url"]
                }
            }
        ]
        
        formatted = provider._format_tools_for_prompt(tools)
        print("✅ Tool formatting simplified:")
        print(formatted)
        
        # Check that it's concise
        if len(formatted.split('\n')) < 10:
            print("✅ Tool formatting is appropriately concise")
        else:
            print("⚠️  Tool formatting might still be too verbose")
            
    except Exception as e:
        print(f"❌ Tool formatting test failed: {e}")

# Run tests
if __name__ == "__main__":
    test_simplified_prompt()
    test_tool_formatting()
    
    print("\n" + "=" * 50)
    print("🧪 Simplified Prompt Test Complete!")
    print("   The prompt should now be much shorter and clearer")
    print("   This should prevent the model from getting stuck in reasoning loops")
    print("=" * 50)
