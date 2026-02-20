import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime
from collections import namedtuple

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestThresholds(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    def test_expiry_thresholds(self):
        fixed_now = datetime(2023, 1, 1)
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        test_data = [
            Row(0, "Med_30_Days", 100, datetime(2023, 1, 31), 10),
            Row(1, "Med_31_Days", 100, datetime(2023, 2, 1), 10),
            Row(2, "Med_7_Days", 100, datetime(2023, 1, 8), 10),
            Row(3, "Med_8_Days", 100, datetime(2023, 1, 9), 10),
            Row(4, "Med_14_Days_LowSales", 100, datetime(2023, 1, 15), 1),
            Row(5, "Med_15_Days_LowSales", 100, datetime(2023, 1, 16), 1),
            Row(6, "Med_Stock_19", 19, datetime(2023, 6, 1), 10),
            Row(7, "Med_Stock_20", 20, datetime(2023, 6, 1), 10),
        ]

        mock_df = MagicMock()
        mock_df.itertuples.return_value = test_data
        # Ensure columns are set for validation
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        with patch('agent.pd') as mock_pd,              patch('agent.datetime') as mock_datetime:

            mock_pd.read_csv.return_value = mock_df
            # Mock to_datetime to pass through (or return list)
            # Since test_data has datetime objects, we don't need conversion?
            # agent.py calls pd.to_datetime(inventory['expiry_date'])
            # We can mock it to return the column itself
            mock_pd.to_datetime.side_effect = lambda x, **kwargs: x

            mock_datetime.now.return_value = fixed_now
            mock_datetime.strptime.side_effect = datetime.strptime

            with patch.object(self.agent, "_validate_path", return_value=True):
                recommendations = self.agent.scan_inventory("dummy.csv")

            # Verify results
            self.assertIsNotNone(recommendations, "scan_inventory returned None")

            alerts = {r['medicine']: r for r in recommendations['expiry_alerts']}
            self.assertIn("Med_30_Days", alerts)
            self.assertNotIn("Med_31_Days", alerts)
            self.assertIn("Med_7_Days", alerts)
            self.assertEqual(alerts["Med_7_Days"]["urgency"], "CRITICAL")

            discounts = {r['medicine']: r for r in recommendations['discount_recommendations']}
            self.assertIn("Med_14_Days_LowSales", discounts)

            restocks = {r['medicine']: r for r in recommendations['restock_orders']}
            self.assertIn("Med_Stock_19", restocks)

if __name__ == '__main__':
    unittest.main()
