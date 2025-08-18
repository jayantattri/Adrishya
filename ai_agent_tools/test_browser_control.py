"""
Comprehensive tests for browser control tools.

This module provides test cases for both basic and enhanced browser control functionality.
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from browser_control_tools import (
        BrowserControlTools, CommandResult, BrowserAction,
        create_browser_controller, execute_browser_command,
        open_url, close_tab, switch_tab
    )
    from enhanced_browser_control import (
        EnhancedBrowserControl, NavigationStrategy, ElementSelector,
        FormField, WorkflowStep, BrowserWorkflow,
        create_enhanced_controller, execute_smart_action, create_login_workflow
    )
    from browser_state_tools import BrowserStateTools, TabInfo
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules for testing: {e}")
    MODULES_AVAILABLE = False


class MockCommandRunner:
    """Mock command runner for testing."""
    
    def __init__(self):
        self.commands_run = []
        self.should_succeed = True
        self.error_message = "Mock error"
    
    def run(self, command_text, count=None, safely=True):
        """Mock run method."""
        self.commands_run.append({
            'command': command_text,
            'count': count,
            'safely': safely
        })
        
        if not self.should_succeed:
            from qutebrowser.commands.cmdexc import Error
            raise Error(self.error_message)


class TestBrowserControlTools(unittest.TestCase):
    """Test cases for basic browser control tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.controller = BrowserControlTools(window_id=0)
        self.mock_runner = MockCommandRunner()
        
        # Mock the command runner
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            pass
    
    def test_initialization(self):
        """Test controller initialization."""
        controller = BrowserControlTools(window_id=1)
        self.assertEqual(controller.window_id, 1)
        self.assertEqual(len(controller._last_results), 0)
    
    @patch('ai_agent_tools.browser_control_tools.runners')
    @patch('ai_agent_tools.browser_control_tools.objreg')
    def test_execute_command_success(self, mock_objreg, mock_runners):
        """Test successful command execution."""
        # Mock objreg and runner
        mock_browser = MagicMock()
        mock_objreg.get.return_value = mock_browser
        
        mock_runner = MockCommandRunner()
        mock_runners.CommandRunner.return_value = mock_runner
        
        controller = BrowserControlTools()
        result = controller.execute_command("open", ["https://example.com"])
        
        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.command, "open")
        self.assertEqual(result.args, ["https://example.com"])
    
    def test_execute_command_with_args(self):
        """Test command execution with arguments."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            result = self.controller.execute_command("open", ["--tab", "https://example.com"])
            
            self.assertEqual(len(self.mock_runner.commands_run), 1)
            self.assertEqual(self.mock_runner.commands_run[0]['command'], 'open --tab https://example.com')
    
    def test_execute_command_with_count(self):
        """Test command execution with count parameter."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            result = self.controller.execute_command("tab-close", count=2)
            
            self.assertEqual(len(self.mock_runner.commands_run), 1)
            self.assertEqual(self.mock_runner.commands_run[0]['count'], 2)
    
    def test_open_url(self):
        """Test URL opening functionality."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            result = self.controller.open_url("https://example.com", bg=True, tab=True)
            
            self.assertEqual(len(self.mock_runner.commands_run), 1)
            command = self.mock_runner.commands_run[0]['command']
            self.assertIn("--bg", command)
            self.assertIn("--tab", command)
            self.assertIn("https://example.com", command)
    
    def test_navigation_commands(self):
        """Test navigation command methods."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Test reload
            self.controller.reload_page(force=True)
            self.assertIn("--force", self.mock_runner.commands_run[-1]['command'])
            
            # Test back navigation
            self.controller.go_back(tab=True, count=2)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--tab", command)
            self.assertEqual(self.mock_runner.commands_run[-1]['count'], 2)
            
            # Test forward navigation
            self.controller.go_forward(quiet=True, index=3)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--quiet", command)
            self.assertIn("--index 3", command)
    
    def test_tab_management(self):
        """Test tab management commands."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Test tab close
            self.controller.tab_close(force=True, count=2)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--force", command)
            
            # Test tab selection
            self.controller.tab_select(3)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("3", command)
            
            # Test tab movement
            self.controller.tab_move("start")
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("start", command)
    
    def test_page_interaction(self):
        """Test page interaction commands."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Test scrolling
            self.controller.scroll("down", count=3)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("down", command)
            self.assertEqual(self.mock_runner.commands_run[-1]['count'], 3)
            
            # Test pixel scrolling
            self.controller.scroll_px(100, 200)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("100 200", command)
            
            # Test zooming
            self.controller.zoom_in(quiet=True, count=2)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--quiet", command)
    
    def test_search_functionality(self):
        """Test search commands."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Test search
            self.controller.search("test query", reverse=True)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--reverse", command)
            self.assertIn("test query", command)
            
            # Test search navigation
            self.controller.search_next(count=2)
            self.assertEqual(self.mock_runner.commands_run[-1]['count'], 2)
    
    def test_configuration_commands(self):
        """Test configuration commands."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Test set config
            self.controller.set_config("content.javascript.enabled", "true", temp=True)
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--temp", command)
            self.assertIn("content.javascript.enabled", command)
            self.assertIn("true", command)
            
            # Test bind key
            self.controller.bind_key("J", "tab-next", mode="normal")
            command = self.mock_runner.commands_run[-1]['command']
            self.assertIn("--mode normal", command)
            self.assertIn("J", command)
            self.assertIn("tab-next", command)
    
    def test_command_history(self):
        """Test command history tracking."""
        with patch.object(self.controller, '_get_command_runner', return_value=self.mock_runner):
            # Execute some commands
            self.controller.open_url("https://example.com")
            self.controller.reload_page()
            self.controller.tab_close()
            
            history = self.controller.get_command_history()
            self.assertEqual(len(history), 3)
            self.assertEqual(history[0].command, "open")
            self.assertEqual(history[1].command, "reload")
            self.assertEqual(history[2].command, "tab-close")
    
    def test_error_handling(self):
        """Test error handling in command execution."""
        mock_runner = MockCommandRunner()
        mock_runner.should_succeed = False
        mock_runner.error_message = "Test error"
        
        with patch.object(self.controller, '_get_command_runner', return_value=mock_runner):
            with patch('ai_agent_tools.browser_control_tools.cmdexc') as mock_cmdexc:
                mock_cmdexc.Error = Exception  # Use standard Exception for testing
                result = self.controller.execute_command("invalid-command")
                
                self.assertFalse(result.success)
                self.assertIsNotNone(result.error)
    
    def test_get_available_commands(self):
        """Test getting available commands."""
        commands = self.controller.get_available_commands()
        
        self.assertIsInstance(commands, dict)
        self.assertIn('open_url', commands)
        self.assertIn('tab_close', commands)
        self.assertIn('scroll', commands)
        
        # Check command structure
        open_cmd = commands['open_url']
        self.assertIsInstance(open_cmd, BrowserAction)
        self.assertEqual(open_cmd.command, 'open')
        self.assertTrue(open_cmd.requires_url)


class TestEnhancedBrowserControl(unittest.TestCase):
    """Test cases for enhanced browser control tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")
        
        # Mock the underlying tools
        self.mock_control_tools = Mock()
        self.mock_state_tools = Mock()
        self.mock_unified_tools = Mock()
        
        self.controller = EnhancedBrowserControl(window_id=0)
        self.controller.control_tools = self.mock_control_tools
        self.controller.state_tools = self.mock_state_tools
        self.controller.unified_tools = self.mock_unified_tools
    
    def test_initialization(self):
        """Test enhanced controller initialization."""
        controller = EnhancedBrowserControl(window_id=1)
        self.assertEqual(controller.window_id, 1)
        self.assertEqual(len(controller._workflow_history), 0)
    
    def test_wait_for_condition(self):
        """Test wait for condition functionality."""
        # Test condition that becomes true
        counter = [0]
        def condition():
            counter[0] += 1
            return counter[0] >= 3
        
        result = self.controller.wait_for_condition(condition, timeout=2.0, interval=0.1)
        self.assertTrue(result)
        self.assertGreaterEqual(counter[0], 3)
    
    def test_wait_for_condition_timeout(self):
        """Test wait for condition timeout."""
        def never_true():
            return False
        
        start_time = time.time()
        result = self.controller.wait_for_condition(never_true, timeout=0.5, interval=0.1)
        elapsed = time.time() - start_time
        
        self.assertFalse(result)
        self.assertGreaterEqual(elapsed, 0.5)
        self.assertLess(elapsed, 1.0)  # Should not take much longer than timeout
    
    def test_smart_navigation(self):
        """Test smart navigation functionality."""
        self.mock_control_tools.open_url.return_value = CommandResult(
            success=True, command="open", args=["https://example.com"]
        )
        
        # Test direct navigation
        result = self.controller.smart_navigation("https://example.com", "direct")
        self.mock_control_tools.open_url.assert_called_with("https://example.com")
        
        # Test new tab navigation
        result = self.controller.smart_navigation("https://example.com", "new_tab")
        self.mock_control_tools.open_url.assert_called_with("https://example.com", tab=True)
        
        # Test background navigation
        result = self.controller.smart_navigation("https://example.com", "background")
        self.mock_control_tools.open_url.assert_called_with("https://example.com", bg=True, tab=True)
    
    def test_smart_scroll(self):
        """Test smart scrolling functionality."""
        self.mock_control_tools.scroll.return_value = CommandResult(
            success=True, command="scroll", args=["down"]
        )
        self.mock_control_tools.scroll_px.return_value = CommandResult(
            success=True, command="scroll-px", args=["0", "400"]
        )
        
        # Test page scrolling
        result = self.controller.smart_scroll("down", "page")
        self.mock_control_tools.scroll.assert_called_with("page-down")
        
        # Test half page scrolling
        result = self.controller.smart_scroll("down", "half")
        self.mock_control_tools.scroll_px.assert_called_with(0, 400)
        
        # Test pixel scrolling
        result = self.controller.smart_scroll("right", 150)
        self.mock_control_tools.scroll_px.assert_called_with(150, 0)
    
    def test_element_selector_creation(self):
        """Test smart element selector creation."""
        # Test login selectors
        selectors = self.controller.create_smart_selectors("login button")
        self.assertGreater(len(selectors), 0)
        
        # Should contain email/username selectors
        css_selectors = [s.value for s in selectors if s.selector_type == "css"]
        self.assertTrue(any("email" in sel for sel in css_selectors))
        
        # Test search selectors
        search_selectors = self.controller.create_smart_selectors("search box")
        search_css = [s.value for s in search_selectors if s.selector_type == "css"]
        self.assertTrue(any("search" in sel for sel in search_css))
    
    def test_find_and_click_element(self):
        """Test element finding and clicking."""
        self.mock_control_tools.click_element.return_value = CommandResult(
            success=True, command="click-element", args=["css", ".button"]
        )
        
        selectors = [
            ElementSelector("css", ".button", "Button class"),
            ElementSelector("id", "submit", "Submit ID")
        ]
        
        result = self.controller.find_and_click_element(selectors)
        self.mock_control_tools.click_element.assert_called_with("css", ".button")
        self.assertTrue(result.success)
    
    def test_fill_form(self):
        """Test form filling functionality."""
        self.mock_control_tools.click_element.return_value = CommandResult(
            success=True, command="click-element", args=[]
        )
        self.mock_control_tools.fake_key.return_value = CommandResult(
            success=True, command="fake-key", args=["<Ctrl-a>"]
        )
        self.mock_control_tools.insert_text.return_value = CommandResult(
            success=True, command="insert-text", args=["test@example.com"]
        )
        
        fields = [
            FormField(
                selector=ElementSelector("css", "input[type='email']", "Email field"),
                value="test@example.com",
                field_type="text"
            )
        ]
        
        results = self.controller.fill_form(fields, submit=False)
        
        # Should have clicked, cleared, and inserted text
        self.assertEqual(len(results), 3)
        self.mock_control_tools.insert_text.assert_called_with("test@example.com")
    
    def test_workflow_creation(self):
        """Test workflow creation."""
        actions = [
            {"type": "navigate", "url": "https://example.com"},
            {"type": "search", "query": "test query"},
            {"type": "click_link", "href": "result", "text": "First Result"}
        ]
        
        workflow = self.controller.create_navigation_workflow(
            "test_workflow", 
            "https://example.com", 
            actions
        )
        
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.start_url, "https://example.com")
        self.assertEqual(len(workflow.steps), 3)
        
        # Check step types
        self.assertEqual(workflow.steps[0].action, "navigate")
        self.assertEqual(workflow.steps[1].action, "search")
        self.assertEqual(workflow.steps[2].action, "click")
    
    def test_intelligent_page_interaction(self):
        """Test intelligent page interaction."""
        self.mock_control_tools.insert_text.return_value = CommandResult(
            success=True, command="insert-text", args=["test query"]
        )
        
        # Test search goal
        result = self.controller.intelligent_page_interaction("search for 'test query'")
        # Should attempt to find search elements and insert text
        # (exact behavior depends on mock setup)
    
    def test_workflow_execution(self):
        """Test workflow execution."""
        # Create a simple workflow
        steps = [
            WorkflowStep(
                step_id="step1",
                action="wait",
                parameters={"duration": 0.1}
            ),
            WorkflowStep(
                step_id="step2", 
                action="wait",
                parameters={"duration": 0.1}
            )
        ]
        
        workflow = BrowserWorkflow(
            name="test_workflow",
            description="Test workflow",
            steps=steps
        )
        
        result = self.controller.execute_workflow(workflow)
        
        self.assertEqual(result["workflow_name"], "test_workflow")
        self.assertEqual(result["steps_completed"], 2)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["step_results"]), 2)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Required modules not available")
    
    @patch('ai_agent_tools.browser_control_tools.BrowserControlTools')
    def test_create_browser_controller(self, mock_controller_class):
        """Test browser controller creation."""
        mock_instance = Mock()
        mock_controller_class.return_value = mock_instance
        
        controller = create_browser_controller(window_id=1)
        mock_controller_class.assert_called_with(1)
        self.assertEqual(controller, mock_instance)
    
    @patch('ai_agent_tools.enhanced_browser_control.EnhancedBrowserControl')
    def test_create_enhanced_controller(self, mock_controller_class):
        """Test enhanced controller creation."""
        mock_instance = Mock()
        mock_controller_class.return_value = mock_instance
        
        controller = create_enhanced_controller(window_id=1)
        mock_controller_class.assert_called_with(1)
        self.assertEqual(controller, mock_instance)
    
    def test_create_login_workflow(self):
        """Test login workflow creation."""
        workflow = create_login_workflow(
            "test_site",
            "https://example.com/login",
            "testuser",
            "testpass"
        )
        
        self.assertEqual(workflow.name, "login_test_site")
        self.assertEqual(workflow.start_url, "https://example.com/login")
        self.assertEqual(len(workflow.steps), 3)
        
        # Check that login form step exists
        form_step = workflow.steps[1]
        self.assertEqual(form_step.action, "fill_form")
        self.assertEqual(len(form_step.parameters["fields"]), 2)


class TestDataStructures(unittest.TestCase):
    """Test data structures used in browser control."""
    
    def test_command_result(self):
        """Test CommandResult dataclass."""
        result = CommandResult(
            success=True,
            command="test",
            args=["arg1", "arg2"],
            message="Success"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.command, "test")
        self.assertEqual(result.args, ["arg1", "arg2"])
        self.assertEqual(result.message, "Success")
        self.assertIsNotNone(result.timestamp)
    
    def test_element_selector(self):
        """Test ElementSelector dataclass."""
        selector = ElementSelector(
            selector_type="css",
            value=".button",
            description="Button element",
            timeout=10.0,
            required=True
        )
        
        self.assertEqual(selector.selector_type, "css")
        self.assertEqual(selector.value, ".button")
        self.assertEqual(selector.description, "Button element")
        self.assertEqual(selector.timeout, 10.0)
        self.assertTrue(selector.required)
    
    def test_workflow_step(self):
        """Test WorkflowStep dataclass."""
        step = WorkflowStep(
            step_id="test_step",
            action="click",
            parameters={"selector": ".button"},
            wait_after=1.0,
            max_retries=3
        )
        
        self.assertEqual(step.step_id, "test_step")
        self.assertEqual(step.action, "click")
        self.assertEqual(step.parameters["selector"], ".button")
        self.assertEqual(step.wait_after, 1.0)
        self.assertEqual(step.max_retries, 3)
    
    def test_browser_workflow(self):
        """Test BrowserWorkflow dataclass."""
        steps = [
            WorkflowStep("step1", "action1", {}),
            WorkflowStep("step2", "action2", {})
        ]
        
        workflow = BrowserWorkflow(
            name="test_workflow",
            description="Test workflow",
            steps=steps,
            start_url="https://example.com"
        )
        
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(workflow.description, "Test workflow")
        self.assertEqual(len(workflow.steps), 2)
        self.assertEqual(workflow.start_url, "https://example.com")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
