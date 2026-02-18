#!/usr/bin/env python3
"""Performance regression tests for StockSense Agent.

Verifies that optimization remains in place:
- No strptime calls inside the loop (vectorized date parsing)
- itertuples() is used instead of iterrows()
- pd.to_datetime() is called for vectorization
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from collections import namedtuple
import os

# Mock pandas before importing agent to avoid ImportError
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent
# We don't import pandas here to avoid confusion. We'll use patch('agent.pd')

class TestOptimization(unittest.TestCase):
    """Test that scan_inventory uses optimized code paths."""
    
    @patch('agent.pd')
    @patch('agent.datetime')
    def test_scan_inventory_optimization(self, mock_datetime, mock_pd):
        """Verify vectorized date parsing and efficient iteration."""
        # Setup mock data
        mock_df = MagicMock()
        
        # Setup itertuples
        # itertuples yields named tuples
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])
        
        # expiry_date should be a datetime object (as if to_datetime worked)
        expiry_dt = datetime(2025, 1, 1)
        
        rows = [
            Row(i, f'TestMed_{i}', 100, expiry_dt, 5)
            for i in range(100)
        ]
        
        mock_df.itertuples.return_value = rows
        
        # Support 'expiry_date' in mock_df.columns check
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        
        # Mock read_csv
        mock_pd.read_csv.return_value = mock_df
        
        # Mock to_datetime (just returns the column)
        # We don't need to return anything specific as long as it doesn't crash,
        # but in the code it does inventory['expiry_date'] = pd.to_datetime(...)

        real_datetime = datetime
        mock_datetime.strptime.side_effect = real_datetime.strptime
        mock_datetime.now.return_value = real_datetime(2023, 1, 1)

        # Run scan_inventory
        agent = StockSenseAgent()
        agent.scan_inventory('dummy.csv')

        # VERIFICATION 1: strptime should NOT be called inside the loop
        print(f"✓ Calls to strptime: {mock_datetime.strptime.call_count}")
        self.assertEqual(mock_datetime.strptime.call_count, 0,
                       "strptime should not be called with vectorized date parsing")

        # VERIFICATION 2: iterrows should NOT be called
        print(f"✓ Calls to iterrows: {mock_df.iterrows.call_count}")
        self.assertEqual(mock_df.iterrows.call_count, 0,
                       "iterrows should not be used (use itertuples instead)")

        # VERIFICATION 3: itertuples SHOULD be called
        print(f"✓ Calls to itertuples: {mock_df.itertuples.call_count}")
        self.assertEqual(mock_df.itertuples.call_count, 1,
                       "itertuples should be called for efficient iteration")

        # VERIFICATION 4: to_datetime SHOULD be called
        print(f"✓ Calls to to_datetime: {mock_pd.to_datetime.call_count}")
        self.assertEqual(mock_pd.to_datetime.call_count, 1,
                       "pd.to_datetime should be called for vectorization")

        # VERIFICATION 5: datetime.now() should be called a small number of times
        print(f"✓ Calls to datetime.now: {mock_datetime.now.call_count}")
        self.assertLess(mock_datetime.now.call_count, 10,
                      "datetime.now should not be called inside the loop")

        print("\n✅ All performance regression tests passed!")

if __name__ == '__main__':
    unittest.main(verbosity=2)
