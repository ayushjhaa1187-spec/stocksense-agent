import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from io import StringIO

# Mock pandas before importing agent
# We need to ensure pandas is mocked in sys.modules so that import pandas returns our mock
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to sys.path to import agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestStockSenseAgent(unittest.TestCase):
    def test_scan_inventory_file_not_found(self):
        """Test that scan_inventory handles FileNotFoundError gracefully."""
        agent = StockSenseAgent()

        # We need to mock pd.read_csv to raise FileNotFoundError
        # Since pandas is mocked, we need to access the mock object
        # import pandas inside the function will return the mock because of sys.modules hack
        import pandas as pd

        # Reset the mock to ensure clean state
        pd.read_csv.reset_mock()

        # Configure the side effect
        pd.read_csv.side_effect = FileNotFoundError("File not found")

        # Capture stdout
        captured_output = StringIO()

        # We need to capture the print output. agent.scan_inventory uses print().
        # We can patch sys.stdout
        with patch('sys.stdout', new=captured_output):
            result = agent.scan_inventory("non_existent_file.csv")

        # Assertions
        self.assertIsNone(result)
        self.assertIn("ERROR: Could not load inventory data from non_existent_file.csv", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
