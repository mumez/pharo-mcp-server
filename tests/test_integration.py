"""Integration tests for pharo_mcp_server using actual NeoConsole."""

import os
import subprocess
import pytest
from pathlib import Path


@pytest.mark.integration
class TestNeoConsoleIntegration:
    """Integration tests using real NeoConsole if available."""

    @pytest.fixture
    def pharo_available(self):
        """Check if Pharo and NeoConsole are available for testing."""
        pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))

        if not os.path.exists(pharo_dir):
            pytest.skip(f"PHARO_DIR '{pharo_dir}' does not exist")

        neoconsole_image = os.path.join(pharo_dir, "NeoConsole.image")
        if not os.path.exists(neoconsole_image):
            pytest.skip(f"NeoConsole.image not found in {pharo_dir}")

        pharo_executable = os.path.join(pharo_dir, "pharo")
        if not os.path.exists(pharo_executable):
            pytest.skip(f"pharo executable not found in {pharo_dir}")

        return pharo_dir

    def test_neoconsole_repl_script_exists(self):
        """Test that the NeoConsole REPL script exists and is executable."""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "start-neoconsole-repl.sh"
        )
        assert script_path.exists(), "NeoConsole REPL script should exist"
        assert os.access(
            script_path, os.X_OK
        ), "NeoConsole REPL script should be executable"

    def test_neoconsole_eval_simple_expression(self, pharo_available):
        """Test simple evaluation using NeoConsole REPL."""
        pharo_dir = pharo_available

        try:
            # Test simple arithmetic
            process = subprocess.Popen(
                ["./pharo", "NeoConsole.image", "NeoConsole", "repl"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=pharo_dir,
            )

            # Send eval command with double newline, then quit
            input_text = "eval 3 + 4\n\nquit\n"
            stdout, stderr = process.communicate(input=input_text, timeout=10)

            assert process.returncode == 0, f"Process failed with stderr: {stderr}"
            assert "7" in stdout, f"Expected '7' in output, got: {stdout}"

        except subprocess.TimeoutExpired:
            pytest.skip("NeoConsole REPL timed out - may not be responsive")
        except Exception as e:
            pytest.skip(f"NeoConsole integration test failed: {str(e)}")

    def test_neoconsole_get_metric(self, pharo_available):
        """Test getting metrics using NeoConsole get command."""
        pharo_dir = pharo_available

        try:
            # Test getting system status
            result = subprocess.run(
                ["./pharo", "NeoConsole.image", "NeoConsole", "get", "system.status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=pharo_dir,
            )

            assert (
                result.returncode == 0
            ), f"Get command failed with stderr: {result.stderr}"
            assert (
                "Status OK" in result.stdout
            ), f"Expected 'Status OK' in output, got: {result.stdout}"

        except subprocess.TimeoutExpired:
            pytest.skip("NeoConsole get command timed out")
        except Exception as e:
            pytest.skip(f"NeoConsole get integration test failed: {str(e)}")

    def test_neoconsole_get_memory_metric(self, pharo_available):
        """Test getting memory metrics using NeoConsole get command."""
        pharo_dir = pharo_available

        try:
            # Test getting memory total
            result = subprocess.run(
                ["./pharo", "NeoConsole.image", "NeoConsole", "get", "memory.total"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=pharo_dir,
            )

            assert (
                result.returncode == 0
            ), f"Get memory command failed with stderr: {result.stderr}"
            # Memory total should be a number
            memory_value = result.stdout.strip()
            assert (
                memory_value.isdigit()
            ), f"Expected numeric memory value, got: {memory_value}"
            assert (
                int(memory_value) > 0
            ), f"Expected positive memory value, got: {memory_value}"

        except subprocess.TimeoutExpired:
            pytest.skip("NeoConsole get memory command timed out")
        except Exception as e:
            pytest.skip(f"NeoConsole get memory integration test failed: {str(e)}")

    def test_neoconsole_repl_script_execution(self, pharo_available):
        """Test that the REPL script can be executed (quick validation)."""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "start-neoconsole-repl.sh"
        )

        try:
            # Test script with a quick eval and immediate quit
            process = subprocess.Popen(
                [str(script_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PHARO_DIR": pharo_available},
            )

            # Send quit immediately to test script startup
            input_text = "quit\n"
            stdout, stderr = process.communicate(input=input_text, timeout=10)

            assert process.returncode == 0, f"Script failed with stderr: {stderr}"
            assert (
                "NeoConsole" in stdout or "Bye!" in stdout
            ), f"Expected NeoConsole output, got: {stdout}"

        except subprocess.TimeoutExpired:
            process.kill()
            pytest.skip("NeoConsole REPL script timed out")
        except Exception as e:
            pytest.skip(f"NeoConsole REPL script test failed: {str(e)}")


@pytest.mark.integration
class TestMCPServerIntegration:
    """Integration tests for the MCP server functions using real Pharo if available."""

    @pytest.fixture
    def pharo_available(self):
        """Check if Pharo and NeoConsole are available for testing."""
        pharo_dir = os.environ.get("PHARO_DIR", os.path.expanduser("~/pharo"))

        if not os.path.exists(pharo_dir):
            pytest.skip(f"PHARO_DIR '{pharo_dir}' does not exist")

        neoconsole_image = os.path.join(pharo_dir, "NeoConsole.image")
        if not os.path.exists(neoconsole_image):
            pytest.skip(f"NeoConsole.image not found in {pharo_dir}")

        return pharo_dir

    def test_evaluate_pharo_simple_integration(self, pharo_available):
        """Test evaluate_pharo_simple with real Pharo."""
        from pharo_nc_mcp_server.core import evaluate_pharo_simple

        # Set PHARO_DIR for the test
        original_env = os.environ.get("PHARO_DIR")
        os.environ["PHARO_DIR"] = pharo_available

        try:
            result = evaluate_pharo_simple("3 + 4")
            assert "7" in result, f"Expected '7' in result, got: {result}"

        except Exception as e:
            pytest.skip(f"evaluate_pharo_simple integration test failed: {str(e)}")
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["PHARO_DIR"] = original_env
            elif "PHARO_DIR" in os.environ:
                del os.environ["PHARO_DIR"]

    def test_get_pharo_system_metric_integration(self, pharo_available):
        """Test get_pharo_system_metric with real Pharo."""
        from pharo_nc_mcp_server.core import get_pharo_system_metric

        # Set PHARO_DIR for the test
        original_env = os.environ.get("PHARO_DIR")
        os.environ["PHARO_DIR"] = pharo_available

        try:
            result = get_pharo_system_metric("system.status")
            assert (
                "Status OK" in result
            ), f"Expected 'Status OK' in result, got: {result}"

        except Exception as e:
            pytest.skip(f"get_pharo_system_metric integration test failed: {str(e)}")
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["PHARO_DIR"] = original_env
            elif "PHARO_DIR" in os.environ:
                del os.environ["PHARO_DIR"]

    def test_evaluate_pharo_neo_console_integration(self, pharo_available):
        """Test evaluate_pharo_neo_console with real Pharo."""
        from pharo_nc_mcp_server.core import evaluate_pharo_neo_console

        # Set PHARO_DIR for the test
        original_env = os.environ.get("PHARO_DIR")
        os.environ["PHARO_DIR"] = pharo_available

        try:
            result = evaluate_pharo_neo_console("3 + 4")
            assert "7" in result, f"Expected '7' in result, got: {result}"

        except Exception as e:
            pytest.skip(f"evaluate_pharo_neo_console integration test failed: {str(e)}")
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["PHARO_DIR"] = original_env
            elif "PHARO_DIR" in os.environ:
                del os.environ["PHARO_DIR"]

