# Scripts

This directory contains utility scripts for the pharo-mcp-server project.

## start-neoconsole-repl.sh

Starts a NeoConsole REPL session for interactive Pharo Smalltalk development and testing.

### Usage

```bash
# Using default PHARO_DIR ($HOME/pharo)
./scripts/start-neoconsole-repl.sh

# Using custom PHARO_DIR
PHARO_DIR=/path/to/pharo ./scripts/start-neoconsole-repl.sh
```

### Requirements

- `PHARO_DIR` environment variable set (defaults to `$HOME/pharo`)
- `NeoConsole.image` file in PHARO_DIR
- `pharo` executable in PHARO_DIR

### Features

- Validates PHARO_DIR and required files before starting
- Provides clear error messages if setup is incomplete
- Changes to PHARO_DIR before executing to ensure correct working directory
- Can be used for manual testing and integration tests

### Integration Testing

This script is used by the integration tests in `tests/test_integration.py` to verify that the MCP server functions work correctly with real Pharo instances.

Run integration tests with:

```bash
# Run all tests including integration tests
uv run pytest

# Run only integration tests (requires Pharo setup)
uv run pytest -m integration

# Run tests excluding integration tests (unit tests only)
uv run pytest -m "not integration"
```
