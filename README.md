# pharo-nc-mcp-server

[![Tests](https://github.com/mumez/pharo-nc-mcp-server/actions/workflows/test.yml/badge.svg)](https://github.com/mumez/pharo-nc-mcp-server/actions/workflows/test.yml)

A local MCP server to evaluate Pharo Smalltalk expressions and get system information via [NeoConsole](https://github.com/svenvc/NeoConsole).

## Prerequisites

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Pharo with NeoConsole installed

### Pharo Setup

1. Install Pharo and NeoConsole
1. Set the `PHARO_DIR` environment variable to your Pharo installation directory (default: `~/pharo`)
1. Ensure `NeoConsole.image` is available in the Pharo directory

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd pharo-nc-mcp-server
```

2. Install dependencies using uv:

```bash
uv sync --dev
```

## Usage

### Running the MCP Server

Start the server:

```bash
uv run pharo-nc-mcp-server
```

### Cursor MCP settings

```json:mcp.json
{
  "mcpServers": {
    "pharo-nc-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/your-path/to/pharo-nc-mcp-server",
        "run",
        "pharo-nc-mcp-server"
      ]
    }
  }
}
```

### MCP Tools Available

#### `evaluate_smalltalk_with_neo_console`

Execute Smalltalk expressions in Pharo using NeoConsole:

```python
# Example usage in MCP client
evaluate_smalltalk_with_neo_console(expression="42 factorial", command="eval")
```

#### `evaluate_simple_smalltalk`

Execute Smalltalk expressions using Pharo's simple -e option:

```python
# Simple evaluation
evaluate_simple_smalltalk(expression="Time now")
```

#### `get_pharo_metric`

Retrieve system metrics from Pharo:

```python
# Get system status
get_pharo_metric(metric="system.status")

# Get memory information
get_pharo_metric(metric="memory.free")
```

#### `get_class_comment`

Get the comment of a Pharo class:

```python
# Get Array class comment
get_class_comment(class_name="Array")
```

#### `get_class_definition`

Get the definition of a Pharo class:

```python
# Get Array class definition
get_class_definition(class_name="Array")
```

#### `get_method_list`

Get the list of method selectors for a Pharo class:

```python
# Get all method selectors for Array class
get_method_list(class_name="Array")
```

#### `get_method_source`

Get the source code of a specific method in a Pharo class:

```python
# Get source code for Array>>asSet method
get_method_source(class_name="Array", selector="asSet")
```

### Environment Variables

- `PHARO_DIR`: Path to Pharo installation directory (default: `~/pharo`)

## Development

### Code Formatting and Linting

```bash
# Format code
uv run black pharo_nc_mcp_server/

# Lint code
uv run ruff check pharo_nc_mcp_server/

# Run tests
uv run python -m pytest

# Or use the test script
./scripts/test.sh
```

### Development Scripts

The project includes several convenience scripts in the `scripts/` directory:

#### `scripts/format.sh`
Formats all code and documentation files in one command:
- Formats Python code using Black
- Formats markdown files using mdformat
- Runs linting checks with Ruff

```bash
./scripts/format.sh
```

#### `scripts/test.sh`
Runs the test suite using pytest:

```bash
./scripts/test.sh
```
