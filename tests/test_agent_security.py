import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestAgentSecurity(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    def test_scan_inventory_path_traversal(self):
        """Test that scan_inventory raises ValueError for paths outside data/"""
        # Test with parent directory traversal
        with self.assertRaises(ValueError):
            self.agent.scan_inventory("../outside.csv")

        # Test with absolute path outside data/
        abs_path = os.path.abspath("outside.csv")
        with self.assertRaises(ValueError):
            self.agent.scan_inventory(abs_path)

    def test_save_recommendations_path_traversal(self):
        """Test that save_recommendations raises ValueError for paths outside output/"""
        # Test with parent directory traversal
        with self.assertRaises(ValueError):
            self.agent.save_recommendations({}, "../hacked.json")

        # Test with absolute path outside output/
        abs_path = os.path.abspath("hacked.json")
        with self.assertRaises(ValueError):
            self.agent.save_recommendations({}, abs_path)

    def test_valid_paths(self):
        """Test that valid paths are accepted"""
        # scan_inventory: valid path inside data/
        # We need to mock pd.read_csv to avoid FileNotFoundError or actual file reading
        with patch('agent.pd.read_csv') as mock_read_csv:
            # Mock return value to be empty DataFrame so it doesn't crash later
            mock_df = MagicMock()
            mock_df.columns = []
            mock_df.itertuples.return_value = []
            mock_read_csv.return_value = mock_df

            # Should not raise ValueError
            self.agent.scan_inventory("data/valid.csv")

            # verify read_csv was called with absolute path or relative?
            # The code passes the path to read_csv directly.
            # But wait, validation happens first.
            mock_read_csv.assert_called_once()

        # save_recommendations: valid path inside output/
        # We need to mock open and os.makedirs
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
            with patch('os.makedirs') as mock_makedirs:
                # Should not raise ValueError
                self.agent.save_recommendations({}, "output/valid.json")

                mock_makedirs.assert_called_once()
                mock_open.assert_called_once()

if __name__ == '__main__':
    unittest.main()
