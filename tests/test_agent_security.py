import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import MedicineRecord, StockSenseAgent

class TestMedicineRecord(unittest.TestCase):
    def setUp(self):
        self.patcher = patch('agent.datetime')
        self.mock_date = self.patcher.start()

        # Wire up strptime to real implementation
        self.mock_date.strptime.side_effect = datetime.strptime

        # Mock now() to return fixed date
        self.fixed_now = datetime(2023, 1, 1)
        self.mock_date.now.return_value = self.fixed_now

    def tearDown(self):
        self.patcher.stop()

    def test_days_until_expiry_valid(self):
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="2023-01-11", daily_sales=1)
        from agent import datetime as agent_datetime
        self.assertEqual(agent_datetime.now(), self.fixed_now)
        self.assertEqual(record.days_until_expiry(), 10)

    def test_days_until_expiry_invalid_format(self):
        record = MedicineRecord(name="Test Med", stock=10, expiry_date="11-01-2023", daily_sales=1)
        with self.assertRaises(ValueError):
            record.days_until_expiry()

class TestStockSenseAgentSecurity(unittest.TestCase):
    def setUp(self):
        pass

    def test_scan_inventory_path_traversal(self):
        agent = StockSenseAgent()
        # Malicious path attempting traversal to /etc/passwd
        # Note: We simulate this by checking if the resolved path is outside data/
        malicious_path = "../etc/passwd"

        # Access the mocked pandas object
        import agent as agent_module
        mock_pd = agent_module.pd
        mock_pd.read_csv.reset_mock()

        # Expectation: scan_inventory should return None (or raise error) and NOT call read_csv
        result = agent.scan_inventory(inventory_file=malicious_path)

        # Verify read_csv was NOT called
        self.assertFalse(mock_pd.read_csv.called, "pd.read_csv should not be called for malicious path")
        self.assertIsNone(result, "Should return None for blocked path")

    def test_scan_inventory_valid_path(self):
        agent = StockSenseAgent()
        valid_path = "data/sample_inventory.csv"

        # Access the mocked pandas object
        import agent as agent_module
        mock_pd = agent_module.pd
        mock_pd.read_csv.reset_mock()

        # Configure mock to avoid crashes during dataframe processing
        mock_df = MagicMock()
        mock_df.columns = ['expiry_date'] # minimal columns
        mock_df.itertuples.return_value = [] # empty iterator
        mock_pd.read_csv.return_value = mock_df

        result = agent.scan_inventory(inventory_file=valid_path)

        # Verify read_csv WAS called
        self.assertTrue(mock_pd.read_csv.called, "pd.read_csv should be called for valid path")
        args, _ = mock_pd.read_csv.call_args
        # The agent now resolves the path to absolute path
        self.assertEqual(args[0], os.path.realpath(valid_path))

if __name__ == '__main__':
    unittest.main()
