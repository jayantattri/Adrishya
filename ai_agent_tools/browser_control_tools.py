"""
Browser Control Tools for Qutebrowser

This module provides tools to control qutebrowser through its command system,
allowing an AI agent to navigate, manage tabs, interact with pages, and configure the browser.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from qutebrowser.misc import objects
    from qutebrowser.utils import objreg, log
    from qutebrowser.commands import runners, cmdexc
    from qutebrowser.api import cmdutils
    from qutebrowser.qt.core import QUrl
    from qutebrowser.qt.widgets import QApplication
    from qutebrowser.browser import browsertab
    from qutebrowser.mainwindow import tabbedbrowser
    from qutebrowser.keyinput import modeman
    from qutebrowser.utils.usertypes import KeyMode
    QUTEBROWSER_AVAILABLE = True
except ImportError as e:
    QUTEBROWSER_AVAILABLE = False
    # Create minimal logging for when qutebrowser is not available
    class DummyLog:
        def warning(self, msg): print(f"Warning: {msg}")
        def error(self, msg): print(f"Error: {msg}")
        def debug(self, msg): print(f"Debug: {msg}")
        def info(self, msg): print(f"Info: {msg}")
    
    class LogContainer:
        misc = DummyLog()
        commands = DummyLog()
    
    log = LogContainer()
    objects = None
    objreg = None
    QApplication = None
    KeyMode = None
    print(f"Warning: Could not import qutebrowser modules: {e}")
    print("This module should be run from within qutebrowser or with proper imports")


@dataclass
class CommandResult:
    """Result of executing a command."""
    success: bool
    command: str
    args: List[str]
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class BrowserAction:
    """Represents a browser action that can be executed."""
    command: str
    description: str
    args: Optional[Dict[str, Any]] = None
    requires_url: bool = False
    requires_tab: bool = False
    mode_restricted: Optional[str] = None


class BrowserControlTools:
    """Main class for controlling qutebrowser through its command system."""
    
    def __init__(self, window_id: int = 0):
        """Initialize the browser control tools.
        
        Args:
            window_id: The window ID to control (default: 0 for current window)
        """
        self.window_id = window_id
        self._command_runner = None
        self._last_results = []  # Store last 10 command results
        
    def _check_availability(self) -> bool:
        """Check if qutebrowser is available."""
        if not QUTEBROWSER_AVAILABLE:
            log.misc.warning("Qutebrowser modules not available")
            return False
        return True
    
    def _get_command_runner(self):
        """Get the command runner for executing commands."""
        if not self._check_availability():
            return None
            
        if self._command_runner is None:
            try:
                # Get the tabbed browser instance to get the command runner
                tabbed_browser = objreg.get('tabbed-browser', scope='window', window=self.window_id)
                if tabbed_browser:
                    self._command_runner = runners.CommandRunner(self.window_id, parent=tabbed_browser)
                else:
                    log.misc.warning(f"Could not get tabbed browser for window {self.window_id}")
                    return None
            except Exception as e:
                log.misc.warning(f"Could not get command runner: {e}")
                return None
        return self._command_runner
    
    def execute_command(self, command: str, args: List[str] = None, count: int = None, 
                       safely: bool = True) -> CommandResult:
        """Execute a qutebrowser command.
        
        Args:
            command: The command name to execute
            args: List of arguments for the command
            count: Count parameter for the command
            safely: Whether to handle errors gracefully
            
        Returns:
            CommandResult object with execution details
        """
        if not self._check_availability():
            return CommandResult(
                success=False,
                command=command,
                args=args or [],
                error="Qutebrowser not available"
            )
        
        runner = self._get_command_runner()
        if not runner:
            return CommandResult(
                success=False,
                command=command,
                args=args or [],
                error="Could not get command runner"
            )
        
        # Construct the full command string
        if args:
            # Properly quote arguments that contain spaces
            quoted_args = []
            for arg in args:
                if ' ' in str(arg) and not (arg.startswith('"') and arg.endswith('"')):
                    quoted_args.append(f'"{arg}"')
                else:
                    quoted_args.append(str(arg))
            command_text = f"{command} {' '.join(quoted_args)}"
        else:
            command_text = command
        
        try:
            log.commands.debug(f"Executing command: {command_text}")
            runner.run(command_text, count=count, safely=safely)
            
            result = CommandResult(
                success=True,
                command=command,
                args=args or [],
                message=f"Command '{command_text}' executed successfully"
            )
        except cmdexc.Error as e:
            result = CommandResult(
                success=False,
                command=command,
                args=args or [],
                error=f"Command error: {str(e)}"
            )
        except Exception as e:
            result = CommandResult(
                success=False,
                command=command,
                args=args or [],
                error=f"Unexpected error: {str(e)}"
            )
        
        # Store result in history (keep last 10)
        self._last_results.append(result)
        if len(self._last_results) > 10:
            self._last_results.pop(0)
            
        return result
    
    def get_command_history(self) -> List[CommandResult]:
        """Get the history of executed commands."""
        return self._last_results.copy()
    
    # Navigation Commands
    def open_url(self, url: str, bg: bool = False, tab: bool = False, 
                 window: bool = False, private: bool = False, related: bool = False,
                 count: int = None) -> CommandResult:
        """Open a URL in the current tab or a new tab/window.
        
        Args:
            url: The URL to open
            bg: Open in a new background tab
            tab: Open in a new tab
            window: Open in a new window  
            private: Open in private browsing mode
            related: Position new tab as related to current one
            count: Tab index to open URL in
            
        Returns:
            CommandResult object
        """
        args = []
        if bg:
            args.append("--bg")
        if tab:
            args.append("--tab")
        if window:
            args.append("--window")
        if private:
            args.append("--private")
        if related:
            args.append("--related")
        args.append(url)
        
        return self.execute_command("open", args, count=count)
    
    def reload_page(self, force: bool = False, count: int = None) -> CommandResult:
        """Reload the current tab or specified tab.
        
        Args:
            force: Bypass page cache
            count: Tab index to reload
            
        Returns:
            CommandResult object
        """
        args = []
        if force:
            args.append("--force")
            
        return self.execute_command("reload", args, count=count)
    
    def stop_loading(self, count: int = None) -> CommandResult:
        """Stop loading in the current tab or specified tab.
        
        Args:
            count: Tab index to stop
            
        Returns:
            CommandResult object
        """
        return self.execute_command("stop", count=count)
    
    def go_back(self, tab: bool = False, bg: bool = False, window: bool = False,
                count: int = None, index: int = None, quiet: bool = False) -> CommandResult:
        """Go back in the history of the current tab.
        
        Args:
            tab: Go back in a new tab
            bg: Go back in a background tab
            window: Go back in a new window
            count: How many pages to go back
            index: Which page to go back to
            quiet: Don't show error if at beginning of history
            
        Returns:
            CommandResult object
        """
        args = []
        if tab:
            args.append("--tab")
        if bg:
            args.append("--bg")
        if window:
            args.append("--window")
        if quiet:
            args.append("--quiet")
        if index is not None:
            args.extend(["--index", str(index)])
            
        return self.execute_command("back", args, count=count)
    
    def go_forward(self, tab: bool = False, bg: bool = False, window: bool = False,
                   count: int = None, index: int = None, quiet: bool = False) -> CommandResult:
        """Go forward in the history of the current tab.
        
        Args:
            tab: Go forward in a new tab
            bg: Go forward in a background tab
            window: Go forward in a new window
            count: How many pages to go forward
            index: Which page to go forward to
            quiet: Don't show error if at end of history
            
        Returns:
            CommandResult object
        """
        args = []
        if tab:
            args.append("--tab")
        if bg:
            args.append("--bg")
        if window:
            args.append("--window")
        if quiet:
            args.append("--quiet")
        if index is not None:
            args.extend(["--index", str(index)])
            
        return self.execute_command("forward", args, count=count)
    
    def go_home(self) -> CommandResult:
        """Open main startpage in current tab.
        
        Returns:
            CommandResult object
        """
        return self.execute_command("home")
    
    def navigate(self, where: str, tab: bool = False, bg: bool = False, 
                 window: bool = False, count: int = None) -> CommandResult:
        """Open typical prev/next links or navigate using the URL path.
        
        Args:
            where: What to open (prev/next/up/increment/decrement/strip)
            tab: Open in a new tab
            bg: Open in a background tab
            window: Open in a new window
            count: Number for increment/decrement/up
            
        Returns:
            CommandResult object
        """
        args = []
        if tab:
            args.append("--tab")
        if bg:
            args.append("--bg")
        if window:
            args.append("--window")
        args.append(where)
        
        return self.execute_command("navigate", args, count=count)
    
    # Tab Management Commands
    def tab_close(self, prev: bool = False, next_: bool = False, opposite: bool = False,
                  force: bool = False, count: int = None) -> CommandResult:
        """Close the current tab or specified tab.
        
        Args:
            prev: Force selecting the tab before current tab
            next_: Force selecting the tab after current tab
            opposite: Force selecting tab in opposite direction
            force: Avoid confirmation for pinned tabs
            count: Tab index to close
            
        Returns:
            CommandResult object
        """
        args = []
        if prev:
            args.append("--prev")
        if next_:
            args.append("--next")
        if opposite:
            args.append("--opposite")
        if force:
            args.append("--force")
            
        return self.execute_command("tab-close", args, count=count)
    
    def tab_new(self, url: str = None, bg: bool = False, window: bool = False,
                private: bool = False, related: bool = False) -> CommandResult:
        """Open a new tab, optionally with a URL.
        
        Args:
            url: URL to open in the new tab
            bg: Open in background
            window: Open in new window instead
            private: Open in private window
            related: Position as related to current tab
            
        Returns:
            CommandResult object
        """
        if url:
            return self.open_url(url, bg=bg, tab=True, window=window, 
                               private=private, related=related)
        else:
            args = []
            if bg:
                args.append("--bg")
            if window:
                args.append("--window")
            if private:
                args.append("--private")
            if related:
                args.append("--related")
                
            return self.execute_command("open", ["--tab"] + args)
    
    def tab_select(self, index: Union[int, str], count: int = None) -> CommandResult:
        """Select tab by index or url/title best match.
        
        Args:
            index: The tab index or identifier to focus
            count: The tab index to focus
            
        Returns:
            CommandResult object
        """
        args = [str(index)]
        return self.execute_command("tab-select", args, count=count)
    
    def tab_focus(self, index: Union[int, str] = None, count: int = None, 
                  no_last: bool = False) -> CommandResult:
        """Select the tab given as argument.
        
        Args:
            index: Tab index to focus (last, stack-next, etc.)
            count: Tab index to focus
            no_last: Avoid focusing last tab if already focused
            
        Returns:
            CommandResult object
        """
        args = []
        if no_last:
            args.append("--no-last")
        if index is not None:
            args.append(str(index))
            
        return self.execute_command("tab-focus", args, count=count)
    
    def tab_next(self, count: int = None) -> CommandResult:
        """Switch to the next tab.
        
        Args:
            count: How many tabs to switch forward
            
        Returns:
            CommandResult object
        """
        return self.execute_command("tab-next", count=count)
    
    def tab_prev(self, count: int = None) -> CommandResult:
        """Switch to the previous tab.
        
        Args:
            count: How many tabs to switch back
            
        Returns:
            CommandResult object
        """
        return self.execute_command("tab-prev", count=count)
    
    def tab_move(self, index: Union[str, int] = None, count: int = None) -> CommandResult:
        """Move the current tab to a new position.
        
        Args:
            index: +, -, start, end, or tab index
            count: Offset for relative movement or new position
            
        Returns:
            CommandResult object
        """
        args = []
        if index is not None:
            args.append(str(index))
            
        return self.execute_command("tab-move", args, count=count)
    
    def tab_clone(self, bg: bool = False, window: bool = False, 
                  private: bool = False) -> CommandResult:
        """Duplicate the current tab.
        
        Args:
            bg: Open in a background tab
            window: Open in a new window
            private: Open in a new private window
            
        Returns:
            CommandResult object
        """
        args = []
        if bg:
            args.append("--bg")
        if window:
            args.append("--window")
        if private:
            args.append("--private")
            
        return self.execute_command("tab-clone", args)
    
    def tab_pin(self, count: int = None) -> CommandResult:
        """Pin/Unpin the current tab or specified tab.
        
        Args:
            count: Tab index to pin/unpin
            
        Returns:
            CommandResult object
        """
        return self.execute_command("tab-pin", count=count)
    
    def tab_mute(self, count: int = None) -> CommandResult:
        """Mute/unmute the current tab or specified tab.
        
        Args:
            count: Tab index to mute/unmute
            
        Returns:
            CommandResult object
        """
        return self.execute_command("tab-mute", count=count)
    
    def tab_only(self, prev: bool = False, next_: bool = False, 
                 pinned: str = "prompt", force: bool = False) -> CommandResult:
        """Close all tabs except for the current one.
        
        Args:
            prev: Keep tabs before the current
            next_: Keep tabs after the current
            pinned: What to do with pinned tabs (prompt/close/keep)
            force: Avoid confirmation for pinned tabs
            
        Returns:
            CommandResult object
        """
        args = []
        if prev:
            args.append("--prev")
        if next_:
            args.append("--next")
        if pinned != "prompt":
            args.extend(["--pinned", pinned])
        if force:
            args.append("--force")
            
        return self.execute_command("tab-only", args)
    
    # Page Interaction Commands
    def scroll(self, direction: str, count: int = None) -> CommandResult:
        """Scroll the current tab in the given direction.
        
        Args:
            direction: Direction to scroll (up/down/left/right/top/bottom/page-up/page-down)
            count: Multiplier for scroll amount
            
        Returns:
            CommandResult object
        """
        args = [direction]
        return self.execute_command("scroll", args, count=count)
    
    def scroll_px(self, dx: int, dy: int, count: int = None) -> CommandResult:
        """Scroll the current tab by specific pixel amounts.
        
        Args:
            dx: Horizontal scroll amount
            dy: Vertical scroll amount
            count: Multiplier
            
        Returns:
            CommandResult object
        """
        args = [str(dx), str(dy)]
        return self.execute_command("scroll-px", args, count=count)
    
    def scroll_to_perc(self, perc: int, horizontal: bool = False, 
                       count: int = None) -> CommandResult:
        """Scroll to a specific percentage of the page.
        
        Args:
            perc: Percentage to scroll to
            horizontal: Scroll horizontally instead of vertically
            count: Percentage to scroll to
            
        Returns:
            CommandResult object
        """
        args = []
        if horizontal:
            args.append("--horizontal")
        args.append(str(perc))
        
        return self.execute_command("scroll-to-perc", args, count=count)
    
    def zoom_in(self, count: int = None, quiet: bool = False) -> CommandResult:
        """Increase the zoom level for the current tab.
        
        Args:
            count: How many steps to zoom in
            quiet: Don't show zoom level message
            
        Returns:
            CommandResult object
        """
        args = []
        if quiet:
            args.append("--quiet")
            
        return self.execute_command("zoom-in", args, count=count)
    
    def zoom_out(self, count: int = None, quiet: bool = False) -> CommandResult:
        """Decrease the zoom level for the current tab.
        
        Args:
            count: How many steps to zoom out
            quiet: Don't show zoom level message
            
        Returns:
            CommandResult object
        """
        args = []
        if quiet:
            args.append("--quiet")
            
        return self.execute_command("zoom-out", args, count=count)
    
    def zoom(self, level: Union[int, str], count: int = None, 
             quiet: bool = False) -> CommandResult:
        """Set the zoom level for the current tab.
        
        Args:
            level: Zoom percentage to set
            count: Zoom percentage to set
            quiet: Don't show zoom level message
            
        Returns:
            CommandResult object
        """
        args = []
        if quiet:
            args.append("--quiet")
        args.append(str(level))
        
        return self.execute_command("zoom", args, count=count)
    
    def search(self, text: str = None, reverse: bool = False) -> CommandResult:
        """Search for text on the current page.
        
        Args:
            text: The text to search for
            reverse: Reverse search direction
            
        Returns:
            CommandResult object
        """
        args = []
        if reverse:
            args.append("--reverse")
        if text:
            args.append(text)
            
        return self.execute_command("search", args)
    
    def search_next(self, count: int = None) -> CommandResult:
        """Continue search to the next term.
        
        Args:
            count: How many elements to ignore
            
        Returns:
            CommandResult object
        """
        return self.execute_command("search-next", count=count)
    
    def search_prev(self, count: int = None) -> CommandResult:
        """Continue search to the previous term.
        
        Args:
            count: How many elements to ignore
            
        Returns:
            CommandResult object
        """
        return self.execute_command("search-prev", count=count)
    
    def click_element(self, filter_type: str, value: str = None) -> CommandResult:
        """Click on an element matching the given filter.
        
        Args:
            filter_type: Filter type (id/css/position/focused)
            value: Filter value (required except for 'focused')
            
        Returns:
            CommandResult object
        """
        args = [filter_type]
        if value is not None:
            args.append(value)
            
        return self.execute_command("click-element", args)
    
    def insert_text(self, text: str) -> CommandResult:
        """Insert text at the current cursor position.
        
        Args:
            text: The text to insert
            
        Returns:
            CommandResult object
        """
        args = [text]
        return self.execute_command("insert-text", args)
    
    def fake_key(self, keystring: str, global_: bool = False) -> CommandResult:
        """Send a fake keypress to the website or qutebrowser.
        
        Args:
            keystring: The keystring to send
            global_: Send keys to qutebrowser UI instead of website
            
        Returns:
            CommandResult object
        """
        args = []
        if global_:
            args.append("--global")
        args.append(keystring)
        
        return self.execute_command("fake-key", args)
    
    # Configuration Commands
    def set_config(self, option: str, value: str, pattern: str = None, 
                   temp: bool = False, print_: bool = False) -> CommandResult:
        """Set a configuration option.
        
        Args:
            option: The name of the option
            value: The value to set
            pattern: URL pattern to use
            temp: Set value temporarily until qutebrowser is closed
            print_: Print the value after setting
            
        Returns:
            CommandResult object
        """
        args = []
        if pattern:
            args.extend(["--pattern", pattern])
        if temp:
            args.append("--temp")
        if print_:
            args.append("--print")
        args.extend([option, value])
        
        return self.execute_command("set", args)
    
    def bind_key(self, key: str, command: str, mode: str = None, 
                 pattern: str = None) -> CommandResult:
        """Bind a key to a command.
        
        Args:
            key: The key to bind
            command: The command to bind to
            mode: The mode to bind in
            pattern: URL pattern to use
            
        Returns:
            CommandResult object
        """
        args = []
        if mode:
            args.extend(["--mode", mode])
        if pattern:
            args.extend(["--pattern", pattern])
        args.extend([key, command])
        
        return self.execute_command("bind", args)
    
    # Window Management Commands
    def fullscreen(self, leave: bool = False, enter: bool = False) -> CommandResult:
        """Toggle fullscreen mode.
        
        Args:
            leave: Only leave fullscreen if entered by page
            enter: Activate fullscreen and don't toggle
            
        Returns:
            CommandResult object
        """
        args = []
        if leave:
            args.append("--leave")
        if enter:
            args.append("--enter")
            
        return self.execute_command("fullscreen", args)
    
    def spawn(self, cmdline: str, userscript: bool = False, verbose: bool = False,
              output: bool = False, output_messages: bool = False, 
              detach: bool = False, count: int = None) -> CommandResult:
        """Spawn an external command.
        
        Args:
            cmdline: The commandline to execute
            userscript: Run as a userscript
            verbose: Show notifications when command started/exited
            output: Show output in a new tab
            output_messages: Show output as messages
            detach: Detach command from qutebrowser
            count: Given to userscripts as $QUTE_COUNT
            
        Returns:
            CommandResult object
        """
        args = []
        if userscript:
            args.append("--userscript")
        if verbose:
            args.append("--verbose")
        if output:
            args.append("--output")
        if output_messages:
            args.append("--output-messages")
        if detach:
            args.append("--detach")
        args.append(cmdline)
        
        return self.execute_command("spawn", args, count=count)
    
    # Utility Commands
    def yank(self, what: str = "url", sel: bool = False, keep: bool = False,
             quiet: bool = False, inline: str = None) -> CommandResult:
        """Yank (copy) something to the clipboard or primary selection.
        
        Args:
            what: What to yank (selection/url/pretty-url/title/domain/inline)
            sel: Use primary selection instead of clipboard
            keep: Stay in visual mode after yanking selection
            quiet: Don't show information message
            inline: Text to yank if what is inline
            
        Returns:
            CommandResult object
        """
        args = []
        if sel:
            args.append("--sel")
        if keep:
            args.append("--keep")
        if quiet:
            args.append("--quiet")
        if inline:
            args.extend(["--inline", inline])
        else:
            args.append(what)
        
        return self.execute_command("yank", args)
    
    def undo(self, window: bool = False, count: int = None, 
             depth: int = None) -> CommandResult:
        """Re-open the last closed tab(s) or window.
        
        Args:
            window: Re-open the last closed window
            count: How deep in undo stack to find tabs
            depth: Same as count but as argument
            
        Returns:
            CommandResult object
        """
        args = []
        if window:
            args.append("--window")
        if depth is not None:
            args.extend(["--depth", str(depth)])
            
        return self.execute_command("undo", args, count=count)
    
    def quit_browser(self, save: bool = False, session: str = None) -> CommandResult:
        """Quit qutebrowser.
        
        Args:
            save: Save open windows even if auto_save.session is off
            session: Session name to save
            
        Returns:
            CommandResult object
        """
        args = []
        if save:
            args.append("--save")
        if session:
            args.append(session)
            
        return self.execute_command("quit", args)
    
    # JavaScript Execution
    def execute_javascript(self, js_code: str, file: bool = False, url: bool = False,
                          quiet: bool = False, world: str = None) -> CommandResult:
        """Evaluate a JavaScript string.
        
        Args:
            js_code: The string/file to evaluate
            file: Interpret js_code as a path to a file
            url: Interpret js_code as a javascript: URL
            quiet: Don't show resulting JS object
            world: JavaScript world to run in
            
        Returns:
            CommandResult object
        """
        args = []
        if file:
            args.append("--file")
        if url:
            args.append("--url")
        if quiet:
            args.append("--quiet")
        if world:
            args.extend(["--world", world])
        args.append(js_code)
        
        return self.execute_command("jseval", args)
    
    # Advanced Interaction Methods
    def perform_action_sequence(self, actions: List[Dict[str, Any]]) -> List[CommandResult]:
        """Perform a sequence of actions.
        
        Args:
            actions: List of action dictionaries with 'method', 'args', 'kwargs'
            
        Returns:
            List of CommandResult objects
        """
        results = []
        for action in actions:
            method_name = action.get('method')
            args = action.get('args', [])
            kwargs = action.get('kwargs', {})
            
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                try:
                    result = method(*args, **kwargs)
                    results.append(result)
                    if not result.success:
                        # Stop on first failure unless specified otherwise
                        break
                except Exception as e:
                    result = CommandResult(
                        success=False,
                        command=method_name,
                        args=args,
                        error=f"Exception in action sequence: {str(e)}"
                    )
                    results.append(result)
                    break
            else:
                result = CommandResult(
                    success=False,
                    command=method_name,
                    args=args,
                    error=f"Unknown method: {method_name}"
                )
                results.append(result)
                break
        
        return results
    
    def get_available_commands(self) -> Dict[str, BrowserAction]:
        """Get a dictionary of all available browser actions.
        
        Returns:
            Dictionary mapping command names to BrowserAction objects
        """
        commands = {
            # Navigation
            'open_url': BrowserAction('open', 'Open a URL', requires_url=True),
            'reload_page': BrowserAction('reload', 'Reload current page'),
            'stop_loading': BrowserAction('stop', 'Stop page loading'),
            'go_back': BrowserAction('back', 'Go back in history'),
            'go_forward': BrowserAction('forward', 'Go forward in history'),
            'go_home': BrowserAction('home', 'Go to home page'),
            'navigate': BrowserAction('navigate', 'Navigate using typical prev/next links'),
            
            # Tab management
            'tab_close': BrowserAction('tab-close', 'Close tab'),
            'tab_new': BrowserAction('open', 'Open new tab'),
            'tab_select': BrowserAction('tab-select', 'Select tab by index'),
            'tab_focus': BrowserAction('tab-focus', 'Focus specific tab'),
            'tab_next': BrowserAction('tab-next', 'Switch to next tab'),
            'tab_prev': BrowserAction('tab-prev', 'Switch to previous tab'),
            'tab_move': BrowserAction('tab-move', 'Move tab position'),
            'tab_clone': BrowserAction('tab-clone', 'Clone current tab'),
            'tab_pin': BrowserAction('tab-pin', 'Pin/unpin tab'),
            'tab_mute': BrowserAction('tab-mute', 'Mute/unmute tab'),
            'tab_only': BrowserAction('tab-only', 'Close all other tabs'),
            
            # Page interaction
            'scroll': BrowserAction('scroll', 'Scroll page'),
            'scroll_px': BrowserAction('scroll-px', 'Scroll by pixels'),
            'scroll_to_perc': BrowserAction('scroll-to-perc', 'Scroll to percentage'),
            'zoom_in': BrowserAction('zoom-in', 'Zoom in'),
            'zoom_out': BrowserAction('zoom-out', 'Zoom out'),
            'zoom': BrowserAction('zoom', 'Set zoom level'),
            'search': BrowserAction('search', 'Search on page'),
            'search_next': BrowserAction('search-next', 'Next search result'),
            'search_prev': BrowserAction('search-prev', 'Previous search result'),
            'click_element': BrowserAction('click-element', 'Click page element'),
            'insert_text': BrowserAction('insert-text', 'Insert text'),
            'fake_key': BrowserAction('fake-key', 'Send fake keypress'),
            
            # Configuration
            'set_config': BrowserAction('set', 'Set configuration option'),
            'bind_key': BrowserAction('bind', 'Bind key to command'),
            
            # Window management
            'fullscreen': BrowserAction('fullscreen', 'Toggle fullscreen'),
            'spawn': BrowserAction('spawn', 'Spawn external command'),
            
            # Utilities
            'yank': BrowserAction('yank', 'Copy to clipboard'),
            'undo': BrowserAction('undo', 'Undo tab close'),
            'quit_browser': BrowserAction('quit', 'Quit browser'),
            'execute_javascript': BrowserAction('jseval', 'Execute JavaScript'),
        }
        
        return commands


# Convenience functions for easy access
def create_browser_controller(window_id: int = 0) -> BrowserControlTools:
    """Create a new browser control tools instance.
    
    Args:
        window_id: Window ID to control
        
    Returns:
        BrowserControlTools instance
    """
    return BrowserControlTools(window_id)


def execute_browser_command(command: str, args: List[str] = None, 
                           window_id: int = 0, count: int = None) -> CommandResult:
    """Execute a browser command directly.
    
    Args:
        command: Command name
        args: Command arguments
        window_id: Window ID to control
        count: Count parameter
        
    Returns:
        CommandResult object
    """
    controller = BrowserControlTools(window_id)
    return controller.execute_command(command, args, count)


def open_url(url: str, bg: bool = False, tab: bool = False, 
             window_id: int = 0) -> CommandResult:
    """Convenience function to open a URL.
    
    Args:
        url: URL to open
        bg: Open in background
        tab: Open in new tab
        window_id: Window ID to control
        
    Returns:
        CommandResult object
    """
    controller = BrowserControlTools(window_id)
    return controller.open_url(url, bg=bg, tab=tab)


def close_tab(count: int = None, window_id: int = 0) -> CommandResult:
    """Convenience function to close a tab.
    
    Args:
        count: Tab index to close
        window_id: Window ID to control
        
    Returns:
        CommandResult object
    """
    controller = BrowserControlTools(window_id)
    return controller.tab_close(count=count)


def switch_tab(index: int, window_id: int = 0) -> CommandResult:
    """Convenience function to switch to a tab.
    
    Args:
        index: Tab index to switch to
        window_id: Window ID to control
        
    Returns:
        CommandResult object
    """
    controller = BrowserControlTools(window_id)
    return controller.tab_focus(index)
