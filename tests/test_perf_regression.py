#!/usr/bin/env python3
"""Performance regression tests for StockSense Agent.

Verifies that optimization remains in place:
- No strptime calls inside the loop (vectorized date parsing)
- Vectorized filtering is used instead of full inventory iteration
- itertuples() is called only on filtered subsets
- pd.to_datetime() is called for vectorization
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from collections import namedtuple

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
import pandas as pd

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'src')))

from agent import StockSenseAgent

class TestOptimization(unittest.TestCase):
    """Test that scan_inventory uses optimized code paths."""
    
    def test_scan_inventory_optimization(self):
        """Verify vectorized filtering and efficient iteration."""
        # Setup mock data
        mock_df = MagicMock()
        
        # Mocking Series for vectorized operations
        mock_series = MagicMock()
        mock_series.__le__.return_value = mock_series
        mock_series.__ge__.return_value = mock_series
        mock_series.__lt__.return_value = mock_series
        mock_series.__gt__.return_value = mock_series
        mock_series.__and__.return_value = mock_series
        
        # Mocking filtered results
        # When we do inventory[mask], it should return a subset mock
        filtered_mock = MagicMock()
        # Ensure 'empty' returns False so we enter the discount loop logic
        type(filtered_mock).empty = PropertyMock(return_value=False)
        
        # Setup itertuples for the filtered results
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales', 'days_left', 'predicted_sales'])
        expiry_dt = datetime(2025, 1, 1)
        rows = [Row(0, 'TestMed', 100, expiry_dt, 5, 10, 50)]
        filtered_mock.itertuples.return_value = rows
        
        # Setup __getitem__ to return mock_series for column access and filtered_mock for masking
        def getitem_side_effect(key):
            if isinstance(key, str):
                return mock_series
            return filtered_mock

        mock_df.__getitem__.side_effect = getitem_side_effect
        mock_df.copy.return_value = filtered_mock
        
        # Support 'expiry_date' in mock_df.columns check
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        
        # Mock read_csv
        pd.read_csv = MagicMock(return_value=mock_df)
        
        # Mock to_datetime (just returns the column)
        pd.to_datetime = MagicMock()

        with patch('agent.datetime') as mock_datetime:
            real_datetime = datetime
            mock_datetime.strptime.side_effect = real_datetime.strptime
            mock_datetime.now.return_value = real_datetime(2023, 1, 1)
            
            # Run scan_inventory
            agent = StockSenseAgent()
            agent.scan_inventory('dummy.csv')
            
            # VERIFICATION 1: strptime should NOT be called
            self.assertEqual(mock_datetime.strptime.call_count, 0)
            
            # VERIFICATION 2: Vectorized filtering should be used
            print(f"✓ Filtering calls (__getitem__): {mock_df.__getitem__.call_count}")
            self.assertGreaterEqual(mock_df.__getitem__.call_count, 3)
            
            # VERIFICATION 3: itertuples should NOT be called on the full mock_df
            print(f"✓ Full iteration check (mock_df.itertuples): {mock_df.itertuples.call_count}")
            self.assertEqual(mock_df.itertuples.call_count, 0)
            
            # VERIFICATION 4: itertuples SHOULD be called on the filtered results
            print(f"✓ Subset iteration check (filtered_mock.itertuples): {filtered_mock.itertuples.call_count}")
            self.assertGreaterEqual(filtered_mock.itertuples.call_count, 2)
            
            # VERIFICATION 5: to_datetime SHOULD be called
            self.assertEqual(pd.to_datetime.call_count, 1)
            
            print("\n✅ All performance regression tests passed!")

if __name__ == '__main__':
    unittest.main()
