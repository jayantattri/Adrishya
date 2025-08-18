"""
Browser State Information Tools for Qutebrowser

This module provides tools to get information about the current state of qutebrowser,
including tab information, window state, navigation state, and more.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from qutebrowser.misc import objects
    from qutebrowser.utils import objreg, log
    from qutebrowser.browser import browsertab
    from qutebrowser.mainwindow import tabbedbrowser
    from qutebrowser.qt.core import QUrl
    from qutebrowser.qt.widgets import QApplication
    QUTEBROWSER_AVAILABLE = True
except ImportError as e:
    QUTEBROWSER_AVAILABLE = False
    # Create minimal logging for when qutebrowser is not available
    class DummyLog:
        def warning(self, msg): print(f"Warning: {msg}")
        def error(self, msg): print(f"Error: {msg}")
        def debug(self, msg): print(f"Debug: {msg}")
    
    class LogContainer:
        misc = DummyLog()
    
    log = LogContainer()
    objects = None
    objreg = None
    QApplication = None
    print(f"Warning: Could not import qutebrowser modules: {e}")
    print("This module should be run from within qutebrowser or with proper imports")


@dataclass
class TabInfo:
    """Information about a browser tab."""
    index: int
    url: str
    title: str
    is_active: bool
    is_loading: bool
    is_pinned: bool
    can_go_back: bool
    can_go_forward: bool
    scroll_position: Optional[Dict[str, int]] = None
    zoom_level: Optional[float] = None


@dataclass
class WindowState:
    """Information about the browser window."""
    window_id: int
    is_fullscreen: bool
    is_maximized: bool
    geometry: Optional[Dict[str, int]] = None
    active_tab_index: int = 0
    total_tabs: int = 0


@dataclass
class NavigationState:
    """Information about navigation state."""
    can_go_back: bool
    can_go_forward: bool
    current_url: str
    page_title: str
    is_loading: bool
    load_progress: Optional[int] = None


@dataclass
class BrowserMetrics:
    """Performance and resource metrics."""
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    network_requests: Optional[int] = None
    page_load_time: Optional[float] = None


class BrowserStateTools:
    """Main class for getting browser state information."""
    
    def __init__(self):
        """Initialize the browser state tools."""
        self._app = None
        self._browsers = {}  # Cache browsers by window_id
        
    def _check_availability(self) -> bool:
        """Check if qutebrowser is available."""
        if not QUTEBROWSER_AVAILABLE:
            log.misc.warning("Qutebrowser modules not available")
            return False
        return True
        
    def _get_app_instance(self):
        """Get the qutebrowser application instance."""
        if not self._check_availability():
            return None
            
        if self._app is None:
            try:
                # Try to get the app from objects
                if objects and hasattr(objects, 'qapp') and objects.qapp is not None:
                    self._app = objects.qapp
                elif QApplication:
                    # Try to get from QApplication
                    self._app = QApplication.instance()
            except Exception as e:
                log.misc.warning(f"Could not get app instance: {e}")
                return None
        return self._app
    
    def _get_browser_instance(self, window_id: int = 0):
        """Get the browser instance for a specific window."""
        if not self._check_availability():
            return None
            
        try:
            # Check cache first
            if window_id in self._browsers:
                browser = self._browsers[window_id]
                # Verify browser is still valid
                if browser and hasattr(browser, 'widget') and browser.widget:
                    return browser
                else:
                    # Remove invalid browser from cache
                    del self._browsers[window_id]
            
            # Try to get from object registry
            if not objreg:
                log.misc.debug("objreg not available")
                return None
                
            # Try multiple approaches to get the browser
            browser = None
            
            # First try with specific window_id
            try:
                browser = objreg.get('tabbed-browser', scope='window', window=window_id)
                log.misc.debug(f"Got browser for window {window_id}")
            except Exception as e:
                log.misc.debug(f"Could not get browser for window {window_id}: {e}")
                
                # Try with current window
                try:
                    browser = objreg.get('tabbed-browser', scope='window', window='current')
                    log.misc.debug("Got browser for current window")
                except Exception as e:
                    log.misc.debug(f"Could not get current window browser: {e}")
                    
                    # Try with last-focused window
                    try:
                        browser = objreg.get('tabbed-browser', scope='window', window='last-focused')
                        log.misc.debug("Got browser for last-focused window")
                    except Exception as e:
                        log.misc.debug(f"Could not get last-focused window browser: {e}")
            
            if browser:
                self._browsers[window_id] = browser
                return browser
            else:
                log.misc.debug(f"No browser found for window_id: {window_id}")
                return None
                
        except Exception as e:
            log.misc.warning(f"Could not get browser instance: {e}")
            return None
    
    def get_current_tab_info(self, window_id: int = 0) -> Optional[TabInfo]:
        """Get information about the currently active tab."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return None
                
            current_tab = browser.widget.currentWidget()
            if not current_tab:
                return None
                
            # Get tab index
            tab_index = browser.widget.indexOf(current_tab)
            
            # Get URL and title safely
            url = ""
            try:
                if hasattr(current_tab, 'url') and current_tab.url():
                    url = current_tab.url().toString()
            except Exception as e:
                log.misc.debug(f"Could not get tab URL: {e}")
                
            title = "Untitled"
            try:
                if hasattr(current_tab, 'title') and current_tab.title():
                    title = current_tab.title()
            except Exception as e:
                log.misc.debug(f"Could not get tab title: {e}")
            
            # Check if loading
            is_loading = False
            try:
                if hasattr(current_tab, 'isLoading'):
                    is_loading = current_tab.isLoading()
            except Exception as e:
                log.misc.debug(f"Could not get loading state: {e}")
            
            # Check if pinned
            is_pinned = False
            try:
                if hasattr(current_tab, 'data') and hasattr(current_tab.data, 'pinned'):
                    is_pinned = current_tab.data.pinned
            except Exception as e:
                log.misc.debug(f"Could not get pinned state: {e}")
            
            # Check navigation state
            can_go_back = False
            can_go_forward = False
            try:
                if hasattr(current_tab, 'history'):
                    history = current_tab.history()
                    can_go_back = history.canGoBack()
                    can_go_forward = history.canGoForward()
            except Exception as e:
                log.misc.debug(f"Could not get navigation state: {e}")
            
            # Get scroll position if available
            scroll_position = None
            try:
                if hasattr(current_tab, 'scroller') and hasattr(current_tab.scroller, 'pos'):
                    pos = current_tab.scroller.pos
                    scroll_position = {'x': pos.x(), 'y': pos.y()}
            except Exception as e:
                log.misc.debug(f"Could not get scroll position: {e}")
                
            # Get zoom level if available
            zoom_level = None
            try:
                if hasattr(current_tab, 'zoom') and hasattr(current_tab.zoom, 'factor'):
                    zoom_level = current_tab.zoom.factor
            except Exception as e:
                log.misc.debug(f"Could not get zoom level: {e}")
            
            return TabInfo(
                index=tab_index,
                url=url,
                title=title,
                is_active=True,
                is_loading=is_loading,
                is_pinned=is_pinned,
                can_go_back=can_go_back,
                can_go_forward=can_go_forward,
                scroll_position=scroll_position,
                zoom_level=zoom_level
            )
            
        except Exception as e:
            log.misc.error(f"Error getting current tab info: {e}")
            return None
    
    def get_all_tabs_info(self, window_id: int = 0) -> List[TabInfo]:
        """Get information about all tabs in the browser."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                log.misc.warning(f"No browser instance found for window_id: {window_id}")
                return []
                
            log.misc.debug(f"Browser instance found: {type(browser)}")
            log.misc.debug(f"Browser widget: {type(browser.widget)}")
            log.misc.debug(f"Widget count: {browser.widget.count()}")
                
            tabs_info = []
            tab_count = browser.widget.count()
            log.misc.debug(f"Found {tab_count} tabs in browser")
            
            for i in range(tab_count):
                tab = browser.widget.widget(i)
                if not tab:
                    continue
                    
                # Get basic tab info
                url = tab.url().toString() if tab.url() else ""
                title = tab.title() or "Untitled"
                is_loading = getattr(tab, 'isLoading', lambda: False)()
                is_pinned = getattr(tab, 'isPinned', lambda: False)()
                
                # Check if this is the active tab
                is_active = (browser.widget.currentIndex() == i)
                
                # Get navigation state
                try:
                    history = tab.history()
                    can_go_back = history.canGoBack() if hasattr(history, 'canGoBack') else False
                    can_go_forward = history.canGoForward() if hasattr(history, 'canGoForward') else False
                except:
                    can_go_back = False
                    can_go_forward = False
                
                tab_info = TabInfo(
                    index=i,
                    url=url,
                    title=title,
                    is_active=is_active,
                    is_loading=is_loading,
                    is_pinned=is_pinned,
                    can_go_back=can_go_back,
                    can_go_forward=can_go_forward
                )
                tabs_info.append(tab_info)
                
            return tabs_info
            
        except Exception as e:
            log.misc.error(f"Error getting all tabs info: {e}")
            return []
    
    def get_window_state(self, window_id: int = 0) -> Optional[WindowState]:
        """Get information about the browser window state."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return None
                
            # Get window information
            window = browser.window()
            if not window:
                return None
                
            # Check window state
            is_fullscreen = window.isFullScreen()
            is_maximized = window.isMaximized()
            
            # Get geometry
            geometry = None
            try:
                geo = window.geometry()
                geometry = {
                    'x': geo.x(),
                    'y': geo.y(),
                    'width': geo.width(),
                    'height': geo.height()
                }
            except:
                pass
                
            # Get tab information
            active_tab_index = browser.widget.currentIndex()
            total_tabs = browser.widget.count()
            
            return WindowState(
                window_id=window_id,
                is_fullscreen=is_fullscreen,
                is_maximized=is_maximized,
                geometry=geometry,
                active_tab_index=active_tab_index,
                total_tabs=total_tabs
            )
            
        except Exception as e:
            log.misc.error(f"Error getting window state: {e}")
            return None
    
    def get_navigation_state(self, window_id: int = 0) -> Optional[NavigationState]:
        """Get information about the current navigation state."""
        try:
            current_tab = self.get_current_tab_info(window_id)
            if not current_tab:
                return None
                
            return NavigationState(
                can_go_back=current_tab.can_go_back,
                can_go_forward=current_tab.can_go_forward,
                current_url=current_tab.url,
                page_title=current_tab.title,
                is_loading=current_tab.is_loading,
                load_progress=None  # Would need to implement progress tracking
            )
            
        except Exception as e:
            log.misc.error(f"Error getting navigation state: {e}")
            return None
    
    def get_browser_metrics(self, window_id: int = 0) -> Optional[BrowserMetrics]:
        """Get performance and resource metrics for the browser."""
        try:
            # This is a placeholder - actual metrics would need more sophisticated implementation
            # For now, return basic structure
            return BrowserMetrics(
                memory_usage=None,
                cpu_usage=None,
                network_requests=None,
                page_load_time=None
            )
            
        except Exception as e:
            log.misc.error(f"Error getting browser metrics: {e}")
            return None
    
    def get_comprehensive_state(self, window_id: int = 0) -> Dict[str, Any]:
        """Get comprehensive browser state information."""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'window_id': window_id,
                'current_tab': None,
                'all_tabs': [],
                'window_state': None,
                'navigation_state': None,
                'browser_metrics': None
            }
            
            # Get current tab info
            current_tab = self.get_current_tab_info(window_id)
            if current_tab:
                state['current_tab'] = asdict(current_tab)
            
            # Get all tabs info
            all_tabs = self.get_all_tabs_info(window_id)
            state['all_tabs'] = [asdict(tab) for tab in all_tabs]
            
            # Get window state
            window_state = self.get_window_state(window_id)
            if window_state:
                state['window_state'] = asdict(window_state)
            
            # Get navigation state
            navigation_state = self.get_navigation_state(window_id)
            if navigation_state:
                state['navigation_state'] = asdict(navigation_state)
            
            # Get browser metrics
            browser_metrics = self.get_browser_metrics(window_id)
            if browser_metrics:
                state['browser_metrics'] = asdict(browser_metrics)
            
            return state
            
        except Exception as e:
            log.misc.error(f"Error getting comprehensive state: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}


# Convenience functions for easy access
def get_current_tab_info(window_id: int = 0) -> Optional[TabInfo]:
    """Get information about the currently active tab."""
    tools = BrowserStateTools()
    return tools.get_current_tab_info(window_id)


def get_all_tabs_info(window_id: int = 0) -> List[TabInfo]:
    """Get information about all tabs in the browser."""
    tools = BrowserStateTools()
    return tools.get_all_tabs_info(window_id)


def get_window_state(window_id: int = 0) -> Optional[WindowState]:
    """Get information about the browser window state."""
    tools = BrowserStateTools()
    return tools.get_window_state(window_id)


def get_navigation_state(window_id: int = 0) -> Optional[NavigationState]:
    """Get information about the current navigation state."""
    tools = BrowserStateTools()
    return tools.get_navigation_state(window_id)


def get_browser_metrics(window_id: int = 0) -> Optional[BrowserMetrics]:
    """Get performance and resource metrics for the browser."""
    tools = BrowserStateTools()
    return tools.get_browser_metrics(window_id)


def get_comprehensive_state(window_id: int = 0) -> Dict[str, Any]:
    """Get comprehensive browser state information."""
    tools = BrowserStateTools()
    return tools.get_comprehensive_state(window_id)

