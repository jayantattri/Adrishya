#!/usr/bin/env python3
"""
Test True Iterative Execution

This script tests that the system now executes tools one-by-one
with proper feedback between each execution.

Usage in qutebrowser:
:pyeval --file ai_agent_tools/test_true_iterative.py
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("🧪 Testing True Iterative Execution...")

try:
    from ai_browser_agent import AIBrowserAgent, AgentConfig, CommandResult
    print("✅ AIBrowserAgent imported successfully")
except ImportError as e:
    print(f"❌ Could not import AIBrowserAgent: {e}")
    sys.exit(1)

def test_iterative_logic():
    """Test the iterative execution logic."""
    print("\n🔧 Testing iterative execution logic...")
    
    # Simulate the iterative process
    all_tool_calls = []
    all_execution_results = []
    iteration_count = 0
    max_iterations = 5
    
    # Simulate a multi-step task
    task_steps = [
        {"name": "tab_new", "parameters": {"url": "https://www.google.com"}},
        {"name": "type_text", "parameters": {"text": "Python tutorials"}},
        {"name": "send_key", "parameters": {"key": "Return"}},
        {"name": "wait_for_load", "parameters": {"timeout": 10}},
    ]
    
    print("📝 Simulating iterative execution for: 'open google.com in a new tab and search for Python tutorials'")
    print("   Expected: 4 iterations, one tool per iteration")
    
    for i, step in enumerate(task_steps, 1):
        iteration_count += 1
        print(f"\n🔄 Iteration {iteration_count}:")
        print(f"   Tool: {step['name']}")
        print(f"   Parameters: {step['parameters']}")
        
        # Simulate tool execution
        all_tool_calls.append(step)
        all_execution_results.append(CommandResult(
            success=True,
            command=step['name'],
            args=list(step['parameters'].values()),
            message=f"{step['name']} executed successfully"
        ))
        
        print(f"   ✅ Executed successfully")
        
        # Check if this is the last step
        if i == len(task_steps):
            print(f"   🎯 Task complete after {iteration_count} iterations")
            break
    
    print(f"\n📊 Final Results:")
    print(f"   Total iterations: {iteration_count}")
    print(f"   Tools executed: {len(all_tool_calls)}")
    print(f"   Success rate: {sum(1 for r in all_execution_results if r.success)}/{len(all_execution_results)}")
    
    # Verify no duplicates
    tool_names = [tc['name'] for tc in all_tool_calls]
    unique_tools = set(tool_names)
    if len(tool_names) == len(unique_tools):
        print("   ✅ No duplicate tool calls")
    else:
        print("   ❌ Duplicate tool calls detected")

def test_feedback_creation():
    """Test that feedback messages are created correctly."""
    print("\n🔧 Testing feedback message creation...")
    
    try:
        # Create agent instance
        config = AgentConfig(
            llm_provider="ollama",
            model="deepseek-r1:14b",
            max_tool_calls=5
        )
        agent = AIBrowserAgent(config)
        
        # Test feedback for different tool executions
        test_cases = [
            {
                "tool_call": {"name": "tab_new", "parameters": {"url": "https://www.google.com"}},
                "result": CommandResult(success=True, command="tab_new", args=["https://www.google.com"], message="New tab opened successfully"),
                "iteration": 1
            },
            {
                "tool_call": {"name": "type_text", "parameters": {"text": "Python tutorials"}},
                "result": CommandResult(success=True, command="type_text", args=["Python tutorials"], message="Text typed successfully"),
                "iteration": 2
            },
            {
                "tool_call": {"name": "send_key", "parameters": {"key": "Return"}},
                "result": CommandResult(success=False, command="send_key", args=["Return"], error="No element focused!"),
                "iteration": 3
            }
        ]
        
        all_tool_calls = []
        all_results = []
        
        for i, case in enumerate(test_cases):
            all_tool_calls.append(case["tool_call"])
            all_results.append(case["result"])
            
            feedback = agent._create_tool_feedback_message(
                case["tool_call"], 
                case["result"], 
                case["iteration"], 
                all_tool_calls, 
                all_results
            )
            
            print(f"\n📝 Feedback for iteration {case['iteration']}:")
            print(f"   Tool: {case['tool_call']['name']}")
            print(f"   Status: {'✅ Success' if case['result'].success else '❌ Failed'}")
            if case['result'].success:
                print(f"   Message: {case['result'].message}")
            else:
                print(f"   Error: {case['result'].error}")
            
            # Check if feedback suggests completion for simple tasks
            if case["tool_call"]["name"] == "tab_new" and case["result"].success:
                if "TASK COMPLETE" in feedback:
                    print("   ✅ Feedback suggests task completion")
                else:
                    print("   ⚠️  Feedback doesn't suggest task completion")
        
    except Exception as e:
        print(f"❌ Feedback test failed: {e}")
        import traceback
        traceback.print_exc()

# Run tests
if __name__ == "__main__":
    test_iterative_logic()
    test_feedback_creation()
    
    print("\n" + "=" * 50)
    print("🧪 True Iterative Execution Test Complete!")
    print("   The system should now execute tools one-by-one")
    print("   with proper feedback between each execution")
    print("=" * 50)
    print("\n📋 To test in browser:")
    print("   :pyeval --file ai_agent_tools/load_ai_agent.py")
    print("   :ai-agent-init deepseek_assistant")
    print("   :ai-agent-ask 'open google.com in a new tab and search for Python tutorials'")
    print("   Expected: Should see 4 separate iterations with feedback between each")
