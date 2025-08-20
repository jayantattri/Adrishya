# AI Agent UI Documentation

## Overview

The `:agent-ui` command opens a beautiful, interactive AI agent interface in a new browser tab. This interface provides real-time streaming of AI agent responses with advanced features like collapsible reasoning sections and beautifully styled tool calls.

## Features

### 🎨 Beautiful Modern UI
- **Gradient backgrounds** with glassmorphism effects
- **Responsive design** that works on different screen sizes
- **Smooth animations** and transitions
- **Custom styled scrollbars** and interactive elements

### 🧠 Reasoning Display
- **Collapsible reasoning sections** with light-colored text
- **Expandable/collapsible** with smooth animations
- **Clear visual separation** between reasoning and final responses
- **Golden gradient headers** for reasoning sections

### 🔧 Tool Call Visualization
- **Colorful tool call cards** with gradient backgrounds
- **Icon-based identification** for different tool types
- **JSON parameter display** with syntax highlighting
- **Individual styling** for each tool call

### ⚡ Real-time Streaming
- **Live text streaming** as the agent generates responses
- **Typing indicators** with animated dots
- **Progressive display** of reasoning, tool calls, and results
- **Smooth scroll-to-bottom** during streaming

### 💬 Interactive Chat Interface
- **Chat-style layout** with user and agent messages
- **Example queries** to get started quickly
- **Status indicators** showing connection and processing state
- **Message counter** and processing feedback

## Usage

### Basic Usage
```
:agent-ui
```

This command opens the AI Agent UI in a new tab.

### Getting Started

1. **Open the interface**:
   ```
   :agent-ui
   ```

2. **Initialize the AI agent** (if not already done):
   ```
   :ai-agent-init deepseek_assistant
   ```

3. **Start chatting**: Type your request in the input field and press Enter.

### Example Queries

The interface provides several example queries to help you get started:

- **🌐 Navigation**: "Navigate to GitHub and search for qutebrowser"
- **🔍 Search & Research**: "Open YouTube and find videos about Python programming"  
- **📑 Tab Management**: "Open a new tab and go to Reddit"
- **🧠 Analysis**: "Analyze the current page content and summarize it"

## Interface Layout

### Header Section
- **Title**: "🤖 AI Agent Interface"
- **Subtitle**: "Intelligent browser automation with real-time streaming"
- **Glassmorphism styling** with backdrop blur effects

### Chat Container
- **Messages area**: Scrollable chat history
- **Input field**: Type your queries here
- **Send button**: Submit your requests
- **Status bar**: Shows connection status and message count

### Message Types

#### User Messages
- **Right-aligned** with gradient blue background
- **Rounded corners** with distinctive styling
- **Shadow effects** for depth

#### Agent Messages
- **Left-aligned** with light background
- **Contains multiple sections**:
  - **Reasoning section** (collapsible, golden header)
  - **Tool calls section** (colorful cards with icons)
  - **Final response** (green success box or red error box)

### Special Features

#### Reasoning Sections
```html
🧠 Reasoning Process ▼
[Collapsible content with agent's thinking process]
```
- Click the header to expand/collapse
- Light italic text for easy differentiation
- Shows the agent's step-by-step thinking

#### Tool Call Cards
```html
🔧 Tool Calls:
┌─────────────────────────────┐
│ 🌐 navigate                 │
│ {"url": "https://github.com"}│
└─────────────────────────────┘
```
- Each tool call gets its own styled card
- Icons help identify tool types
- Parameters shown in formatted JSON

## Technical Implementation

### Architecture
- **Single HTML file** embedded in Python command
- **Pure JavaScript** for interactivity (no external dependencies)
- **CSS3 features**: Gradients, animations, glassmorphism
- **Responsive design** with flexbox and grid layouts

### Communication
- **Fallback system**: Tries real agent first, falls back to simulation
- **Error handling**: Graceful degradation when agent is unavailable
- **Status feedback**: Clear indication of processing states

### Styling Features
- **CSS Custom Properties** for consistent theming
- **Smooth animations** using CSS transitions and keyframes
- **Modern font stack** with system fonts
- **Color coordination** with semantic color coding

## Customization

### Extending Tool Icons
Add new tool icons in the `getToolIcon()` function:
```javascript
const icons = {
    'navigate': '🌐',
    'click': '👆',
    'type': '⌨️',
    'your_tool': '🎯',  // Add custom icons here
    // ...
};
```

### Modifying Colors
Main color variables can be adjusted in the CSS:
- **Primary gradient**: `#667eea` to `#764ba2`
- **Reasoning gradient**: `#ffd89b` to `#19547b`  
- **Tool call gradient**: `#a8edea` to `#fed6e3`
- **Success color**: `#10b981`
- **Error color**: `#ef4444`

## Integration with Existing AI Agent

The UI automatically detects if the AI agent is initialized:
- **Shows setup message** if agent is not ready
- **Provides initialization command** for quick setup
- **Falls back to simulation** for testing purposes
- **Handles errors gracefully** with user feedback

## Browser Compatibility

- **Modern browsers** with ES6+ support
- **Chrome/Chromium** (including qutebrowser)
- **Firefox** 
- **Safari**
- **Edge**

## Performance Considerations

- **Efficient rendering** with minimal DOM manipulation
- **Smooth animations** at 60fps
- **Memory efficient** with proper cleanup
- **Responsive to user input** with immediate feedback

## Troubleshooting

### Common Issues

1. **Agent not responding**:
   - Check if agent is initialized with `:ai-agent-status`
   - Initialize with `:ai-agent-init deepseek_assistant`

2. **Interface not loading**:
   - Ensure qutebrowser supports data URLs
   - Check console for JavaScript errors

3. **Styling issues**:
   - Verify CSS3 support in browser
   - Check for conflicting user stylesheets

### Debug Mode
The interface includes console logging for debugging:
- Open browser developer tools
- Check console for detailed error messages
- Monitor network requests for API calls

## Future Enhancements

### Planned Features
- **Real WebSocket streaming** for true real-time updates
- **Voice input/output** for hands-free operation
- **Customizable themes** and color schemes
- **Export chat history** functionality
- **Plugin system** for custom tool integrations

### Potential Improvements
- **Offline mode** with local AI models
- **Multi-language support** for international users
- **Accessibility features** for screen readers
- **Mobile optimization** for touch interfaces

## Command Reference

### Related Commands
- `:agent-ui` - Open AI Agent UI (this command)
- `:ai-agent-init <profile>` - Initialize AI agent
- `:ai-agent-ask <query>` - Direct agent query
- `:ai-agent-status` - Check agent status
- `:ai-query <query>` - Ask about browser state

### Configuration
The UI respects existing AI agent configuration from `agent_config.json` and integrates seamlessly with the current agent setup.

---

*Created as part of the qutebrowser AI agent integration project.*
