"""
Unified Browser State Tools for Qutebrowser

This module provides a unified interface to all browser state information tools,
combining tab information, page content, performance metrics, and more.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from .browser_state_tools import (
        BrowserStateTools, TabInfo, WindowState, NavigationState, BrowserMetrics,
        get_current_tab_info, get_all_tabs_info, get_window_state, 
        get_navigation_state, get_browser_metrics, get_comprehensive_state
    )
    from .page_content_tools import (
        PageContentTools, PageContent, LinkInfo, FormInfo,
        get_page_text_content, get_page_links, get_page_forms, get_page_images,
        get_page_headings, get_meta_tags, get_page_structure, get_comprehensive_page_content
    )
    from .performance_tools import (
        PerformanceTools, SystemMetrics, BrowserProcessMetrics, TabPerformanceMetrics,
        NetworkMetrics, PerformanceSnapshot,
        get_system_metrics, get_browser_process_metrics, get_tab_performance_metrics,
        get_network_metrics, get_performance_snapshot, get_performance_trends,
        get_resource_usage_summary
    )
except ImportError as e:
    print(f"Warning: Could not import browser state tools: {e}")
    # Create placeholder classes for when imports fail
    class TabInfo: pass
    class WindowState: pass
    class NavigationState: pass
    class BrowserMetrics: pass
    class PageContent: pass
    class SystemMetrics: pass
    class BrowserProcessMetrics: pass
    class PerformanceSnapshot: pass
    
    # Create placeholder tools classes
    class BrowserStateTools:
        def get_current_tab_info(self, *args): return None
        def get_all_tabs_info(self, *args): return []
        def get_window_state(self, *args): return None
        def get_navigation_state(self, *args): return None
        def get_browser_metrics(self, *args): return None
        
    class PageContentTools:
        def get_comprehensive_page_content(self, *args): return None
        
    class PerformanceTools:
        def get_performance_snapshot(self, *args): 
            return PerformanceSnapshot()
        def get_resource_usage_summary(self, *args): 
            return {'error': 'Performance tools not available'}
        def get_system_metrics(self, *args): 
            return None


@dataclass
class CompleteBrowserState:
    """Complete browser state information combining all tools."""
    timestamp: str
    window_id: int
    
    # Basic browser state
    current_tab: Optional[Dict[str, Any]] = None
    all_tabs: List[Dict[str, Any]] = None
    window_state: Optional[Dict[str, Any]] = None
    navigation_state: Optional[Dict[str, Any]] = None
    browser_metrics: Optional[Dict[str, Any]] = None
    
    # Page content
    page_content: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    system_metrics: Optional[Dict[str, Any]] = None
    browser_process: Optional[Dict[str, Any]] = None
    tab_performance: List[Dict[str, Any]] = None
    network_metrics: Optional[Dict[str, Any]] = None
    performance_score: Optional[float] = None
    
    # Summary information
    summary: Optional[Dict[str, Any]] = None


class UnifiedBrowserStateTools:
    """Unified interface to all browser state tools."""
    
    def __init__(self):
        """Initialize the unified browser state tools."""
        self.browser_tools = BrowserStateTools()
        self.page_content_tools = PageContentTools()
        self.performance_tools = PerformanceTools()
        
    def get_complete_browser_state(self, window_id: int = 0) -> CompleteBrowserState:
        """Get complete browser state information from all tools."""
        try:
            # Get basic browser state
            current_tab = self.browser_tools.get_current_tab_info(window_id)
            all_tabs = self.browser_tools.get_all_tabs_info(window_id)
            window_state = self.browser_tools.get_window_state(window_id)
            navigation_state = self.browser_tools.get_navigation_state(window_id)
            browser_metrics = self.browser_tools.get_browser_metrics(window_id)
            
            # Get page content
            page_content = self.page_content_tools.get_comprehensive_page_content(window_id)
            
            # Get performance metrics
            performance_snapshot = self.performance_tools.get_performance_snapshot(window_id)
            
            # Get resource usage summary
            resource_summary = self.performance_tools.get_resource_usage_summary(window_id)
            
            # Convert dataclasses to dictionaries for JSON serialization
            current_tab_dict = asdict(current_tab) if current_tab else None
            all_tabs_dict = [asdict(tab) for tab in all_tabs] if all_tabs else []
            window_state_dict = asdict(window_state) if window_state else None
            navigation_state_dict = asdict(navigation_state) if navigation_state else None
            browser_metrics_dict = asdict(browser_metrics) if browser_metrics else None
            
            page_content_dict = asdict(page_content) if page_content else None
            
            system_metrics_dict = asdict(performance_snapshot.system_metrics) if performance_snapshot.system_metrics else None
            browser_process_dict = asdict(performance_snapshot.browser_process) if performance_snapshot.browser_process else None
            tab_performance_dict = [asdict(tab) for tab in performance_snapshot.tab_performance] if performance_snapshot.tab_performance else []
            network_metrics_dict = asdict(performance_snapshot.network_metrics) if performance_snapshot.network_metrics else None
            
            return CompleteBrowserState(
                timestamp=datetime.now().isoformat(),
                window_id=window_id,
                current_tab=current_tab_dict,
                all_tabs=all_tabs_dict,
                window_state=window_state_dict,
                navigation_state=navigation_state_dict,
                browser_metrics=browser_metrics_dict,
                page_content=page_content_dict,
                system_metrics=system_metrics_dict,
                browser_process=browser_process_dict,
                tab_performance=tab_performance_dict,
                network_metrics=network_metrics_dict,
                performance_score=performance_snapshot.overall_score,
                summary=resource_summary
            )
            
        except Exception as e:
            print(f"Error getting complete browser state: {e}")
            return CompleteBrowserState(
                timestamp=datetime.now().isoformat(),
                window_id=window_id
            )
    
    def get_browser_overview(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a high-level overview of browser state."""
        try:
            complete_state = self.get_complete_browser_state(window_id)
            
            overview = {
                'timestamp': complete_state.timestamp,
                'window_id': complete_state.window_id,
                'active_tab': {
                    'title': complete_state.current_tab.get('title', 'Unknown') if complete_state.current_tab else 'Unknown',
                    'url': complete_state.current_tab.get('url', '') if complete_state.current_tab else '',
                    'is_loading': complete_state.current_tab.get('is_loading', False) if complete_state.current_tab else False
                } if complete_state.current_tab else None,
                'tab_count': len(complete_state.all_tabs) if complete_state.all_tabs else 0,
                'window_status': {
                    'is_fullscreen': complete_state.window_state.get('is_fullscreen', False) if complete_state.window_state else False,
                    'is_maximized': complete_state.window_state.get('is_maximized', False) if complete_state.window_state else False,
                    'total_tabs': complete_state.window_state.get('total_tabs', 0) if complete_state.window_state else 0
                } if complete_state.window_state else None,
                'navigation': {
                    'can_go_back': complete_state.navigation_state.get('can_go_back', False) if complete_state.navigation_state else False,
                    'can_go_forward': complete_state.navigation_state.get('can_go_forward', False) if complete_state.navigation_state else False
                } if complete_state.navigation_state else None,
                'performance': {
                    'score': complete_state.performance_score,
                    'system_health': complete_state.summary.get('system_health', 'Unknown') if complete_state.summary else 'Unknown',
                    'browser_health': complete_state.summary.get('browser_health', 'Unknown') if complete_state.summary else 'Unknown'
                } if complete_state.summary else None,
                'page_content': {
                    'title': complete_state.page_content.get('title', '') if complete_state.page_content else '',
                    'link_count': len(complete_state.page_content.get('links', [])) if complete_state.page_content else 0,
                    'form_count': len(complete_state.page_content.get('forms', [])) if complete_state.page_content else 0,
                    'image_count': len(complete_state.page_content.get('images', [])) if complete_state.page_content else 0
                } if complete_state.page_content else None
            }
            
            return overview
            
        except Exception as e:
            print(f"Error getting browser overview: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'window_id': window_id,
                'error': str(e)
            }
    
    def get_tab_summary(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a summary of all tabs."""
        try:
            all_tabs = self.browser_tools.get_all_tabs_info(window_id)
            
            if not all_tabs:
                return {'tabs': [], 'count': 0, 'active_index': -1}
            
            active_index = -1
            tabs_summary = []
            
            for tab in all_tabs:
                tab_info = {
                    'index': tab.index,
                    'title': tab.title,
                    'url': tab.url,
                    'is_active': tab.is_active,
                    'is_loading': tab.is_loading,
                    'is_pinned': tab.is_pinned
                }
                tabs_summary.append(tab_info)
                
                if tab.is_active:
                    active_index = tab.index
            
            return {
                'tabs': tabs_summary,
                'count': len(all_tabs),
                'active_index': active_index
            }
            
        except Exception as e:
            print(f"Error getting tab summary: {e}")
            return {'error': str(e), 'tabs': [], 'count': 0, 'active_index': -1}
    
    def get_performance_summary(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        try:
            snapshot = self.performance_tools.get_performance_snapshot(window_id)
            resource_summary = self.performance_tools.get_resource_usage_summary(window_id)
            
            summary = {
                'timestamp': snapshot.timestamp,
                'overall_score': snapshot.overall_score,
                'system_health': resource_summary.get('system_health', 'Unknown'),
                'browser_health': resource_summary.get('browser_health', 'Unknown'),
                'recommendations': resource_summary.get('recommendations', [])
            }
            
            if snapshot.system_metrics:
                summary['system'] = {
                    'cpu_percent': snapshot.system_metrics.cpu_percent,
                    'memory_percent': snapshot.system_metrics.memory_percent,
                    'memory_available_gb': round(snapshot.system_metrics.memory_available / (1024**3), 2),
                    'memory_total_gb': round(snapshot.system_metrics.memory_total / (1024**3), 2)
                }
            
            if snapshot.browser_process:
                summary['browser'] = {
                    'memory_percent': snapshot.browser_process.memory_percent,
                    'memory_mb': round(snapshot.browser_process.memory_rss / (1024**2), 2),
                    'threads': snapshot.browser_process.num_threads
                }
            
            return summary
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def get_page_content_summary(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a summary of page content."""
        try:
            page_content = self.page_content_tools.get_comprehensive_page_content(window_id)
            
            if not page_content:
                return {'error': 'Could not get page content'}
            
            summary = {
                'title': page_content.title,
                'url': page_content.url,
                'content_length': len(page_content.main_text) if page_content.main_text else 0,
                'links': {
                    'count': len(page_content.links),
                    'external_count': len([link for link in page_content.links if link.is_external]),
                    'download_count': len([link for link in page_content.links if link.is_download])
                },
                'forms': {
                    'count': len(page_content.forms),
                    'input_count': sum(len(form.inputs) for form in page_content.forms)
                },
                'images': {
                    'count': len(page_content.images)
                },
                'headings': {
                    'count': len(page_content.headings),
                    'levels': list(set(heading.level for heading in page_content.headings))
                },
                'meta_tags': {
                    'count': len(page_content.meta_tags),
                    'keys': list(page_content.meta_tags.keys())
                }
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting page content summary: {e}")
            return {'error': str(e)}
    
    def get_quick_status(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a quick status overview for the AI agent."""
        try:
            # Get essential information quickly
            current_tab = self.browser_tools.get_current_tab_info(window_id)
            window_state = self.browser_tools.get_window_state(window_id)
            system_metrics = self.performance_tools.get_system_metrics()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'window_id': window_id,
                'status': 'ready'
            }
            
            if current_tab:
                status['current_page'] = {
                    'title': current_tab.title,
                    'url': current_tab.url,
                    'is_loading': current_tab.is_loading
                }
            
            if window_state:
                status['window'] = {
                    'tab_count': window_state.total_tabs,
                    'active_tab_index': window_state.active_tab_index,
                    'is_fullscreen': window_state.is_fullscreen
                }
            
            if system_metrics:
                status['system'] = {
                    'cpu_percent': system_metrics.cpu_percent,
                    'memory_percent': system_metrics.memory_percent,
                    'health': 'good' if system_metrics.cpu_percent < 70 and system_metrics.memory_percent < 80 else 'moderate'
                }
            
            return status
            
        except Exception as e:
            print(f"Error getting quick status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'window_id': window_id,
                'status': 'error',
                'error': str(e)
            }


# Convenience functions for easy access
def get_complete_browser_state(window_id: int = 0) -> CompleteBrowserState:
    """Get complete browser state information from all tools."""
    tools = UnifiedBrowserStateTools()
    return tools.get_complete_browser_state(window_id)


def get_browser_overview(window_id: int = 0) -> Dict[str, Any]:
    """Get a high-level overview of browser state."""
    tools = UnifiedBrowserStateTools()
    return tools.get_browser_overview(window_id)


def get_tab_summary(window_id: int = 0) -> Dict[str, Any]:
    """Get a summary of all tabs."""
    tools = UnifiedBrowserStateTools()
    return tools.get_tab_summary(window_id)


def get_performance_summary(window_id: int = 0) -> Dict[str, Any]:
    """Get a summary of performance metrics."""
    tools = UnifiedBrowserStateTools()
    return tools.get_performance_summary(window_id)


def get_page_content_summary(window_id: int = 0) -> Dict[str, Any]:
    """Get a summary of page content."""
    tools = UnifiedBrowserStateTools()
    return tools.get_page_content_summary(window_id)


def get_quick_status(window_id: int = 0) -> Dict[str, Any]:
    """Get a quick status overview for the AI agent."""
    tools = UnifiedBrowserStateTools()
    return tools.get_quick_status(window_id)

