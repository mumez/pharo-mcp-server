#!/bin/bash

# Start NeoConsole REPL for Pharo Smalltalk
# Usage: ./scripts/start-neoconsole-repl.sh

set -e

# Default PHARO_DIR if not set
if [ -z "$PHARO_DIR" ]; then
    PHARO_DIR="$HOME/pharo"
fi

echo "Starting NeoConsole REPL..."
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

# Change to PHARO_DIR and start NeoConsole REPL
cd "$PHARO_DIR"
exec ./pharo NeoConsole.image NeoConsole repl