import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestConfig(unittest.TestCase):
    """Test configuration logic for StockSenseAgent."""

    def setUp(self):
        # Patch sys.modules to mock pandas for the agent module
        self.pandas_mock = MagicMock()
        self.modules_patcher = patch.dict(sys.modules, {'pandas': self.pandas_mock})
        self.modules_patcher.start()

        # Ensure we import/reload agent with the mocked pandas
        if 'agent' in sys.modules:
            del sys.modules['agent']
        import agent
        self.agent_module = agent
        self.agent = agent.StockSenseAgent()

        # Mock datetime
        self.datetime_patcher = patch('agent.datetime')
        self.mock_datetime = self.datetime_patcher.start()
        self.mock_datetime.now.return_value = MagicMock()
        self.mock_datetime.strptime.side_effect = MagicMock()

    def tearDown(self):
        self.datetime_patcher.stop()
        self.modules_patcher.stop()
        # Clean up agent module to avoid polluting other tests
        if 'agent' in sys.modules:
            del sys.modules['agent']

    def test_default_inventory_file(self):
        """Test scan_inventory uses DEFAULT_INVENTORY_FILE when no args provided."""
        # Ensure INVENTORY_FILE env var is not set
        with patch.dict(os.environ, {}, clear=True):
            # Assert constant exists
            if not hasattr(self.agent_module, 'DEFAULT_INVENTORY_FILE'):
                self.fail("DEFAULT_INVENTORY_FILE constant not found in agent module")

            default_file = self.agent_module.DEFAULT_INVENTORY_FILE

            # Setup read_csv mock on the mocked pandas
            self.pandas_mock.read_csv = MagicMock()

            self.agent.scan_inventory()
            self.pandas_mock.read_csv.assert_called_with(default_file)

    def test_env_var_override(self):
        """Test scan_inventory uses INVENTORY_FILE env var when set."""
        env_file = "env_inventory.csv"

        # Setup read_csv mock
        self.pandas_mock.read_csv = MagicMock()

        with patch.dict(os.environ, {"INVENTORY_FILE": env_file}):
            self.agent.scan_inventory()
            self.pandas_mock.read_csv.assert_called_with(env_file)

    def test_argument_override(self):
        """Test scan_inventory uses argument when provided, ignoring env var."""
        arg_file = "arg_inventory.csv"
        env_file = "env_inventory.csv"

        # Setup read_csv mock
        self.pandas_mock.read_csv = MagicMock()

        with patch.dict(os.environ, {"INVENTORY_FILE": env_file}):
            self.agent.scan_inventory(arg_file)
            self.pandas_mock.read_csv.assert_called_with(arg_file)

if __name__ == '__main__':
    unittest.main()
