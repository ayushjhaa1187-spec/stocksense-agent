import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from io import StringIO
from datetime import datetime

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import AFTER mocking
from agent import StockSenseAgent

class TestStockSenseAgent(unittest.TestCase):
    def test_scan_inventory_file_not_found(self):
        """Test that scan_inventory handles FileNotFoundError gracefully."""
        agent = StockSenseAgent()

        # We need to mock pd.read_csv to raise FileNotFoundError
        # Access the mocked pandas in sys.modules
        pd_mock = sys.modules['pandas']

        # Reset mock
        if isinstance(pd_mock.read_csv, MagicMock):
            pd_mock.read_csv.reset_mock()
        pd_mock.read_csv.side_effect = FileNotFoundError("File not found")

        # Capture stdout
        captured_output = StringIO()

        with patch('sys.stdout', new=captured_output):
            result = agent.scan_inventory("non_existent_file.csv")

        self.assertIsNone(result)
        self.assertIn("ERROR: Could not load inventory data from non_existent_file.csv", captured_output.getvalue())

    def test_scan_inventory_happy_path(self):
        """Test scan_inventory with valid data generating recommendations."""
        agent = StockSenseAgent()

        fixed_now = datetime(2023, 1, 1)

        # Sample data
        # 1. Expiring Med: 2023-01-06 (5 days) -> ALERT (<=30)
        # 2. Discount Med: 2023-01-11 (10 days) -> ALERT (<=30) AND DISCOUNT (7 <= days <= 14)
        # 3. Restock Med: 2023-02-01 (31 days) -> NO ALERT (>30). Stock 10 (<20) -> RESTOCK.
        # 4. Safe Med: 2023-06-01 (151 days) -> NO ACTION.

        sample_data = [
            {'name': 'Expiring Med', 'stock': 100, 'expiry_date': '2023-01-06', 'daily_sales': 5},
            {'name': 'Discount Med', 'stock': 100, 'expiry_date': '2023-01-11', 'daily_sales': 1},
            {'name': 'Restock Med', 'stock': 10, 'expiry_date': '2023-02-01', 'daily_sales': 5},
            {'name': 'Safe Med', 'stock': 100, 'expiry_date': '2023-06-01', 'daily_sales': 5},
        ]

        # Mock pd.read_csv to return a DataFrame-like object
        pd_mock = sys.modules['pandas']
        pd_mock.read_csv.side_effect = None

        mock_df = MagicMock()

        # Create mock series objects that support dictionary access
        def create_mock_series(data):
            series = MagicMock()
            series.__getitem__.side_effect = lambda key: data[key]
            return series

        mock_rows = []
        for i, row_data in enumerate(sample_data):
            # Simulate (index, series) tuple
            mock_rows.append((i, create_mock_series(row_data)))

        mock_df.iterrows.return_value = mock_rows
        pd_mock.read_csv.return_value = mock_df

        # Patch datetime in agent module
        with patch('agent.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.strptime.side_effect = datetime.strptime

            # Capture output
            with patch('sys.stdout', new=StringIO()) as fake_out:
                recommendations = agent.scan_inventory("dummy.csv")

        # Verify structure
        self.assertIsNotNone(recommendations)

        # Expiry alerts: Expiring Med (5 days) and Discount Med (10 days)
        self.assertEqual(len(recommendations['expiry_alerts']), 2)
        alert_names = [r['medicine'] for r in recommendations['expiry_alerts']]
        self.assertIn('Expiring Med', alert_names)
        self.assertIn('Discount Med', alert_names)

        # Discount recommendations: Discount Med (10 days)
        self.assertEqual(len(recommendations['discount_recommendations']), 1)
        self.assertEqual(recommendations['discount_recommendations'][0]['medicine'], 'Discount Med')

        # Restock orders: Restock Med (stock 10 < 20)
        self.assertEqual(len(recommendations['restock_orders']), 1)
        self.assertEqual(recommendations['restock_orders'][0]['medicine'], 'Restock Med')

if __name__ == '__main__':
    unittest.main()
