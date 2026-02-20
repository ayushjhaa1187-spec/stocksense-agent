import unittest
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to sys.path to import agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# We need to import the module to patch 'datetime' inside it
import agent
from agent import MedicineRecord

class TestMedicineRecord(unittest.TestCase):
    def test_days_until_expiry(self):
        """Test days until expiry calculation."""
        # Fixed 'now' time
        fixed_now = datetime(2023, 1, 1)

        # Patch 'agent.datetime' because MedicineRecord uses 'datetime.now()' and 'datetime.strptime'
        # The import in agent.py is 'from datetime import datetime'
        # So 'agent.datetime' refers to the datetime class.

        with patch('agent.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.strptime.side_effect = datetime.strptime

            # Case 1: Future expiry (10 days)
            # 2023-01-11 is 10 days after 2023-01-01
            medicine = MedicineRecord("Future Med", 100, "2023-01-11", 5)
            self.assertEqual(medicine.days_until_expiry(), 10)

            # Case 2: Past expiry (1 day ago)
            # 2022-12-31 is 1 day before 2023-01-01
            medicine = MedicineRecord("Past Med", 100, "2022-12-31", 5)
            self.assertEqual(medicine.days_until_expiry(), -1)

            # Case 3: Today expiry (0 days)
            medicine = MedicineRecord("Today Med", 100, "2023-01-01", 5)
            self.assertEqual(medicine.days_until_expiry(), 0)

    def test_predicted_sales(self):
        """Test sales prediction logic."""
        fixed_now = datetime(2023, 1, 1)

        with patch('agent.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_now
            mock_dt.strptime.side_effect = datetime.strptime

            # 10 days left * 5 sales/day = 50
            medicine = MedicineRecord("Med", 100, "2023-01-11", 5)
            self.assertEqual(medicine.predicted_sales_before_expiry(), 50)

            # Expired (-1 days) * 5 = 0 (max(0, -1) -> 0)
            medicine_expired = MedicineRecord("Expired", 100, "2022-12-31", 5)
            self.assertEqual(medicine_expired.predicted_sales_before_expiry(), 0)

if __name__ == '__main__':
    unittest.main()
