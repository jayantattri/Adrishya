#!/usr/bin/env python3
"""
Test script for AI Agent Streaming

This script demonstrates how the AI agent streaming works in real-time.
Run this to see the streaming output in action.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from streaming_agent import create_streaming_agent


def streaming_callback(update_type: str, content: str, **kwargs):
    """Callback function to handle streaming updates."""
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


class MockAgent:
    """Mock AI agent for testing streaming functionality."""
    
    async def process_query(self, query: str):
        """Mock process_query method that simulates AI processing."""
        import time
        
        # Simulate thinking
        await asyncio.sleep(1)
        
        # Simulate tool execution
        await asyncio.sleep(0.5)
        
        # Return mock response
        return MockResponse(
            success=True,
            message=f"Successfully processed: {query}",
            thinking="This is a mock reasoning process that shows how streaming works.",
            tool_calls=[
                {"name": "navigate", "parameters": {"url": "https://example.com"}},
                {"name": "click", "parameters": {"selector": "button"}}
            ],
            execution_results=[
                MockResult(success=True, message="Navigation successful"),
                MockResult(success=True, message="Click successful")
            ]
        )


class MockResponse:
    """Mock response object."""
    
    def __init__(self, success, message, thinking=None, tool_calls=None, execution_results=None):
        self.success = success
        self.message = message
        self.thinking = thinking
        self.tool_calls = tool_calls or []
        self.execution_results = execution_results or []


class MockResult:
    """Mock execution result."""
    
    def __init__(self, success, message):
        self.success = success
        self.message = message


async def test_streaming():
    """Test the streaming functionality."""
    print("🤖 Testing AI Agent Streaming")
    print("=" * 40)
    
    # Create mock agent
    mock_agent = MockAgent()
    
    # Create streaming wrapper
    streaming_agent = create_streaming_agent(mock_agent)
    streaming_agent.set_streaming_callback(streaming_callback)
    
    # Test query
    query = "Open example.com and click the first button"
    
    print(f"Query: {query}")
    print("-" * 40)
    
    # Process with streaming
    response = await streaming_agent.process_query_with_streaming(query)
    
    print("-" * 40)
    print(f"Final Result: {response['message']}")
    print("✅ Streaming test completed!")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_streaming())
