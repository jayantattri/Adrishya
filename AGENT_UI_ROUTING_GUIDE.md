# Agent UI Routing Guide

## Overview

This guide explains how to route requests from the agent UI to the real AI agent in qutebrowser.

## 🚀 Quick Start

### 1. Open the Agent UI
```bash
:agent-ui
```

### 2. Initialize the AI Agent
```bash
:agent-init
```

### 3. Check Agent Status
```bash
:agent-status
```

### 4. Test with a Direct Query
```bash
:agent-query "open youtube.com"
```

## 🔧 How It Works

### Architecture

1. **Agent UI** (`:agent-ui`) - Opens a beautiful web interface in a new tab
2. **Agent Router** (`ai_agent_router.py`) - Routes requests to the real AI agent
3. **Real AI Agent** - Your enhanced sequential agent or original AI agent
4. **Command System** - qutebrowser commands that bridge the UI and agent

### Request Flow

```
User Input (UI) → JavaScript → qute://command → Python Command → Agent Router → Real AI Agent → Response → UI Display
```

## 📁 Files Created/Modified

### New Files
- `qutebrowser/commands/ai_agent_router.py` - Main routing logic
- `AGENT_UI_ROUTING_GUIDE.md` - This guide

### Modified Files
- `qutebrowser/commands/ai_state_query.py` - Updated with new commands and routing

## 🎯 Available Commands

### Core Commands
- `:agent-ui` - Open the AI Agent interface
- `:agent-init` - Initialize the AI agent
- `:agent-status` - Check agent status
- `:agent-query "your query"` - Process a query directly

### UI Integration Commands
- `:agent-ui-query "your query"` - Process query from UI (called internally)

## 🔄 Agent Selection

The system automatically tries to use the best available agent:

1. **Enhanced Sequential Agent** (preferred) - From `ai_agent_tools/enhanced_sequential_agent.py`
2. **Original AI Agent** (fallback) - From `ai_agent_tools/ai_browser_agent.py`

## 🛠️ Troubleshooting

### Agent Not Initializing
```bash
# Check if the agent tools are available
ls ai_agent_tools/

# Try manual initialization
:agent-init

# Check status
:agent-status
```

### UI Not Responding
1. Make sure the agent is initialized: `:agent-status`
2. Try a direct query: `:agent-query "test"`
3. Check browser console for errors

### Import Errors
If you see import errors, make sure:
1. The `ai_agent_tools/` directory exists
2. The required agent files are present
3. Python can find the modules

## 🎨 UI Features

The agent UI provides:
- **Real-time streaming** of agent responses
- **Collapsible reasoning** sections
- **Beautiful tool call** visualization
- **Interactive chat** interface
- **Example queries** to get started

## 🔗 Integration Points

### JavaScript → Python
The UI uses `fetch('qute://command/agent-ui-query', ...)` to call Python commands.

### Python → Agent
The router uses `await router.process_query(query)` to process requests.

### Agent → UI
Results are returned as JSON and displayed in the UI with streaming.

## 🚀 Next Steps

1. **Test the system** with simple queries
2. **Customize the UI** styling if needed
3. **Add more commands** for specific use cases
4. **Extend the agent** with new capabilities

## 📝 Example Usage

```bash
# Start the system
:agent-ui
:agent-init

# Test with various queries
:agent-query "open youtube.com"
:agent-query "search for python tutorials"
:agent-query "open a new tab and go to github"
```

The system is now ready to route requests from your beautiful agent UI to the real AI agent! 🎉
