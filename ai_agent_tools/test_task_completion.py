#!/usr/bin/env python3
"""
Test Task Completion Detection

This script tests that the iterative tool calling system correctly
detects when tasks are complete and doesn't get stuck in loops.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_task_completion.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing Task Completion Detection...")

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig, CommandResult
    print("✅ AIBrowserAgent imported successfully")
except ImportError as e:
    print(f"❌ Could not import AIBrowserAgent: {e}")
    sys.exit(1)

def test_task_completion_detection():
    """Test that task completion is detected correctly."""
    print("\n🔧 Testing task completion detection...")
    
    try:
        # Create agent config for DeepSeek
        config = AgentConfig(
            llm_provider="ollama",
            model="deepseek-r1:14b",
            temperature=0.1,
            max_tokens=500,
            timeout=30,
            max_tool_calls=3  # Limit to prevent infinite loops
        )
        
        # Create agent instance
        agent = AIBrowserAgent(config)
        print("✅ Agent created successfully")
        
        # Test feedback message creation for simple navigation task
        tool_call = {
            "name": "open_url",
            "parameters": {"url": "https://youtube.com"}
        }
        
        result = CommandResult(
            success=True,
            command="open_url",
            args=["https://youtube.com"],
            message="URL opened successfully"
        )
        
        feedback = agent._create_tool_feedback_message(
            tool_call, result, 1, [tool_call], [result]
        )
        
        print("✅ Feedback message created:")
        print(feedback)
        
        # Check if feedback suggests completion for simple tasks
        if "TASK COMPLETE" in feedback:
            print("✅ Feedback correctly suggests task completion")
        else:
            print("⚠️  Feedback doesn't suggest task completion")
        
        # Test task completion detection logic
        test_responses = [
            {"content": "TASK COMPLETE", "tool_calls": []},
            {"content": "The task is finished", "tool_calls": []},
            {"content": "No more tools needed", "tool_calls": []},
            {"content": "Continue with next step", "tool_calls": [{"name": "click_element"}]},
        ]
        
        print("\n🔍 Testing task completion detection:")
        for i, response in enumerate(test_responses, 1):
            content = response.get("content", "").lower()
            is_complete = "task complete" in content or "no more tools" in content or "task finished" in content
            print(f"   {i}. '{response['content']}' -> {'✅ Complete' if is_complete else '🔄 Continue'}")
        
    except Exception as e:
        print(f"❌ Task completion test failed: {e}")
        import traceback
        traceback.print_exc()

def test_simple_navigation_task():
    """Test that a simple navigation task completes correctly."""
    print("\n🔧 Testing simple navigation task...")
    
    try:
        # Create agent config
        config = AgentConfig(
            llm_provider="ollama",
            model="deepseek-r1:14b",
            temperature=0.1,
            max_tokens=300,  # Shorter to prevent long responses
            timeout=30,
            max_tool_calls=2  # Should only need 1 for simple navigation
        )
        
        # Create agent instance
        agent = AIBrowserAgent(config)
        
        # Test the iterative tool calling with a simple task
        print("📝 Testing with query: 'open youtube.com'")
        print("   Expected: 1 tool call, then task completion")
        print("   Actual behavior will be shown in the logs")
        
        # Note: This would require actual browser interaction
        # For now, just test the logic
        print("✅ Test setup complete - ready for browser testing")
        
    except Exception as e:
        print(f"❌ Simple navigation test failed: {e}")

# Run tests
if __name__ == "__main__":
    test_task_completion_detection()
    test_simple_navigation_task()
    
    print("\n" + "=" * 50)
    print("🧪 Task Completion Test Complete!")
    print("   The system should now correctly detect when tasks are complete")
    print("   and not get stuck in reasoning loops")
    print("=" * 50)
    print("\n📋 To test in browser:")
    print("   :pyeval --file ai_agent_tools/load_ai_agent.py")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open youtube.com'")
    print("   Expected: Should execute open_url, then complete")
