import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import MedicineRecord

class TestMedicineRecord(unittest.TestCase):
    def setUp(self):
        self.mock_datetime_patcher = patch('agent.datetime')
        self.mock_datetime = self.mock_datetime_patcher.start()

        # Wire up strptime to real implementation
        self.mock_datetime.strptime.side_effect = datetime.strptime

        # Mock datetime.now()
        self.fixed_now = datetime(2023, 1, 1)
        self.mock_datetime.now.return_value = self.fixed_now

    def tearDown(self):
        self.mock_datetime_patcher.stop()

    def test_days_until_expiry_valid(self):
        # expiry_date is 10 days after fixed_now (2023-01-01)
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="2023-01-11", daily_sales=1)
        self.assertEqual(record.days_until_expiry(), 10)

    def test_days_until_expiry_invalid_format(self):
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="11-01-2023", daily_sales=1)
        with self.assertRaises(ValueError):
            record.days_until_expiry()

if __name__ == '__main__':
    unittest.main()
