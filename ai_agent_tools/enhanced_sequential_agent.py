"""
Enhanced Sequential AI Agent for Qutebrowser

This module implements an improved AI browser assistant with better sequential execution
handling and state management to prevent tool execution loops.

Key improvements:
- True sequential tool execution (one tool at a time)
- Enhanced state tracking and loop prevention
- Better error handling and recovery
- Improved feedback mechanisms
- Comprehensive logging and debugging
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from browser_control_tools import (
        BrowserControlTools, CommandResult, create_browser_controller
    )
    from enhanced_browser_control import (
        EnhancedBrowserControl, create_enhanced_controller
    )
    from unified_state_tools import (
        get_quick_status, get_browser_overview, get_page_content_summary
    )
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Browser tools not available: {e}")
    TOOLS_AVAILABLE = False
    # Create minimal placeholder classes
    class BrowserControlTools:
        def __init__(self, *args, **kwargs): pass
    class EnhancedBrowserControl:
        def __init__(self, *args, **kwargs): pass
    class CommandResult:
        def __init__(self, success=False, command="", args=None, message="", error=""):
            self.success = success
            self.command = command
            self.args = args or []
            self.message = message
            self.error = error

# LLM Provider imports (optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests package not available. Install with: pip install requests")


@dataclass
class SequentialAgentConfig:
    """Configuration for the enhanced sequential AI browser agent."""
    llm_provider: str = "ollama"  # openai, anthropic, ollama, custom
    model: str = "deepseek-r1:14b"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 1500
    timeout: int = 30
    max_tool_calls: int = 8  # Increased for better sequential execution
    debug: bool = True
    enable_loop_prevention: bool = True
    enable_state_tracking: bool = True


@dataclass
class SequentialAgentResponse:
    """Response from the enhanced sequential AI agent."""
    success: bool
    message: str
    tool_calls: List[Dict[str, Any]]
    execution_results: List[CommandResult]
    thinking: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    execution_stats: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.execution_stats is None:
            self.execution_stats = {}


@dataclass
class ExecutionState:
    """State tracking for sequential execution."""
    iteration_count: int = 0
    max_iterations: int = 8
    all_tool_calls: List[Dict[str, Any]] = None
    all_execution_results: List[CommandResult] = None
    executed_tool_signatures: set = None
    current_context: Dict[str, Any] = None
    task_completed: bool = False
    last_error: Optional[str] = None
    start_time: float = None
    last_tool_time: float = None
    
    def __post_init__(self):
        if self.all_tool_calls is None:
            self.all_tool_calls = []
        if self.all_execution_results is None:
            self.all_execution_results = []
        if self.executed_tool_signatures is None:
            self.executed_tool_signatures = set()
        if self.current_context is None:
            self.current_context = {}
        if self.start_time is None:
            self.start_time = time.time()


class SequentialLLMProvider:
    """Base class for LLM providers with enhanced sequential execution support."""
    
    def __init__(self, config: SequentialAgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]], 
                              execution_state: ExecutionState) -> Dict[str, Any]:
        """Generate response with enhanced sequential execution support."""
        raise NotImplementedError("Subclasses must implement generate_response")
    
    def _extract_tool_calls_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from response content with enhanced parsing."""
        tool_calls = []
        
        # Look for tool call patterns in the response
        lines = content.split('\n')
        execute_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check for section markers
            if line == "EXECUTE:":
                execute_section = True
                continue
            elif line in ["THINKING:", "ACTION:", "TASK COMPLETE", "NO MORE TOOLS"]:
                execute_section = False
                continue
            
            # Extract tool calls from TOOL_CALL: format
            if line.startswith('TOOL_CALL:'):
                try:
                    tool_data = json.loads(line[10:])  # Remove 'TOOL_CALL:' prefix
                    tool_calls.append(tool_data)
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Failed to parse tool call '{line}': {e}")
                    # Try to extract JSON from the line
                    try:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_content = line[json_start:]
                            tool_data = json.loads(json_content)
                            tool_calls.append(tool_data)
                    except:
                        continue
                continue
            
            # If in EXECUTE section, try to parse JSON lines
            if execute_section and line and line.startswith('{'):
                try:
                    tool_data = json.loads(line)
                    if 'name' in tool_data and 'parameters' in tool_data:
                        tool_calls.append(tool_data)
                except json.JSONDecodeError:
                    continue
        
        # Validate tool calls
        valid_tool_calls = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict) and 'name' in tool_call:
                # Ensure parameters is a dict
                if 'parameters' not in tool_call:
                    tool_call['parameters'] = {}
                elif not isinstance(tool_call['parameters'], dict):
                    tool_call['parameters'] = {}
                
                valid_tool_calls.append(tool_call)
        
        self.logger.debug(f"Extracted {len(valid_tool_calls)} valid tool calls from content")
        return valid_tool_calls


class SequentialOllamaProvider(SequentialLLMProvider):
    """Ollama local model provider with enhanced sequential execution."""
    
    def __init__(self, config: SequentialAgentConfig):
        super().__init__(config)
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not available. Install with: pip install requests")
        
        self.base_url = config.api_base or "http://localhost:11434"
    
    async def generate_response(self, messages: List[Dict[str, str]], 
                              tools: List[Dict[str, Any]], 
                              execution_state: ExecutionState) -> Dict[str, Any]:
        """Generate response using Ollama API with enhanced sequential execution support."""
        try:
            # Create a specialized prompt for sequential execution
            system_prompt = self._create_sequential_system_prompt(tools, execution_state)
            
            # Add tools to system message
            enhanced_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    enhanced_messages.append({
                        "role": "system", 
                        "content": system_prompt
                    })
                else:
                    enhanced_messages.append(msg)
            
            payload = {
                "model": self.config.model,
                "messages": enhanced_messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result_data = response.json()
            full_content = result_data.get("message", {}).get("content", "")
            
            # Separate reasoning from action response
            reasoning, action_response, tool_calls = self._parse_sequential_response(full_content)
            
            return {
                "content": action_response,
                "reasoning": reasoning,
                "tool_calls": tool_calls,
                "full_response": full_content
            }
            
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _create_sequential_system_prompt(self, tools: List[Dict[str, Any]], 
                                       execution_state: ExecutionState) -> str:
        """Create a system prompt optimized for sequential execution."""
        tools_text = self._format_tools_for_prompt(tools)
        
        # Add execution state context
        state_context = ""
        if execution_state.all_tool_calls:
            state_context = f"\n\n📊 CURRENT EXECUTION STATE:\n"
            state_context += f"   Iteration: {execution_state.iteration_count}/{execution_state.max_iterations}\n"
            state_context += f"   Tools executed: {len(execution_state.all_tool_calls)}\n"
            state_context += f"   Successful: {sum(1 for r in execution_state.all_execution_results if r.success)}\n"
            state_context += f"   Failed: {sum(1 for r in execution_state.all_execution_results if not r.success)}\n"
            
            if execution_state.all_tool_calls:
                state_context += f"   Last tool: {execution_state.all_tool_calls[-1]['name']}\n"
        
        prompt = f"""You are an AI browser assistant that controls a real web browser. You have access to browser automation tools.

AVAILABLE BROWSER TOOLS:
{tools_text}

{state_context}

CRITICAL SEQUENTIAL EXECUTION RULES:
1. Execute ONE tool at a time
2. Wait for feedback before calling the next tool
3. Use feedback to decide the next step
4. Continue until task is complete
5. If task is complete, respond with "TASK COMPLETE"
6. NEVER call multiple tools in one response
7. ALWAYS provide the EXECUTE section with actual tool calls

RESPONSE FORMAT:
THINKING:
[Brief reasoning about what the user wants and next step]

ACTION:
[Simple action plan for the next tool]

EXECUTE:
[Single tool call in JSON format:
TOOL_CALL: {{"name": "tool_name", "parameters": {{"param": "value"}}}}
]

SIMPLE EXAMPLES:
User: "open google.com"
THINKING: User wants to navigate to Google's homepage
ACTION: Open Google.com using open_url tool
EXECUTE:
TOOL_CALL: {{"name": "open_url", "parameters": {{"url": "https://www.google.com"}}}}

User: "search for Python tutorials"
THINKING: User wants to search for Python tutorials on Google
ACTION: Type "Python tutorials" in the search box
EXECUTE:
TOOL_CALL: {{"name": "type_text", "parameters": {{"text": "Python tutorials", "clear_first": true}}}}

User: "click the first result"
THINKING: User wants to click the first search result
ACTION: Click the first result on the page
EXECUTE:
TOOL_CALL: {{"name": "click_element", "parameters": {{"selector_type": "css", "selector_value": "h3"}}}}

SEQUENTIAL EXECUTION PATTERNS:
1. Navigation: open_url → wait for page load
2. Search: open_url → type_text → send_key(Enter)
3. Form filling: type_text → send_key(Enter)
4. Element interaction: click_element → wait for response
5. Tab management: tab_new → open_url

IMPORTANT:
- Call ONLY ONE tool per response
- Use feedback to determine next action
- If no more actions needed, say "TASK COMPLETE"
- If tool fails, try alternative approach
- Always include EXECUTE section with tool call
"""
        return prompt
    
    def _parse_sequential_response(self, content: str) -> tuple:
        """Parse sequential model response to separate thinking from actions."""
        reasoning = ""
        action_response = ""
        tool_calls = []
        
        # Split content into sections
        sections = content.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            
            if line.startswith('THINKING:'):
                current_section = 'thinking'
                continue
            elif line.startswith('ACTION:'):
                current_section = 'action'
                continue
            elif line.startswith('EXECUTE:'):
                current_section = 'execute'
                continue
            elif line.startswith('TOOL_CALL:'):
                current_section = 'execute'
                # Parse tool call
                try:
                    tool_data = json.loads(line[10:])  # Remove 'TOOL_CALL:' prefix
                    tool_calls.append(tool_data)
                except json.JSONDecodeError:
                    # Try to extract JSON from the line
                    try:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_content = line[json_start:]
                            tool_data = json.loads(json_content)
                            tool_calls.append(tool_data)
                    except:
                        continue
                continue
            
            # Add content to appropriate section
            if current_section == 'thinking':
                reasoning += line + '\n'
            elif current_section == 'action':
                action_response += line + '\n'
            elif current_section == 'execute' and not line.startswith('TOOL_CALL:'):
                action_response += line + '\n'
        
        # Clean up whitespace
        reasoning = reasoning.strip()
        action_response = action_response.strip()
        
        return reasoning, action_response, tool_calls
    
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompt."""
        tools_text = ""
        for tool in tools:
            tools_text += f"\n{tool['name']}: {tool['description']}\n"
            if 'parameters' in tool and 'properties' in tool['parameters']:
                props = tool['parameters']['properties']
                if props:
                    tools_text += "  Parameters: "
                    param_list = []
                    for param_name, param_info in props.items():
                        param_type = param_info.get('type', 'any')
                        required = param_name in tool['parameters'].get('required', [])
                        req_text = "*" if required else ""
                        param_list.append(f"{param_name}{req_text} ({param_type})")
                    tools_text += ", ".join(param_list) + "\n"
        
        return tools_text


class EnhancedSequentialAgent:
    """Enhanced AI browser agent with improved sequential execution handling."""
    
    def __init__(self, config: SequentialAgentConfig = None):
        self.config = config or SequentialAgentConfig()
        self.logger = self._setup_logging()
        
        # Initialize browser controllers
        if TOOLS_AVAILABLE:
            self.browser_controller = create_browser_controller()
            self.enhanced_controller = create_enhanced_controller()
        else:
            self.browser_controller = None
            self.enhanced_controller = None
        
        # Initialize LLM provider
        self.llm_provider = self._initialize_llm_provider()
        
        # Load tools configuration
        self.tools_config = self._load_tools_config()
        
        # State tracking
        self.conversation_history = []
        self.last_response = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent."""
        logger = logging.getLogger(__name__)
        if self.config.debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _initialize_llm_provider(self) -> SequentialLLMProvider:
        """Initialize the appropriate LLM provider."""
        if self.config.llm_provider == "ollama":
            return SequentialOllamaProvider(self.config)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration."""
        try:
            with open('agent_tools.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning("agent_tools.json not found, using default tools")
            return {"tools": []}
    
    async def process_query(self, user_query: str) -> SequentialAgentResponse:
        """Process a natural language query with enhanced sequential execution."""
        if not TOOLS_AVAILABLE:
            return SequentialAgentResponse(
                success=False,
                message="Browser control tools are not available",
                tool_calls=[],
                execution_results=[],
                error="Tools not loaded"
            )
        
        try:
            # Initialize execution state
            execution_state = ExecutionState(
                max_iterations=self.config.max_tool_calls,
                current_context=self._get_current_context()
            )
            
            # Get current context
            context = self._get_current_context()
            
            # Build enhanced context
            enhanced_context = self._build_enhanced_context(user_query, context)
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": enhanced_context}
            ]
            
            # Add conversation history
            if self.conversation_history:
                recent_history = self.conversation_history[-6:]
                history_context = "\n\n📚 PREVIOUS CONVERSATION (for context only):\n"
                for entry in recent_history:
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    if role == "user":
                        history_context += f"👤 User: {content}\n"
                    elif role == "assistant":
                        short_content = content[:200] + "..." if len(content) > 200 else content
                        history_context += f"🤖 Assistant: {short_content}\n"
                
                history_context += "\n⚠️  REMEMBER: The CURRENT REQUEST above is your priority!"
                messages.append({"role": "user", "content": history_context})
            
            # Execute sequential tool calling
            final_response = await self._execute_sequential_tool_calling(
                messages, user_query, execution_state
            )
            
            # Create response with execution statistics
            execution_stats = {
                'total_iterations': execution_state.iteration_count,
                'total_tools_executed': len(execution_state.all_tool_calls),
                'successful_tools': sum(1 for r in execution_state.all_execution_results if r.success),
                'failed_tools': sum(1 for r in execution_state.all_execution_results if not r.success),
                'execution_time': time.time() - execution_state.start_time,
                'task_completed': execution_state.task_completed
            }
            
            response = SequentialAgentResponse(
                success=True,
                message=final_response.get("content", "Task completed"),
                tool_calls=execution_state.all_tool_calls,
                execution_results=execution_state.all_execution_results,
                thinking=final_response.get("reasoning"),
                error=execution_state.last_error,
                execution_stats=execution_stats
            )
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": response.message}
            ])
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            self.last_response = response
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return SequentialAgentResponse(
                success=False,
                message=f"Error processing your request: {str(e)}",
                tool_calls=[],
                execution_results=[],
                error=str(e)
            )
    
    async def _execute_sequential_tool_calling(self, initial_messages: List[Dict[str, Any]], 
                                             user_query: str, execution_state: ExecutionState) -> Dict[str, Any]:
        """Execute sequential tool calling with enhanced state management."""
        messages = initial_messages.copy()
        final_response = None
        
        while (execution_state.iteration_count < execution_state.max_iterations and 
               not execution_state.task_completed):
            
            execution_state.iteration_count += 1
            execution_state.last_tool_time = time.time()
            
            self.logger.debug(f"Starting iteration {execution_state.iteration_count}")
            
            # Get LLM response
            try:
                llm_response = await self.llm_provider.generate_response(
                    messages=messages,
                    tools=self.tools_config.get("tools", []),
                    execution_state=execution_state
                )
            except Exception as e:
                self.logger.error(f"LLM API error in iteration {execution_state.iteration_count}: {e}")
                execution_state.last_error = f"LLM API error: {str(e)}"
                break
            
            self.logger.debug(f"LLM Response (iteration {execution_state.iteration_count}): {llm_response}")
            
            # Check if LLM wants to call tools
            tool_calls = llm_response.get("tool_calls", [])
            
            # If no tool calls in response, try to extract from content
            if not tool_calls:
                content = llm_response.get("content", "")
                tool_calls = self.llm_provider._extract_tool_calls_from_content(content)
                self.logger.debug(f"Extracted tool calls from content: {tool_calls}")
            
            # Check if LLM indicates task is complete
            content = llm_response.get("content", "").lower()
            if any(phrase in content for phrase in ["task complete", "no more tools", "task finished", "completed"]):
                self.logger.debug("LLM indicated task is complete")
                execution_state.task_completed = True
                final_response = llm_response
                break
            
            if not tool_calls:
                # No tool calls found - check if this is appropriate
                self.logger.debug("No tool calls found in LLM response")
                
                # Check if this looks like a simple navigation request that should have a tool call
                user_query_lower = user_query.lower()
                if any(keyword in user_query_lower for keyword in ['open', 'go to', 'navigate', 'visit', 'search']):
                    self.logger.warning("Navigation/search request detected but no tool call provided")
                    error_message = f"Your request '{user_query}' requires browser actions, but no tools were called. Please use appropriate browser tools to complete the task."
                    messages.append({"role": "user", "content": error_message})
                    continue
                
                # No more tool calls, we're done
                self.logger.debug("No more tool calls, task completed")
                execution_state.task_completed = True
                final_response = llm_response
                break
            
            # Execute ONLY the first tool call - enforce true sequential execution
            if tool_calls:
                first_tool_call = tool_calls[0]
                tool_name = first_tool_call["name"]
                parameters = first_tool_call.get("parameters", {})
                
                # Create tool signature for duplicate detection
                tool_signature = self._create_tool_signature(tool_name, parameters)
                
                # Check for duplicate tool calls to prevent infinite loops
                if tool_signature in execution_state.executed_tool_signatures:
                    self.logger.warning(f"Duplicate tool call detected: {tool_signature}")
                    self.logger.debug("Stopping execution to prevent infinite loops")
                    
                    duplicate_message = f"Tool {tool_name} with parameters {parameters} was already executed. Please try a different approach or indicate task completion."
                    messages.append({"role": "user", "content": duplicate_message})
                    continue
                
                # Add to executed signatures
                execution_state.executed_tool_signatures.add(tool_signature)
                
                self.logger.debug(f"Executing tool: {tool_name} with parameters: {parameters}")
                
                # Execute the tool
                try:
                    result = await self._execute_single_tool(tool_name, parameters)
                except Exception as e:
                    self.logger.error(f"Error executing tool {tool_name}: {e}")
                    result = CommandResult(
                        success=False,
                        command=tool_name,
                        args=[],
                        error=str(e)
                    )
                
                # Add to our tracking
                execution_state.all_tool_calls.append(first_tool_call)
                execution_state.all_execution_results.append(result)
                
                # Create comprehensive feedback message for the LLM
                feedback_message = self._create_enhanced_tool_feedback_message(
                    first_tool_call, result, execution_state
                )
                
                # Add the feedback to messages for next iteration
                messages.append({"role": "assistant", "content": f"I executed: {tool_name}({parameters})"})
                messages.append({"role": "user", "content": feedback_message})
                
                # Check if we should continue based on tool result
                if not result.success:
                    self.logger.warning(f"Tool {tool_name} failed: {result.error}")
                    execution_state.last_error = result.error
                    
                    error_message = f"Tool {tool_name} failed with error: {result.error}. Please try a different approach or provide more specific instructions."
                    messages.append({"role": "user", "content": error_message})
                
                # Update final response
                final_response = llm_response
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.5)
        
        # If we hit max iterations, log warning
        if execution_state.iteration_count >= execution_state.max_iterations:
            self.logger.warning(f"Reached maximum iterations ({execution_state.max_iterations}), stopping tool execution")
        
        return final_response or {"content": "Task processing completed"}
    
    def _create_tool_signature(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Create a unique signature for a tool call to detect duplicates."""
        normalized_params = {}
        for key, value in parameters.items():
            if key == "url" and isinstance(value, str):
                normalized_params[key] = value.lower().rstrip('/')
            elif isinstance(value, (str, int, float, bool)):
                normalized_params[key] = value
            else:
                normalized_params[key] = str(value)
        
        sorted_params = sorted(normalized_params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        
        return f"{tool_name}:{param_str}"
    
    def _create_enhanced_tool_feedback_message(self, tool_call: Dict[str, Any], result: CommandResult, 
                                             execution_state: ExecutionState) -> str:
        """Create a comprehensive feedback message for the LLM after tool execution."""
        tool_name = tool_call["name"]
        parameters = tool_call.get("parameters", {})
        iteration = execution_state.iteration_count
        
        feedback_parts = []
        feedback_parts.append(f"🔧 TOOL EXECUTION FEEDBACK (Iteration {iteration}):")
        feedback_parts.append(f"   Tool: {tool_name}")
        feedback_parts.append(f"   Parameters: {parameters}")
        
        if result.success:
            feedback_parts.append(f"   ✅ Status: SUCCESS")
            if result.message:
                feedback_parts.append(f"   📤 Message: {result.message}")
        else:
            feedback_parts.append(f"   ❌ Status: FAILED")
            if result.error:
                feedback_parts.append(f"   🚨 Error: {result.error}")
        
        # Add summary of all previous executions
        if len(execution_state.all_tool_calls) > 1:
            feedback_parts.append("")
            feedback_parts.append("📋 PREVIOUS TOOL EXECUTIONS:")
            for i, (prev_call, prev_result) in enumerate(zip(execution_state.all_tool_calls[:-1], 
                                                           execution_state.all_execution_results[:-1]), 1):
                prev_tool = prev_call["name"]
                prev_success = "✅" if prev_result.success else "❌"
                feedback_parts.append(f"   {i}. {prev_tool}: {prev_success}")
        
        # Add execution statistics
        feedback_parts.append("")
        feedback_parts.append("📊 EXECUTION STATISTICS:")
        feedback_parts.append(f"   Total tools executed: {len(execution_state.all_tool_calls)}")
        feedback_parts.append(f"   Successful: {sum(1 for r in execution_state.all_execution_results if r.success)}")
        feedback_parts.append(f"   Failed: {sum(1 for r in execution_state.all_execution_results if not r.success)}")
        feedback_parts.append(f"   Iterations remaining: {execution_state.max_iterations - iteration}")
        
        # Add intelligent next step guidance
        feedback_parts.append("")
        feedback_parts.append("🎯 NEXT STEP GUIDANCE:")
        
        if result.success:
            # Provide context-aware guidance based on the tool executed
            if tool_name == "open_url" and "url" in parameters:
                url = parameters["url"]
                if "google.com" in url.lower():
                    feedback_parts.append("   ✅ Google opened successfully. If you need to search, use 'type_text' to enter search terms and 'send_key' with 'Enter' to submit.")
                elif "youtube.com" in url.lower():
                    feedback_parts.append("   ✅ YouTube opened successfully. You can now browse videos or search for content.")
                else:
                    feedback_parts.append("   ✅ Page opened successfully. You can now interact with the page content.")
            elif tool_name == "type_text":
                feedback_parts.append("   ✅ Text entered successfully. Use 'send_key' with 'Enter' to submit forms or search.")
            elif tool_name == "send_key":
                feedback_parts.append("   ✅ Key sent successfully. The action should be completed.")
            else:
                feedback_parts.append("   ✅ Tool executed successfully. Continue with the next step to complete the task.")
            
            # Check if this might complete the task
            if tool_name in ["open_url", "send_key"] and iteration >= 2:
                feedback_parts.append("   💡 If this completes your task, respond with 'TASK COMPLETE'. Otherwise, continue with the next step.")
        else:
            feedback_parts.append("   ❌ Tool failed. Please try a different approach or provide more specific instructions.")
            feedback_parts.append("   💡 Consider using different parameters or a different tool to achieve the same goal.")
        
        return "\n".join(feedback_parts)
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current browser context."""
        try:
            if TOOLS_AVAILABLE:
                return get_quick_status()
            else:
                return {"error": "Tools not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _build_enhanced_context(self, user_query: str, context: Dict[str, Any]) -> str:
        """Build enhanced context for the LLM."""
        context_parts = []
        context_parts.append(f"🎯 CURRENT REQUEST: {user_query}")
        context_parts.append("")
        context_parts.append("📊 CURRENT BROWSER STATE:")
        
        if "error" in context:
            context_parts.append(f"   ❌ Error: {context['error']}")
        else:
            current_page = context.get("current_page", {})
            context_parts.append(f"   🌐 Current URL: {current_page.get('url', 'Unknown')}")
            context_parts.append(f"   📄 Title: {current_page.get('title', 'Unknown')}")
            context_parts.append(f"   📊 Tab count: {context.get('tab_count', 0)}")
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are an AI browser assistant that controls a real web browser. You have access to browser automation tools.

Your primary goal is to help users navigate and interact with web pages efficiently. You should:
1. Execute one tool at a time
2. Wait for feedback before proceeding
3. Use appropriate tools for each action
4. Provide clear feedback about what you're doing
5. Complete tasks step by step

Always use the available browser tools to perform actions rather than giving manual instructions."""
    
    async def _execute_single_tool(self, tool_name: str, parameters: Dict[str, Any]) -> CommandResult:
        """Execute a single tool call."""
        try:
            # Navigation tools
            if tool_name == "open_url":
                return self.browser_controller.open_url(**parameters)
            
            elif tool_name == "navigate_back":
                return self.browser_controller.go_back(**parameters)
            
            elif tool_name == "navigate_forward":
                return self.browser_controller.go_forward(**parameters)
            
            elif tool_name == "reload_page":
                return self.browser_controller.reload_page(**parameters)
            
            elif tool_name == "stop_loading":
                return self.browser_controller.stop_loading()
            
            # Page interaction tools
            elif tool_name == "scroll_page":
                direction = parameters["direction"]
                amount = parameters.get("amount", "page")
                count = parameters.get("count", 1)
                
                if amount == "page":
                    return self.browser_controller.scroll(direction, count=count)
                else:
                    return self.enhanced_controller.smart_scroll(direction, amount)
            
            elif tool_name == "search_page":
                return self.browser_controller.search(
                    parameters["text"],
                    reverse=parameters.get("reverse", False)
                )
            
            # Tab management tools
            elif tool_name == "tab_new":
                url = parameters.get("url")
                if url:
                    return self.browser_controller.open_url(
                        url, tab=True, bg=parameters.get("bg", False),
                        private=parameters.get("private", False)
                    )
                else:
                    return self.browser_controller.tab_new(bg=parameters.get("bg", False))
            
            elif tool_name == "tab_close":
                return self.browser_controller.tab_close(**parameters)
            
            elif tool_name == "tab_switch":
                direction = parameters.get("direction")
                index = parameters.get("index")
                count = parameters.get("count", 1)
                
                if index:
                    return self.browser_controller.tab_focus(index)
                elif direction == "next":
                    return self.browser_controller.tab_next(count=count)
                elif direction == "prev":
                    return self.browser_controller.tab_prev(count=count)
                elif direction == "first":
                    return self.browser_controller.tab_focus(1)
                elif direction == "last":
                    return self.browser_controller.tab_focus("last")
            
            # Element interaction tools
            elif tool_name == "click_element":
                return self.browser_controller.click_element(
                    parameters["selector_type"],
                    parameters.get("selector_value")
                )
            
            elif tool_name == "type_text":
                text = parameters["text"]
                clear_first = parameters.get("clear_first", False)
                
                if clear_first:
                    # Clear existing text first
                    self.browser_controller.fake_key("<Ctrl-a>")
                
                return self.browser_controller.insert_text(text)
            
            elif tool_name == "send_key":
                return self.browser_controller.fake_key(
                    parameters["key"],
                    global_=parameters.get("global", False)
                )
            
            # Information gathering tools
            elif tool_name == "get_page_info":
                try:
                    info = get_page_content_summary()
                    return CommandResult(
                        success=True,
                        command="get_page_info",
                        args=[],
                        message=json.dumps(info, indent=2)
                    )
                except Exception as e:
                    return CommandResult(
                        success=False,
                        command="get_page_info",
                        args=[],
                        error=str(e)
                    )
            
            else:
                return CommandResult(
                    success=False,
                    command=tool_name,
                    args=[],
                    error=f"Unknown tool: {tool_name}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                command=tool_name,
                args=[],
                error=str(e)
            )


# Convenience function to create an enhanced sequential agent
def create_enhanced_sequential_agent(config: SequentialAgentConfig = None) -> EnhancedSequentialAgent:
    """Create an enhanced sequential agent with the given configuration."""
    return EnhancedSequentialAgent(config)


# Example usage
if __name__ == "__main__":
    # Create agent
    config = SequentialAgentConfig(
        llm_provider="ollama",
        model="deepseek-r1:14b",
        debug=True
    )
    
    agent = create_enhanced_sequential_agent(config)
    
    # Example usage
    async def test_agent():
        response = await agent.process_query("open google.com and search for Python tutorials")
        print(f"Success: {response.success}")
        print(f"Message: {response.message}")
        print(f"Tools executed: {len(response.tool_calls)}")
        print(f"Execution stats: {response.execution_stats}")
    
    # Run test
    asyncio.run(test_agent())
