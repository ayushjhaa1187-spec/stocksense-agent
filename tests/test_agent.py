import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import MedicineRecord

class TestMedicineRecord(unittest.TestCase):

    def setUp(self):
        # Create a patcher for datetime in agent module
        self.patcher = patch('agent.datetime')
        self.mock_datetime = self.patcher.start()

        # Configure the mock
        self.real_datetime = datetime
        self.mock_datetime.strptime.side_effect = self.real_datetime.strptime
        self.mock_datetime.now.return_value = self.real_datetime(2023, 1, 1)

    def tearDown(self):
        self.patcher.stop()

    def test_days_until_expiry_valid(self):
        # expiry_date is 10 days after fixed_now (2023-01-01)
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="2023-01-11", daily_sales=1)

        # Verify the mock is working as expected
        from agent import datetime as agent_datetime
        self.assertEqual(agent_datetime.now(), self.real_datetime(2023, 1, 1))

        self.assertEqual(record.days_until_expiry(), 10)

    def test_days_until_expiry_invalid_format(self):
        # Invalid date format
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="11-01-2023", daily_sales=1)

        with self.assertRaises(ValueError):
            record.days_until_expiry()

if __name__ == '__main__':
    unittest.main()
