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
    from qutebrowser.utils import objreg
    from qutebrowser.browser import browsertab
    from qutebrowser.mainwindow import tabbedbrowser
    from qutebrowser.qt.core import QUrl
    from qutebrowser.qt.widgets import QApplication
except ImportError as e:
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
        self._browser = None
        self._active_window_id = None
        
    def _get_app_instance(self):
        """Get the qutebrowser application instance."""
        if self._app is None:
            try:
                # Try to get the app from objects
                if hasattr(objects, 'qapp') and objects.qapp is not None:
                    self._app = objects.qapp
                else:
                    # Try to get from QApplication
                    self._app = QApplication.instance()
            except Exception as e:
                print(f"Warning: Could not get app instance: {e}")
                return None
        return self._app
    
    def _get_browser_instance(self, window_id: int = 0):
        """Get the browser instance for a specific window."""
        try:
            if self._browser is None:
                # Try to get from object registry
                browser = objreg.get('tabbed-browser', scope='window', window=window_id)
                if browser:
                    self._browser = browser
                    self._active_window_id = window_id
            return self._browser
        except Exception as e:
            print(f"Warning: Could not get browser instance: {e}")
            return None
    
    def get_current_tab_info(self, window_id: int = 0) -> Optional[TabInfo]:
        """Get information about the currently active tab."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return None
                
            current_tab = browser.currentWidget()
            if not current_tab:
                return None
                
            # Get tab index
            tab_index = browser.indexOf(current_tab)
            
            # Get URL and title
            url = current_tab.url().toString() if current_tab.url() else ""
            title = current_tab.title() or "Untitled"
            
            # Check if loading
            is_loading = current_tab.isLoading()
            
            # Check if pinned
            is_pinned = getattr(current_tab, 'isPinned', lambda: False)()
            
            # Check navigation state
            can_go_back = current_tab.history().canGoBack()
            can_go_forward = current_tab.history().canGoForward()
            
            # Get scroll position if available
            scroll_position = None
            try:
                if hasattr(current_tab, 'scrollPosition'):
                    pos = current_tab.scrollPosition()
                    scroll_position = {'x': pos.x(), 'y': pos.y()}
            except:
                pass
                
            # Get zoom level if available
            zoom_level = None
            try:
                if hasattr(current_tab, 'zoomFactor'):
                    zoom_level = current_tab.zoomFactor()
            except:
                pass
            
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
            print(f"Error getting current tab info: {e}")
            return None
    
    def get_all_tabs_info(self, window_id: int = 0) -> List[TabInfo]:
        """Get information about all tabs in the browser."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return []
                
            tabs_info = []
            for i in range(browser.count()):
                tab = browser.widget(i)
                if not tab:
                    continue
                    
                # Get basic tab info
                url = tab.url().toString() if tab.url() else ""
                title = tab.title() or "Untitled"
                is_loading = tab.isLoading()
                is_pinned = getattr(tab, 'isPinned', lambda: False)()
                
                # Check if this is the active tab
                is_active = (browser.currentIndex() == i)
                
                # Get navigation state
                can_go_back = tab.history().canGoBack()
                can_go_forward = tab.history().canGoForward()
                
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
            print(f"Error getting all tabs info: {e}")
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
            active_tab_index = browser.currentIndex()
            total_tabs = browser.count()
            
            return WindowState(
                window_id=window_id,
                is_fullscreen=is_fullscreen,
                is_maximized=is_maximized,
                geometry=geometry,
                active_tab_index=active_tab_index,
                total_tabs=total_tabs
            )
            
        except Exception as e:
            print(f"Error getting window state: {e}")
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
            print(f"Error getting navigation state: {e}")
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
            print(f"Error getting browser metrics: {e}")
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
            print(f"Error getting comprehensive state: {e}")
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

