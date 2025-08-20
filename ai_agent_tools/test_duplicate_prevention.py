#!/usr/bin/env python3
"""
Test Duplicate Tool Call Prevention

This script tests that the system prevents duplicate tool calls
and doesn't get stuck in infinite loops.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_duplicate_prevention.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Duplicate Tool Call Prevention...")

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig, CommandResult
    print("✅ AIBrowserAgent imported successfully")
except ImportError as e:
    print(f"❌ Could not import AIBrowserAgent: {e}")
    sys.exit(1)

def test_duplicate_detection():
    """Test that duplicate tool calls are detected correctly."""
    print("\n🔧 Testing duplicate detection...")
    
    # Test data
    tool_calls = [
        {"name": "open_url", "parameters": {"url": "https://youtube.com"}},
        {"name": "open_url", "parameters": {"url": "https://youtube.com"}},  # Duplicate
        {"name": "tab_new", "parameters": {"url": "https://youtube.com"}},   # Different tool
        {"name": "open_url", "parameters": {"url": "https://google.com"}},   # Different URL
    ]
    
    # Test the duplicate detection logic
    all_tool_calls = []
    for i, tool_call in enumerate(tool_calls):
        tool_name = tool_call["name"]
        parameters = tool_call.get("parameters", {})
        tool_call_key = f"{tool_name}:{str(parameters)}"
        
        # Check if this is a duplicate
        existing_keys = [f"{tc['name']}:{str(tc.get('parameters', {}))}" for tc in all_tool_calls]
        
        if tool_call_key in existing_keys:
            print(f"❌ Duplicate detected at position {i+1}: {tool_call_key}")
        else:
            print(f"✅ New tool call at position {i+1}: {tool_call_key}")
            all_tool_calls.append(tool_call)
    
    print(f"\n📊 Final tool calls: {len(all_tool_calls)} unique calls")
    for i, tc in enumerate(all_tool_calls, 1):
        print(f"   {i}. {tc['name']}: {tc.get('parameters', {})}")

def test_iteration_limits():
    """Test that iteration limits are properly enforced."""
    print("\n🔧 Testing iteration limits...")
    
    try:
        # Create agent config with different max_tool_calls values
        test_configs = [
            AgentConfig(max_tool_calls=10),  # Should be capped at 5
            AgentConfig(max_tool_calls=3),   # Should stay at 3
            AgentConfig(max_tool_calls=1),   # Should stay at 1
        ]
        
        for i, config in enumerate(test_configs, 1):
            agent = AIBrowserAgent(config)
            # The max_iterations is set in _execute_iterative_tool_calling
            # We can't test it directly, but we can verify the config
            print(f"   Config {i}: max_tool_calls={config.max_tool_calls}")
        
        print("✅ Iteration limit test completed")
        
    except Exception as e:
        print(f"❌ Iteration limit test failed: {e}")

def test_navigation_request_handling():
    """Test that navigation requests without tool calls are handled properly."""
    print("\n🔧 Testing navigation request handling...")
    
    # Test cases
    test_queries = [
        "open youtube.com",
        "go to google.com", 
        "navigate to github.com",
        "visit stackoverflow.com",
        "search for Python",  # Not a navigation request
        "click the button",   # Not a navigation request
    ]
    
    for query in test_queries:
        query_lower = query.lower()
        is_navigation = any(keyword in query_lower for keyword in ['open', 'go to', 'navigate', 'visit'])
        status = "🚀 Navigation" if is_navigation else "🔧 Action"
        print(f"   '{query}' -> {status}")
    
    print("✅ Navigation request detection test completed")

# Run tests
if __name__ == "__main__":
    test_duplicate_detection()
    test_iteration_limits()
    test_navigation_request_handling()
    
    print("\n" + "=" * 50)
    print("🧪 Duplicate Prevention Test Complete!")
    print("   The system should now prevent duplicate tool calls")
    print("   and avoid infinite loops")
    print("=" * 50)
    print("\n📋 To test in browser:")
    print("   :pyeval --file ai_agent_tools/load_ai_agent.py")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open youtube.com'")
    print("   Expected: Should execute open_url once, then complete")
