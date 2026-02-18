import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime
from collections import namedtuple

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
import pandas as pd

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent, MedicineRecord

class TestThresholds(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    def test_expiry_thresholds(self):
        # We need to mock pd.read_csv to return a dataframe with specific values
        # The values should test the boundary conditions: 30 days, 31 days, 7 days, 8 days, etc.

        # We also need to mock datetime.now() to have a fixed reference point.
        fixed_now = datetime(2023, 1, 1)

        # Helper to create row
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        # Scenarios:
        # 1. Expires in 30 days (should alert) -> 2023-01-31
        # 2. Expires in 31 days (no alert) -> 2023-02-01
        # 3. Expires in 7 days (critical) -> 2023-01-08
        # 4. Expires in 8 days (high) -> 2023-01-09
        # 5. Discount window: 14 days (should recommend discount if sales low) -> 2023-01-15
        # 6. Discount window: 15 days (no discount) -> 2023-01-16
        # 7. Restock: stock 19 (should restock)
        # 8. Restock: stock 20 (no restock)

        test_data = [
            Row(0, "Med_30_Days", 100, datetime(2023, 1, 31), 10), # 30 days left
            Row(1, "Med_31_Days", 100, datetime(2023, 2, 1), 10),  # 31 days left
            Row(2, "Med_7_Days", 100, datetime(2023, 1, 8), 10),   # 7 days left
            Row(3, "Med_8_Days", 100, datetime(2023, 1, 9), 10),   # 8 days left
            Row(4, "Med_14_Days_LowSales", 100, datetime(2023, 1, 15), 1), # 14 days left, low sales -> discount
            Row(5, "Med_15_Days_LowSales", 100, datetime(2023, 1, 16), 1), # 15 days left, low sales -> no discount
            Row(6, "Med_Stock_19", 19, datetime(2023, 6, 1), 10),   # Stock 19 -> restock
            Row(7, "Med_Stock_20", 20, datetime(2023, 6, 1), 10),   # Stock 20 -> no restock
        ]

        mock_df = MagicMock()
        mock_df.itertuples.return_value = test_data
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        pd.read_csv = MagicMock(return_value=mock_df)
        pd.to_datetime = MagicMock(side_effect=lambda x: x) # Pass through

        with patch('agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.strptime.side_effect = datetime.strptime

            recommendations = self.agent.scan_inventory("dummy.csv")

            # Verify Expiry Alerts
            alerts = {r['medicine']: r for r in recommendations['expiry_alerts']}
            self.assertIn("Med_30_Days", alerts)
            self.assertNotIn("Med_31_Days", alerts)
            self.assertIn("Med_7_Days", alerts)
            self.assertEqual(alerts["Med_7_Days"]["urgency"], "CRITICAL")
            self.assertIn("Med_8_Days", alerts)
            self.assertEqual(alerts["Med_8_Days"]["urgency"], "HIGH")

            # Verify Discount Recommendations
            discounts = {r['medicine']: r for r in recommendations['discount_recommendations']}
            self.assertIn("Med_14_Days_LowSales", discounts)
            self.assertNotIn("Med_15_Days_LowSales", discounts)

            # Verify Restock Orders
            restocks = {r['medicine']: r for r in recommendations['restock_orders']}
            self.assertIn("Med_Stock_19", restocks)
            self.assertNotIn("Med_Stock_20", restocks)

if __name__ == '__main__':
    unittest.main()
