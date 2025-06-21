#!/bin/bash
# Format all code and documentation files

set -e

echo "🔧 Formatting Python code..."
uv run black pharo_nc_mcp_server/

echo "📝 Formatting markdown files..."
uv run mdformat README.md scripts/README.md

echo "🔍 Running linting checks..."
uv run ruff check pharo_nc_mcp_server/

echo "✅ All formatting complete!"