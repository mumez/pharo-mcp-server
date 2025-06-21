"""FastMCP server for Pharo Smalltalk evaluation."""

from fastmcp import FastMCP, Context
from pydantic import BaseModel
from .core import (
    evaluate_pharo_neo_console,
    evaluate_pharo_simple,
    install_pharo_package,
    get_pharo_system_metric,
    get_class_comment,
    get_class_definition,
    get_method_list,
    get_method_source,
    get_neo_console_command_history,
)


class PharoEvalRequest(BaseModel):
    """Request model for Pharo expression evaluation."""

    expression: str
    command: str = "eval"


mcp = FastMCP("pharo-nc-mcp-server")


@mcp.tool("evaluate_smalltalk_with_neo_console")
def evaluate_code(_: Context, expression: str, command: str = "eval") -> str:
    """
    Evaluate a Pharo Smalltalk expression using NeoConsole.

    Args:
        expression: The Smalltalk expression to evaluate
        command: The NeoConsole command to use (default: eval)

    Returns:
        The result of the evaluation
    """
    return evaluate_pharo_neo_console(expression, command)


@mcp.tool("quit_neo_console")
def quit_neo_console(_: Context) -> str:
    """
    Send quit command to NeoConsole to terminate the REPL session.

    Returns:
        The result of the quit command
    """
    return evaluate_pharo_neo_console("", "quit")


@mcp.tool("evaluate_simple_smalltalk")
def evaluate_simple(_: Context, expression: str) -> str:
    """
    Evaluate a Pharo Smalltalk expression using the simple -e option.

    Args:
        expression: The Smalltalk expression to evaluate

    Returns:
        The result of the evaluation
    """
    return evaluate_pharo_simple(expression)


@mcp.tool("get_pharo_metric")
def get_pharo_metric(_: Context, metric: str) -> str:
    """
    Get a system metric from Pharo using NeoConsole.

    Args:
        metric: The metric to retrieve (e.g., 'system.status', 'memory.free')

    Returns:
        The metric value
    """
    return get_pharo_system_metric(metric)


@mcp.tool("install_package")
def install_package(_: Context, baseline: str, repository: str) -> str:
    """
    Install a Pharo package using Metacello.

    Args:
        baseline: The baseline name of the package (e.g., 'Historia')
        repository: The repository URL (e.g., 'github://mumez/Historia:main/src')

    Returns:
        The result of the package installation
    """
    return install_pharo_package(baseline, repository)


@mcp.tool("get_class_comment")
def get_class_comment_tool(_: Context, class_name: str) -> str:
    """
    Get the comment of a Pharo class.

    Args:
        class_name: The name of the class to get the comment for

    Returns:
        The class comment
    """
    return get_class_comment(class_name)


@mcp.tool("get_class_definition")
def get_class_definition_tool(_: Context, class_name: str) -> str:
    """
    Get the definition of a Pharo class.

    Args:
        class_name: The name of the class to get the definition for

    Returns:
        The class definition
    """
    return get_class_definition(class_name)


@mcp.tool("get_method_list")
def get_method_list_tool(_: Context, class_name: str) -> str:
    """
    Get the list of method selectors for a Pharo class.

    Args:
        class_name: The name of the class to get method selectors for

    Returns:
        The list of method selectors
    """
    return get_method_list(class_name)


@mcp.tool("get_method_source")
def get_method_source_tool(_: Context, class_name: str, selector: str) -> str:
    """
    Get the source code of a specific method in a Pharo class.

    Args:
        class_name: The name of the class
        selector: The method selector (message name)

    Returns:
        The method source code
    """
    return get_method_source(class_name, selector)


@mcp.tool("get_neo_console_command_history")
def get_neo_console_command_history_tool(_: Context) -> str:
    """
    Get the command history from the current NeoConsole session.

    Returns:
        The command history as a string, showing numbered entries of previously executed commands
    """
    return get_neo_console_command_history()


@mcp.tool("shutdown_repl_session")
def shutdown_repl_session(_: Context) -> str:
    """
    Shutdown the persistent NeoConsole REPL session and server.

    Returns:
        The result of the shutdown operation
    """
    from .core import _close_telnet_connection

    _close_telnet_connection()
    return "NeoConsole REPL session shutdown complete"


if __name__ == "__main__":
    mcp.run()
