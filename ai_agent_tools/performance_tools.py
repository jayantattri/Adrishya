"""
Performance and System Information Tools for Qutebrowser

This module provides tools to get information about browser performance,
system resources, and operational metrics.
"""

import sys
import os
import time
import psutil
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Add qutebrowser to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from qutebrowser.misc import objects
    from qutebrowser.utils import objreg
    from qutebrowser.browser import browsertab
    from qutebrowser.qt.core import QUrl, QTimer
    from qutebrowser.qt.widgets import QApplication
except ImportError as e:
    print(f"Warning: Could not import qutebrowser modules: {e}")
    print("This module should be run from within qutebrowser or with proper imports")


@dataclass
class SystemMetrics:
    """System-level performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_available: int
    memory_total: int
    memory_used: int
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int


@dataclass
class BrowserProcessMetrics:
    """Browser-specific process metrics."""
    process_id: int
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    memory_vms: int
    num_threads: int
    create_time: float
    status: str


@dataclass
class TabPerformanceMetrics:
    """Performance metrics for individual tabs."""
    tab_index: int
    url: str
    load_time: Optional[float]
    memory_usage: Optional[int]
    render_time: Optional[float]
    network_requests: Optional[int]
    javascript_execution_time: Optional[float]


@dataclass
class NetworkMetrics:
    """Network-related performance metrics."""
    total_requests: int
    active_requests: int
    bytes_downloaded: int
    bytes_uploaded: int
    average_response_time: float
    failed_requests: int
    cache_hit_rate: float


@dataclass
class PerformanceSnapshot:
    """Complete performance snapshot."""
    timestamp: str
    system_metrics: Optional[SystemMetrics]
    browser_process: Optional[BrowserProcessMetrics]
    tab_performance: List[TabPerformanceMetrics]
    network_metrics: Optional[NetworkMetrics]
    overall_score: Optional[float]


class PerformanceTools:
    """Tools for getting performance and system information."""
    
    def __init__(self):
        """Initialize the performance tools."""
        self._browser = None
        self._active_window_id = None
        self._last_snapshot = None
        
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
    
    def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Get system-level performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            memory_total = memory.total
            memory_used = memory.used
            
            # Disk usage
            disk_usage_percent = 0.0
            try:
                disk = psutil.disk_usage('/')
                disk_usage_percent = disk.percent
            except:
                pass
            
            # Network I/O
            network_io = {'bytes_sent': 0, 'bytes_recv': 0}
            try:
                net_io = psutil.net_io_counters()
                network_io['bytes_sent'] = net_io.bytes_sent
                network_io['bytes_recv'] = net_io.bytes_recv
            except:
                pass
            
            # Process count
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available=memory_available,
                memory_total=memory_total,
                memory_used=memory_used,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                process_count=process_count
            )
            
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return None
    
    def get_browser_process_metrics(self) -> Optional[BrowserProcessMetrics]:
        """Get metrics for the qutebrowser process."""
        try:
            current_pid = os.getpid()
            process = psutil.Process(current_pid)
            
            # Get process metrics
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            num_threads = process.num_threads()
            create_time = process.create_time()
            status = process.status()
            
            return BrowserProcessMetrics(
                process_id=current_pid,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_rss=memory_info.rss,
                memory_vms=memory_info.vms,
                num_threads=num_threads,
                create_time=create_time,
                status=status
            )
            
        except Exception as e:
            print(f"Error getting browser process metrics: {e}")
            return None
    
    def get_tab_performance_metrics(self, window_id: int = 0) -> List[TabPerformanceMetrics]:
        """Get performance metrics for all tabs."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return []
                
            tabs_metrics = []
            for i in range(browser.count()):
                tab = browser.widget(i)
                if not tab:
                    continue
                    
                # Get basic tab info
                url = tab.url().toString() if tab.url() else ""
                
                # These metrics would need to be implemented with actual measurement
                # For now, return placeholder values
                load_time = None
                memory_usage = None
                render_time = None
                network_requests = None
                javascript_execution_time = None
                
                # Example of how to implement actual metrics:
                # load_time = tab.load_time if hasattr(tab, 'load_time') else None
                # memory_usage = tab.memory_usage if hasattr(tab, 'memory_usage') else None
                
                tab_metrics = TabPerformanceMetrics(
                    tab_index=i,
                    url=url,
                    load_time=load_time,
                    memory_usage=memory_usage,
                    render_time=render_time,
                    network_requests=network_requests,
                    javascript_execution_time=javascript_execution_time
                )
                tabs_metrics.append(tab_metrics)
                
            return tabs_metrics
            
        except Exception as e:
            print(f"Error getting tab performance metrics: {e}")
            return []
    
    def get_network_metrics(self, window_id: int = 0) -> Optional[NetworkMetrics]:
        """Get network-related performance metrics."""
        try:
            # This would need to be implemented by tracking network requests
            # For now, return placeholder values
            return NetworkMetrics(
                total_requests=0,
                active_requests=0,
                bytes_downloaded=0,
                bytes_uploaded=0,
                average_response_time=0.0,
                failed_requests=0,
                cache_hit_rate=0.0
            )
            
        except Exception as e:
            print(f"Error getting network metrics: {e}")
            return None
    
    def calculate_performance_score(self, system_metrics: SystemMetrics, 
                                  browser_process: BrowserProcessMetrics) -> float:
        """Calculate an overall performance score."""
        try:
            score = 100.0
            
            # Deduct points for high resource usage
            if system_metrics.cpu_percent > 80:
                score -= 20
            elif system_metrics.cpu_percent > 60:
                score -= 10
                
            if system_metrics.memory_percent > 90:
                score -= 25
            elif system_metrics.memory_percent > 80:
                score -= 15
            elif system_metrics.memory_percent > 70:
                score -= 5
                
            if browser_process.memory_percent > 50:
                score -= 15
            elif browser_process.memory_percent > 30:
                score -= 10
                
            # Ensure score doesn't go below 0
            return max(0.0, score)
            
        except Exception as e:
            print(f"Error calculating performance score: {e}")
            return 50.0  # Default middle score
    
    def get_performance_snapshot(self, window_id: int = 0) -> PerformanceSnapshot:
        """Get a complete performance snapshot."""
        try:
            # Get all metrics
            system_metrics = self.get_system_metrics()
            browser_process = self.get_browser_process_metrics()
            tab_performance = self.get_tab_performance_metrics(window_id)
            network_metrics = self.get_network_metrics(window_id)
            
            # Calculate overall score
            overall_score = None
            if system_metrics and browser_process:
                overall_score = self.calculate_performance_score(system_metrics, browser_process)
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.now().isoformat(),
                system_metrics=system_metrics,
                browser_process=browser_process,
                tab_performance=tab_performance,
                network_metrics=network_metrics,
                overall_score=overall_score
            )
            
            self._last_snapshot = snapshot
            return snapshot
            
        except Exception as e:
            print(f"Error getting performance snapshot: {e}")
            return PerformanceSnapshot(
                timestamp=datetime.now().isoformat(),
                system_metrics=None,
                browser_process=None,
                tab_performance=[],
                network_metrics=None,
                overall_score=None
            )
    
    def get_performance_trends(self, window_id: int = 0, 
                              interval_seconds: int = 5, 
                              num_samples: int = 10) -> List[PerformanceSnapshot]:
        """Get performance trends over time."""
        try:
            trends = []
            for i in range(num_samples):
                snapshot = self.get_performance_snapshot(window_id)
                trends.append(snapshot)
                
                if i < num_samples - 1:  # Don't sleep after the last sample
                    time.sleep(interval_seconds)
                    
            return trends
            
        except Exception as e:
            print(f"Error getting performance trends: {e}")
            return []
    
    def get_resource_usage_summary(self, window_id: int = 0) -> Dict[str, Any]:
        """Get a summary of resource usage."""
        try:
            snapshot = self.get_performance_snapshot(window_id)
            
            summary = {
                'timestamp': snapshot.timestamp,
                'overall_score': snapshot.overall_score,
                'system_health': 'Unknown',
                'browser_health': 'Unknown',
                'recommendations': []
            }
            
            # Assess system health
            if snapshot.system_metrics:
                cpu = snapshot.system_metrics.cpu_percent
                memory = snapshot.system_metrics.memory_percent
                
                if cpu < 50 and memory < 70:
                    summary['system_health'] = 'Good'
                elif cpu < 80 and memory < 85:
                    summary['system_health'] = 'Moderate'
                else:
                    summary['system_health'] = 'Poor'
                    summary['recommendations'].append('Consider closing unnecessary applications')
                    summary['recommendations'].append('Monitor system resource usage')
            
            # Assess browser health
            if snapshot.browser_process:
                browser_memory = snapshot.browser_process.memory_percent
                
                if browser_memory < 30:
                    summary['browser_health'] = 'Good'
                elif browser_memory < 50:
                    summary['browser_health'] = 'Moderate'
                else:
                    summary['browser_health'] = 'Poor'
                    summary['recommendations'].append('Consider closing unused tabs')
                    summary['recommendations'].append('Restart browser if performance is poor')
            
            return summary
            
        except Exception as e:
            print(f"Error getting resource usage summary: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}


# Convenience functions for easy access
def get_system_metrics() -> Optional[SystemMetrics]:
    """Get system-level performance metrics."""
    tools = PerformanceTools()
    return tools.get_system_metrics()


def get_browser_process_metrics() -> Optional[BrowserProcessMetrics]:
    """Get metrics for the qutebrowser process."""
    tools = PerformanceTools()
    return tools.get_browser_process_metrics()


def get_tab_performance_metrics(window_id: int = 0) -> List[TabPerformanceMetrics]:
    """Get performance metrics for all tabs."""
    tools = PerformanceTools()
    return tools.get_tab_performance_metrics(window_id)


def get_network_metrics(window_id: int = 0) -> Optional[NetworkMetrics]:
    """Get network-related performance metrics."""
    tools = PerformanceTools()
    return tools.get_network_metrics(window_id)


def get_performance_snapshot(window_id: int = 0) -> PerformanceSnapshot:
    """Get a complete performance snapshot."""
    tools = PerformanceTools()
    return tools.get_performance_snapshot(window_id)


def get_performance_trends(window_id: int = 0, 
                          interval_seconds: int = 5, 
                          num_samples: int = 10) -> List[PerformanceSnapshot]:
    """Get performance trends over time."""
    tools = PerformanceTools()
    return tools.get_performance_trends(window_id, interval_seconds, num_samples)


def get_resource_usage_summary(window_id: int = 0) -> Dict[str, Any]:
    """Get a summary of resource usage."""
    tools = PerformanceTools()
    return tools.get_resource_usage_summary(window_id)

