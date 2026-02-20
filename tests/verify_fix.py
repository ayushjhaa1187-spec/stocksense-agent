import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
# Mock dotenv
sys.modules['dotenv'] = MagicMock()

import agent

class TestAgentPaths(unittest.TestCase):
    def setUp(self):
        # Clear environment variables
        if "INVENTORY_FILE" in os.environ:
            del os.environ["INVENTORY_FILE"]
        if "OUTPUT_FILE" in os.environ:
            del os.environ["OUTPUT_FILE"]

    @patch('os.getenv')
    def test_scan_inventory_default_path(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default: default if key == "INVENTORY_FILE" else None

        # We need to mock pd.read_csv because it's called inside scan_inventory
        with patch('pandas.read_csv') as mock_read_csv:
            a = agent.StockSenseAgent()
            a.scan_inventory()

            # Check if getenv was called with INVENTORY_FILE
            mock_getenv.assert_any_call("INVENTORY_FILE", "data/sample_inventory.csv")
            # Check if read_csv was called with the default path
            mock_read_csv.assert_called_with("data/sample_inventory.csv")

    @patch('os.getenv')
    def test_scan_inventory_env_path(self, mock_getenv):
        env_path = "env/my_inventory.csv"
        mock_getenv.side_effect = lambda key, default: env_path if key == "INVENTORY_FILE" else None

        with patch('pandas.read_csv') as mock_read_csv:
            a = agent.StockSenseAgent()
            a.scan_inventory()

            mock_read_csv.assert_called_with(env_path)

    @patch('os.getenv')
    def test_save_recommendations_default_path(self, mock_getenv):
        mock_getenv.side_effect = lambda key, default: default if key == "OUTPUT_FILE" else None

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            with patch('os.makedirs') as mock_makedirs:
                with patch('json.dump') as mock_json_dump:
                    a = agent.StockSenseAgent()
                    a.save_recommendations({"test": "data"})

                    mock_getenv.assert_any_call("OUTPUT_FILE", "output/recommendations.json")
                    mock_file.assert_called_with("output/recommendations.json", "w")

    @patch('os.getenv')
    def test_save_recommendations_env_path(self, mock_getenv):
        env_path = "env/my_output.json"
        mock_getenv.side_effect = lambda key, default: env_path if key == "OUTPUT_FILE" else None

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            with patch('os.makedirs') as mock_makedirs:
                with patch('json.dump') as mock_json_dump:
                    a = agent.StockSenseAgent()
                    a.save_recommendations({"test": "data"})

                    mock_file.assert_called_with(env_path, "w")

if __name__ == '__main__':
    unittest.main()
