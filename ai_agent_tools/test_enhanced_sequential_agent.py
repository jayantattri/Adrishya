"""
Test script for the Enhanced Sequential AI Agent

This script demonstrates the improved sequential execution handling and state management
that prevents tool execution loops and provides better feedback.
"""

import asyncio
import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_sequential_agent import (
    EnhancedSequentialAgent, 
    SequentialAgentConfig, 
    create_enhanced_sequential_agent
)


async def test_enhanced_sequential_agent():
    """Test the enhanced sequential agent with various scenarios."""
    
    print("🚀 Testing Enhanced Sequential AI Agent")
    print("=" * 50)
    
    # Create agent configuration
    config = SequentialAgentConfig(
        llm_provider="ollama",
        model="deepseek-r1:14b",
        debug=True,
        max_tool_calls=8,
        enable_loop_prevention=True,
        enable_state_tracking=True
    )
    
    # Create agent
    agent = create_enhanced_sequential_agent(config)
    
    print(f"✅ Agent created with configuration:")
    print(f"   - LLM Provider: {config.llm_provider}")
    print(f"   - Model: {config.model}")
    print(f"   - Max Tool Calls: {config.max_tool_calls}")
    print(f"   - Loop Prevention: {config.enable_loop_prevention}")
    print(f"   - State Tracking: {config.enable_state_tracking}")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Simple Navigation",
            "query": "open google.com",
            "expected_tools": ["open_url"],
            "description": "Basic URL navigation test"
        },
        {
            "name": "Search Task",
            "query": "open google.com and search for Python tutorials",
            "expected_tools": ["open_url", "type_text", "send_key"],
            "description": "Multi-step search task"
        },
        {
            "name": "Tab Management",
            "query": "open youtube.com in a new tab",
            "expected_tools": ["tab_new", "open_url"],
            "description": "Tab creation and navigation"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Query: '{scenario['query']}'")
        print(f"   Expected tools: {scenario['expected_tools']}")
        print()
        
        try:
            # Process the query
            print("   🔄 Processing query...")
            response = await agent.process_query(scenario['query'])
            
            # Display results
            print(f"   ✅ Success: {response.success}")
            print(f"   📝 Message: {response.message}")
            print(f"   🔧 Tools executed: {len(response.tool_calls)}")
            
            if response.tool_calls:
                print("   📋 Tool execution details:")
                for j, tool_call in enumerate(response.tool_calls, 1):
                    tool_name = tool_call.get('name', 'unknown')
                    parameters = tool_call.get('parameters', {})
                    result = response.execution_results[j-1] if j <= len(response.execution_results) else None
                    
                    status = "✅" if result and result.success else "❌"
                    print(f"      {j}. {tool_name}: {status}")
                    print(f"         Parameters: {parameters}")
                    if result:
                        if result.success and result.message:
                            print(f"         Result: {result.message}")
                        elif not result.success and result.error:
                            print(f"         Error: {result.error}")
            
            # Display execution statistics
            if response.execution_stats:
                stats = response.execution_stats
                print(f"   📊 Execution Statistics:")
                print(f"      - Total iterations: {stats.get('total_iterations', 0)}")
                print(f"      - Total tools executed: {stats.get('total_tools_executed', 0)}")
                print(f"      - Successful tools: {stats.get('successful_tools', 0)}")
                print(f"      - Failed tools: {stats.get('failed_tools', 0)}")
                print(f"      - Execution time: {stats.get('execution_time', 0):.2f}s")
                print(f"      - Task completed: {stats.get('task_completed', False)}")
            
            if response.error:
                print(f"   ❌ Error: {response.error}")
            
            if response.thinking:
                print(f"   🧠 Reasoning: {response.thinking}")
            
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
        
        print("-" * 50)
        print()


async def test_loop_prevention():
    """Test the loop prevention mechanism."""
    
    print("🔄 Testing Loop Prevention Mechanism")
    print("=" * 50)
    
    config = SequentialAgentConfig(
        llm_provider="ollama",
        model="deepseek-r1:14b",
        debug=True,
        max_tool_calls=5,
        enable_loop_prevention=True
    )
    
    agent = create_enhanced_sequential_agent(config)
    
    # Test a query that might cause loops
    problematic_query = "open google.com open google.com open google.com"
    
    print(f"🧪 Testing loop prevention with query: '{problematic_query}'")
    print("   This query might cause the agent to try opening Google multiple times.")
    print()
    
    try:
        response = await agent.process_query(problematic_query)
        
        print(f"✅ Success: {response.success}")
        print(f"📝 Message: {response.message}")
        print(f"🔧 Tools executed: {len(response.tool_calls)}")
        
        # Check if loop prevention worked
        unique_tools = set()
        for tool_call in response.tool_calls:
            tool_name = tool_call.get('name', 'unknown')
            parameters = tool_call.get('parameters', {})
            signature = f"{tool_name}:{str(parameters)}"
            unique_tools.add(signature)
        
        print(f"🔄 Unique tool signatures: {len(unique_tools)}")
        print(f"📊 Total tool calls: {len(response.tool_calls)}")
        
        if len(unique_tools) == len(response.tool_calls):
            print("✅ Loop prevention working correctly - no duplicate tool calls detected")
        else:
            print("⚠️  Potential loop detected - some tool calls were duplicated")
        
        if response.execution_stats:
            stats = response.execution_stats
            print(f"📊 Execution Statistics:")
            print(f"   - Iterations: {stats.get('total_iterations', 0)}")
            print(f"   - Task completed: {stats.get('task_completed', False)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("-" * 50)
    print()


async def test_error_recovery():
    """Test error recovery and handling."""
    
    print("🛠️  Testing Error Recovery and Handling")
    print("=" * 50)
    
    config = SequentialAgentConfig(
        llm_provider="ollama",
        model="deepseek-r1:14b",
        debug=True,
        max_tool_calls=5
    )
    
    agent = create_enhanced_sequential_agent(config)
    
    # Test with a query that might cause errors
    error_prone_query = "open invalid-url-that-does-not-exist.com"
    
    print(f"🧪 Testing error recovery with query: '{error_prone_query}'")
    print("   This query should trigger error handling mechanisms.")
    print()
    
    try:
        response = await agent.process_query(error_prone_query)
        
        print(f"✅ Success: {response.success}")
        print(f"📝 Message: {response.message}")
        print(f"🔧 Tools executed: {len(response.tool_calls)}")
        
        if response.error:
            print(f"❌ Error captured: {response.error}")
        
        if response.execution_results:
            print("📋 Tool execution results:")
            for i, result in enumerate(response.execution_results, 1):
                status = "✅" if result.success else "❌"
                print(f"   {i}. {result.command}: {status}")
                if not result.success and result.error:
                    print(f"      Error: {result.error}")
        
        if response.execution_stats:
            stats = response.execution_stats
            print(f"📊 Execution Statistics:")
            print(f"   - Failed tools: {stats.get('failed_tools', 0)}")
            print(f"   - Successful tools: {stats.get('successful_tools', 0)}")
            print(f"   - Task completed: {stats.get('task_completed', False)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("-" * 50)
    print()


async def main():
    """Run all tests."""
    
    print("🧪 Enhanced Sequential AI Agent Test Suite")
    print("=" * 60)
    print()
    
    # Run basic functionality tests
    await test_enhanced_sequential_agent()
    
    # Run loop prevention tests
    await test_loop_prevention()
    
    # Run error recovery tests
    await test_error_recovery()
    
    print("🎉 All tests completed!")
    print()
    print("📋 Summary of Improvements:")
    print("   ✅ True sequential tool execution (one tool at a time)")
    print("   ✅ Enhanced state tracking and loop prevention")
    print("   ✅ Better error handling and recovery")
    print("   ✅ Improved feedback mechanisms")
    print("   ✅ Comprehensive logging and debugging")
    print("   ✅ Execution statistics and monitoring")
    print()
    print("🚀 The enhanced agent should now handle complex multi-step tasks")
    print("   without getting stuck in tool execution loops!")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
