"""
Page Content Information Tools for Qutebrowser

This module provides tools to get information about the content of web pages,
including text content, form inputs, links, and page structure.
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
class PageElement:
    """Information about a page element."""
    tag_name: str
    text_content: str
    attributes: Dict[str, str]
    element_type: str  # 'link', 'form', 'input', 'button', 'text', etc.


@dataclass
class FormInfo:
    """Information about a form on the page."""
    form_id: str
    action_url: str
    method: str
    inputs: List[Dict[str, str]]
    submit_buttons: List[Dict[str, str]]


@dataclass
class LinkInfo:
    """Information about links on the page."""
    url: str
    text: str
    title: str
    is_external: bool
    is_download: bool


@dataclass
class PageContent:
    """Comprehensive page content information."""
    url: str
    title: str
    main_text: str
    links: List[LinkInfo]
    forms: List[FormInfo]
    images: List[Dict[str, str]]
    headings: List[Dict[str, str]]
    meta_tags: Dict[str, str]
    page_structure: Dict[str, Any]


class PageContentTools:
    """Tools for getting page content information."""
    
    def __init__(self):
        """Initialize the page content tools."""
        self._browsers = {}  # Cache browsers by window_id
        
    def _check_availability(self) -> bool:
        """Check if qutebrowser is available."""
        if not QUTEBROWSER_AVAILABLE:
            log.misc.warning("Qutebrowser modules not available")
            return False
        return True
        
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
    
    def _get_current_tab(self, window_id: int = 0):
        """Get the currently active tab."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return None
            return browser.widget.currentWidget()
        except Exception as e:
            log.misc.error(f"Error getting current tab: {e}")
            return None
    
    def _execute_js_safely(self, tab, js_code: str) -> Optional[Any]:
        """Execute JavaScript safely on the given tab."""
        try:
            if not tab:
                log.misc.debug("No tab provided for JavaScript execution")
                return None
                
            # Check if we're running outside qutebrowser (for testing)
            if not QUTEBROWSER_AVAILABLE:
                log.misc.debug("Running outside qutebrowser, returning mock JS data")
                return self._get_mock_js_result(js_code)
                
            log.misc.debug(f"Executing JavaScript on tab: {type(tab).__name__}")
            log.misc.debug(f"JavaScript code length: {len(js_code)} characters")
                
            # Try different methods to execute JavaScript in qutebrowser
            if hasattr(tab, 'run_js_async'):
                return self._execute_with_run_js_async(tab, js_code)
            elif hasattr(tab, 'page') and hasattr(tab.page(), 'runJavaScript'):
                return self._execute_with_qt_webengine(tab, js_code)
            else:
                log.misc.debug("No JavaScript execution method available")
                return None
                
        except Exception as e:
            log.misc.debug(f"Error executing JavaScript: {e}")
            return None
    
    def _execute_with_run_js_async(self, tab, js_code: str) -> Optional[Any]:
        """Execute JavaScript using qutebrowser's run_js_async method."""
        try:
            log.misc.debug("Using run_js_async for JavaScript execution")
            result = {'value': None, 'error': None, 'completed': False}
            
            def callback(js_result):
                result['value'] = js_result
                result['completed'] = True
                
            def error_callback(error):
                result['error'] = str(error)
                result['completed'] = True
            
            tab.run_js_async(js_code, callback, error_callback)
            
            # Wait for result with improved timeout handling
            import time
            timeout = 5.0  # Increased timeout to 5 seconds
            start_time = time.time()
            sleep_interval = 0.01
            
            while not result['completed'] and (time.time() - start_time) < timeout:
                time.sleep(sleep_interval)
                # Process Qt events if available
                if QApplication and QApplication.instance():
                    QApplication.processEvents()
            
            if result['completed']:
                if result['error']:
                    log.misc.debug(f"JavaScript execution error: {result['error']}")
                    return None
                log.misc.debug("JavaScript execution completed successfully")
                return result['value']
            else:
                log.misc.debug(f"JavaScript execution timed out after {timeout}s")
                return None
                
        except Exception as e:
            log.misc.debug(f"Error with run_js_async: {e}")
            return None
    
    def _execute_with_qt_webengine(self, tab, js_code: str) -> Optional[Any]:
        """Execute JavaScript using Qt WebEngine's runJavaScript method."""
        try:
            log.misc.debug("Using Qt WebEngine runJavaScript")
            page = tab.page()
            result = {'value': None, 'completed': False}
            
            def js_callback(js_result):
                result['value'] = js_result
                result['completed'] = True
            
            page.runJavaScript(js_code, js_callback)
            
            # Wait for result with improved timeout handling
            import time
            timeout = 5.0  # Increased timeout
            start_time = time.time()
            
            while not result['completed'] and (time.time() - start_time) < timeout:
                time.sleep(0.01)
                # Process Qt events if available
                if QApplication and QApplication.instance():
                    QApplication.processEvents()
            
            if result['completed']:
                log.misc.debug("Qt WebEngine JavaScript execution completed")
                return result['value']
            else:
                log.misc.debug(f"Qt WebEngine JavaScript execution timed out after {timeout}s")
                return None
                
        except Exception as e:
            log.misc.debug(f"Error with Qt WebEngine JavaScript: {e}")
            return None
    
    def _get_mock_js_result(self, js_code: str) -> Optional[Any]:
        """Return mock JavaScript results for testing outside qutebrowser."""
        try:
            # Basic mock results based on the JavaScript code
            if "document.links" in js_code:
                return [
                    {
                        'url': 'https://example.com',
                        'text': 'Example Link',
                        'title': 'Example Link Title',
                        'is_external': True,
                        'is_download': False
                    },
                    {
                        'url': 'https://github.com/qutebrowser/qutebrowser',
                        'text': 'Qutebrowser GitHub',
                        'title': 'Qutebrowser Repository',
                        'is_external': True,
                        'is_download': False
                    }
                ]
            elif "document.forms" in js_code:
                return [
                    {
                        'id': 'search-form',
                        'action': '/search',
                        'method': 'GET',
                        'inputs': [
                            {'type': 'text', 'name': 'q', 'placeholder': 'Search...'},
                            {'type': 'submit', 'value': 'Search'}
                        ]
                    }
                ]
            elif "document.images" in js_code:
                return [
                    {'src': 'logo.png', 'alt': 'Logo', 'width': 100, 'height': 50},
                    {'src': 'banner.jpg', 'alt': 'Banner', 'width': 800, 'height': 200}
                ]
            elif "document.querySelectorAll" in js_code and "h1,h2,h3" in js_code:
                return [
                    {'tag': 'h1', 'text': 'Main Title', 'level': 1},
                    {'tag': 'h2', 'text': 'Section Title', 'level': 2},
                    {'tag': 'h3', 'text': 'Subsection Title', 'level': 3}
                ]
            elif "document.title" in js_code:
                return "Mock Page Title - AI Agent Tools Test"
            elif "document.body.innerText" in js_code:
                return "This is mock page content for testing the AI agent tools when running outside of qutebrowser."
            else:
                log.misc.debug(f"No mock data available for JavaScript: {js_code[:100]}...")
                return None
                
        except Exception as e:
            log.misc.debug(f"Error generating mock JavaScript result: {e}")
            return None
    
    def get_page_text_content(self, window_id: int = 0) -> Optional[str]:
        """Get the main text content of the current page."""
        try:
            # If running outside qutebrowser, return mock content
            if not QUTEBROWSER_AVAILABLE:
                return (
                    "Mock Page Content for AI Agent Tools Test\n\n"
                    "This is a comprehensive test page demonstrating the AI agent tools for qutebrowser. "
                    "The tools provide complete browser state information including tab management, "
                    "page content analysis, and performance monitoring.\n\n"
                    "Key Features:\n"
                    "• Browser state monitoring and tab management\n"
                    "• Page content extraction and analysis\n"
                    "• Performance metrics and system resource tracking\n"
                    "• Network monitoring and request analysis\n"
                    "• Real-time state updates and event handling\n\n"
                    "This mock content is displayed because the tools are currently running outside "
                    "of the qutebrowser environment. When run within qutebrowser, these tools will "
                    "extract actual page content using JavaScript execution.\n\n"
                    "For more information, visit the qutebrowser repository on GitHub."
                )
            
            tab = self._get_current_tab(window_id)
            if not tab:
                log.misc.debug("No tab available for text content extraction")
                return "No tab available for text content extraction"
                
            # Try to get text content using JavaScript
            js_code = """
            (function() {
                try {
                    // Get main content text, excluding scripts and styles
                    var clonedDoc = document.cloneNode(true);
                    var scripts = clonedDoc.querySelectorAll('script, style, nav, header, footer, aside');
                    for (var i = 0; i < scripts.length; i++) {
                        scripts[i].remove();
                    }
                    
                    // Get text from main content areas
                    var mainContent = clonedDoc.querySelector('main, .main-content, .content, #content, .post-content');
                    if (mainContent) {
                        return mainContent.innerText || mainContent.textContent || '';
                    }
                    
                    // Fallback to body text
                    var body = clonedDoc.body;
                    if (body) {
                        return body.innerText || body.textContent || '';
                    }
                    return '';
                } catch (e) {
                    return document.body ? document.body.innerText : '';
                }
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            if result and isinstance(result, str) and result.strip():
                return result.strip()
            else:
                log.misc.debug("JavaScript execution failed, using fallback")
                return "Content extraction failed - JavaScript not available"
                
        except Exception as e:
            log.misc.error(f"Error getting page text content: {e}")
            return None
    
    def get_page_links(self, window_id: int = 0) -> List[LinkInfo]:
        """Get all links on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                log.misc.warning("No tab found for getting page links")
                return []
                
            log.misc.debug(f"Getting page links for tab: {type(tab)}")
            log.misc.debug(f"Tab URL: {tab.url().toString() if tab.url() else 'No URL'}")
                
            # First, test if JavaScript execution works at all
            test_js = """
            (function() {
                return {
                    document_ready: document.readyState,
                    title: document.title,
                    url: window.location.href,
                    link_count: document.querySelectorAll('a[href]').length,
                    body_text_length: document.body ? document.body.innerText.length : 0
                };
            })();
            """
            
            test_result = self._execute_js_safely(tab, test_js)
            log.misc.debug(f"JavaScript test result: {test_result}")
            
            # JavaScript to extract link information
            js_code = """
            (function() {
                var links = [];
                var linkElements = document.querySelectorAll('a[href]');
                var currentHostname = window.location.hostname;
                
                for (var i = 0; i < linkElements.length; i++) {
                    var link = linkElements[i];
                    var href = link.href;
                    var text = (link.textContent || link.innerText || '').trim();
                    var title = link.title || link.getAttribute('aria-label') || '';
                    
                    // Skip empty or invalid links
                    if (!href || href === '#' || href.startsWith('javascript:')) {
                        continue;
                    }
                    
                    // Determine if external
                    var isExternal = false;
                    try {
                        var linkUrl = new URL(href);
                        isExternal = linkUrl.hostname !== currentHostname;
                    } catch (e) {
                        // Relative URL, not external
                        isExternal = false;
                    }
                    
                    // Check if it's a download link
                    var isDownload = link.hasAttribute('download') || 
                                   /\\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|tar|gz|exe|dmg|pkg|deb|rpm)$/i.test(href);
                    
                    links.push({
                        url: href,
                        text: text,
                        title: title,
                        is_external: isExternal,
                        is_download: isDownload
                    });
                }
                
                return links;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            log.misc.debug(f"JavaScript result for links: {result}")
            links = []
            
            if result and isinstance(result, list):
                for link_data in result:
                    try:
                        link_info = LinkInfo(
                            url=link_data.get('url', ''),
                            text=link_data.get('text', ''),
                            title=link_data.get('title', ''),
                            is_external=link_data.get('is_external', False),
                            is_download=link_data.get('is_download', False)
                        )
                        links.append(link_info)
                    except Exception as e:
                        log.misc.debug(f"Error parsing link data: {e}")
            else:
                # Fallback behavior
                if not QUTEBROWSER_AVAILABLE:
                    log.misc.debug("Running outside qutebrowser, using mock data")
                    # Create mock links for testing
                    mock_links = [
                        LinkInfo(
                            url="https://example.com",
                            text="Example Link",
                            title="Example Link Title",
                            is_external=True,
                            is_download=False
                        ),
                        LinkInfo(
                            url="https://github.com/qutebrowser/qutebrowser",
                            text="Qutebrowser GitHub",
                            title="Qutebrowser Repository",
                            is_external=True,
                            is_download=False
                        )
                    ]
                    links.extend(mock_links)
                    log.misc.debug(f"Mock data: Added {len(mock_links)} links")
                else:
                    log.misc.debug("JavaScript execution not available, trying fallback method")
                    try:
                        # Try to get basic page info from tab object
                        url = tab.url().toString() if tab and tab.url() else "about:blank"
                        title = tab.title() if tab and hasattr(tab, 'title') else "Untitled"
                        
                        # Create a basic link info for the current page
                        links.append(LinkInfo(
                            url=url,
                            text=title,
                            title=title,
                            is_external=False,
                            is_download=False
                        ))
                        
                        log.misc.debug(f"Fallback: Found 1 link (current page: {title})")
                    except Exception as e:
                        log.misc.debug(f"Fallback method failed: {e}")
                        
            return links
            
        except Exception as e:
            log.misc.error(f"Error getting page links: {e}")
            return []
    
    def get_page_forms(self, window_id: int = 0) -> List[FormInfo]:
        """Get all forms on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            # JavaScript to extract form information
            js_code = """
            (function() {
                var forms = [];
                var formElements = document.querySelectorAll('form');
                
                for (var i = 0; i < formElements.length; i++) {
                    var form = formElements[i];
                    var inputs = [];
                    var submitButtons = [];
                    
                    // Get form inputs, textareas, and selects
                    var formInputs = form.querySelectorAll('input, textarea, select');
                    for (var j = 0; j < formInputs.length; j++) {
                        var input = formInputs[j];
                        
                        // Skip submit buttons (we'll handle them separately)
                        if (input.type === 'submit' || input.type === 'button') {
                            continue;
                        }
                        
                        var inputInfo = {
                            type: input.type || input.tagName.toLowerCase(),
                            name: input.name || '',
                            id: input.id || '',
                            placeholder: input.placeholder || '',
                            required: input.required || false,
                            value: input.type === 'password' ? '[HIDDEN]' : (input.value || ''),
                            label: ''
                        };
                        
                        // Try to find associated label
                        var label = null;
                        if (input.id) {
                            label = document.querySelector('label[for="' + input.id + '"]');
                        }
                        if (!label) {
                            label = input.closest('label');
                        }
                        if (label) {
                            inputInfo.label = (label.textContent || '').trim();
                        }
                        
                        inputs.push(inputInfo);
                    }
                    
                    // Get submit buttons
                    var buttons = form.querySelectorAll('button[type="submit"], input[type="submit"], button:not([type])');
                    for (var j = 0; j < buttons.length; j++) {
                        var button = buttons[j];
                        submitButtons.push({
                            text: button.textContent || button.value || 'Submit',
                            type: button.type || 'submit',
                            name: button.name || '',
                            id: button.id || ''
                        });
                    }
                    
                    // If no explicit submit buttons, check for input[type="submit"]
                    if (submitButtons.length === 0) {
                        var submitInputs = form.querySelectorAll('input[type="submit"]');
                        for (var k = 0; k < submitInputs.length; k++) {
                            var submitInput = submitInputs[k];
                            submitButtons.push({
                                text: submitInput.value || 'Submit',
                                type: 'submit',
                                name: submitInput.name || '',
                                id: submitInput.id || ''
                            });
                        }
                    }
                    
                    forms.push({
                        form_id: form.id || 'form_' + i,
                        action_url: form.action || window.location.href,
                        method: (form.method || 'GET').toUpperCase(),
                        inputs: inputs,
                        submit_buttons: submitButtons
                    });
                }
                
                return forms;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            forms = []
            
            if result and isinstance(result, list):
                for form_data in result:
                    try:
                        form_info = FormInfo(
                            form_id=form_data.get('form_id', ''),
                            action_url=form_data.get('action_url', ''),
                            method=form_data.get('method', 'GET'),
                            inputs=form_data.get('inputs', []),
                            submit_buttons=form_data.get('submit_buttons', [])
                        )
                        forms.append(form_info)
                    except Exception as e:
                        log.misc.debug(f"Error parsing form data: {e}")
                        
            return forms
            
        except Exception as e:
            log.misc.error(f"Error getting page forms: {e}")
            return []
    
    def get_page_images(self, window_id: int = 0) -> List[Dict[str, str]]:
        """Get all images on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            js_code = """
            (function() {
                var images = [];
                var imgElements = document.querySelectorAll('img');
                
                for (var i = 0; i < imgElements.length; i++) {
                    var img = imgElements[i];
                    
                    // Skip if no src
                    if (!img.src) continue;
                    
                    images.push({
                        src: img.src,
                        alt: img.alt || '',
                        title: img.title || '',
                        width: img.naturalWidth || img.width || 0,
                        height: img.naturalHeight || img.height || 0,
                        loading: img.loading || 'auto'
                    });
                }
                
                return images;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            log.misc.error(f"Error getting page images: {e}")
            return []
    
    def get_page_headings(self, window_id: int = 0) -> List[Dict[str, str]]:
        """Get all headings on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            js_code = """
            (function() {
                var headings = [];
                var headingElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                
                for (var i = 0; i < headingElements.length; i++) {
                    var heading = headingElements[i];
                    var text = (heading.textContent || heading.innerText || '').trim();
                    
                    if (text) {
                        headings.push({
                            level: heading.tagName.toLowerCase(),
                            text: text,
                            id: heading.id || '',
                            position: i + 1
                        });
                    }
                }
                
                return headings;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            return result if isinstance(result, list) else []
            
        except Exception as e:
            log.misc.error(f"Error getting page headings: {e}")
            return []
    
    def get_meta_tags(self, window_id: int = 0) -> Dict[str, str]:
        """Get meta tags from the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return {}
                
            js_code = """
            (function() {
                var metaTags = {};
                var metaElements = document.querySelectorAll('meta');
                
                for (var i = 0; i < metaElements.length; i++) {
                    var meta = metaElements[i];
                    var name = meta.getAttribute('name') || meta.getAttribute('property') || meta.getAttribute('http-equiv');
                    var content = meta.getAttribute('content');
                    
                    if (name && content) {
                        metaTags[name] = content;
                    }
                }
                
                // Also get title
                var titleElement = document.querySelector('title');
                if (titleElement) {
                    metaTags['title'] = titleElement.textContent || '';
                }
                
                return metaTags;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            return result if isinstance(result, dict) else {}
            
        except Exception as e:
            log.misc.error(f"Error getting meta tags: {e}")
            return {}
    
    def get_page_structure(self, window_id: int = 0) -> Dict[str, Any]:
        """Get the overall structure of the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return {}
                
            js_code = """
            (function() {
                var structure = {
                    sections: [],
                    navigation: [],
                    main_content: [],
                    sidebar: [],
                    footer: [],
                    header: [],
                    landmarks: [],
                    semantic_elements: {}
                };
                
                // Analyze semantic HTML5 elements
                var semanticSelectors = {
                    'header': 'header, .header',
                    'nav': 'nav, .nav, .navigation, .navbar, .menu',
                    'main': 'main, .main, .content, #content, .main-content',
                    'aside': 'aside, .sidebar, .aside, .side-panel',
                    'footer': 'footer, .footer',
                    'section': 'section, .section',
                    'article': 'article, .article, .post'
                };
                
                for (var elementType in semanticSelectors) {
                    var elements = document.querySelectorAll(semanticSelectors[elementType]);
                    var elementData = [];
                    
                    for (var i = 0; i < elements.length; i++) {
                        var element = elements[i];
                        var text = (element.textContent || '').trim();
                        var preview = text.length > 100 ? text.substring(0, 100) + '...' : text;
                        
                        elementData.push({
                            tag: element.tagName.toLowerCase(),
                            id: element.id || '',
                            class: element.className || '',
                            text_preview: preview,
                            text_length: text.length,
                            child_count: element.children.length
                        });
                    }
                    
                    structure.semantic_elements[elementType] = elementData;
                }
                
                // Find ARIA landmarks
                var landmarkElements = document.querySelectorAll('[role]');
                for (var i = 0; i < landmarkElements.length; i++) {
                    var landmark = landmarkElements[i];
                    structure.landmarks.push({
                        role: landmark.getAttribute('role'),
                        tag: landmark.tagName.toLowerCase(),
                        id: landmark.id || '',
                        label: landmark.getAttribute('aria-label') || landmark.getAttribute('aria-labelledby') || ''
                    });
                }
                
                // Analyze page layout
                structure.layout_analysis = {
                    total_elements: document.querySelectorAll('*').length,
                    text_nodes: document.evaluate('//text()[normalize-space()]', document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null).snapshotLength,
                    images: document.querySelectorAll('img').length,
                    links: document.querySelectorAll('a[href]').length,
                    forms: document.querySelectorAll('form').length,
                    tables: document.querySelectorAll('table').length,
                    lists: document.querySelectorAll('ul, ol').length
                };
                
                return structure;
            })();
            """
            
            result = self._execute_js_safely(tab, js_code)
            return result if isinstance(result, dict) else {}
            
        except Exception as e:
            log.misc.error(f"Error getting page structure: {e}")
            return {}
    
    def get_comprehensive_page_content(self, window_id: int = 0) -> Optional[PageContent]:
        """Get comprehensive information about the current page content."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return None
                
            # Get basic page info
            url = tab.url().toString() if tab.url() else ""
            title = tab.title() or "Untitled"
            
            # Get various content components
            main_text = self.get_page_text_content(window_id) or ""
            links = self.get_page_links(window_id)
            forms = self.get_page_forms(window_id)
            images = self.get_page_images(window_id)
            headings = self.get_page_headings(window_id)
            meta_tags = self.get_meta_tags(window_id)
            page_structure = self.get_page_structure(window_id)
            
            return PageContent(
                url=url,
                title=title,
                main_text=main_text,
                links=links,
                forms=forms,
                images=images,
                headings=headings,
                meta_tags=meta_tags,
                page_structure=page_structure
            )
            
        except Exception as e:
            log.misc.error(f"Error getting comprehensive page content: {e}")
            return None


# Convenience functions for easy access
def get_page_text_content(window_id: int = 0) -> Optional[str]:
    """Get the main text content of the current page."""
    tools = PageContentTools()
    return tools.get_page_text_content(window_id)


def get_page_links(window_id: int = 0) -> List[LinkInfo]:
    """Get all links on the current page."""
    tools = PageContentTools()
    return tools.get_page_links(window_id)


def get_page_forms(window_id: int = 0) -> List[FormInfo]:
    """Get all forms on the current page."""
    tools = PageContentTools()
    return tools.get_page_forms(window_id)


def get_page_images(window_id: int = 0) -> List[Dict[str, str]]:
    """Get all images on the current page."""
    tools = PageContentTools()
    return tools.get_page_images(window_id)


def get_page_headings(window_id: int = 0) -> List[Dict[str, str]]:
    """Get all headings on the current page."""
    tools = PageContentTools()
    return tools.get_page_headings(window_id)


def get_meta_tags(window_id: int = 0) -> Dict[str, str]:
    """Get meta tags from the current page."""
    tools = PageContentTools()
    return tools.get_meta_tags(window_id)


def get_page_structure(window_id: int = 0) -> Dict[str, Any]:
    """Get the overall structure of the current page."""
    tools = PageContentTools()
    return tools.get_page_structure(window_id)


def get_comprehensive_page_content(window_id: int = 0) -> Optional[PageContent]:
    """Get comprehensive information about the current page content."""
    tools = PageContentTools()
    return tools.get_comprehensive_page_content(window_id)

