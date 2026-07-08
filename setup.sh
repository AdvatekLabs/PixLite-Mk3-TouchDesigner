#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
launchctl setenv TD_PIXLITE "$SCRIPT_DIR"
if ! grep -q 'TD_PIXLITE' ~/.zshenv 2>/dev/null; then
    echo "export TD_PIXLITE=\"$SCRIPT_DIR\"" >> ~/.zshenv
fi
export TD_PIXLITE="$SCRIPT_DIR"
echo "TD_PIXLITE set to $SCRIPT_DIR"
