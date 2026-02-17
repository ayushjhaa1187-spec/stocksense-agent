import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add root directory to sys.path
sys.path.append(os.getcwd())

# Mock pandas before importing src.agent
sys.modules["pandas"] = MagicMock()

from src.agent import MedicineRecord, StockSenseAgent

class TestAgentRefactor(unittest.TestCase):
    def test_medicine_record_signature(self):
        """Test that predicted_sales_before_expiry accepts an optional argument."""
        # Note: MedicineRecord is instantiated here, but since we import it after mocking pandas,
        # it should be fine. However, MedicineRecord doesn't depend on pandas.
        med = MedicineRecord("Test", 100, "2025-01-01", 10)

        # Should accept argument
        # We need to mock days_until_expiry inside MedicineRecord if we don't pass argument
        # But for test purposes, let's just test signature.

        # Test with argument
        # If we pass 5, it should use 5.
        result = med.predicted_sales_before_expiry(5)
        self.assertEqual(result, 50) # 10 * 5

        # Test without argument (should still work if possible, but might fail due to real datetime parsing if we don't mock datetime)
        # We'll just check if it accepts the argument for now as per requirement.

    @patch('src.agent.pd')
    @patch('src.agent.MedicineRecord')
    def test_scan_inventory_calls_with_argument(self, MockMed, mock_pd):
        """Test that scan_inventory calls predicted_sales_before_expiry WITH argument."""
        # Setup mock DataFrame
        mock_df = MagicMock()
        mock_pd.read_csv.return_value = mock_df

        # Create a row. iterrows yields (index, Series)
        row = MagicMock()
        # Mock dictionary access
        row.__getitem__.side_effect = lambda key: {'name': 'TestMed', 'stock': 100, 'expiry_date': '2025-01-01', 'daily_sales': 10}[key]
        mock_df.iterrows.return_value = [(0, row)]

        agent = StockSenseAgent()

        instance = MockMed.return_value
        # Set days_until_expiry to return 10 (triggers the logic)
        instance.days_until_expiry.return_value = 10
        instance.stock = 100
        instance.name = 'TestMed'
        # We need predicted_sales to return something < stock * 0.5 (50) to trigger recommendation print
        instance.predicted_sales_before_expiry.return_value = 40

        agent.scan_inventory("dummy.csv")

        # Verify predicted_sales_before_expiry was called with 10
        instance.predicted_sales_before_expiry.assert_called_with(10)

if __name__ == "__main__":
    unittest.main()
