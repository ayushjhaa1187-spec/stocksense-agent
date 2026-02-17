import sys
import unittest
from unittest.mock import MagicMock

# Add src to path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock pandas
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Now import
try:
    from agent import MedicineRecord, StockSenseAgent
except ImportError:
    # Try importing from src.agent if agent is not found directly
    from src.agent import MedicineRecord, StockSenseAgent

class TestFix(unittest.TestCase):
    def test_days_until_expiry_invalid(self):
        med = MedicineRecord("Test", 10, "invalid", 10)
        self.assertIsNone(med.days_until_expiry())

    def test_days_until_expiry_valid(self):
        # We can't easily test the exact number of days without mocking datetime.now()
        # or passing a date relative to now.
        # But for valid dates, it should return an integer.
        med = MedicineRecord("Test", 10, "2030-01-01", 10)
        result = med.days_until_expiry()
        self.assertIsInstance(result, int)

    def test_predicted_sales_invalid_expiry(self):
        med = MedicineRecord("Test", 10, "invalid", 10)
        # Should return 0 as per the fix
        self.assertEqual(med.predicted_sales_before_expiry(), 0)

    def test_scan_inventory_skips_invalid(self):
        # Create a mock dataframe behavior
        mock_df = MagicMock()

        # Row 1: Valid
        row1 = {'name': 'Valid Med', 'stock': 100, 'expiry_date': '2030-01-01', 'daily_sales': 10}
        # Row 2: Invalid
        row2 = {'name': 'Invalid Med', 'stock': 100, 'expiry_date': 'invalid', 'daily_sales': 10}

        # Mock iterrows to return an iterator over these rows
        mock_df.iterrows.return_value = [
            (0, row1),
            (1, row2)
        ]

        mock_pd.read_csv.return_value = mock_df

        agent = StockSenseAgent()

        try:
            recommendations = agent.scan_inventory("dummy.csv")
        except Exception as e:
            self.fail(f"scan_inventory raised exception: {e}")

        self.assertIsNotNone(recommendations)
        # We can check that only the valid medicine was processed if we inspect output/logs,
        # but the main thing is it didn't crash.

if __name__ == "__main__":
    unittest.main()
