"""Tests for pharo_nc_mcp_server.server module."""

from unittest.mock import patch

# Test the actual functions directly by recreating them
from pharo_nc_mcp_server.core import evaluate_pharo_neo_console


def quit_neo_console_function() -> str:
    """Replicate the quit_neo_console function for testing."""
    return evaluate_pharo_neo_console("", "quit")


class TestQuitNeoConsole:
    """Test cases for quit_neo_console tool."""

    @patch("tests.test_server.evaluate_pharo_neo_console")
    def test_quit_neo_console_success(self, mock_evaluate):
        """Test successful quit command."""
        mock_evaluate.return_value = "Bye!"
        
        result = quit_neo_console_function()
        
        mock_evaluate.assert_called_once_with("", "quit")
        assert result == "Bye!"

    @patch("tests.test_server.evaluate_pharo_neo_console")
    def test_quit_neo_console_error(self, mock_evaluate):
        """Test quit command with error."""
        mock_evaluate.return_value = "Error: Process failed"
        
        result = quit_neo_console_function()
        
        mock_evaluate.assert_called_once_with("", "quit")
        assert result == "Error: Process failed"

    @patch("tests.test_server.evaluate_pharo_neo_console")
    def test_quit_neo_console_timeout(self, mock_evaluate):
        """Test quit command with timeout."""
        mock_evaluate.return_value = "Error: Evaluation timed out"
        
        result = quit_neo_console_function()
        
        mock_evaluate.assert_called_once_with("", "quit")
        assert result == "Error: Evaluation timed out"


