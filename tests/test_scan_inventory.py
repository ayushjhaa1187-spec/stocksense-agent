import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from collections import namedtuple
import sys
import os

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestScanInventory(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    @patch('agent.pd')
    @patch('agent.datetime')
    def test_scan_inventory_success(self, mock_datetime, mock_pd):
        """Test scanning inventory with various scenarios (expiry, discount, restock, normal)"""

        # 1. Setup Date Mocks
        current_date = datetime(2024, 1, 1)
        mock_datetime.now.return_value = current_date
        mock_datetime.strptime.side_effect = datetime.strptime

        # 2. Setup Inventory Data
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        rows = [
            Row(0, 'CriticalMed', 100, datetime(2024, 1, 5), 10),
            Row(1, 'DiscountMed', 200, datetime(2024, 1, 10), 10),
            Row(2, 'RestockMed', 10, datetime(2025, 1, 1), 5),
            Row(3, 'NormalMed', 100, datetime(2025, 1, 1), 5)
        ]

        # 3. Mock pandas read_csv and itertuples
        mock_df = MagicMock()
        mock_df.itertuples.return_value = rows
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        # mock_pd is the mock object for pandas module
        mock_pd.read_csv.return_value = mock_df

        # 4. Run the method
        recommendations = self.agent.scan_inventory("dummy.csv")

        # 5. Verify Results
        self.assertIsNotNone(recommendations)

        # Verify Expiry Alerts
        alerts = recommendations['expiry_alerts']
        self.assertEqual(len(alerts), 2, "Should have 2 expiry alerts")

        critical_alert = next((a for a in alerts if a['medicine'] == 'CriticalMed'), None)
        self.assertIsNotNone(critical_alert)
        self.assertEqual(critical_alert['urgency'], 'CRITICAL')

        high_alert = next((a for a in alerts if a['medicine'] == 'DiscountMed'), None)
        self.assertIsNotNone(high_alert)
        self.assertEqual(high_alert['urgency'], 'HIGH')

        # Verify Discount Recommendations
        discounts = recommendations['discount_recommendations']
        self.assertEqual(len(discounts), 1, "Should have 1 discount recommendation")
        self.assertEqual(discounts[0]['medicine'], 'DiscountMed')
        self.assertEqual(discounts[0]['discount_percent'], 10)

        # Verify Restock Orders
        restocks = recommendations['restock_orders']
        self.assertEqual(len(restocks), 1, "Should have 1 restock order")
        self.assertEqual(restocks[0]['medicine'], 'RestockMed')

        print("\n✅ Test scan_inventory success scenario passed!")

if __name__ == '__main__':
    unittest.main()
