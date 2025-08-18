# JavaScript Execution Troubleshooting

## Problem
AI commands that require JavaScript execution show fallback messages instead of detailed page content.

## Quick Fix
1. Enable JavaScript: `:set content.javascript.enabled true`
2. Wait for page to fully load
3. Try on regular web pages (not chrome://, about:, etc.)

## Debug Command
Run this to diagnose issues:
```
:ai-debug-js
```

## Common Issues
- JavaScript disabled in config
- Page not fully loaded
- Special page types (chrome://, about:, etc.)
- Security restrictions
- QtWebKit backend (use QtWebEngine)

## Expected vs Actual
**Expected**: Detailed page content, links, forms, images
**Actual**: Basic title and limited content with fallback message
