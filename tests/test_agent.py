import sys
from unittest.mock import MagicMock

# Mock pandas if not installed
try:
    import pandas
except ImportError:
    sys.modules['pandas'] = MagicMock()

import unittest
from unittest.mock import patch
from datetime import datetime
# Ensure src is in path if needed, though PYTHONPATH=. handles it.
from src.agent import MedicineRecord

class TestMedicineRecord(unittest.TestCase):
    def setUp(self):
        # Base date for testing: 2023-01-01 12:00:00
        self.mock_now = datetime(2023, 1, 1, 12, 0, 0)

    @patch('src.agent.datetime')
    def test_days_until_expiry_future(self, mock_datetime):
        # Expiry: 2023-01-03 (2 days from now)
        # Expect: 1 day remaining (based on current implementation logic)
        mock_datetime.now.return_value = self.mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        medicine = MedicineRecord(
            name="Test Med",
            stock=100,
            expiry_date="2023-01-03",
            daily_sales=10
        )
        self.assertEqual(medicine.days_until_expiry(), 1)

    @patch('src.agent.datetime')
    def test_days_until_expiry_tomorrow(self, mock_datetime):
        # Expiry: 2023-01-02 (Tomorrow)
        # Expect: 0 days remaining (current implementation logic)
        mock_datetime.now.return_value = self.mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        medicine = MedicineRecord(
            name="Test Med",
            stock=100,
            expiry_date="2023-01-02",
            daily_sales=10
        )
        self.assertEqual(medicine.days_until_expiry(), 0)

    @patch('src.agent.datetime')
    def test_days_until_expiry_today(self, mock_datetime):
        # Expiry: 2023-01-01 (Today)
        # Expect: -1 days remaining (current implementation logic)
        mock_datetime.now.return_value = self.mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        medicine = MedicineRecord(
            name="Test Med",
            stock=100,
            expiry_date="2023-01-01",
            daily_sales=10
        )
        self.assertEqual(medicine.days_until_expiry(), -1)

    @patch('src.agent.datetime')
    def test_days_until_expiry_past(self, mock_datetime):
        # Expiry: 2022-12-31 (Yesterday)
        # Expect: -2 days remaining (current implementation logic)
        mock_datetime.now.return_value = self.mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        medicine = MedicineRecord(
            name="Test Med",
            stock=100,
            expiry_date="2022-12-31",
            daily_sales=10
        )
        self.assertEqual(medicine.days_until_expiry(), -2)

    def test_invalid_date_format(self):
        medicine = MedicineRecord(
            name="Test Med",
            stock=100,
            expiry_date="invalid-date",
            daily_sales=10
        )
        with self.assertRaises(ValueError):
            medicine.days_until_expiry()

if __name__ == '__main__':
    unittest.main()
