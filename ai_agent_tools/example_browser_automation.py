"""
Example Browser Automation with AI Agent Tools

This file demonstrates how to use the browser control tools for various automation tasks.
These examples show real-world usage patterns for AI agents controlling qutebrowser.
"""

import time
import json
from typing import Dict, List, Any

try:
    from ai_agent_tools import (
        # Control tools
        BrowserControlTools, EnhancedBrowserControl,
        create_browser_controller, create_enhanced_controller,
        
        # State tools
        get_quick_status, get_browser_overview, get_tab_summary,
        
        # Data structures
        ElementSelector, FormField, WorkflowStep, BrowserWorkflow,
        CommandResult, NavigationStrategy,
        
        # Convenience functions
        execute_smart_action, create_login_workflow
    )
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import AI agent tools: {e}")
    print("This example should be run from within qutebrowser")
    TOOLS_AVAILABLE = False


def demonstrate_basic_control():
    """Demonstrate basic browser control functionality."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping basic control demo")
        return
        
    print("=== Basic Browser Control Demo ===")
    
    # Create a controller
    controller = create_browser_controller()
    
    # Get current status
    status = get_quick_status()
    print(f"Current browser status: {status}")
    
    # Open a new tab with a website
    print("Opening example.com in new tab...")
    result = controller.open_url("https://example.com", tab=True)
    print(f"Open result: {result.success}")
    
    if result.success:
        # Wait for page to load
        time.sleep(2)
        
        # Get page info
        tab_summary = get_tab_summary()
        print(f"Active tab: {tab_summary.get('active_index', 'Unknown')}")
        print(f"Total tabs: {tab_summary.get('count', 'Unknown')}")
        
        # Scroll down the page
        scroll_result = controller.scroll("down", count=3)
        print(f"Scroll result: {scroll_result.success}")
        
        # Search for something on the page
        search_result = controller.search("Example")
        print(f"Search result: {search_result.success}")
        
        # Go back
        back_result = controller.go_back()
        print(f"Back result: {search_result.success}")
        
        # Close the tab
        close_result = controller.tab_close()
        print(f"Close tab result: {close_result.success}")
    
    print("Basic control demo completed.\n")


def demonstrate_enhanced_control():
    """Demonstrate enhanced browser control with smart features."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping enhanced control demo")
        return
        
    print("=== Enhanced Browser Control Demo ===")
    
    # Create enhanced controller
    enhanced = create_enhanced_controller()
    
    # Demonstrate smart navigation
    print("Smart navigation to search engine...")
    nav_result = enhanced.smart_navigation("https://duckduckgo.com", strategy="new_tab")
    print(f"Navigation result: {nav_result.success}")
    
    if nav_result.success:
        # Wait for page load
        enhanced.wait_for_page_load(timeout=10)
        
        # Perform intelligent interaction - search
        print("Performing intelligent search...")
        search_result = execute_smart_action(
            "search for 'qutebrowser features'",
            context={}
        )
        print(f"Smart search result: {search_result.success}")
        
        # Smart scroll
        print("Smart scrolling...")
        scroll_result = enhanced.smart_scroll("down", "half")
        print(f"Smart scroll result: {scroll_result.success}")
        
        # Find and click elements intelligently
        print("Finding search results...")
        selectors = enhanced.create_smart_selectors("first search result")
        click_result = enhanced.find_and_click_element(selectors)
        print(f"Click result: {click_result.success}")
    
    print("Enhanced control demo completed.\n")


def demonstrate_form_automation():
    """Demonstrate automated form filling."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping form demo")
        return
        
    print("=== Form Automation Demo ===")
    
    enhanced = create_enhanced_controller()
    
    # Navigate to a form page (example)
    nav_result = enhanced.smart_navigation("https://httpbin.org/forms/post")
    
    if nav_result.success:
        enhanced.wait_for_page_load()
        
        # Define form fields
        form_fields = [
            FormField(
                selector=ElementSelector("css", "input[name='custname']", "Customer name field"),
                value="Test User",
                field_type="text"
            ),
            FormField(
                selector=ElementSelector("css", "input[name='custtel']", "Phone field"),
                value="123-456-7890",
                field_type="text"
            ),
            FormField(
                selector=ElementSelector("css", "input[name='custemail']", "Email field"),
                value="test@example.com",
                field_type="text"
            )
        ]
        
        # Fill the form
        print("Filling form fields...")
        form_results = enhanced.fill_form(form_fields, submit=False)
        
        success_count = sum(1 for r in form_results if r.success)
        print(f"Form filling completed: {success_count}/{len(form_results)} fields successful")
    
    print("Form automation demo completed.\n")


def demonstrate_workflow_automation():
    """Demonstrate complete workflow automation."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping workflow demo")
        return
        
    print("=== Workflow Automation Demo ===")
    
    enhanced = create_enhanced_controller()
    
    # Create a search workflow
    workflow_actions = [
        {"type": "navigate", "url": "https://duckduckgo.com"},
        {"type": "search", "query": "qutebrowser documentation", "select_first": True}
    ]
    
    workflow = enhanced.create_navigation_workflow(
        name="search_documentation",
        start_url="https://duckduckgo.com",
        target_actions=workflow_actions
    )
    
    # Execute the workflow
    print("Executing search workflow...")
    workflow_result = enhanced.execute_workflow(workflow)
    
    print(f"Workflow '{workflow_result['workflow_name']}' completed:")
    print(f"  Success: {workflow_result['success']}")
    print(f"  Steps completed: {workflow_result['steps_completed']}/{len(workflow.steps)}")
    print(f"  Duration: {workflow_result.get('duration', 0):.2f} seconds")
    
    if not workflow_result['success']:
        print(f"  Error: {workflow_result.get('error', 'Unknown error')}")
    
    # Show step details
    for i, step_result in enumerate(workflow_result['step_results']):
        print(f"  Step {i+1} ({step_result['step_id']}): {'✓' if step_result['success'] else '✗'}")
        if not step_result['success']:
            print(f"    Error: {step_result.get('error', 'Unknown')}")
    
    print("Workflow automation demo completed.\n")


def demonstrate_login_workflow():
    """Demonstrate login automation workflow."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping login demo")
        return
        
    print("=== Login Workflow Demo ===")
    
    # Create a login workflow (example for a test site)
    login_workflow = create_login_workflow(
        site_name="httpbin",
        login_url="https://httpbin.org/basic-auth/user/passwd",
        username="user",
        password="passwd"
    )
    
    enhanced = create_enhanced_controller()
    
    print("Executing login workflow...")
    login_result = enhanced.execute_workflow(login_workflow)
    
    print(f"Login workflow completed:")
    print(f"  Success: {login_result['success']}")
    print(f"  Duration: {login_result.get('duration', 0):.2f} seconds")
    
    if not login_result['success']:
        print(f"  Error: {login_result.get('error', 'Unknown error')}")
    
    print("Login workflow demo completed.\n")


def demonstrate_browser_state_integration():
    """Demonstrate integration between control and state tools."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping integration demo")
        return
        
    print("=== Browser State Integration Demo ===")
    
    controller = create_browser_controller()
    enhanced = create_enhanced_controller()
    
    # Get initial state
    initial_state = enhanced.get_current_state()
    print("Initial browser state:")
    if isinstance(initial_state, dict) and 'current_tab' in initial_state:
        current_tab = initial_state['current_tab']
        if current_tab:
            print(f"  Current URL: {current_tab.get('url', 'Unknown')}")
            print(f"  Current title: {current_tab.get('title', 'Unknown')}")
            print(f"  Loading: {current_tab.get('is_loading', False)}")
    
    # Open a new page and monitor state changes
    print("\nOpening new page and monitoring state changes...")
    nav_result = controller.open_url("https://example.com")
    
    if nav_result.success:
        # Wait for navigation and get updated state
        enhanced.wait_for_page_load()
        time.sleep(1)
        
        updated_state = enhanced.get_current_state()
        if isinstance(updated_state, dict) and 'current_tab' in updated_state:
            current_tab = updated_state['current_tab']
            if current_tab:
                print(f"  New URL: {current_tab.get('url', 'Unknown')}")
                print(f"  New title: {current_tab.get('title', 'Unknown')}")
                print(f"  Loading: {current_tab.get('is_loading', False)}")
        
        # Get comprehensive browser overview
        overview = get_browser_overview()
        print(f"\nBrowser Overview:")
        print(f"  Active tab: {overview.get('active_tab', {}).get('title', 'Unknown')}")
        print(f"  Total tabs: {overview.get('tab_count', 0)}")
        print(f"  Window fullscreen: {overview.get('window_status', {}).get('is_fullscreen', False)}")
    
    print("Browser state integration demo completed.\n")


def demonstrate_advanced_automation():
    """Demonstrate advanced automation scenarios."""
    if not TOOLS_AVAILABLE:
        print("Tools not available - skipping advanced demo")
        return
        
    print("=== Advanced Automation Demo ===")
    
    enhanced = create_enhanced_controller()
    
    # Create a complex workflow with error handling
    complex_steps = [
        WorkflowStep(
            step_id="open_site",
            action="navigate",
            parameters={"url": "https://example.com"},
            wait_after=2.0
        ),
        WorkflowStep(
            step_id="scroll_explore",
            action="scroll",
            parameters={"direction": "down", "amount": "page"},
            wait_after=1.0,
            error_handling="continue"
        ),
        WorkflowStep(
            step_id="search_text",
            action="search",
            parameters={"text": "example"},
            wait_after=1.0,
            error_handling="continue"
        ),
        WorkflowStep(
            step_id="take_screenshot",
            action="execute_js",
            parameters={"code": "console.log('Page explored');"},
            error_handling="continue"
        )
    ]
    
    complex_workflow = BrowserWorkflow(
        name="explore_page",
        description="Explore a webpage comprehensively",
        steps=complex_steps,
        start_url="https://example.com"
    )
    
    print("Executing complex exploration workflow...")
    result = enhanced.execute_workflow(complex_workflow)
    
    print(f"Complex workflow results:")
    print(f"  Name: {result['workflow_name']}")
    print(f"  Success: {result['success']}")
    print(f"  Steps completed: {result['steps_completed']}")
    print(f"  Total duration: {result.get('duration', 0):.2f} seconds")
    
    # Show detailed step results
    for step_result in result['step_results']:
        status = "✓" if step_result['success'] else "✗"
        duration = step_result.get('duration', 0)
        print(f"  {status} {step_result['step_id']}: {duration:.2f}s")
        if not step_result['success']:
            print(f"    Error: {step_result.get('error', 'Unknown')}")
    
    # Get workflow history
    history = enhanced.get_workflow_history()
    print(f"\nTotal workflows executed: {len(history)}")
    
    print("Advanced automation demo completed.\n")


def run_all_demos():
    """Run all demonstration functions."""
    print("🤖 AI Agent Browser Control Tools - Comprehensive Demo\n")
    print("This demo showcases the full capabilities of the browser control tools.")
    print("Each demo section shows different aspects of browser automation.\n")
    
    try:
        # Run all demonstrations
        demonstrate_basic_control()
        demonstrate_enhanced_control()
        demonstrate_form_automation()
        demonstrate_workflow_automation()
        demonstrate_login_workflow()
        demonstrate_browser_state_integration()
        demonstrate_advanced_automation()
        
        print("🎉 All demos completed successfully!")
        print("\nThese examples show how an AI agent can:")
        print("• Control browser navigation and tab management")
        print("• Interact with web pages intelligently")
        print("• Fill forms and automate user workflows")
        print("• Monitor browser state and performance")
        print("• Execute complex automation sequences")
        print("• Handle errors and adapt to different scenarios")
        
    except Exception as e:
        print(f"❌ Demo encountered an error: {e}")
        print("This may be normal if running outside qutebrowser environment")


def create_custom_workflow_example():
    """Example of creating a custom automation workflow."""
    if not TOOLS_AVAILABLE:
        print("Tools not available for custom workflow example")
        return None
        
    print("=== Custom Workflow Creation Example ===")
    
    # Define a workflow for researching a topic
    research_steps = [
        WorkflowStep(
            step_id="open_search_engine",
            action="navigate", 
            parameters={"url": "https://duckduckgo.com"},
            wait_after=2.0
        ),
        WorkflowStep(
            step_id="perform_search",
            action="search",
            parameters={"text": "{search_topic}", "select_first": False},
            wait_after=1.0
        ),
        WorkflowStep(
            step_id="open_first_result",
            action="click",
            parameters={
                "selectors": [
                    {"selector_type": "css", "value": ".result__a", "description": "First result link"}
                ]
            },
            wait_after=3.0
        ),
        WorkflowStep(
            step_id="scroll_and_read",
            action="scroll",
            parameters={"direction": "down", "amount": "page"},
            wait_after=2.0,
            max_retries=1
        ),
        WorkflowStep(
            step_id="save_page",
            action="key",
            parameters={"key": "<Ctrl-s>"},
            error_handling="continue"
        )
    ]
    
    research_workflow = BrowserWorkflow(
        name="research_topic",
        description="Automated research workflow for any topic",
        steps=research_steps,
        start_url="https://duckduckgo.com",
        expected_duration=15.0
    )
    
    print("Custom research workflow created!")
    print(f"Workflow has {len(research_workflow.steps)} steps")
    print(f"Expected duration: {research_workflow.expected_duration} seconds")
    
    return research_workflow


if __name__ == "__main__":
    # Check if we're in the right environment
    if not TOOLS_AVAILABLE:
        print("⚠️  AI Agent Tools not available.")
        print("This script should be run from within qutebrowser with the tools loaded.")
        print("To use these tools:")
        print("1. Load the tools in qutebrowser using load_in_qutebrowser.py")
        print("2. Run this script from qutebrowser's Python console")
        exit(1)
    
    # Run the comprehensive demo
    run_all_demos()
    
    # Show how to create custom workflows
    print("\n" + "="*50)
    custom_workflow = create_custom_workflow_example()
    
    print("\n📖 For more examples and documentation, see:")
    print("• browser_control_tools.py - Basic browser control")
    print("• enhanced_browser_control.py - Advanced automation")
    print("• test_browser_control.py - Comprehensive test suite")
    print("• README.md - Full documentation and usage guide")
