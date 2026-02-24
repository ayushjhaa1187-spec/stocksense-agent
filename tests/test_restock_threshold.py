import sys
import unittest
from unittest.mock import MagicMock, patch
import os
from datetime import datetime

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestRestockThreshold(unittest.TestCase):
    def setUp(self):
        # Determine if we need to mock environment for import
        self.agent_was_imported = 'agent' in sys.modules
        self.modules_patcher = None

        if not self.agent_was_imported:
            # Create a minimal mock for pandas to allow import
            mock_pandas = MagicMock()
            self.modules_patcher = patch.dict(sys.modules, {'pandas': mock_pandas})
            self.modules_patcher.start()

            # Now we can import agent
            import agent
        else:
            import agent

        self.agent_module = agent
        self.StockSenseAgent = agent.StockSenseAgent

        # Now create our test-specific mock pandas
        self.mock_pandas = MagicMock()
        self.mock_pandas.to_datetime = MagicMock(side_effect=lambda x: x)
        self.mock_df = MagicMock()
        self.mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        self.mock_pandas.read_csv.return_value = self.mock_df

        # Patch agent.pd with our mock
        # We use patch.object on the module
        self.pd_patcher = patch.object(self.agent_module, 'pd', self.mock_pandas)
        self.pd_patcher.start()

    def tearDown(self):
        # Stop patching agent.pd
        self.pd_patcher.stop()

        # Clean up if we modified sys.modules
        if self.modules_patcher:
            self.modules_patcher.stop()
            # If we introduced agent, remove it to be clean
            if 'agent' in sys.modules and not self.agent_was_imported:
                del sys.modules['agent']

    def test_default_threshold(self):
        # Setup data
        row = MagicMock()
        row.name = "LowStockMed"
        row.stock = 19
        row.expiry_date = datetime(2025, 1, 1)
        row.daily_sales = 1

        self.mock_df.itertuples.return_value = [row]

        with patch('agent.datetime') as mock_agent_datetime:
            mock_agent_datetime.now.return_value = datetime(2023, 1, 1)
            mock_agent_datetime.strptime.side_effect = datetime.strptime

            agent = self.StockSenseAgent()
            recommendations = agent.scan_inventory('dummy.csv')

            restock_orders = recommendations['restock_orders']

            self.assertEqual(len(restock_orders), 1)
            self.assertEqual(restock_orders[0]['medicine'], "LowStockMed")

    def test_custom_threshold(self):
        # Setup data
        row = MagicMock()
        row.name = "MedStock25"
        row.stock = 25
        row.expiry_date = datetime(2025, 1, 1)
        row.daily_sales = 1

        self.mock_df.itertuples.return_value = [row]

        with patch('agent.datetime') as mock_agent_datetime:
            mock_agent_datetime.now.return_value = datetime(2023, 1, 1)

            agent = self.StockSenseAgent(restock_threshold=30)
            recommendations = agent.scan_inventory('dummy.csv')

            restock_orders = recommendations['restock_orders']
            self.assertEqual(len(restock_orders), 1)
            self.assertEqual(restock_orders[0]['medicine'], "MedStock25")

if __name__ == '__main__':
    unittest.main()
