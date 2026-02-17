import sys
import unittest
from unittest.mock import MagicMock
import os

# Mock pandas before importing src.agent
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from agent import StockSenseAgent
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

class TestStockSenseAgent(unittest.TestCase):
    def test_scan_inventory(self):
        # Setup mock data for pd.read_csv
        mock_df = MagicMock()
        mock_pd.read_csv.return_value = mock_df

        # Mock iterrows to yield a sample row
        # The row needs to support __getitem__ for 'name', 'stock', etc.
        sample_row = {
            'name': 'TestMed',
            'stock': 100,
            'expiry_date': '2026-12-31', # Future date
            'daily_sales': 10
        }
        # iterrows yields (index, row)
        mock_df.iterrows.return_value = [(0, sample_row)]

        agent = StockSenseAgent()
        # We pass a dummy file path, but since read_csv is mocked, it doesn't matter
        recommendations = agent.scan_inventory(inventory_file="dummy_file.csv")

        self.assertIsNotNone(recommendations)
        self.assertIn("expiry_alerts", recommendations)
        print("scan_inventory executed successfully")

if __name__ == '__main__':
    unittest.main()
