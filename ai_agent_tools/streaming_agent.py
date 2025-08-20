"""
Streaming Agent Wrapper

This module provides a streaming wrapper for AI agents that can show real-time
updates in the terminal as the agent processes queries.
"""

import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StreamingUpdate:
    """Represents a streaming update from the AI agent."""
    update_type: str  # "thinking", "tool_call", "tool_result", "progress", "error"
    content: str
    metadata: Dict[str, Any] = None


class StreamingAgentWrapper:
    """Wrapper that adds streaming capabilities to any AI agent."""
    
    def __init__(self, agent):
        """Initialize the streaming wrapper with an AI agent.
        
        Args:
            agent: The AI agent to wrap with streaming capabilities
        """
        self.agent = agent
        self.streaming_callback = None
    
    def set_streaming_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]):
        """Set the streaming callback function.
        
        Args:
            callback: Function to call with streaming updates
                Signature: callback(update_type, content, **kwargs)
        """
        self.streaming_callback = callback
    
    async def process_query_with_streaming(self, query: str) -> Dict[str, Any]:
        """Process a query with real-time streaming updates.
        
        Args:
            query: The user's query string
            
        Returns:
            Response dictionary with results
        """
        if not self.streaming_callback:
            # Fall back to regular processing
            return await self._process_regular(query)
        
        try:
            # Start streaming
            self.streaming_callback("progress", "Starting AI analysis...")
            
            # Check if agent supports streaming
            if hasattr(self.agent, 'process_query_with_streaming'):
                # Use agent's built-in streaming
                self.agent.set_streaming_callback(self.streaming_callback)
                response = await self.agent.process_query_with_streaming(query)
            else:
                # Use our wrapper streaming
                response = await self._process_with_wrapper_streaming(query)
            
            # Final success message
            self.streaming_callback("progress", "Task completed successfully!")
            
            return response
            
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            self.streaming_callback("error", error_msg)
            return {"success": False, "error": error_msg}
    
    async def _process_regular(self, query: str) -> Dict[str, Any]:
        """Process query using the regular agent method."""
        if hasattr(self.agent, 'process_query'):
            response = await self.agent.process_query(query)
            return self._format_response(response)
        elif hasattr(self.agent, 'ask'):
            response = await self.agent.ask(query)
            return response
        else:
            raise NotImplementedError("Agent does not support query processing")
    
    async def _process_with_wrapper_streaming(self, query: str) -> Dict[str, Any]:
        """Process query with wrapper-provided streaming."""
        try:
            # Show initial progress
            self.streaming_callback("progress", "Analyzing query...")
            
            # Process the query
            response = await self._process_regular(query)
            
            # Stream the response details
            if response.get("success"):
                # Show reasoning if available
                if hasattr(response, 'thinking') and response.thinking:
                    self.streaming_callback("thinking", response.thinking)
                
                # Show tool calls if available
                tool_calls = response.get("tool_calls", [])
                if tool_calls:
                    self.streaming_callback("progress", f"Executed {len(tool_calls)} tools")
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.get("name", "unknown")
                        params = tool_call.get("parameters", {})
                        self.streaming_callback("tool_call", f"Tool {i}: {tool_name}", 
                                             tool_name=tool_name, parameters=params)
                
                # Show execution results if available
                if hasattr(response, 'execution_results') and response.execution_results:
                    successful = sum(1 for r in response.execution_results if r.success)
                    total = len(response.execution_results)
                    self.streaming_callback("progress", f"Results: {successful}/{total} successful")
            
            return response
            
        except Exception as e:
            self.streaming_callback("error", f"Processing failed: {str(e)}")
            raise
    
    def _format_response(self, response) -> Dict[str, Any]:
        """Format the agent response into a standard dictionary."""
        if hasattr(response, '__dict__'):
            # Convert object to dict
            return {
                "success": getattr(response, 'success', True),
                "message": getattr(response, 'message', ''),
                "thinking": getattr(response, 'thinking', None),
                "tool_calls": getattr(response, 'tool_calls', []),
                "execution_results": getattr(response, 'execution_results', []),
                "error": getattr(response, 'error', None),
                "execution_stats": getattr(response, 'execution_stats', {})
            }
        elif isinstance(response, dict):
            return response
        else:
            return {"success": True, "message": str(response)}


def create_streaming_agent(agent) -> StreamingAgentWrapper:
    """Create a streaming wrapper for an AI agent.
    
    Args:
        agent: The AI agent to wrap
        
    Returns:
        StreamingAgentWrapper instance
    """
    return StreamingAgentWrapper(agent)
