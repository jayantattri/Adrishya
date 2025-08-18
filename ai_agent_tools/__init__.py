"""
AI Agent Tools for Qutebrowser

This package provides comprehensive tools for an AI agent to interact with and control qutebrowser.
It includes tools for:
- Getting browser state information (tabs, windows, page content, performance)
- Controlling browser actions (navigation, tab management, page interaction)
- Advanced automation workflows and smart interactions
- Enhanced browser control with natural language processing
- AI-powered browser assistant with LLM integration

Modules:
- browser_state_tools: Get information about browser state
- page_content_tools: Extract and analyze page content  
- performance_tools: Monitor browser and system performance
- unified_state_tools: Unified interface to all state tools
- browser_control_tools: Control browser through qutebrowser commands
- enhanced_browser_control: Advanced automation and smart interactions
- ai_browser_agent: AI agent with LLM integration for natural language control
- agent_interface: Interactive interface for easy AI agent usage

Key Features:
- Natural language browser control using LLMs (OpenAI, Anthropic, Ollama)
- Comprehensive browser automation and workflow system
- Real-time browser state monitoring and performance tracking
- Smart element detection and interaction strategies
- Multi-step workflow automation with error handling
- Customizable agent profiles for different use cases
"""

__version__ = "1.0.0"
__author__ = "AI Agent Tools Developer"

# Import main classes for easy access
try:
    from .browser_state_tools import (
        BrowserStateTools, TabInfo, WindowState, NavigationState, BrowserMetrics,
        get_current_tab_info, get_all_tabs_info, get_window_state, 
        get_navigation_state, get_browser_metrics, get_comprehensive_state
    )
    from .browser_control_tools import (
        BrowserControlTools, CommandResult, BrowserAction,
        create_browser_controller, execute_browser_command,
        open_url, close_tab, switch_tab
    )
    from .enhanced_browser_control import (
        EnhancedBrowserControl, NavigationStrategy, ElementSelector,
        FormField, WorkflowStep, BrowserWorkflow,
        create_enhanced_controller, execute_smart_action, create_login_workflow
    )
    from .unified_state_tools import (
        UnifiedBrowserStateTools, CompleteBrowserState,
        get_complete_browser_state, get_browser_overview, get_tab_summary,
        get_performance_summary, get_page_content_summary, get_quick_status
    )
    
    # AI Agent components (optional imports)
    try:
        from .ai_browser_agent import (
            AIBrowserAgent, AgentConfig, AgentResponse,
            OpenAIProvider, AnthropicProvider, OllamaProvider,
            create_ai_agent, ask_ai_agent
        )
        AI_AGENT_AVAILABLE = True
    except ImportError:
        AI_AGENT_AVAILABLE = False
    
    # Define what's available when using "from ai_agent_tools import *"
    __all__ = [
        # State tools
        'BrowserStateTools', 'TabInfo', 'WindowState', 'NavigationState', 'BrowserMetrics',
        'get_current_tab_info', 'get_all_tabs_info', 'get_window_state', 
        'get_navigation_state', 'get_browser_metrics', 'get_comprehensive_state',
        
        # Control tools  
        'BrowserControlTools', 'CommandResult', 'BrowserAction',
        'create_browser_controller', 'execute_browser_command',
        'open_url', 'close_tab', 'switch_tab',
        
        # Enhanced control
        'EnhancedBrowserControl', 'NavigationStrategy', 'ElementSelector',
        'FormField', 'WorkflowStep', 'BrowserWorkflow',
        'create_enhanced_controller', 'execute_smart_action', 'create_login_workflow',
        
        # Unified tools
        'UnifiedBrowserStateTools', 'CompleteBrowserState',
        'get_complete_browser_state', 'get_browser_overview', 'get_tab_summary',
        'get_performance_summary', 'get_page_content_summary', 'get_quick_status'
    ]
    
    # Add AI agent tools if available
    if AI_AGENT_AVAILABLE:
        __all__.extend([
            'AIBrowserAgent', 'AgentConfig', 'AgentResponse',
            'OpenAIProvider', 'AnthropicProvider', 'OllamaProvider',
            'create_ai_agent', 'ask_ai_agent'
        ])
    
except ImportError as e:
    print(f"Warning: Some AI agent tools could not be imported: {e}")
    print("This is normal if running outside of qutebrowser environment")
    __all__ = []

