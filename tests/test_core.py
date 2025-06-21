"""Tests for pharo_mcp_server.core module."""

from unittest.mock import patch, MagicMock
import subprocess
import os

from pharo_nc_mcp_server.core import (
    evaluate_pharo_neo_console,
    evaluate_pharo_simple,
    install_pharo_package,
    get_pharo_system_metric,
    get_class_comment,
    get_class_definition,
    get_method_list,
    get_method_source,
)


class TestEvaluatePharoNeoConsole:
    """Test cases for evaluate_pharo_neo_console function."""

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_evaluate_expression_success(self, mock_send_telnet):
        """Test successful expression evaluation."""
        # Setup mock
        mock_send_telnet.return_value = "eval 42 factorial\n\n1405006117752879898543142606244511569936384000000000"

        result = evaluate_pharo_neo_console("42 factorial")

        # Assertions
        assert "1405006117752879898543142606244511569936384000000000" in result
        mock_send_telnet.assert_called_once_with("eval 42 factorial\n")

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_evaluate_expression_with_custom_command(self, mock_send_telnet):
        """Test expression evaluation with custom command."""
        mock_send_telnet.return_value = "get system.status\nStatus OK"

        result = evaluate_pharo_neo_console("system.status", "get")

        assert "Status OK" in result
        mock_send_telnet.assert_called_once_with("get system.status")

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_evaluate_expression_with_history_command(self, mock_send_telnet):
        """Test expression evaluation with history command (no expression)."""
        mock_send_telnet.return_value = "history\n1: 3+3\n2: Array comment"

        result = evaluate_pharo_neo_console("", "history")

        assert "1: 3+3" in result
        assert "2: Array comment" in result
        mock_send_telnet.assert_called_once_with("history")

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    def test_evaluate_expression_process_error(self, mock_send_telnet):
        """Test handling of process errors."""
        mock_send_telnet.side_effect = Exception("Process failed")

        result = evaluate_pharo_neo_console("invalid expression")

        assert "Error: Process failed" in result

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    def test_evaluate_expression_timeout(self, mock_send_telnet):
        """Test handling of timeout."""
        mock_send_telnet.side_effect = Exception("Evaluation timed out")

        result = evaluate_pharo_neo_console("long running expression")

        assert "Error: Evaluation timed out" in result

    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    def test_evaluate_expression_file_not_found(self, mock_send_telnet):
        """Test handling of missing NeoConsole."""
        mock_send_telnet.side_effect = Exception("Failed to start NeoConsole server")

        result = evaluate_pharo_neo_console("42 factorial")

        assert "Error: Failed to start NeoConsole server" in result


class TestEvaluatePharoSimple:
    """Test cases for evaluate_pharo_simple function."""

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_evaluate_simple_success(self, mock_run):
        """Test successful simple expression evaluation."""
        mock_run.return_value = MagicMock(stdout="42\n", stderr="", returncode=0)

        result = evaluate_pharo_simple("6 * 7")

        # Assertions
        assert result == "42"
        mock_run.assert_called_once_with(
            ["./pharo", "Pharo.image", "-e", "6 * 7"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/test/pharo",
        )

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_evaluate_simple_error(self, mock_run):
        """Test simple evaluation with process error."""
        mock_run.return_value = MagicMock(
            stdout="", stderr="Syntax error", returncode=1
        )

        result = evaluate_pharo_simple("invalid syntax")

        assert result == "Error: Syntax error"

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_evaluate_simple_timeout(self, mock_run):
        """Test simple evaluation timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        result = evaluate_pharo_simple("long running")

        assert result == "Error: Evaluation timed out"

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_evaluate_simple_file_not_found(self, mock_run):
        """Test simple evaluation with missing Pharo."""
        mock_run.side_effect = FileNotFoundError()

        result = evaluate_pharo_simple("42")

        assert "Error: Pharo not found" in result

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_evaluate_simple_no_output(self, mock_run):
        """Test simple evaluation with no output."""
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)

        result = evaluate_pharo_simple("nil")

        assert result == "No output"

    def test_evaluate_simple_default_pharo_dir(self):
        """Test default PHARO_DIR when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pharo_nc_mcp_server.core.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="result", stderr="", returncode=0
                )

                evaluate_pharo_simple("test")

                # Check that default path is used
                call_args = mock_run.call_args
                expected_path = os.path.expanduser("~/pharo")
                assert call_args.kwargs["cwd"] == expected_path


class TestInstallPharoPackage:
    """Test cases for install_pharo_package function."""

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_install_package_success(self, mock_evaluate):
        """Test successful package installation."""
        mock_evaluate.return_value = "Package installed successfully"

        result = install_pharo_package("Historia", "github://mumez/Historia:main/src")

        # Check that evaluate_pharo_neo_console was called with correct Metacello expression
        mock_evaluate.assert_called_once()
        call_args = mock_evaluate.call_args[0]
        assert "Metacello new" in call_args[0]
        assert "baseline: 'Historia'" in call_args[0]
        assert "repository: 'github://mumez/Historia:main/src'" in call_args[0]
        assert "load." in call_args[0]
        assert call_args[1] == "eval"

        assert result == "Package installed successfully"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_install_package_error(self, mock_evaluate):
        """Test package installation error handling."""
        mock_evaluate.return_value = "Error: Package not found"

        result = install_pharo_package("NonExistent", "github://invalid/repo")

        assert result == "Error: Package not found"


class TestGetPharoSystemMetric:
    """Test cases for get_pharo_system_metric function."""

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_get_metric_success(self, mock_run):
        """Test successful metric retrieval."""
        mock_run.return_value = MagicMock(stdout="94466048\n", stderr="", returncode=0)

        result = get_pharo_system_metric("memory.total")

        mock_run.assert_called_once_with(
            ["./pharo", "NeoConsole.image", "NeoConsole", "get", "memory.total"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/test/pharo",
        )
        assert result == "94466048"

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_get_metric_error(self, mock_run):
        """Test metric retrieval error handling."""
        mock_run.return_value = MagicMock(
            stdout="", stderr="Unknown metric", returncode=1
        )

        result = get_pharo_system_metric("invalid.metric")

        assert result == "Error: Unknown metric"

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_get_metric_timeout(self, mock_run):
        """Test metric retrieval timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)

        result = get_pharo_system_metric("system.status")

        assert result == "Error: Evaluation timed out"

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    def test_get_metric_file_not_found(self, mock_run):
        """Test metric retrieval with missing NeoConsole."""
        mock_run.side_effect = FileNotFoundError()

        result = get_pharo_system_metric("system.status")

        assert "Error: NeoConsole not found" in result

    def test_get_metric_default_pharo_dir(self):
        """Test default PHARO_DIR when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pharo_nc_mcp_server.core.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="result", stderr="", returncode=0
                )

                get_pharo_system_metric("system.status")

                # Check that default path is used
                call_args = mock_run.call_args
                expected_path = os.path.expanduser("~/pharo")
                assert call_args.kwargs["cwd"] == expected_path


class TestIntegration:
    """Integration tests."""

    @patch("pharo_nc_mcp_server.core.subprocess.run")
    @patch("pharo_nc_mcp_server.core._send_telnet_command")
    @patch.dict(os.environ, {"PHARO_DIR": "/test/pharo"})
    def test_full_workflow(self, mock_send_telnet, mock_run):
        """Test a complete workflow with multiple operations."""
        # Setup mock for get_pharo_system_metric (uses subprocess.run)
        mock_run.return_value = MagicMock(
            stdout="Status OK - Clock 2025-06-19T23:37:11.519251+09:00 - Allocated 94,466,048 bytes - 20.23 % free.\n",
            stderr="",
            returncode=0,
        )

        # Setup mock for evaluate_pharo_neo_console (uses telnet)
        mock_send_telnet.return_value = "eval 42 factorial\n\n1405006117752879898543142606244511569936384000000000"

        # Test system status
        result1 = get_pharo_system_metric("system.status")
        assert "Status OK" in result1

        # Test factorial calculation
        result2 = evaluate_pharo_neo_console("42 factorial")
        assert "1405006117752879898543142606244511569936384000000000" in result2


class TestGetClassComment:
    """Test cases for get_class_comment function."""

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_comment_success(self, mock_evaluate):
        """Test successful class comment retrieval."""
        mock_evaluate.return_value = (
            "I represent an object that holds a reference to another object."
        )

        result = get_class_comment("Array")

        mock_evaluate.assert_called_once_with("Array comment")
        assert (
            result == "I represent an object that holds a reference to another object."
        )

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_comment_error(self, mock_evaluate):
        """Test class comment retrieval error handling."""
        mock_evaluate.return_value = "Error: Class not found"

        result = get_class_comment("NonExistentClass")

        mock_evaluate.assert_called_once_with("NonExistentClass comment")
        assert result == "Error: Class not found"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_comment_empty(self, mock_evaluate):
        """Test class comment retrieval with empty comment."""
        mock_evaluate.return_value = ""

        result = get_class_comment("SomeClass")

        mock_evaluate.assert_called_once_with("SomeClass comment")
        assert result == ""


class TestGetClassDefinition:
    """Test cases for get_class_definition function."""

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_definition_success(self, mock_evaluate):
        """Test successful class definition retrieval."""
        mock_evaluate.return_value = "ArrayedCollection variableSubclass: #Array\n\tinstanceVariableNames: ''\n\tclassVariableNames: ''\n\tpoolDictionaries: ''\n\tcategory: 'Collections-Sequenceable'"

        result = get_class_definition("Array")

        mock_evaluate.assert_called_once_with("Array definitionString")
        assert "ArrayedCollection variableSubclass: #Array" in result

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_definition_error(self, mock_evaluate):
        """Test class definition retrieval error handling."""
        mock_evaluate.return_value = "Error: Class not found"

        result = get_class_definition("NonExistentClass")

        mock_evaluate.assert_called_once_with("NonExistentClass definitionString")
        assert result == "Error: Class not found"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_class_definition_with_special_characters(self, mock_evaluate):
        """Test class definition with special characters in class name."""
        mock_evaluate.return_value = (
            "Object subclass: #TestClass\n\tinstanceVariableNames: 'var1 var2'"
        )

        result = get_class_definition("TestClass")

        mock_evaluate.assert_called_once_with("TestClass definitionString")
        assert "Object subclass: #TestClass" in result


class TestGetMethodList:
    """Test cases for get_method_list function."""

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_list_success(self, mock_evaluate):
        """Test successful method list retrieval."""
        mock_evaluate.return_value = (
            "#(#at: #at:put: #size #do: #collect: #select: #asSet)"
        )

        result = get_method_list("Array")

        mock_evaluate.assert_called_once_with("Array selectors")
        assert "#at:" in result
        assert "#size" in result
        assert "#asSet" in result

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_list_error(self, mock_evaluate):
        """Test method list retrieval error handling."""
        mock_evaluate.return_value = "Error: Class not found"

        result = get_method_list("NonExistentClass")

        mock_evaluate.assert_called_once_with("NonExistentClass selectors")
        assert result == "Error: Class not found"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_list_empty(self, mock_evaluate):
        """Test method list retrieval with no methods."""
        mock_evaluate.return_value = "#()"

        result = get_method_list("EmptyClass")

        mock_evaluate.assert_called_once_with("EmptyClass selectors")
        assert result == "#()"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_list_complex_selectors(self, mock_evaluate):
        """Test method list with complex selectors."""
        mock_evaluate.return_value = (
            "#(#at:ifAbsent: #at:put:ifAbsent: #keyAtValue:ifAbsent:)"
        )

        result = get_method_list("Dictionary")

        mock_evaluate.assert_called_once_with("Dictionary selectors")
        assert "#at:ifAbsent:" in result
        assert "#keyAtValue:ifAbsent:" in result


class TestGetMethodSource:
    """Test cases for get_method_source function."""

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_success(self, mock_evaluate):
        """Test successful method source retrieval."""
        mock_evaluate.return_value = (
            'asSet\n\t"Convert the receiver to a Set."\n\t^ Set withAll: self'
        )

        result = get_method_source("Array", "asSet")

        mock_evaluate.assert_called_once_with("Array sourceCodeAt: #asSet")
        assert "asSet" in result
        assert "Set withAll: self" in result

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_error(self, mock_evaluate):
        """Test method source retrieval error handling."""
        mock_evaluate.return_value = "Error: Method not found"

        result = get_method_source("Array", "nonExistentMethod")

        mock_evaluate.assert_called_once_with("Array sourceCodeAt: #nonExistentMethod")
        assert result == "Error: Method not found"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_class_not_found(self, mock_evaluate):
        """Test method source retrieval with non-existent class."""
        mock_evaluate.return_value = "Error: Class not found"

        result = get_method_source("NonExistentClass", "someMethod")

        mock_evaluate.assert_called_once_with(
            "NonExistentClass sourceCodeAt: #someMethod"
        )
        assert result == "Error: Class not found"

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_complex_selector(self, mock_evaluate):
        """Test method source retrieval with complex selector."""
        mock_evaluate.return_value = 'at:ifAbsent:\n\t"Answer the value at the given key, or the result of evaluating aBlock if not found."\n\t^ self at: key ifAbsent: aBlock'

        result = get_method_source("Dictionary", "at:ifAbsent:")

        mock_evaluate.assert_called_once_with("Dictionary sourceCodeAt: #at:ifAbsent:")
        assert "at:ifAbsent:" in result
        assert "aBlock" in result

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_with_special_characters(self, mock_evaluate):
        """Test method source with special characters in method name."""
        mock_evaluate.return_value = '= anObject\n\t"Answer whether the receiver and the argument represent the same object."\n\t^ self == anObject'

        result = get_method_source("Object", "=")

        mock_evaluate.assert_called_once_with("Object sourceCodeAt: #=")
        assert "= anObject" in result
        assert "self == anObject" in result

    @patch("pharo_nc_mcp_server.core.evaluate_pharo_neo_console")
    def test_get_method_source_multiline(self, mock_evaluate):
        """Test method source retrieval with multiline code."""
        multiline_source = """collect: aBlock
\t\"Evaluate aBlock with each of the receiver's elements as the argument.
\tCollect the resulting values into a collection like the receiver.\"
\t| newCollection |
\tnewCollection := self species new.
\tself do: [ :each | newCollection add: (aBlock value: each) ].
\t^ newCollection"""
        mock_evaluate.return_value = multiline_source

        result = get_method_source("Array", "collect:")

        mock_evaluate.assert_called_once_with("Array sourceCodeAt: #collect:")
        assert "collect: aBlock" in result
        assert "newCollection := self species new" in result
        assert "^ newCollection" in result


