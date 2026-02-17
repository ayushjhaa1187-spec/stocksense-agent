import unittest
from unittest.mock import MagicMock, patch
import sys
import datetime

# Mock pandas before importing src.agent
sys.modules["pandas"] = MagicMock()

from src.agent import StockSenseAgent, MedicineRecord

class TestStockSenseAgent(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    @patch('src.agent.pd.read_csv')
    @patch('src.agent.os.path.exists')
    @patch('src.agent.datetime')
    def test_scan_inventory_expiry_alert(self, mock_datetime, mock_exists, mock_read_csv):
        # Setup mock date to be 2026-01-01
        # Inventory item expires 2026-01-10 (9 days left -> Alert)

        fixed_now = datetime.datetime(2026, 1, 1)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.datetime.strptime(*args, **kwargs)

        mock_exists.return_value = True

        # Mock DataFrame
        mock_df = MagicMock()
        data = {
            'name': 'TestMed',
            'stock': 100,
            'expiry_date': '2026-01-10',
            'daily_sales': 5
        }
        # Iterate over one row
        mock_df.iterrows.return_value = [(0, data)]
        mock_read_csv.return_value = mock_df

        recommendations = self.agent.scan_inventory("dummy.csv")

        self.assertEqual(len(recommendations['expiry_alerts']), 1)
        self.assertEqual(recommendations['expiry_alerts'][0]['medicine'], 'TestMed')
        self.assertEqual(recommendations['expiry_alerts'][0]['days_left'], 9)

    @patch('src.agent.pd.read_csv')
    @patch('src.agent.os.path.exists')
    @patch('src.agent.datetime')
    def test_scan_inventory_restock(self, mock_datetime, mock_exists, mock_read_csv):
        # Setup mock date
        fixed_now = datetime.datetime(2025, 1, 1)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.datetime.strptime(*args, **kwargs)

        mock_exists.return_value = True

        # Mock DataFrame
        mock_df = MagicMock()
        data = {
            'name': 'LowStockMed',
            'stock': 10,  # Less than 20 -> Restock
            'expiry_date': '2027-01-01',
            'daily_sales': 5
        }
        mock_df.iterrows.return_value = [(0, data)]
        mock_read_csv.return_value = mock_df

        recommendations = self.agent.scan_inventory("dummy.csv")

        self.assertEqual(len(recommendations['restock_orders']), 1)
        self.assertEqual(recommendations['restock_orders'][0]['medicine'], 'LowStockMed')

if __name__ == '__main__':
    unittest.main()
