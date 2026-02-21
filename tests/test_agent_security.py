
import pytest
import os
import sys
from unittest.mock import MagicMock, patch

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestStockSenseSecurity:

    @pytest.fixture
    def agent(self):
        return StockSenseAgent()

    def test_save_recommendations_path_traversal(self, agent):
        """Test that save_recommendations raises ValueError for path traversal attempt."""
        # Attempt to write to a file outside the output directory
        # e.g., ../vulnerable.txt
        traversal_path = os.path.join("output", "..", "vulnerable.txt")

        # We expect a ValueError because the path resolves outside of output/
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            agent.save_recommendations({"test": "data"}, output_file=traversal_path)

    def test_scan_inventory_path_traversal(self, agent):
        """Test that scan_inventory raises ValueError for path traversal attempt."""
        # Attempt to read from a file outside the data directory
        # e.g., ../vulnerable.csv
        traversal_path = os.path.join("data", "..", "vulnerable.csv")

        # We expect a ValueError because the path resolves outside of data/
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            agent.scan_inventory(inventory_file=traversal_path)

    def test_save_recommendations_valid_path(self, agent):
        """Test that save_recommendations works for valid paths within output/."""
        valid_path = os.path.join("output", "valid_test.json")

        # Mock open() to avoid actual file I/O during test
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            with patch("os.makedirs") as mock_makedirs:
                agent.save_recommendations({"test": "data"}, output_file=valid_path)

                # Verify that open was called with the valid path
                mock_open.assert_called_with(valid_path, "w")

    def test_scan_inventory_valid_path(self, agent):
        """Test that scan_inventory works for valid paths within data/."""
        valid_path = os.path.join("data", "valid_test.csv")

        # Mock pd.read_csv to return a DataFrame
        # We need to ensure that pd.read_csv is called with the valid path

        # We need to re-import or get the mocked pandas from sys.modules
        mock_pd = sys.modules['pandas']
        mock_df = MagicMock()
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        mock_df.itertuples.return_value = [] # Empty iterator for simplicity
        mock_pd.read_csv.return_value = mock_df

        # We also need to patch os.path.exists or just let it fail if validate_path succeeds
        # The test is focused on validate_path NOT raising ValueError.

        # However, scan_inventory calls pd.read_csv.
        # If validate_path succeeds, it proceeds to read_csv.

        with patch("builtins.print"): # Suppress print output
            agent.scan_inventory(inventory_file=valid_path)

        # Verify read_csv was called with valid_path
        mock_pd.read_csv.assert_called_with(valid_path)
