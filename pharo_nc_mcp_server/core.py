"""Core functions for Pharo MCP server without FastMCP decorators."""

import subprocess
import os
import socket
import threading
import time
import atexit


# Global telnet connection and NeoConsole server process
_telnet_connection = None
_neoconsole_process = None
_connection_lock = threading.Lock()


# Export internal functions for testing
__all__ = [
    'evaluate_pharo_neo_console',
    'evaluate_pharo_simple', 
    'install_pharo_package',
    'get_pharo_system_metric',
    'get_class_comment',
    'get_class_definition',
    'get_method_list',
    'get_method_source',
    '_send_telnet_command',
    '_close_telnet_connection'
]


def _start_neoconsole_server():
    """Start NeoConsole telnet server."""
    global _neoconsole_process
    
    pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))
    
    try:
        cmd = ["./pharo", "NeoConsole.image", "NeoConsole", "server"]
        _neoconsole_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=pharo_dir,
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        return True
    except Exception as e:
        print(f"Failed to start NeoConsole server: {e}")
        return False


def _get_socket_connection():
    """Get or create socket connection to NeoConsole server."""
    global _telnet_connection
    
    with _connection_lock:
        if _telnet_connection is None:
            # Start server if not running
            if _neoconsole_process is None or _neoconsole_process.poll() is not None:
                if not _start_neoconsole_server():
                    raise Exception("Failed to start NeoConsole server")
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect(("localhost", 4999))
                _telnet_connection = sock
                # Read greeting message
                _read_until_prompt(sock)
            except Exception as e:
                raise Exception(f"Failed to connect to NeoConsole server: {e}")
        
        return _telnet_connection


def _read_until_prompt(sock, timeout=5):
    """Read from socket until we see the pharo> prompt."""
    sock.settimeout(timeout)
    data = b""
    while b"pharo> " not in data:
        chunk = sock.recv(1024)
        if not chunk:
            break
        data += chunk
    return data.decode()


def _read_until_prompt_or_close(sock, timeout=30):
    """Read from socket until we see the pharo> prompt or connection closes."""
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            if b"pharo> " in data:
                break
        except socket.timeout:
            break
    return data.decode()


def _send_telnet_command(command: str, expect_prompt: bool = True) -> str:
    """Send command via socket and get response."""
    try:
        sock = _get_socket_connection()
        
        # Send command
        sock.send(f"{command}\n".encode())
        
        if expect_prompt:
            # Read until next prompt
            response = _read_until_prompt_or_close(sock, timeout=30)
            # Remove the trailing prompt
            if response.endswith("pharo> "):
                response = response[:-7]
        else:
            # For quit command, read until connection closes
            response = _read_until_prompt_or_close(sock, timeout=10)
        
        return response.strip()
        
    except Exception as e:
        # Reset connection on error
        _close_telnet_connection()
        raise Exception(f"Telnet communication error: {e}")


def _close_telnet_connection():
    """Close socket connection and stop server."""
    global _telnet_connection, _neoconsole_process
    
    with _connection_lock:
        if _telnet_connection:
            try:
                _telnet_connection.close()
            except Exception:
                pass
            _telnet_connection = None
        
        if _neoconsole_process:
            try:
                _neoconsole_process.terminate()
                _neoconsole_process.wait(timeout=5)
            except Exception:
                try:
                    _neoconsole_process.kill()
                except Exception:
                    pass
            _neoconsole_process = None


# Register cleanup function
atexit.register(_close_telnet_connection)


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
    Evaluate a Pharo Smalltalk expression using NeoConsole via telnet.

    Args:
        expression: The Smalltalk expression to evaluate
        command: The NeoConsole command to use (default: eval)

    Returns:
        The result of the evaluation
    """
    try:
        if command == "eval":
            # For eval command, send expression and empty line to execute
            if expression.strip():
                full_command = f"eval {expression}\n"
            else:
                return "Error: Empty expression"
        elif command == "quit":
            # For quit command, close connection
            response = _send_telnet_command("quit", expect_prompt=False)
            _close_telnet_connection()
            return "NeoConsole session terminated"
        else:
            # For other commands (get, history, etc.)
            if expression.strip():
                full_command = f"{command} {expression}"
            else:
                full_command = command
        
        response = _send_telnet_command(full_command)
        
        # Clean up response by removing command echo and empty lines
        lines = response.split('\n')
        result_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and command echoes
            if not line:
                continue
            # Skip lines that just echo our command
            if line.startswith(command) and (not expression or expression in line):
                continue
            result_lines.append(line)
        
        return '\n'.join(result_lines) if result_lines else "No output"
        
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
