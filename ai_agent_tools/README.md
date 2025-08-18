# Qutebrowser AI Agent Tools

A comprehensive set of tools for AI agents to get information about qutebrowser's current state, including tab information, page content, performance metrics, and system resources.

## Overview

These tools provide AI agents with visibility into qutebrowser's internal state, allowing them to:
- Monitor browser tabs and navigation
- Analyze page content and structure
- Track performance and resource usage
- Make informed decisions about browser control actions

## Architecture

The tools are organized into several specialized modules:

### 1. Browser State Tools (`browser_state_tools.py`)
- **Tab Information**: Current tab details, all tabs overview, tab management
- **Window State**: Window properties, fullscreen status, geometry
- **Navigation State**: Back/forward availability, page loading status
- **Browser Metrics**: Basic browser operational metrics

### 2. Page Content Tools (`page_content_tools.py`)
- **Text Content**: Main page text extraction
- **Links**: All links with metadata (external, download, etc.)
- **Forms**: Form structure and input fields
- **Images**: Image information and metadata
- **Headings**: Page heading hierarchy
- **Meta Tags**: HTML meta information
- **Page Structure**: Overall page layout analysis

### 3. Performance Tools (`performance_tools.py`)
- **System Metrics**: CPU, memory, disk, network usage
- **Browser Process**: Process-specific performance data
- **Tab Performance**: Individual tab metrics
- **Network Metrics**: Request tracking and performance
- **Performance Scoring**: Overall health assessment

### 4. Unified Interface (`unified_state_tools.py`)
- **Complete State**: All information in one call
- **Browser Overview**: High-level summary
- **Quick Status**: Essential information for AI agents
- **Specialized Summaries**: Focused information for specific use cases

## Installation

1. **Clone or copy** the `ai_agent_tools` directory to your project
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure qutebrowser** is running and accessible

## Usage

### Basic Usage

```python
from ai_agent_tools.unified_state_tools import get_quick_status, get_browser_overview

# Get quick status
status = get_quick_status()
print(f"Current page: {status['current_page']['title']}")

# Get comprehensive overview
overview = get_browser_overview()
print(f"Total tabs: {overview['tab_count']}")
```

### Advanced Usage

```python
from ai_agent_tools.browser_state_tools import get_current_tab_info
from ai_agent_tools.page_content_tools import get_page_links
from ai_agent_tools.performance_tools import get_performance_snapshot

# Get detailed tab information
current_tab = get_current_tab_info()
if current_tab:
    print(f"URL: {current_tab.url}")
    print(f"Can go back: {current_tab.can_go_back}")

# Get page links
links = get_page_links()
external_links = [link for link in links if link.is_external]

# Get performance metrics
snapshot = get_performance_snapshot()
print(f"Performance score: {snapshot.overall_score}")
```

### Complete State Information

```python
from ai_agent_tools.unified_state_tools import get_complete_browser_state

# Get everything in one call
complete_state = get_complete_browser_state()

# Access different types of information
current_tab = complete_state.current_tab
all_tabs = complete_state.all_tabs
performance_score = complete_state.performance_score
system_health = complete_state.summary['system_health']
```

## Data Structures

### TabInfo
```python
@dataclass
class TabInfo:
    index: int
    url: str
    title: str
    is_active: bool
    is_loading: bool
    is_pinned: bool
    can_go_back: bool
    can_go_forward: bool
    scroll_position: Optional[Dict[str, int]]
    zoom_level: Optional[float]
```

### PageContent
```python
@dataclass
class PageContent:
    url: str
    title: str
    main_text: str
    links: List[LinkInfo]
    forms: List[FormInfo]
    images: List[Dict[str, str]]
    headings: List[Dict[str, str]]
    meta_tags: Dict[str, str]
    page_structure: Dict[str, Any]
```

### PerformanceSnapshot
```python
@dataclass
class PerformanceSnapshot:
    timestamp: str
    system_metrics: Optional[SystemMetrics]
    browser_process: Optional[BrowserProcessMetrics]
    tab_performance: List[TabPerformanceMetrics]
    network_metrics: Optional[NetworkMetrics]
    overall_score: Optional[float]
```

## API Reference

### Core Functions

#### Browser State
- `get_current_tab_info(window_id=0)` → `Optional[TabInfo]`
- `get_all_tabs_info(window_id=0)` → `List[TabInfo]`
- `get_window_state(window_id=0)` → `Optional[WindowState]`
- `get_navigation_state(window_id=0)` → `Optional[NavigationState]`

#### Page Content
- `get_page_text_content(window_id=0)` → `Optional[str]`
- `get_page_links(window_id=0)` → `List[LinkInfo]`
- `get_page_forms(window_id=0)` → `List[FormInfo]`
- `get_comprehensive_page_content(window_id=0)` → `Optional[PageContent]`

#### Performance
- `get_system_metrics()` → `Optional[SystemMetrics]`
- `get_browser_process_metrics()` → `Optional[BrowserProcessMetrics]`
- `get_performance_snapshot(window_id=0)` → `PerformanceSnapshot`
- `get_resource_usage_summary(window_id=0)` → `Dict[str, Any]`

#### Unified Interface
- `get_quick_status(window_id=0)` → `Dict[str, Any]`
- `get_browser_overview(window_id=0)` → `Dict[str, Any]`
- `get_complete_browser_state(window_id=0)` → `CompleteBrowserState`

## Examples

### Example 1: Monitor Browser Health
```python
from ai_agent_tools.performance_tools import get_resource_usage_summary

summary = get_resource_usage_summary()
if summary['system_health'] == 'Poor':
    print("System performance is poor. Consider closing applications.")
if summary['browser_health'] == 'Poor':
    print("Browser performance is poor. Consider closing unused tabs.")
```

### Example 2: Analyze Current Page
```python
from ai_agent_tools.page_content_tools import get_comprehensive_page_content

content = get_comprehensive_page_content()
if content:
    print(f"Page has {len(content.links)} links")
    print(f"Page has {len(content.forms)} forms")
    print(f"Page has {len(content.images)} images")
```

### Example 3: Tab Management
```python
from ai_agent_tools.browser_state_tools import get_all_tabs_info

tabs = get_all_tabs_info()
for tab in tabs:
    if tab.is_loading:
        print(f"Tab {tab.index}: {tab.title} is loading")
    if tab.is_pinned:
        print(f"Tab {tab.index}: {tab.title} is pinned")
```

## Error Handling

All tools include comprehensive error handling:

```python
try:
    status = get_quick_status()
    if 'error' in status:
        print(f"Error: {status['error']}")
    else:
        print(f"Status: {status['status']}")
except Exception as e:
    print(f"Tool error: {e}")
```

## Performance Considerations

- **Quick Status**: Fastest, returns essential information only
- **Browser Overview**: Moderate speed, good balance of detail and performance
- **Complete State**: Slowest, returns all available information
- **Individual Tools**: Vary in speed based on what they access

## Integration with AI Agents

These tools are designed to work seamlessly with AI agents:

1. **State Awareness**: AI agents can understand current browser state
2. **Decision Making**: Tools provide data for informed decisions
3. **Monitoring**: Continuous monitoring capabilities for dynamic environments
4. **Error Handling**: Robust error handling for reliable operation

## Future Enhancements

Planned improvements include:
- **Real-time Updates**: Event-driven state updates
- **JavaScript Integration**: Better page content extraction
- **Network Monitoring**: Enhanced network request tracking
- **Custom Metrics**: User-defined performance metrics
- **Export Formats**: Multiple output formats (JSON, CSV, etc.)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure qutebrowser is running and accessible
2. **Permission Errors**: Check if tools have access to browser state
3. **Performance Issues**: Use quick status for frequent updates
4. **Missing Data**: Some information may not be available in all contexts

### Debug Mode

Enable debug output by setting environment variable:
```bash
export QB_DEBUG=1
```

## Contributing

To contribute to these tools:

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## License

This project is licensed under the same license as qutebrowser (GPL-3.0-or-later).

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example code
3. Check qutebrowser documentation
4. Open an issue in the repository

---

**Note**: These tools are designed to work with qutebrowser and require proper access to the browser's internal state. They should be run from within qutebrowser or with appropriate permissions.

