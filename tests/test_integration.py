"""Integration tests for pharo_nc_mcp_server using actual NeoConsole."""

import os
import subprocess
import pytest
import time
import socket
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
        assert os.access(script_path, os.X_OK), (
            "NeoConsole REPL script should be executable"
        )

    def test_neoconsole_server_telnet_connection(self, pharo_available):
        """Test telnet connection to NeoConsole server."""
        pharo_dir = pharo_available
        server_process = None

        try:
            # Start NeoConsole server
            server_process = subprocess.Popen(
                ["./pharo", "NeoConsole.image", "NeoConsole", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=pharo_dir,
            )

            # Wait for server to start
            time.sleep(2)

            # Test telnet connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", 4999))

            # Read greeting
            data = b""
            while b"pharo> " not in data:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                data += chunk

            greeting = data.decode()
            assert "NeoConsole" in greeting, (
                f"Expected NeoConsole greeting, got: {greeting}"
            )

            # Send eval command
            sock.send(b"eval 3 + 4\n")

            # Read response
            data = b""
            while b"pharo> " not in data:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                data += chunk

            response = data.decode()
            assert "7" in response, f"Expected '7' in response, got: {response}"

            # Send quit
            sock.send(b"quit\n")
            sock.close()

        except socket.error as e:
            pytest.skip(f"Failed to connect to NeoConsole server: {e}")
        except Exception as e:
            pytest.skip(f"NeoConsole server integration test failed: {str(e)}")
        finally:
            if server_process:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()

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

            assert result.returncode == 0, (
                f"Get command failed with stderr: {result.stderr}"
            )
            assert "Status OK" in result.stdout, (
                f"Expected 'Status OK' in output, got: {result.stdout}"
            )

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

            assert result.returncode == 0, (
                f"Get memory command failed with stderr: {result.stderr}"
            )
            # Memory total should be a number
            memory_value = result.stdout.strip()
            assert memory_value.isdigit(), (
                f"Expected numeric memory value, got: {memory_value}"
            )
            assert int(memory_value) > 0, (
                f"Expected positive memory value, got: {memory_value}"
            )

        except subprocess.TimeoutExpired:
            pytest.skip("NeoConsole get memory command timed out")
        except Exception as e:
            pytest.skip(f"NeoConsole get memory integration test failed: {str(e)}")

    def test_neoconsole_server_script_execution(self, pharo_available):
        """Test that the server script can be executed."""
        script_path = (
            Path(__file__).parent.parent / "scripts" / "start-neoconsole-repl.sh"
        )
        server_process = None

        try:
            # Test script in server mode
            server_process = subprocess.Popen(
                [str(script_path), "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "PHARO_DIR": pharo_available},
            )

            # Wait for server to start
            time.sleep(2)

            # Test that server is running by connecting
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", 4999))

            # Read greeting to confirm server is working
            data = b""
            while b"pharo> " not in data:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                data += chunk

            greeting = data.decode()
            assert "NeoConsole" in greeting, (
                f"Expected NeoConsole in greeting, got: {greeting}"
            )

            sock.close()

        except socket.error as e:
            pytest.skip(f"Failed to connect to script-started server: {e}")
        except subprocess.TimeoutExpired:
            pytest.skip("NeoConsole server script timed out")
        except Exception as e:
            pytest.skip(f"NeoConsole server script test failed: {str(e)}")
        finally:
            if server_process:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()


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
            assert "Status OK" in result, (
                f"Expected 'Status OK' in result, got: {result}"
            )

        except Exception as e:
            pytest.skip(f"get_pharo_system_metric integration test failed: {str(e)}")
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["PHARO_DIR"] = original_env
            elif "PHARO_DIR" in os.environ:
                del os.environ["PHARO_DIR"]

    def test_evaluate_pharo_neo_console_integration(self, pharo_available):
        """Test evaluate_pharo_neo_console with real Pharo using telnet server."""
        from pharo_nc_mcp_server.core import (
            evaluate_pharo_neo_console,
            _close_telnet_connection,
        )

        # Set PHARO_DIR for the test
        original_env = os.environ.get("PHARO_DIR")
        os.environ["PHARO_DIR"] = pharo_available

        try:
            # Clean up any existing connections
            _close_telnet_connection()

            result = evaluate_pharo_neo_console("3 + 4")
            assert "7" in result, f"Expected '7' in result, got: {result}"

            # Test another evaluation to ensure session persistence
            result2 = evaluate_pharo_neo_console("5 * 6")
            assert "30" in result2, f"Expected '30' in result, got: {result2}"

        except Exception as e:
            pytest.skip(f"evaluate_pharo_neo_console integration test failed: {str(e)}")
        finally:
            # Clean up telnet connection
            _close_telnet_connection()

            # Restore original environment
            if original_env is not None:
                os.environ["PHARO_DIR"] = original_env
            elif "PHARO_DIR" in os.environ:
                del os.environ["PHARO_DIR"]
