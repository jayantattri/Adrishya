"""
Enhanced Browser Control Tools for Qutebrowser

This module provides advanced browser control capabilities including:
- Smart action sequences and automation workflows
- Element detection and interaction strategies
- Integration with browser state monitoring
- Advanced page navigation and manipulation
- Form filling and automated interactions
"""

import sys
import os
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from .browser_control_tools import BrowserControlTools, CommandResult, BrowserAction
    from .browser_state_tools import BrowserStateTools, TabInfo
    from .unified_state_tools import UnifiedBrowserStateTools
    TOOLS_AVAILABLE = True
except ImportError:
    try:
        from browser_control_tools import BrowserControlTools, CommandResult, BrowserAction
        from browser_state_tools import BrowserStateTools, TabInfo
        from unified_state_tools import UnifiedBrowserStateTools
        TOOLS_AVAILABLE = True
    except ImportError:
        TOOLS_AVAILABLE = False
        print("Warning: Could not import browser tools modules")
        # Create minimal placeholder classes
        class BrowserControlTools:
            def __init__(self, *args, **kwargs): pass
        class BrowserStateTools:
            def __init__(self, *args, **kwargs): pass
        class UnifiedBrowserStateTools:
            def __init__(self, *args, **kwargs): pass
        @dataclass
        class CommandResult:
            success: bool = False
            command: str = ""
            args: List[str] = None
            error: Optional[str] = None
            timestamp: str = ""
        @dataclass
        class BrowserAction:
            command: str = ""
            description: str = ""


@dataclass
class NavigationStrategy:
    """Strategy for navigating to a specific page or state."""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    success_criteria: List[str]
    max_attempts: int = 3
    wait_between_steps: float = 1.0


@dataclass
class ElementSelector:
    """Selector for finding elements on a page."""
    selector_type: str  # css, id, xpath, text, etc.
    value: str
    description: str
    timeout: float = 5.0
    required: bool = True


@dataclass
class FormField:
    """Information about a form field to fill."""
    selector: ElementSelector
    value: str
    field_type: str = "text"  # text, select, checkbox, radio, etc.
    validation: Optional[str] = None


@dataclass
class WorkflowStep:
    """A single step in an automated workflow."""
    step_id: str
    action: str
    parameters: Dict[str, Any]
    success_criteria: Optional[List[str]] = None
    error_handling: Optional[str] = None
    wait_after: float = 0.5
    max_retries: int = 2


@dataclass
class BrowserWorkflow:
    """A complete workflow of browser automation steps."""
    name: str
    description: str
    steps: List[WorkflowStep]
    start_url: Optional[str] = None
    expected_duration: Optional[float] = None
    rollback_steps: Optional[List[WorkflowStep]] = None


class EnhancedBrowserControl:
    """Enhanced browser control with automation and smart interaction capabilities."""
    
    def __init__(self, window_id: int = 0):
        """Initialize enhanced browser control.
        
        Args:
            window_id: Window ID to control
        """
        self.window_id = window_id
        self.control_tools = BrowserControlTools(window_id) if TOOLS_AVAILABLE else None
        self.state_tools = BrowserStateTools() if TOOLS_AVAILABLE else None
        self.unified_tools = UnifiedBrowserStateTools() if TOOLS_AVAILABLE else None
        
        self._workflow_history = []
        self._element_cache = {}
        self._navigation_strategies = self._initialize_navigation_strategies()
    
    def _initialize_navigation_strategies(self) -> Dict[str, NavigationStrategy]:
        """Initialize common navigation strategies."""
        strategies = {}
        
        # Search strategy
        strategies['search'] = NavigationStrategy(
            name="search",
            description="Perform a search using site's search functionality",
            steps=[
                {"action": "find_search_box", "wait": 1.0},
                {"action": "click_element", "selector": "search_box"},
                {"action": "type_text", "text": "{search_term}"},
                {"action": "submit_search"}
            ],
            success_criteria=["search_results_visible", "url_contains_search"]
        )
        
        # Login strategy
        strategies['login'] = NavigationStrategy(
            name="login",
            description="Log into a website using credentials",
            steps=[
                {"action": "find_login_form", "wait": 1.0},
                {"action": "fill_username", "selector": "username_field"},
                {"action": "fill_password", "selector": "password_field"},
                {"action": "submit_login", "selector": "login_button"}
            ],
            success_criteria=["logged_in_indicator", "url_changed", "user_menu_visible"]
        )
        
        # Purchase/checkout strategy
        strategies['checkout'] = NavigationStrategy(
            name="checkout",
            description="Complete a purchase or checkout process",
            steps=[
                {"action": "review_cart", "wait": 1.0},
                {"action": "proceed_to_checkout"},
                {"action": "fill_shipping_info"},
                {"action": "select_payment_method"},
                {"action": "confirm_order"}
            ],
            success_criteria=["order_confirmation", "success_message", "order_number_visible"]
        )
        
        return strategies
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get comprehensive current browser state.
        
        Returns:
            Dictionary with current state information
        """
        if not self.unified_tools:
            return {"error": "State tools not available"}
        
        return self.unified_tools.get_complete_browser_state(self.window_id)
    
    def wait_for_condition(self, condition_func: Callable[[], bool], 
                          timeout: float = 10.0, interval: float = 0.5) -> bool:
        """Wait for a condition to become true.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            
        Returns:
            True if condition was met, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception:
                pass
            time.sleep(interval)
        return False
    
    def wait_for_page_load(self, timeout: float = 30.0) -> bool:
        """Wait for page to finish loading.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if page loaded, False if timeout
        """
        def is_loaded():
            if not self.state_tools:
                return True
            current_tab = self.state_tools.get_current_tab_info(self.window_id)
            return current_tab and not current_tab.is_loading
        
        return self.wait_for_condition(is_loaded, timeout)
    
    def wait_for_url_change(self, initial_url: str, timeout: float = 10.0) -> bool:
        """Wait for URL to change from initial URL.
        
        Args:
            initial_url: The starting URL
            timeout: Maximum time to wait
            
        Returns:
            True if URL changed, False if timeout
        """
        def url_changed():
            if not self.state_tools:
                return True
            current_tab = self.state_tools.get_current_tab_info(self.window_id)
            return current_tab and current_tab.url != initial_url
        
        return self.wait_for_condition(url_changed, timeout)
    
    def smart_navigation(self, target_url: str, strategy: str = "direct",
                        wait_for_load: bool = True) -> CommandResult:
        """Navigate to a URL using smart strategies.
        
        Args:
            target_url: URL to navigate to
            strategy: Navigation strategy (direct, new_tab, background)
            wait_for_load: Whether to wait for page to load
            
        Returns:
            CommandResult object
        """
        if not self.control_tools:
            return CommandResult(
                success=False,
                command="smart_navigation",
                args=[target_url, strategy],
                error="Control tools not available"
            )
        
        # Get current state
        current_state = self.get_current_state()
        current_url = ""
        if isinstance(current_state, dict) and 'current_tab' in current_state and current_state['current_tab']:
            current_url = current_state['current_tab'].get('url', '')
        
        # Choose navigation method based on strategy
        if strategy == "new_tab":
            result = self.control_tools.open_url(target_url, tab=True)
        elif strategy == "background":
            result = self.control_tools.open_url(target_url, bg=True, tab=True)
        elif strategy == "new_window":
            result = self.control_tools.open_url(target_url, window=True)
        else:  # direct
            result = self.control_tools.open_url(target_url)
        
        if result.success and wait_for_load:
            self.wait_for_page_load()
            if strategy == "direct":
                self.wait_for_url_change(current_url)
        
        return result
    
    def smart_scroll(self, direction: str, amount: Union[str, int] = "page",
                    smooth: bool = True) -> CommandResult:
        """Scroll with smart amount detection.
        
        Args:
            direction: Direction to scroll (up, down, left, right, top, bottom)
            amount: Amount to scroll (page, half, line, number)
            smooth: Whether to use smooth scrolling
            
        Returns:
            CommandResult object
        """
        if not self.control_tools:
            return CommandResult(
                success=False,
                command="smart_scroll",
                args=[direction, str(amount)],
                error="Control tools not available"
            )
        
        if amount == "page":
            if direction in ["up", "down"]:
                return self.control_tools.scroll(f"page-{direction}")
            else:
                return self.control_tools.scroll(direction)
        elif amount == "half":
            # Scroll half a page by using pixel scrolling
            # Get window dimensions to calculate half page
            if direction == "down":
                return self.control_tools.scroll_px(0, 400)  # Approximate half page
            elif direction == "up":
                return self.control_tools.scroll_px(0, -400)
            elif direction == "left":
                return self.control_tools.scroll_px(-400, 0)
            elif direction == "right":
                return self.control_tools.scroll_px(400, 0)
        elif amount == "line":
            count = 3 if direction in ["up", "down"] else 1
            return self.control_tools.scroll(direction, count=count)
        elif isinstance(amount, int):
            if direction in ["up", "down"]:
                dy = amount if direction == "down" else -amount
                return self.control_tools.scroll_px(0, dy)
            else:
                dx = amount if direction == "right" else -amount
                return self.control_tools.scroll_px(dx, 0)
        else:
            return self.control_tools.scroll(direction)
    
    def find_and_click_element(self, selectors: List[ElementSelector],
                              click_options: Dict[str, Any] = None) -> CommandResult:
        """Find and click an element using multiple selector strategies.
        
        Args:
            selectors: List of selectors to try
            click_options: Additional options for clicking
            
        Returns:
            CommandResult object
        """
        if not self.control_tools:
            return CommandResult(
                success=False,
                command="find_and_click_element",
                args=[],
                error="Control tools not available"
            )
        
        for selector in selectors:
            # Try to click using the selector
            if selector.selector_type == "css":
                result = self.control_tools.click_element("css", selector.value)
            elif selector.selector_type == "id":
                result = self.control_tools.click_element("id", selector.value)
            elif selector.selector_type == "focused":
                result = self.control_tools.click_element("focused")
            else:
                continue
                
            if result.success:
                return result
                
            # If required and failed, continue to next selector
            if not selector.required:
                continue
        
        return CommandResult(
            success=False,
            command="find_and_click_element",
            args=[],
            error="Could not find any clickable element with given selectors"
        )
    
    def fill_form(self, fields: List[FormField], submit: bool = True,
                  submit_selector: ElementSelector = None) -> List[CommandResult]:
        """Fill out a form with given field data.
        
        Args:
            fields: List of form fields to fill
            submit: Whether to submit the form after filling
            submit_selector: Selector for submit button
            
        Returns:
            List of CommandResult objects
        """
        results = []
        
        if not self.control_tools:
            return [CommandResult(
                success=False,
                command="fill_form",
                args=[],
                error="Control tools not available"
            )]
        
        for field in fields:
            # Click on the field first
            click_result = self.find_and_click_element([field.selector])
            results.append(click_result)
            
            if not click_result.success:
                continue
            
            # Insert the text
            if field.field_type == "text":
                # Clear existing text first
                clear_result = self.control_tools.fake_key("<Ctrl-a>")
                results.append(clear_result)
                
                # Insert new text
                insert_result = self.control_tools.insert_text(field.value)
                results.append(insert_result)
            
            # Add a small delay between fields
            time.sleep(0.3)
        
        # Submit form if requested
        if submit:
            if submit_selector:
                submit_result = self.find_and_click_element([submit_selector])
            else:
                # Try common submit methods
                submit_selectors = [
                    ElementSelector("css", "input[type='submit']", "Submit button"),
                    ElementSelector("css", "button[type='submit']", "Submit button"),
                    ElementSelector("css", ".submit-btn", "Submit button class"),
                    ElementSelector("css", "#submit", "Submit button ID")
                ]
                submit_result = self.find_and_click_element(submit_selectors)
            
            results.append(submit_result)
        
        return results
    
    def execute_workflow(self, workflow: BrowserWorkflow) -> Dict[str, Any]:
        """Execute a complete browser automation workflow.
        
        Args:
            workflow: The workflow to execute
            
        Returns:
            Dictionary with execution results
        """
        start_time = time.time()
        results = {
            "workflow_name": workflow.name,
            "start_time": start_time,
            "end_time": None,
            "duration": None,
            "success": False,
            "steps_completed": 0,
            "step_results": [],
            "error": None
        }
        
        if not self.control_tools:
            results["error"] = "Control tools not available"
            return results
        
        try:
            # Navigate to start URL if provided
            if workflow.start_url:
                nav_result = self.smart_navigation(workflow.start_url)
                if not nav_result.success:
                    results["error"] = f"Failed to navigate to start URL: {nav_result.error}"
                    return results
            
            # Execute each step
            for i, step in enumerate(workflow.steps):
                step_start_time = time.time()
                step_result = {
                    "step_id": step.step_id,
                    "action": step.action,
                    "start_time": step_start_time,
                    "success": False,
                    "attempts": 0,
                    "error": None
                }
                
                # Try the step with retries
                for attempt in range(step.max_retries + 1):
                    step_result["attempts"] = attempt + 1
                    
                    try:
                        # Execute the step based on action type
                        action_result = self._execute_workflow_step(step)
                        
                        if action_result.success:
                            step_result["success"] = True
                            step_result["result"] = asdict(action_result)
                            break
                        else:
                            step_result["error"] = action_result.error
                    
                    except Exception as e:
                        step_result["error"] = str(e)
                    
                    if attempt < step.max_retries:
                        time.sleep(0.5)  # Wait before retry
                
                step_result["end_time"] = time.time()
                step_result["duration"] = step_result["end_time"] - step_start_time
                results["step_results"].append(step_result)
                
                if step_result["success"]:
                    results["steps_completed"] += 1
                    # Wait after successful step
                    if step.wait_after > 0:
                        time.sleep(step.wait_after)
                else:
                    # Handle step failure
                    if step.error_handling == "continue":
                        continue
                    elif step.error_handling == "skip_remaining":
                        break
                    else:  # stop
                        results["error"] = f"Step {step.step_id} failed: {step_result['error']}"
                        break
            
            # Check if workflow completed successfully
            if results["steps_completed"] == len(workflow.steps):
                results["success"] = True
        
        except Exception as e:
            results["error"] = f"Workflow execution error: {str(e)}"
        
        finally:
            results["end_time"] = time.time()
            results["duration"] = results["end_time"] - start_time
            self._workflow_history.append(results)
        
        return results
    
    def _execute_workflow_step(self, step: WorkflowStep) -> CommandResult:
        """Execute a single workflow step.
        
        Args:
            step: The workflow step to execute
            
        Returns:
            CommandResult object
        """
        action = step.action
        params = step.parameters
        
        # Navigation actions
        if action == "navigate":
            return self.smart_navigation(params["url"], params.get("strategy", "direct"))
        elif action == "back":
            return self.control_tools.go_back()
        elif action == "forward":
            return self.control_tools.go_forward()
        elif action == "reload":
            return self.control_tools.reload_page(force=params.get("force", False))
        
        # Tab actions
        elif action == "new_tab":
            return self.control_tools.tab_new(params.get("url"))
        elif action == "close_tab":
            return self.control_tools.tab_close()
        elif action == "switch_tab":
            return self.control_tools.tab_focus(params["index"])
        
        # Page interaction
        elif action == "scroll":
            return self.smart_scroll(params["direction"], params.get("amount", "page"))
        elif action == "click":
            selectors = [ElementSelector(**sel) for sel in params["selectors"]]
            return self.find_and_click_element(selectors)
        elif action == "type":
            return self.control_tools.insert_text(params["text"])
        elif action == "key":
            return self.control_tools.fake_key(params["key"])
        
        # Form actions
        elif action == "fill_form":
            fields = [FormField(**field) for field in params["fields"]]
            results = self.fill_form(fields, params.get("submit", True))
            # Return last result or first failure
            for result in results:
                if not result.success:
                    return result
            return results[-1] if results else CommandResult(success=False, command=action, args=[])
        
        # Search actions
        elif action == "search":
            search_result = self.control_tools.search(params["text"])
            if search_result.success and params.get("select_first", False):
                # Click first result if requested
                time.sleep(1.0)  # Wait for search results
                first_result_selectors = [
                    ElementSelector("css", "a[href*='search']", "First search result"),
                    ElementSelector("css", ".search-result:first-child a", "First result link"),
                    ElementSelector("css", ".result:first-child a", "First result")
                ]
                return self.find_and_click_element(first_result_selectors)
            return search_result
        
        # Wait actions
        elif action == "wait":
            time.sleep(params.get("duration", 1.0))
            return CommandResult(success=True, command=action, args=[])
        elif action == "wait_for_load":
            success = self.wait_for_page_load(params.get("timeout", 30.0))
            return CommandResult(success=success, command=action, args=[])
        
        # JavaScript actions
        elif action == "execute_js":
            return self.control_tools.execute_javascript(params["code"])
        
        # Configuration actions
        elif action == "set_config":
            return self.control_tools.set_config(params["option"], params["value"])
        
        else:
            return CommandResult(
                success=False,
                command=action,
                args=[],
                error=f"Unknown workflow action: {action}"
            )
    
    def create_navigation_workflow(self, name: str, start_url: str, 
                                 target_actions: List[Dict[str, Any]]) -> BrowserWorkflow:
        """Create a navigation workflow from high-level actions.
        
        Args:
            name: Name of the workflow
            start_url: Starting URL
            target_actions: List of high-level actions to perform
            
        Returns:
            BrowserWorkflow object
        """
        steps = []
        
        for i, action in enumerate(target_actions):
            step_id = f"step_{i+1}_{action.get('type', 'action')}"
            
            if action["type"] == "search":
                steps.append(WorkflowStep(
                    step_id=step_id,
                    action="search",
                    parameters={
                        "text": action["query"],
                        "select_first": action.get("select_first", False)
                    }
                ))
            
            elif action["type"] == "click_link":
                steps.append(WorkflowStep(
                    step_id=step_id,
                    action="click",
                    parameters={
                        "selectors": [
                            {"selector_type": "css", "value": f"a[href*='{action['href']}']", "description": "Link by href"},
                            {"selector_type": "css", "value": f"a:contains('{action.get('text', '')}')", "description": "Link by text"}
                        ]
                    }
                ))
            
            elif action["type"] == "fill_form":
                steps.append(WorkflowStep(
                    step_id=step_id,
                    action="fill_form",
                    parameters={
                        "fields": action["fields"],
                        "submit": action.get("submit", True)
                    }
                ))
            
            elif action["type"] == "navigate":
                steps.append(WorkflowStep(
                    step_id=step_id,
                    action="navigate",
                    parameters={
                        "url": action["url"],
                        "strategy": action.get("strategy", "direct")
                    }
                ))
        
        return BrowserWorkflow(
            name=name,
            description=f"Automated workflow: {name}",
            steps=steps,
            start_url=start_url
        )
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of executed workflows.
        
        Returns:
            List of workflow execution results
        """
        return self._workflow_history.copy()
    
    def create_smart_selectors(self, element_description: str) -> List[ElementSelector]:
        """Create smart selectors for finding elements based on description.
        
        Args:
            element_description: Natural language description of element
            
        Returns:
            List of ElementSelector objects
        """
        selectors = []
        desc_lower = element_description.lower()
        
        # Login/auth related
        if "login" in desc_lower or "sign in" in desc_lower:
            selectors.extend([
                ElementSelector("css", "input[type='email']", "Email input"),
                ElementSelector("css", "input[name*='email']", "Email field"),
                ElementSelector("css", "input[name*='username']", "Username field"),
                ElementSelector("css", "#email", "Email ID"),
                ElementSelector("css", "#username", "Username ID"),
                ElementSelector("css", ".login-input", "Login input class")
            ])
        
        if "password" in desc_lower:
            selectors.extend([
                ElementSelector("css", "input[type='password']", "Password input"),
                ElementSelector("css", "input[name*='password']", "Password field"),
                ElementSelector("css", "#password", "Password ID")
            ])
        
        if "submit" in desc_lower or "send" in desc_lower or "login" in desc_lower:
            selectors.extend([
                ElementSelector("css", "input[type='submit']", "Submit input"),
                ElementSelector("css", "button[type='submit']", "Submit button"),
                ElementSelector("css", ".submit", "Submit class"),
                ElementSelector("css", ".login-button", "Login button"),
                ElementSelector("css", "button:contains('Login')", "Login button text"),
                ElementSelector("css", "button:contains('Sign in')", "Sign in button")
            ])
        
        # Search related
        if "search" in desc_lower:
            selectors.extend([
                ElementSelector("css", "input[type='search']", "Search input"),
                ElementSelector("css", "input[name*='search']", "Search field"),
                ElementSelector("css", "input[placeholder*='search']", "Search placeholder"),
                ElementSelector("css", "#search", "Search ID"),
                ElementSelector("css", ".search-input", "Search input class")
            ])
        
        # Navigation related
        if "next" in desc_lower:
            selectors.extend([
                ElementSelector("css", "a:contains('Next')", "Next link"),
                ElementSelector("css", ".next", "Next class"),
                ElementSelector("css", "button:contains('Next')", "Next button")
            ])
        
        if "previous" in desc_lower or "prev" in desc_lower:
            selectors.extend([
                ElementSelector("css", "a:contains('Previous')", "Previous link"),
                ElementSelector("css", "a:contains('Prev')", "Prev link"),
                ElementSelector("css", ".prev", "Prev class"),
                ElementSelector("css", ".previous", "Previous class")
            ])
        
        # Shopping/ecommerce related
        if "cart" in desc_lower or "basket" in desc_lower:
            selectors.extend([
                ElementSelector("css", ".cart", "Cart class"),
                ElementSelector("css", ".basket", "Basket class"),
                ElementSelector("css", "a[href*='cart']", "Cart link"),
                ElementSelector("css", "#cart", "Cart ID")
            ])
        
        if "buy" in desc_lower or "purchase" in desc_lower or "add to cart" in desc_lower:
            selectors.extend([
                ElementSelector("css", "button:contains('Add to cart')", "Add to cart button"),
                ElementSelector("css", "button:contains('Buy')", "Buy button"),
                ElementSelector("css", ".add-to-cart", "Add to cart class"),
                ElementSelector("css", ".buy-button", "Buy button class")
            ])
        
        return selectors
    
    def intelligent_page_interaction(self, goal: str, context: Dict[str, Any] = None) -> CommandResult:
        """Perform intelligent page interaction based on natural language goal.
        
        Args:
            goal: Natural language description of what to do
            context: Additional context information
            
        Returns:
            CommandResult object
        """
        goal_lower = goal.lower()
        context = context or {}
        
        # Analyze goal and create appropriate action
        if "search for" in goal_lower:
            # Extract search term
            search_term = goal_lower.split("search for")[-1].strip()
            if "'" in search_term:
                search_term = search_term.split("'")[1]
            elif '"' in search_term:
                search_term = search_term.split('"')[1]
            
            # Find search box and perform search
            search_selectors = self.create_smart_selectors("search")
            click_result = self.find_and_click_element(search_selectors)
            if click_result.success:
                return self.control_tools.insert_text(search_term)
            return click_result
        
        elif "login" in goal_lower or "sign in" in goal_lower:
            # Perform login
            username = context.get("username", "")
            password = context.get("password", "")
            
            if not username or not password:
                return CommandResult(
                    success=False,
                    command="intelligent_interaction",
                    args=[goal],
                    error="Username and password required for login"
                )
            
            # Create login form fields
            fields = [
                FormField(
                    selector=ElementSelector("css", "input[type='email'], input[name*='email'], input[name*='username']", "Username field"),
                    value=username
                ),
                FormField(
                    selector=ElementSelector("css", "input[type='password']", "Password field"),
                    value=password
                )
            ]
            
            results = self.fill_form(fields, submit=True)
            return results[-1] if results else CommandResult(success=False, command="login", args=[])
        
        elif "click" in goal_lower:
            # Extract what to click
            click_target = goal_lower.replace("click", "").strip()
            selectors = self.create_smart_selectors(click_target)
            return self.find_and_click_element(selectors)
        
        elif "scroll" in goal_lower:
            # Extract scroll direction and amount
            direction = "down"  # default
            amount = "page"     # default
            
            if "up" in goal_lower:
                direction = "up"
            elif "down" in goal_lower:
                direction = "down"
            elif "left" in goal_lower:
                direction = "left"
            elif "right" in goal_lower:
                direction = "right"
            
            if "top" in goal_lower:
                direction = "top"
            elif "bottom" in goal_lower:
                direction = "bottom"
            
            return self.smart_scroll(direction, amount)
        
        elif "go to" in goal_lower or "navigate to" in goal_lower:
            # Extract URL
            url = goal_lower.split("go to")[-1].split("navigate to")[-1].strip()
            if not url.startswith("http"):
                url = "https://" + url
            return self.smart_navigation(url)
        
        else:
            return CommandResult(
                success=False,
                command="intelligent_interaction",
                args=[goal],
                error=f"Could not understand goal: {goal}"
            )


# Convenience functions
def create_enhanced_controller(window_id: int = 0) -> EnhancedBrowserControl:
    """Create an enhanced browser controller.
    
    Args:
        window_id: Window ID to control
        
    Returns:
        EnhancedBrowserControl instance
    """
    return EnhancedBrowserControl(window_id)


def execute_smart_action(goal: str, context: Dict[str, Any] = None, 
                        window_id: int = 0) -> CommandResult:
    """Execute a smart action based on natural language goal.
    
    Args:
        goal: Natural language description of action
        context: Additional context
        window_id: Window ID to control
        
    Returns:
        CommandResult object
    """
    controller = EnhancedBrowserControl(window_id)
    return controller.intelligent_page_interaction(goal, context)


def create_login_workflow(site_name: str, login_url: str, 
                         username: str, password: str) -> BrowserWorkflow:
    """Create a login workflow for a website.
    
    Args:
        site_name: Name of the website
        login_url: URL of login page
        username: Username to use
        password: Password to use
        
    Returns:
        BrowserWorkflow object
    """
    steps = [
        WorkflowStep(
            step_id="navigate_to_login",
            action="navigate",
            parameters={"url": login_url}
        ),
        WorkflowStep(
            step_id="fill_login_form",
            action="fill_form",
            parameters={
                "fields": [
                    {
                        "selector": {
                            "selector_type": "css",
                            "value": "input[type='email'], input[name*='email'], input[name*='username']",
                            "description": "Username field"
                        },
                        "value": username,
                        "field_type": "text"
                    },
                    {
                        "selector": {
                            "selector_type": "css", 
                            "value": "input[type='password']",
                            "description": "Password field"
                        },
                        "value": password,
                        "field_type": "text"
                    }
                ],
                "submit": True
            }
        ),
        WorkflowStep(
            step_id="wait_for_login",
            action="wait_for_load",
            parameters={"timeout": 10.0}
        )
    ]
    
    return BrowserWorkflow(
        name=f"login_{site_name}",
        description=f"Login workflow for {site_name}",
        steps=steps,
        start_url=login_url
    )
