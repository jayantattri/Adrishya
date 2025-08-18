# Qutebrowser Commands Reference

This document contains a comprehensive list of all commands available in qutebrowser, organized by category. Each command includes its description, arguments, and usage examples.

## Table of Contents
- [Browser Navigation](#browser-navigation)
- [Tab Management](#tab-management)
- [Zoom and Display](#zoom-and-display)
- [Scrolling](#scrolling)
- [Caret Browsing](#caret-browsing)
- [Configuration](#configuration)
- [Sessions](#sessions)
- [Miscellaneous](#miscellaneous)
- [Debug Commands](#debug-commands)
- [Readline Commands](#readline-commands)
- [Browser Commands](#browser-commands)
- [Search and Navigation](#search-and-navigation)
- [Bookmarks and Quickmarks](#bookmarks-and-quickmarks)
- [Downloads and Files](#downloads-and-files)
- [JavaScript and Development](#javascript-and-development)
- [System and Window Management](#system-and-window-management)

---

## Browser Navigation

### `open` / `:open`
**Description:** Open a URL in the current tab or a new tab/window.

**Arguments:**
- `url`: The URL to open
- `bg`: Open in a new background tab
- `tab`: Open in a new tab
- `window`: Open in a new window
- `related`: Position new tab as related to current one
- `count`: Tab index to open URL in
- `secure`: Force HTTPS
- `private`: Open in private browsing mode

**Example:**
```
:open https://example.com
:open --bg https://example.com
:open --tab --count 2 https://example.com
```

### `reload`
**Description:** Reload the current tab or specified tab.

**Arguments:**
- `count`: Tab index to reload
- `force`: Bypass page cache

**Example:**
```
:reload
:reload --force
:reload 2
```

### `stop`
**Description:** Stop loading in the current tab or specified tab.

**Arguments:**
- `count`: Tab index to stop

**Example:**
```
:stop
:stop 2
```

### `home`
**Description:** Open main startpage in current tab.

**Arguments:** None

**Example:**
```
:home
```

---

## Tab Management

### `tab-close`
**Description:** Close the current tab or specified tab.

**Arguments:**
- `prev`: Force selecting the tab before current tab
- `next_`: Force selecting the tab after current tab
- `opposite`: Force selecting tab in opposite direction
- `force`: Avoid confirmation for pinned tabs
- `count`: Tab index to close

**Example:**
```
:tab-close
:tab-close --force
:tab-close 3
```

### `tab-pin`
**Description:** Pin/Unpin the current tab or specified tab.

**Arguments:**
- `count`: Tab index to pin/unpin

**Example:**
```
:tab-pin
:tab-pin 2
```

### `tab-mute`
**Description:** Mute/unmute the current tab or specified tab.

**Arguments:**
- `count`: Tab index to mute/unmute

**Example:**
```
:tab-mute
:tab-mute 2
```

### `tab-clone`
**Description:** Duplicate the current tab.

**Arguments:**
- `bg`: Open in a background tab
- `window`: Open in a new window
- `private`: Open in a new private window

**Example:**
```
:tab-clone
:tab-clone --bg
:tab-clone --window
```

### `tab-take`
**Description:** Take a tab from another window.

**Arguments:**
- `index`: The [win_id/]index of the tab to take
- `keep`: Keep the old tab around

**Example:**
```
:tab-take 2
:tab-take 1/3
:tab-take 2 --keep
```

### `tab-give`
**Description:** Give the current tab to a new or existing window.

**Arguments:**
- `win_id`: Window ID to give the tab to
- `keep`: Keep the old tab around
- `count`: Overrides win_id
- `private`: Detach into a private instance

**Example:**
```
:tab-give
:tab-give 2
:tab-give --private
```

### `tab-only`
**Description:** Close all tabs except for the current one.

**Arguments:**
- `prev`: Keep tabs before the current
- `next_`: Keep tabs after the current
- `pinned`: What to do with pinned tabs (prompt/close/keep)
- `force`: Avoid confirmation for pinned tabs

**Example:**
```
:tab-only
:tab-only --prev
:tab-only --pinned close
```

### `tab-prev`
**Description:** Switch to the previous tab.

**Arguments:**
- `count`: How many tabs to switch back

**Example:**
```
:tab-prev
:tab-prev 3
```

### `tab-next`
**Description:** Switch to the next tab.

**Arguments:**
- `count`: How many tabs to switch forward

**Example:**
```
:tab-next
:tab-next 2
```

### `tab-select`
**Description:** Select tab by index or url/title best match.

**Arguments:**
- `index`: The [win_id/]index of the tab to focus
- `count`: The tab index to focus

**Example:**
```
:tab-select 2
:tab-select 1/3
:tab-select
```

### `tab-focus`
**Description:** Select the tab given as argument.

**Arguments:**
- `index`: Tab index to focus
- `count`: Tab index to focus
- `no_last`: Avoid focusing last tab if already focused

**Example:**
```
:tab-focus 2
:tab-focus last
:tab-focus stack-next
```

### `tab-move`
**Description:** Move the current tab to a new position.

**Arguments:**
- `index`: +, -, start, end, or tab index
- `count`: Offset for relative movement or new position

**Example:**
```
:tab-move start
:tab-move + 2
:tab-move 3
```

---

## Zoom and Display

### `zoom-in`
**Description:** Increase the zoom level for the current tab.

**Arguments:**
- `count`: How many steps to zoom in
- `quiet`: Don't show zoom level message

**Example:**
```
:zoom-in
:zoom-in 3
:zoom-in --quiet
```

### `zoom-out`
**Description:** Decrease the zoom level for the current tab.

**Arguments:**
- `count`: How many steps to zoom out
- `quiet`: Don't show zoom level message

**Example:**
```
:zoom-out
:zoom-out 2
:zoom-out --quiet
```

### `zoom`
**Description:** Set the zoom level for the current tab.

**Arguments:**
- `level`: Zoom percentage to set
- `count`: Zoom percentage to set
- `quiet`: Don't show zoom level message

**Example:**
```
:zoom 150
:zoom 75%
:zoom --quiet 200
```

---

## Scrolling

### `scroll`
**Description:** Scroll the current tab in the given direction.

**Arguments:**
- `direction`: Direction to scroll (up/down/left/right/top/bottom/page-up/page-down)
- `count`: Multiplier for scroll amount

**Example:**
```
:scroll down
:scroll up 3
:scroll page-down
:scroll top
```

### `scroll-px`
**Description:** Scroll the current tab by specific pixel amounts.

**Arguments:**
- `dx`: Horizontal scroll amount
- `dy`: Vertical scroll amount
- `count`: Multiplier

**Example:**
```
:scroll-px 0 100
:scroll-px 50 0 2
```

### `scroll-to-perc`
**Description:** Scroll to a specific percentage of the page.

**Arguments:**
- `perc`: Percentage to scroll to
- `horizontal`: Scroll horizontally instead of vertically
- `count`: Percentage to scroll to

**Example:**
```
:scroll-to-perc 50
:scroll-to-perc --horizontal 25
:scroll-to-perc 75
```

### `scroll-to-anchor`
**Description:** Scroll to the given anchor in the document.

**Arguments:**
- `name`: The anchor to scroll to

**Example:**
```
:scroll-to-anchor section1
```

### `scroll-page`
**Description:** Scroll the frame page-wise.

**Arguments:**
- `x`: How many pages to scroll to the right
- `y`: How many pages to scroll down
- `top_navigate`: Action to run when scrolling up at top (prev/decrement)
- `bottom_navigate`: Action to run when scrolling down at bottom (next/increment)
- `count`: Multiplier

**Example:**
```
:scroll-page 0 1
:scroll-page 1 0 --top_navigate prev
:scroll-page 0 2 --bottom_navigate next
```

---

## Caret Browsing

### `move-to-next-line`
**Description:** Move the cursor or selection to the next line.

**Arguments:**
- `count`: How many lines to move

**Example:**
```
:move-to-next-line
:move-to-next-line 3
```

### `move-to-prev-line`
**Description:** Move the cursor or selection to the previous line.

**Arguments:**
- `count`: How many lines to move

**Example:**
```
:move-to-prev-line
:move-to-prev-line 2
```

### `move-to-next-char`
**Description:** Move the cursor or selection to the next character.

**Arguments:**
- `count`: How many characters to move

**Example:**
```
:move-to-next-char
:move-to-next-char 5
```

### `move-to-prev-char`
**Description:** Move the cursor or selection to the previous character.

**Arguments:**
- `count`: How many characters to move

**Example:**
```
:move-to-prev-char
:move-to-prev-char 3
```

### `move-to-next-word`
**Description:** Move the cursor or selection to the next word.

**Arguments:**
- `count`: How many words to move

**Example:**
```
:move-to-next-word
:move-to-next-word 2
```

### `move-to-prev-word`
**Description:** Move the cursor or selection to the previous word.

**Arguments:**
- `count`: How many words to move

**Example:**
```
:move-to-prev-word
:move-to-prev-word 3
```

### `move-to-start-of-line`
**Description:** Move the cursor or selection to the start of the line.

**Arguments:** None

**Example:**
```
:move-to-start-of-line
```

### `move-to-end-of-line`
**Description:** Move the cursor or selection to the end of the line.

**Arguments:** None

**Example:**
```
:move-to-end-of-line
```

### `move-to-start-of-document`
**Description:** Move the cursor or selection to the start of the document.

**Arguments:** None

**Example:**
```
:move-to-start-of-document
```

### `move-to-end-of-document`
**Description:** Move the cursor or selection to the end of the document.

**Arguments:** None

**Example:**
```
:move-to-end-of-document
```

### `selection-toggle`
**Description:** Toggle text selection mode.

**Arguments:**
- `line`: Toggle line selection mode

**Example:**
```
:selection-toggle
:selection-toggle --line
```

### `selection-drop`
**Description:** Drop the current selection.

**Arguments:** None

**Example:**
```
:selection-drop
```

### `selection-follow`
**Description:** Follow the current selection.

**Arguments:**
- `tab`: Open selection in new tab

**Example:**
```
:selection-follow
:selection-follow --tab
```

---

## Configuration

### `set`
**Description:** Set a configuration option.

**Arguments:**
- `option`: The name of the option
- `value`: The value to set
- `pattern`: URL pattern to use
- `temp`: Set value temporarily until qutebrowser is closed
- `print_`: Print the value after setting

**Example:**
```
:set content.javascript.enabled true
:set url.start_pages "https://example.com"
:set --temp content.images false
```

### `bind`
**Description:** Bind a key to a command.

**Arguments:**
- `key`: The key to bind
- `command`: The command to bind to
- `mode`: The mode to bind in
- `pattern`: URL pattern to use

**Example:**
```
:bind J tab-next
:bind --mode insert <Ctrl-v> insert-text
:bind --pattern *://example.com/* J tab-next
```

---

## Sessions

### `session-load`
**Description:** Load a session.

**Arguments:**
- `name`: The name of the session
- `clear`: Close all existing windows
- `temp`: Don't set as current session
- `force`: Force loading internal sessions
- `delete`: Delete the saved session after loading

**Example:**
```
:session-load work
:session-load work --clear
:session-load work --force
```

### `session-save`
**Description:** Save a session.

**Arguments:**
- `name`: The name of the session
- `current`: Save the current session
- `quiet`: Don't show confirmation message
- `force`: Force saving internal sessions
- `only_active_window`: Save only tabs of currently active window
- `with_private`: Include private windows
- `no_history`: Don't store tab history

**Example:**
```
:session-save work
:session-save work --clear
:session-save --current
```

### `session-delete`
**Description:** Delete a saved session.

**Arguments:**
- `name`: The name of the session to delete

**Example:**
```
:session-delete work
```

---

## Miscellaneous

### `print`
**Description:** Print the current tab.

**Arguments:**
- `preview`: Show preview instead of printing
- `count`: Tab index to print
- `pdf`: File path to write PDF to

**Example:**
```
:print
:print --preview
:print --pdf ~/page.pdf
```

### `screenshot`
**Description:** Take a screenshot of the current tab.

**Arguments:**
- `count`: Tab index to screenshot
- `to_file`: Save to file instead of clipboard
- `selection`: Take screenshot of selected area

**Example:**
```
:screenshot
:screenshot --to-file ~/screenshot.png
:screenshot --selection
```

### `insert-text`
**Description:** Insert text at the current cursor position.

**Arguments:**
- `text`: The text to insert

**Example:**
```
:insert-text Hello World
```

### `click-element`
**Description:** Click on an element matching the given filter.

**Arguments:**
- `filter_`: Filter type (id/css/position/focused)
- `value`: Filter value

**Example:**
```
:click-element id submit-button
:click-element css .button
:click-element focused
```

### `adblock-update`
**Description:** Update block lists for both host and Brave ad blockers.

**Arguments:** None

**Example:**
```
:adblock-update
```

---

## Debug Commands

### `debug-dump-page`
**Description:** Dump the current page's content to a file.

**Arguments:**
- `dest`: Destination file path
- `plain`: Dump as plain text instead of HTML

**Example:**
```
:debug-dump-page ~/page.html
:debug-dump-page ~/page.txt --plain
```

### `debug-webaction`
**Description:** Debug web actions.

**Arguments:**
- `action`: The action to debug
- `count`: Action count

**Example:**
```
:debug-webaction click 2
```

### `debug-crash`
**Description:** Trigger a crash for debugging purposes.

**Arguments:**
- `typ`: Crash type (exception/segfault)

**Example:**
```
:debug-crash exception
:debug-crash segfault
```

### `debug-trace`
**Description:** Enable trace logging.

**Arguments:**
- `expr`: Expression to trace

**Example:**
```
:debug-trace
:debug-trace "function_name"
```

### `devtools`
**Description:** Open developer tools.

**Arguments:**
- `position`: Position for devtools (left/right/top/bottom)

**Example:**
```
:devtools
:devtools --position right
```

---

## Readline Commands

### `rl-backward-char`
**Description:** Move back a character (readline-style).

**Arguments:** None

**Example:**
```
:rl-backward-char
```

### `rl-forward-char`
**Description:** Move forward a character (readline-style).

**Arguments:** None

**Example:**
```
:rl-forward-char
```

### `rl-backward-word`
**Description:** Move back to the start of the current or previous word.

**Arguments:** None

**Example:**
```
:rl-backward-word
```

### `rl-forward-word`
**Description:** Move forward to the end of the next word.

**Arguments:** None

**Example:**
```
:rl-forward-word
```

### `rl-beginning-of-line`
**Description:** Move to the start of the line.

**Arguments:** None

**Example:**
```
:rl-beginning-of-line
```

### `rl-end-of-line`
**Description:** Move to the end of the line.

**Arguments:** None

**Example:**
```
:rl-end-of-line
```

### `rl-kill-line`
**Description:** Remove characters from cursor to end of line.

**Arguments:** None

**Example:**
```
:rl-kill-line
```

### `rl-rubout`
**Description:** Delete backwards using given characters as boundaries.

**Arguments:**
- `delim`: Delimiter characters

**Example:**
```
:rl-rubout " "
:rl-rubout "/"
```

---

## Browser Commands

### `back`
**Description:** Go back in the history of the current tab.

**Arguments:**
- `tab`: Go back in a new tab
- `bg`: Go back in a background tab
- `window`: Go back in a new window
- `count`: How many pages to go back
- `index`: Which page to go back to
- `quiet`: Don't show error if at beginning of history

**Example:**
```
:back
:back --tab
:back 3
:back --index 5
```

### `forward`
**Description:** Go forward in the history of the current tab.

**Arguments:**
- `tab`: Go forward in a new tab
- `bg`: Go forward in a background tab
- `window`: Go forward in a new window
- `count`: How many pages to go forward
- `index`: Which page to go forward to
- `quiet`: Don't show error if at end of history

**Example:**
```
:forward
:forward --tab
:forward 2
:forward --index 3
```

### `navigate`
**Description:** Open typical prev/next links or navigate using the URL path.

**Arguments:**
- `where`: What to open (prev/next/up/increment/decrement/strip)
- `tab`: Open in a new tab
- `bg`: Open in a background tab
- `window`: Open in a new window
- `count`: Number for increment/decrement/up

**Example:**
```
:navigate prev
:navigate next --tab
:navigate up 2
:navigate increment 5
```

### `yank`
**Description:** Yank (copy) something to the clipboard or primary selection.

**Arguments:**
- `what`: What to yank (selection/url/pretty-url/title/domain/inline)
- `sel`: Use primary selection instead of clipboard
- `keep`: Stay in visual mode after yanking selection
- `quiet`: Don't show information message
- `inline`: Text to yank if what is inline

**Example:**
```
:yank url
:yank title --sel
:yank selection --keep
:yank inline "Hello World"
```

### `undo`
**Description:** Re-open the last closed tab(s) or window.

**Arguments:**
- `window`: Re-open the last closed window
- `count`: How deep in undo stack to find tabs
- `depth`: Same as count but as argument

**Example:**
```
:undo
:undo 3
:undo --window
```

---

## Search and Navigation

### `search`
**Description:** Search for text on the current page.

**Arguments:**
- `text`: The text to search for
- `reverse`: Reverse search direction

**Example:**
```
:search hello
:search world --reverse
:search
```

### `search-next`
**Description:** Continue search to the next term.

**Arguments:**
- `count`: How many elements to ignore

**Example:**
```
:search-next
:search-next 3
```

### `search-prev`
**Description:** Continue search to the previous term.

**Arguments:**
- `count`: How many elements to ignore

**Example:**
```
:search-prev
:search-prev 2
```

---

## Bookmarks and Quickmarks

### `bookmark-add`
**Description:** Save the current page as a bookmark.

**Arguments:**
- `url`: URL to save as bookmark
- `title`: Title of the new bookmark
- `toggle`: Remove bookmark if it already exists

**Example:**
```
:bookmark-add
:bookmark-add --title "My Bookmark"
:bookmark-add --toggle
```

### `bookmark-load`
**Description:** Load a bookmark.

**Arguments:**
- `url`: The URL of the bookmark to load
- `tab`: Load in a new tab
- `bg`: Load in a background tab
- `window`: Load in a new window
- `delete`: Delete the bookmark afterwards

**Example:**
```
:bookmark-load https://example.com
:bookmark-load https://example.com --tab
:bookmark-load https://example.com --delete
```

### `bookmark-del`
**Description:** Delete a bookmark.

**Arguments:**
- `url`: The URL of the bookmark to delete
- `all_`: Delete all bookmarks

**Example:**
```
:bookmark-del https://example.com
:bookmark-del --all
```

### `bookmark-list`
**Description:** Show all bookmarks/quickmarks.

**Arguments:**
- `jump`: Jump to the "bookmarks" header
- `tab`: Open in a new tab
- `bg`: Open in a background tab
- `window`: Open in a new window

**Example:**
```
:bookmark-list
:bookmark-list --jump
:bookmark-list --tab
```

### `quickmark-save`
**Description:** Save the current page as a quickmark.

**Arguments:** None

**Example:**
```
:quickmark-save
```

### `quickmark-load`
**Description:** Load a quickmark.

**Arguments:**
- `name`: The name of the quickmark to load
- `tab`: Load in a new tab
- `bg`: Load in a background tab
- `window`: Load in a new window

**Example:**
```
:quickmark-load work
:quickmark-load work --tab
```

### `quickmark-del`
**Description:** Delete a quickmark.

**Arguments:**
- `name`: The name of the quickmark to delete
- `all_`: Delete all quickmarks

**Example:**
```
:quickmark-del work
:quickmark-del --all
```

---

## Downloads and Files

### `download`
**Description:** Download a given URL or current page.

**Arguments:**
- `url`: The URL to download
- `dest`: The file path to write the download to
- `mhtml_`: Download current page as mhtml file

**Example:**
```
:download
:download https://example.com/file.pdf
:download --dest ~/downloads/file.pdf
:download --mhtml
```

### `view-source`
**Description:** Show the source of the current page.

**Arguments:**
- `edit`: Edit the source in external editor
- `pygments`: Use pygments for highlighting

**Example:**
```
:view-source
:view-source --edit
:view-source --pygments
```

---

## JavaScript and Development

### `jseval`
**Description:** Evaluate a JavaScript string.

**Arguments:**
- `js_code`: The string/file to evaluate
- `file`: Interpret js-code as a path to a file
- `url`: Interpret js-code as a javascript: URL
- `quiet`: Don't show resulting JS object
- `world`: JavaScript world to run in

**Example:**
```
:jseval "alert('Hello')"
:jseval --file script.js
:jseval --url "javascript:alert('Hello')"
:jseval --quiet "console.log('test')"
```

### `fake-key`
**Description:** Send a fake keypress to the website or qutebrowser.

**Arguments:**
- `keystring`: The keystring to send
- `global_`: Send keys to qutebrowser UI instead of website

**Example:**
```
:fake-key <Enter>
:fake-key xy
:fake-key <Ctrl-c> --global
```

### `edit-text`
**Description:** Open external editor with currently selected form field.

**Arguments:** None

**Example:**
```
:edit-text
```

### `edit-url`
**Description:** Navigate to a URL formed in an external editor.

**Arguments:**
- `url`: URL to edit
- `bg`: Open in background tab
- `tab`: Open in new tab
- `window`: Open in new window
- `private`: Open in private browsing mode
- `related`: Position new tab as related

**Example:**
```
:edit-url
:edit-url --tab
:edit-url --window
```

---

## System and Window Management

### `quit`
**Description:** Quit qutebrowser.

**Arguments:**
- `save`: Save open windows even if auto_save.session is off
- `session`: Session name to save

**Example:**
```
:quit
:quit --save
:quit --save work
```

### `restart`
**Description:** Restart qutebrowser while keeping existing tabs open.

**Arguments:** None

**Example:**
```
:restart
```

### `spawn`
**Description:** Spawn an external command.

**Arguments:**
- `cmdline`: The commandline to execute
- `userscript`: Run as a userscript
- `verbose`: Show notifications when command started/exited
- `output`: Show output in a new tab
- `output_messages`: Show output as messages
- `detach`: Detach command from qutebrowser
- `count`: Given to userscripts as $QUTE_COUNT

**Example:**
```
:spawn firefox
:spawn --userscript script.py
:spawn --output "ls -la"
:spawn --detach "long-running-process"
```

### `history`
**Description:** Show browsing history.

**Arguments:**
- `tab`: Open in a new tab
- `bg`: Open in a background tab
- `window`: Open in a new window

**Example:**
```
:history
:history --tab
:history --window
```

### `help`
**Description:** Show help about a command or setting.

**Arguments:**
- `topic`: The topic to show help for
- `tab`: Open in a new tab
- `bg`: Open in a background tab
- `window`: Open in a new window

**Example:**
```
:help
:help :open
:help content.javascript.enabled
:help --tab
```

### `messages`
**Description:** Show a log of past messages.

**Arguments:**
- `level`: Include messages with level or higher severity
- `plain`: Show plaintext instead of HTML
- `logfilter`: Comma-separated filter string
- `tab`: Open in a new tab
- `bg`: Open in a background tab
- `window`: Open in a new window

**Example:**
```
:messages
:messages --level warning
:messages --plain
:messages --logfilter "webview,network"
```

### `fullscreen`
**Description:** Toggle fullscreen mode.

**Arguments:**
- `leave`: Only leave fullscreen if entered by page
- `enter`: Activate fullscreen and don't toggle

**Example:**
```
:fullscreen
:fullscreen --leave
:fullscreen --enter
```

### `set-mark`
**Description:** Set a mark at the current scroll position.

**Arguments:**
- `key`: Mark identifier (capital indicates global mark)

**Example:**
```
:set-mark a
:set-mark A
```

### `jump-mark`
**Description:** Jump to the mark named by key.

**Arguments:**
- `key`: Mark identifier (capital indicates global mark)

**Example:**
```
:jump-mark a
:jump-mark A
```

### `hints`
**Description:** Extract all interactive elements for LLM processing.

**Arguments:** None

**Example:**
```
:hints
```

### `hints-enhanced`
**Description:** Enhanced version of hints command with callback integration.

**Arguments:**
- `callback_name`: Name of the callback to use for processing hints data

**Example:**
```
:hints-enhanced
:hints-enhanced complex_task
```

---

## Notes

- Most commands support a `count` argument that can be specified as a number before the command (e.g., `2:tab-close`)
- Commands with `--help` flag will show detailed help information
- Some commands are only available in specific modes (e.g., caret commands only work in caret mode)
- Debug commands are only available when qutebrowser is run with `--debug` flag
- The `count` argument typically refers to tab index (1-based) unless otherwise specified
- Many commands support tab, background, and window variants for flexible opening options
- The `--force` flag is often used to bypass confirmations or restrictions
- Commands that modify state (like `:set`, `:bind`) can use URL patterns for site-specific behavior

For more detailed information about specific commands, use `:help <command>` in qutebrowser.
