#!/bin/bash
# Format all code and documentation files

set -e

echo "🔧 Formatting Python code with ruff..."
uv run ruff format pharo_nc_mcp_server/ tests/

echo "📝 Checking if mdformat is available..."
if uv run mdformat --version >/dev/null 2>&1; then
    echo "Formatting markdown files..."
    uv run mdformat README.md scripts/README.md 2>/dev/null || echo "Warning: Some markdown files could not be formatted"
else
    echo "mdformat not available, skipping markdown formatting"
fi

echo "🔍 Running linting checks..."
uv run ruff check pharo_nc_mcp_server/ tests/

echo "✅ All formatting complete!"