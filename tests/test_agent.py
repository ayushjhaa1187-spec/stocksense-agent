import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Mock pandas before importing src.agent
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent import StockSenseAgent

class TestStockSenseAgent(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    def test_scan_inventory_missing_columns(self):
        # Setup mock dataframe returned by pd.read_csv
        mock_df = MagicMock()
        # Simulate missing 'stock' column
        mock_df.columns = ['name', 'expiry_date', 'daily_sales']

        # Make iterrows yield a row that will cause KeyError
        # Because 'stock' is missing in columns, accessing row['stock'] should fail if it behaves like a Series
        # But here row is a MagicMock.
        # We need to simulate that accessing 'stock' on the row fails.

        mock_row = MagicMock()
        def get_item(key):
            if key == 'stock':
                raise KeyError("'stock'")
            return "some_value"
        mock_row.__getitem__.side_effect = get_item

        mock_df.iterrows.return_value = [(0, mock_row)]

        # Mock pd.read_csv to return our mock_df
        with patch('src.agent.pd.read_csv', return_value=mock_df):
            # Capture stdout
            from io import StringIO
            captured_output = StringIO()
            original_stdout = sys.stdout
            sys.stdout = captured_output

            try:
                result = self.agent.scan_inventory('dummy.csv')

                # If we reach here without exception, check if validation logic was hit (which is not yet implemented)
                # But currently it should raise KeyError.

            except KeyError:
                # This is expected behavior BEFORE fix.
                # But validation should PREVENT this.
                pass
                # For the test to FAIL before fix, I should assert that KeyError was NOT raised?
                # No, I want to assert that the function returns None and prints an error,
                # instead of raising KeyError.
            else:
                 # If no exception, maybe it returned None?
                 if result is None:
                     # This means it handled it.
                     pass
                 else:
                     # This means it proceeded unexpectedly.
                     pass

            sys.stdout = original_stdout

    def test_scan_inventory_missing_columns_fails(self):
        """Test that missing columns cause KeyError (reproduction) or are handled (fix)"""
        mock_df = MagicMock()
        mock_df.columns = ['name', 'expiry_date', 'daily_sales'] # Missing 'stock'

        mock_row = MagicMock()
        def get_item(key):
            if key == 'stock':
                raise KeyError("'stock'")
            return "val"
        mock_row.__getitem__.side_effect = get_item
        mock_df.iterrows.return_value = [(0, mock_row)]

        with patch('src.agent.pd.read_csv', return_value=mock_df):
            # EXPECTATION: The function should NOT raise KeyError.
            # It should handle the missing column gracefully.
            try:
                self.agent.scan_inventory('dummy.csv')
            except KeyError:
                self.fail("scan_inventory raised KeyError! Missing column validation failed.")

if __name__ == '__main__':
    unittest.main()
