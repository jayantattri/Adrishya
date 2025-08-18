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
    from qutebrowser.utils import objreg
    from qutebrowser.browser import browsertab
    from qutebrowser.qt.core import QUrl
    from qutebrowser.qt.widgets import QApplication
except ImportError as e:
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
        self._browser = None
        self._active_window_id = None
        
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
    
    def _get_current_tab(self, window_id: int = 0):
        """Get the currently active tab."""
        try:
            browser = self._get_browser_instance(window_id)
            if not browser:
                return None
            return browser.currentWidget()
        except Exception as e:
            print(f"Error getting current tab: {e}")
            return None
    
    def get_page_text_content(self, window_id: int = 0) -> Optional[str]:
        """Get the main text content of the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return None
                
            # Try to get text content using JavaScript
            # This is a simplified approach - in practice, you'd want more sophisticated text extraction
            try:
                # Execute JavaScript to get page text
                js_code = """
                function getPageText() {
                    // Remove script and style elements
                    var scripts = document.getElementsByTagName('script');
                    var styles = document.getElementsByTagName('style');
                    for (var i = 0; i < scripts.length; i++) scripts[i].style.display = 'none';
                    for (var i = 0; i < styles.length; i++) styles[i].style.display = 'none';
                    
                    // Get text content
                    var body = document.body;
                    if (body) {
                        return body.innerText || body.textContent || '';
                    }
                    return '';
                }
                getPageText();
                """
                
                # Note: This would need to be implemented using qutebrowser's JavaScript execution
                # For now, return a placeholder
                return "Page text content would be extracted here using JavaScript execution"
                
            except Exception as e:
                print(f"Error executing JavaScript: {e}")
                return None
                
        except Exception as e:
            print(f"Error getting page text content: {e}")
            return None
    
    def get_page_links(self, window_id: int = 0) -> List[LinkInfo]:
        """Get all links on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            # This would use JavaScript to extract link information
            # For now, return placeholder structure
            links = []
            
            # Example of what the JavaScript would return:
            # var links = document.querySelectorAll('a');
            # for (var i = 0; i < links.length; i++) {
            #     var link = links[i];
            #     links.push({
            #         url: link.href,
            #         text: link.textContent,
            #         title: link.title,
            #         is_external: link.hostname !== window.location.hostname,
            #         is_download: link.download !== undefined
            #     });
            # }
            
            return links
            
        except Exception as e:
            print(f"Error getting page links: {e}")
            return []
    
    def get_page_forms(self, window_id: int = 0) -> List[FormInfo]:
        """Get all forms on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            # This would use JavaScript to extract form information
            forms = []
            
            # Example JavaScript for form extraction:
            # var forms = document.querySelectorAll('form');
            # for (var i = 0; i < forms.length; i++) {
            #     var form = forms[i];
            #     var inputs = [];
            #     var submitButtons = [];
            #     
            #     // Get form inputs
            #     var formInputs = form.querySelectorAll('input, textarea, select');
            #     for (var j = 0; j < formInputs.length; j++) {
            #         var input = formInputs[j];
            #         inputs.push({
            #             type: input.type,
            #             name: input.name,
            #             id: input.id,
            #             value: input.value,
            #             placeholder: input.placeholder
            #         });
            #     }
            #     
            #     // Get submit buttons
            #     var buttons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            #     for (var j = 0; j < buttons.length; j++) {
            #         var button = buttons[j];
            #         submitButtons.push({
            #             text: button.textContent || button.value,
            #             type: button.type,
            #             name: button.name
            #         });
            #     }
            #     
            #     forms.push({
            #         id: form.id,
            #         action: form.action,
            #         method: form.method,
            #         inputs: inputs,
            #         submitButtons: submitButtons
            #     });
            # }
            
            return forms
            
        except Exception as e:
            print(f"Error getting page forms: {e}")
            return []
    
    def get_page_images(self, window_id: int = 0) -> List[Dict[str, str]]:
        """Get all images on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            # This would use JavaScript to extract image information
            images = []
            
            # Example JavaScript:
            # var images = document.querySelectorAll('img');
            # for (var i = 0; i < images.length; i++) {
            #     var img = images[i];
            #     images.push({
            #         src: img.src,
            #         alt: img.alt,
            #         title: img.title,
            #         width: img.width,
            #         height: img.height
            #     });
            # }
            
            return images
            
        except Exception as e:
            print(f"Error getting page images: {e}")
            return []
    
    def get_page_headings(self, window_id: int = 0) -> List[Dict[str, str]]:
        """Get all headings on the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return []
                
            # This would use JavaScript to extract heading information
            headings = []
            
            # Example JavaScript:
            # var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            # for (var i = 0; i < headings.length; i++) {
            #     var heading = headings[i];
            #     headings.push({
            #         level: heading.tagName.toLowerCase(),
            #         text: heading.textContent,
            #         id: heading.id
            #     });
            # }
            
            return headings
            
        except Exception as e:
            print(f"Error getting page headings: {e}")
            return []
    
    def get_meta_tags(self, window_id: int = 0) -> Dict[str, str]:
        """Get meta tags from the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return {}
                
            # This would use JavaScript to extract meta tag information
            meta_tags = {}
            
            # Example JavaScript:
            # var metaTags = document.querySelectorAll('meta');
            # for (var i = 0; i < metaTags.length; i++) {
            #     var meta = metaTags[i];
            #     var name = meta.getAttribute('name') || meta.getAttribute('property');
            #     var content = meta.getAttribute('content');
            #     if (name && content) {
            #         metaTags[name] = content;
            #     }
            # }
            
            return meta_tags
            
        except Exception as e:
            print(f"Error getting meta tags: {e}")
            return {}
    
    def get_page_structure(self, window_id: int = 0) -> Dict[str, Any]:
        """Get the overall structure of the current page."""
        try:
            tab = self._get_current_tab(window_id)
            if not tab:
                return {}
                
            # This would analyze the DOM structure
            structure = {
                'sections': [],
                'navigation': [],
                'main_content': [],
                'sidebar': [],
                'footer': []
            }
            
            # Example JavaScript for structure analysis:
            # var structure = {};
            # 
            # // Look for common structural elements
            # var nav = document.querySelector('nav, .nav, .navigation, .menu');
            # if (nav) structure.navigation = nav.textContent;
            # 
            # var main = document.querySelector('main, .main, .content, #content');
            # if (main) structure.main_content = main.textContent;
            # 
            # var sidebar = document.querySelector('.sidebar, .side, .aside');
            # if (sidebar) structure.sidebar = sidebar.textContent;
            # 
            # var footer = document.querySelector('footer, .footer');
            # if (footer) structure.footer = footer.textContent;
            
            return structure
            
        except Exception as e:
            print(f"Error getting page structure: {e}")
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
            print(f"Error getting comprehensive page content: {e}")
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

