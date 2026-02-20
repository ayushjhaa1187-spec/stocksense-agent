
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Adjust sys.path to find src.agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock pandas before importing src.agent
mock_pd = MagicMock()
sys.modules["pandas"] = mock_pd

# Create a mock DataFrame
mock_df = MagicMock()
mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
# Create namedtuple-like objects for itertuples
from collections import namedtuple
Medicine = namedtuple('Medicine', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])
mock_df.itertuples.return_value = [
    Medicine(0, 'TestDrug', 100, '2025-01-01', 10)
]
mock_pd.read_csv.return_value = mock_df
mock_pd.to_datetime.return_value = '2025-01-01'

from src.agent import StockSenseAgent

class TestStockSenseAgentSecurity(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()
        # Mock os.makedirs to avoid creating directories
        self.makedirs_patcher = patch('os.makedirs')
        self.mock_makedirs = self.makedirs_patcher.start()
        # Mock open to avoid creating files
        self.open_patcher = patch('builtins.open', new_callable=unittest.mock.mock_open)
        self.mock_open = self.open_patcher.start()

    def tearDown(self):
        self.makedirs_patcher.stop()
        self.open_patcher.stop()
        mock_pd.reset_mock()

    def test_scan_inventory_path_traversal(self):
        """Test that scan_inventory blocks path traversal."""
        invalid_path = "../../../etc/passwd"

        # Should return None and log error
        result = self.agent.scan_inventory(inventory_file=invalid_path)

        self.assertIsNone(result)
        mock_pd.read_csv.assert_not_called()

    def test_scan_inventory_valid_path(self):
        """Test that scan_inventory allows valid paths."""
        # We need to simulate a valid path relative to CWD
        # Assuming current working directory is repo root
        # Create a dummy file in data/ to pass validate_path?
        # No, validate_path uses realpath. If file doesn't exist, realpath still works on Linux/Mac unless it's strict?
        # But we are mocking pandas, so read_csv won't fail on missing file.
        # However, validate_path checks if path is inside 'data'.
        # 'data/test.csv' -> repo/data/test.csv. 'data' -> repo/data. Match.

        valid_path = "data/test.csv"

        result = self.agent.scan_inventory(inventory_file=valid_path)

        # result should be a dict if successful
        self.assertIsNotNone(result)
        self.assertIn("timestamp", result)
        mock_pd.read_csv.assert_called_with(valid_path)

    def test_save_recommendations_path_traversal(self):
        """Test that save_recommendations blocks path traversal."""
        invalid_path = "../../../etc/passwd"
        recommendations = {"test": "data"}

        # Should catch ValueError and print error (not raise)
        self.agent.save_recommendations(recommendations, output_file=invalid_path)

        # Verify open was NOT called
        self.mock_open.assert_not_called()

    def test_save_recommendations_valid_path(self):
        """Test that save_recommendations allows valid paths."""
        valid_path = "output/recommendations.json"
        recommendations = {"test": "data"}

        self.agent.save_recommendations(recommendations, output_file=valid_path)

        # Verify open WAS called
        self.mock_open.assert_called_with(valid_path, "w")

if __name__ == "__main__":
    unittest.main()
