import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure pandas is mocked so agent can be imported
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src path to import agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestScanInventory(unittest.TestCase):
    def test_scan_inventory_missing_columns(self):
        """Test that scan_inventory handles missing columns gracefully (returns None)."""

        # Setup mock dataframe
        mock_df = MagicMock()
        mock_df.columns = ['name', 'expiry_date', 'daily_sales'] # Missing 'stock'

        # Patch agent.pd to ensure we control the pandas used by agent
        with patch('agent.pd') as mock_pd:
            mock_pd.read_csv.return_value = mock_df

            # Create agent instance
            agent_instance = StockSenseAgent()

            # Patch _validate_path to bypass security check
            with patch.object(agent_instance, '_validate_path', return_value=True):
                # Run scan_inventory
                result = agent_instance.scan_inventory("dummy.csv")

            # Expect None (graceful failure) instead of crash
            self.assertIsNone(result, "scan_inventory should return None when columns are missing")

if __name__ == '__main__':
    unittest.main()
