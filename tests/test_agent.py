
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agent import MedicineRecord

class TestMedicineRecord(unittest.TestCase):
    def setUp(self):
        # Fixed "now" for testing: 2023-10-27 10:00:00
        self.fixed_now = datetime(2023, 10, 27, 10, 0, 0)

    def _configure_mock_datetime(self, mock_dt):
        """Helper to configure the mocked datetime class."""
        mock_dt.now.return_value = self.fixed_now
        # Delegate strptime to the real datetime class
        mock_dt.strptime.side_effect = lambda d, f: datetime.strptime(d, f)
        return mock_dt

    @patch('agent.datetime')
    def test_predicted_sales_before_expiry_future(self, mock_datetime):
        """Test sales prediction for an item expiring in the future."""
        self._configure_mock_datetime(mock_datetime)

        # Expiry: 2023-11-06 (10 days from 2023-10-27)
        # Note: 2023-11-06 00:00:00 - 2023-10-27 10:00:00 = 9 days, 14 hours
        # .days = 9
        # Wait, 10 days from 27th is 6th Nov?
        # 27 + 10 = 37 -> Nov 6.
        # Nov 6 - Oct 27 = 10 days.
        # But time is 00:00:00 vs 10:00:00.
        # So diff is 9 days 14 hours. .days returns 9.
        # So expected multiplier is 9.

        expiry_date = "2023-11-06"
        daily_sales = 5
        stock = 100

        med = MedicineRecord("Future Med", stock, expiry_date, daily_sales)

        # Expected: 5 * 9 = 45
        expected_sales = 45

        self.assertEqual(med.predicted_sales_before_expiry(), expected_sales)

    @patch('agent.datetime')
    def test_predicted_sales_before_expiry_expired(self, mock_datetime):
        """Test sales prediction for an expired item."""
        self._configure_mock_datetime(mock_datetime)

        # Expiry: 2023-10-20 (7 days ago)
        expiry_date = "2023-10-20"
        daily_sales = 5
        stock = 100

        med = MedicineRecord("Expired Med", stock, expiry_date, daily_sales)

        # Expected: 0
        self.assertEqual(med.predicted_sales_before_expiry(), 0)

    @patch('agent.datetime')
    def test_predicted_sales_before_expiry_today(self, mock_datetime):
        """Test sales prediction for an item expiring today."""
        self._configure_mock_datetime(mock_datetime)

        # Expiry: 2023-10-27 (Today)
        # Diff: 2023-10-27 00:00:00 - 2023-10-27 10:00:00 = -10 hours
        # .days = -1
        # max(0, -1) = 0

        expiry_date = "2023-10-27"
        daily_sales = 5
        stock = 100

        med = MedicineRecord("Today Med", stock, expiry_date, daily_sales)

        # Expected: 0
        self.assertEqual(med.predicted_sales_before_expiry(), 0)

    @patch('agent.datetime')
    def test_predicted_sales_before_expiry_tomorrow(self, mock_datetime):
        """Test sales prediction for an item expiring tomorrow."""
        self._configure_mock_datetime(mock_datetime)

        # Expiry: 2023-10-28 (Tomorrow)
        # Diff: 2023-10-28 00:00:00 - 2023-10-27 10:00:00 = 14 hours
        # .days = 0
        # Wait, 14 hours is 0 days.
        # max(0, 0) = 0?

        # Let's check logic:
        # If I have something expiring tomorrow, can I sell it today?
        # Yes, probably.
        # But the calculation gives 0 days.
        # This highlights a potential issue or specific definition of "days remaining".
        # If "days until expiry" means "full 24h periods", then 0 is correct.
        # If it means "calendar days", then it should be 1.

        # Based on current implementation:
        # (Tomorrow midnight - Today 10am).days = 0.
        # So predicted sales = 0.

        expiry_date = "2023-10-28"
        daily_sales = 5
        stock = 100

        med = MedicineRecord("Tomorrow Med", stock, expiry_date, daily_sales)

        # Expected: 0 according to current logic
        self.assertEqual(med.predicted_sales_before_expiry(), 0)

    @patch('agent.datetime')
    def test_predicted_sales_before_expiry_day_after_tomorrow(self, mock_datetime):
        """Test sales prediction for an item expiring in 2 days."""
        self._configure_mock_datetime(mock_datetime)

        # Expiry: 2023-10-29
        # Diff: 2023-10-29 00:00:00 - 2023-10-27 10:00:00 = 1 day, 14 hours
        # .days = 1

        expiry_date = "2023-10-29"
        daily_sales = 5
        stock = 100

        med = MedicineRecord("Day After Tomorrow Med", stock, expiry_date, daily_sales)

        # Expected: 5 * 1 = 5
        self.assertEqual(med.predicted_sales_before_expiry(), 5)

if __name__ == '__main__':
    unittest.main()
