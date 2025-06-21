"""Core functions for Pharo MCP server without FastMCP decorators."""

import subprocess
import os


def evaluate_pharo_simple(expression: str) -> str:
    """
    Evaluate a Pharo Smalltalk expression using the simple -e argument.

    Args:
        expression: The Smalltalk expression to evaluate

    Returns:
        The result of the evaluation
    """
    pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))

    try:
        # Use pharo -e option for simple evaluation
        cmd = ["./pharo", "Pharo.image", "-e", expression]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=pharo_dir
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return result.stdout.strip() if result.stdout.strip() else "No output"

    except subprocess.TimeoutExpired:
        return "Error: Evaluation timed out"
    except FileNotFoundError:
        return f"Error: Pharo not found at {pharo_dir}. Please check PHARO_DIR environment variable."
    except Exception as e:
        return f"Error: {str(e)}"


def evaluate_pharo_neo_console(expression: str, command: str = "eval") -> str:
    """
    Evaluate a Pharo Smalltalk expression using NeoConsole.

    Args:
        expression: The Smalltalk expression to evaluate
        command: The NeoConsole command to use (default: eval)

    Returns:
        The result of the evaluation
    """
    pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))

    try:
        # Launch pharo vm with NeoConsole repl arguments
        cmd = ["./pharo", "NeoConsole.image", "NeoConsole", "repl"]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=pharo_dir,
        )

        # Send command and expression
        if command == "eval":
            # eval requires an empty line to execute
            input_text = f"{command} {expression}\n\nquit\n"
        else:
            # For non-eval commands, only add expression if it's not empty
            if expression.strip():
                input_text = f"{command} {expression}\nquit\n"
            else:
                input_text = f"{command}\nquit\n"
        stdout, stderr = process.communicate(input=input_text, timeout=30)

        if process.returncode != 0:
            return f"Error: {stderr}"

        # Parse output to extract result
        lines = stdout.strip().split("\n")

        # Filter out greeting, prompts, and system messages
        result_lines = []

        for line in lines:
            line = line.strip()

            # Skip greeting and system info lines
            if (
                line.startswith("NeoConsole")
                or "SNAPSHOT.build" in line
                or "Bit)" in line
            ):
                continue

            # Skip command prompt lines containing our input
            expected_command = (
                f"{command} {expression}".strip() if expression.strip() else command
            )
            if line.startswith("pharo>") and (
                expected_command in line or line == "pharo>"
            ):
                continue

            # Check if this is the quit command or Bye!
            if line == "quit" or line == "Bye!":
                break

            # Check if this line starts with 'pharo>' - it might be a result line
            if line.startswith("pharo>"):
                # Extract everything after 'pharo> '
                result_part = line[7:]  # Skip 'pharo> '
                if result_part:
                    result_lines.append(result_part)
                continue

            # Collect non-empty result lines
            if line:
                result_lines.append(line)

        return "\n".join(result_lines) if result_lines else "No output"

    except subprocess.TimeoutExpired:
        return "Error: Evaluation timed out"
    except FileNotFoundError:
        return f"Error: NeoConsole not found at {pharo_dir}. Please check PHARO_DIR environment variable."
    except Exception as e:
        return f"Error: {str(e)}"


def install_pharo_package(baseline: str, repository: str) -> str:
    """
    Install a Pharo package using Metacello.

    Args:
        baseline: The baseline name of the package (e.g., 'Historia')
        repository: The repository URL (e.g., 'github://mumez/Historia:main/src')

    Returns:
        The result of the package installation
    """
    metacello_neo_console = f"""Metacello new
  baseline: '{baseline}';
  repository: '{repository}';
  load."""

    return evaluate_pharo_neo_console(metacello_neo_console, "eval")


def get_pharo_system_metric(metric: str) -> str:
    """
    Get a system metric from Pharo using NeoConsole get command.

    Args:
        metric: The metric to retrieve (e.g., 'system.status', 'memory.free')

    Returns:
        The metric value
    """
    pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))

    try:
        # Use NeoConsole get command directly
        cmd = ["./pharo", "NeoConsole.image", "NeoConsole", "get", metric]

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=pharo_dir
        )

        if result.returncode != 0:
            return f"Error: {result.stderr}"

        return result.stdout.strip() if result.stdout.strip() else "No output"

    except subprocess.TimeoutExpired:
        return "Error: Evaluation timed out"
    except FileNotFoundError:
        return f"Error: NeoConsole not found at {pharo_dir}. Please check PHARO_DIR environment variable."
    except Exception as e:
        return f"Error: {str(e)}"


def get_class_comment(class_name: str) -> str:
    """
    Get the comment of a Pharo class.

    Args:
        class_name: The name of the class to get the comment for

    Returns:
        The class comment
    """
    expression = f"{class_name} comment"
    return evaluate_pharo_neo_console(expression)


def get_class_definition(class_name: str) -> str:
    """
    Get the definition of a Pharo class.

    Args:
        class_name: The name of the class to get the definition for

    Returns:
        The class definition
    """
    expression = f"{class_name} definitionString"
    return evaluate_pharo_neo_console(expression)


def get_method_list(class_name: str) -> str:
    """
    Get the list of method selectors for a Pharo class.

    Args:
        class_name: The name of the class to get method selectors for

    Returns:
        The list of method selectors
    """
    expression = f"{class_name} selectors"
    return evaluate_pharo_neo_console(expression)


def get_method_source(class_name: str, selector: str) -> str:
    """
    Get the source code of a specific method in a Pharo class.

    Args:
        class_name: The name of the class
        selector: The method selector (message name)

    Returns:
        The method source code
    """
    expression = f"{class_name} sourceCodeAt: #{selector}"
    return evaluate_pharo_neo_console(expression)
