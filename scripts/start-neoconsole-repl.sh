#!/bin/bash

# Start NeoConsole telnet server for Pharo Smalltalk
# Usage: ./scripts/start-neoconsole-repl.sh [server|repl]
# Default: server mode (for persistent sessions)

set -e

# Get mode from first argument, default to server
MODE=${1:-server}

# Default PHARO_DIR if not set
if [ -z "$PHARO_DIR" ]; then
    PHARO_DIR="$HOME/pharo"
fi

echo "Starting NeoConsole in $MODE mode..."
echo "PHARO_DIR: $PHARO_DIR"

# Check if PHARO_DIR exists
if [ ! -d "$PHARO_DIR" ]; then
    echo "Error: PHARO_DIR '$PHARO_DIR' does not exist"
    echo "Please set PHARO_DIR environment variable or create the directory"
    exit 1
fi

# Check if NeoConsole.image exists
if [ ! -f "$PHARO_DIR/NeoConsole.image" ]; then
    echo "Error: NeoConsole.image not found in $PHARO_DIR"
    echo "Please ensure NeoConsole.image is available"
    exit 1
fi

# Check if pharo executable exists
if [ ! -f "$PHARO_DIR/pharo" ]; then
    echo "Error: pharo executable not found in $PHARO_DIR"
    echo "Please ensure pharo executable is available"
    exit 1
fi

# Change to PHARO_DIR and start NeoConsole
cd "$PHARO_DIR"

if [ "$MODE" = "server" ]; then
    echo "Starting NeoConsole telnet server on port 4999..."
    echo "Connect with: telnet localhost 4999"
    echo "Or use the MCP server tools to interact with it."
    exec ./pharo NeoConsole.image NeoConsole server
elif [ "$MODE" = "repl" ]; then
    echo "Starting NeoConsole direct REPL..."
    exec ./pharo NeoConsole.image NeoConsole repl
else
    echo "Error: Unknown mode '$MODE'. Use 'server' or 'repl'"
    exit 1
fi