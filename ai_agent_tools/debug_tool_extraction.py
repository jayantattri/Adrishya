#!/usr/bin/env python3
"""
Debug Tool Extraction

This script helps debug why the tool extraction isn't working properly.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/debug_tool_extraction.py
"""

import sys
import os
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🐛 Debugging Tool Extraction...")

def test_tool_extraction():
    """Test the tool extraction logic with various response formats."""
    print("\n🔧 Testing tool extraction...")
    
    try:
        from ai_browser_agent import OllamaProvider, AgentConfig
        
        config = AgentConfig(llm_provider="ollama", model="deepseek-r1:14b")
        provider = OllamaProvider(config)
        
        # Test cases
        test_responses = [
            # Good response with tool call
            """THINKING: User wants to open YouTube in a new tab
ACTION: Open YouTube in a new tab using tab_new tool
EXECUTE:
TOOL_CALL: {"name": "tab_new", "parameters": {"url": "https://www.youtube.com"}}""",
            
            # Response without tool call (the problematic one)
            """THINKING: User wants to open YouTube in a new tab
ACTION: Open YouTube in a new tab using tab_new tool
EXECUTE:
[No tool call provided]""",
            
            # Response with malformed tool call
            """THINKING: User wants to open YouTube
ACTION: Open YouTube
EXECUTE:
TOOL_CALL: {"name": "open_url", "parameters": {"url": "https://youtube.com"}}""",
            
            # Response with multiple tool calls
            """THINKING: User wants to search for Python
ACTION: Open Google and search
EXECUTE:
TOOL_CALL: {"name": "open_url", "parameters": {"url": "https://www.google.com"}}
TOOL_CALL: {"name": "type_text", "parameters": {"text": "Python"}}""",
        ]
        
        for i, response in enumerate(test_responses, 1):
            print(f"\n📝 Test Case {i}:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            
            tool_calls = provider._extract_tool_calls_from_content(response)
            print(f"🔍 Extracted tool calls: {tool_calls}")
            
            if tool_calls:
                print("✅ Tool calls found!")
                for j, tool_call in enumerate(tool_calls, 1):
                    print(f"   {j}. {tool_call['name']}: {tool_call.get('parameters', {})}")
            else:
                print("❌ No tool calls found")
        
    except Exception as e:
        print(f"❌ Tool extraction test failed: {e}")
        import traceback
        traceback.print_exc()

def test_response_parsing():
    """Test parsing of different response formats."""
    print("\n🔧 Testing response parsing...")
    
    # Simulate the actual response format from the logs
    problematic_response = {
        "content": """THINKING: User wants to open YouTube in a new tab
ACTION: Open YouTube in a new tab using tab_new tool
EXECUTE:
[The model is thinking about JSON format but not providing the actual tool call]""",
        "tool_calls": [],
        "reasoning": "The model is overthinking the JSON format",
        "full_response": "Full response with reasoning loop"
    }
    
    print("📝 Problematic Response:")
    print("-" * 40)
    print(json.dumps(problematic_response, indent=2))
    print("-" * 40)
    
    # Test extraction
    try:
        from ai_browser_agent import OllamaProvider, AgentConfig
        
        config = AgentConfig(llm_provider="ollama", model="deepseek-r1:14b")
        provider = OllamaProvider(config)
        
        tool_calls = provider._extract_tool_calls_from_content(problematic_response["content"])
        print(f"🔍 Extracted tool calls: {tool_calls}")
        
        if not tool_calls:
            print("❌ No tool calls found - this explains the issue!")
            print("💡 The model is not providing the TOOL_CALL: line in the EXECUTE section")
        
    except Exception as e:
        print(f"❌ Response parsing test failed: {e}")

# Run tests
if __name__ == "__main__":
    test_tool_extraction()
    test_response_parsing()
    
    print("\n" + "=" * 50)
    print("🐛 Debug Complete!")
    print("   This should help identify why tool extraction is failing")
    print("=" * 50)
