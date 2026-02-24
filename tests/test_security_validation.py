import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestSecurityValidation:

    @pytest.fixture
    def agent(self):
        return StockSenseAgent()

    @pytest.fixture
    def setup_dirs(self):
        # Create dummy directories for testing if they don't exist
        created_data = False
        created_output = False

        if not os.path.exists("data"):
            os.makedirs("data")
            created_data = True

        if not os.path.exists("output"):
            os.makedirs("output")
            created_output = True

        yield

        # Cleanup not strictly necessary as these are standard dirs,
        # but could clean up test artifacts if needed.

    def test_validate_path_valid(self, agent, setup_dirs):
        # Test valid paths
        # Note: These files don't need to exist for _validate_path,
        # but the directory structure matters for realpath

        # Valid data path
        valid_data = "data/test.csv"
        # We compare absolute paths
        expected = os.path.realpath(valid_data)
        assert agent._validate_path(valid_data, "data") == expected

        # Valid output path
        valid_output = "output/test.json"
        expected = os.path.realpath(valid_output)
        assert agent._validate_path(valid_output, "output") == expected

    def test_validate_path_traversal(self, agent, setup_dirs):
        # Test path traversal attempts

        # Attempt to escape data directory
        with pytest.raises(ValueError, match="Security Alert"):
            agent._validate_path("data/../secret.txt", "data")

        # Attempt to access file in parent
        with pytest.raises(ValueError, match="Security Alert"):
            agent._validate_path("../outside.txt", "data")

        # Attempt to access absolute path (assuming /etc/passwd exists or is outside)
        # Even if it doesn't exist, it should resolve to outside of CWD/data
        with pytest.raises(ValueError, match="Security Alert"):
            # Use a path that is definitely outside
            agent._validate_path(os.path.abspath("outside.txt"), "data")

    def test_scan_inventory_security(self, agent, setup_dirs):
        # Test scan_inventory with invalid path
        # Should return None and check for error logging (mock print?)

        with patch('builtins.print') as mock_print:
            result = agent.scan_inventory(inventory_file="data/../secret.csv")
            assert result is None

            # Verify error message
            # The exact message depends on the ValueError raised
            args, _ = mock_print.call_args
            assert "ERROR: Security Alert" in args[0]

    def test_save_recommendations_security(self, agent, setup_dirs):
        # Test save_recommendations with invalid path

        target = "src/hacked_test.txt"

        # Ensure target doesn't exist
        if os.path.exists(target):
            os.remove(target)

        with patch('builtins.print') as mock_print:
            agent.save_recommendations({}, output_file=target)

            # Verify file was NOT created
            assert not os.path.exists(target)

            # Verify error message
            args, _ = mock_print.call_args
            assert "ERROR: Security Alert" in args[0]
