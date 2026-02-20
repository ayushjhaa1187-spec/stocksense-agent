#!/usr/bin/env python3
"""Performance regression tests for StockSense Agent."""

import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from collections import namedtuple
import os

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestOptimization(unittest.TestCase):
    """Test that scan_inventory uses optimized code paths."""
    
    def test_scan_inventory_optimization(self):
        """Verify vectorized date parsing and efficient iteration."""
        # Setup mock data
        mock_df = MagicMock()
        
        # Setup itertuples
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])
        expiry_dt = datetime(2025, 1, 1)
        rows = [
            Row(i, f'TestMed_{i}', 100, expiry_dt, 5)
            for i in range(100)
        ]
        mock_df.itertuples.return_value = rows
        
        # Support 'expiry_date' in mock_df.columns check
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']
        
        with patch('agent.pd') as mock_pd,              patch('agent.datetime') as mock_datetime:

            mock_pd.read_csv.return_value = mock_df
            mock_pd.to_datetime.return_value = [expiry_dt] * 100

            real_datetime = datetime
            mock_datetime.strptime.side_effect = real_datetime.strptime
            mock_datetime.now.return_value = real_datetime(2023, 1, 1)
            
            # Run scan_inventory
            agent = StockSenseAgent()
            
            # Patch _validate_path
            with patch.object(agent, '_validate_path', return_value=True):
                agent.scan_inventory('dummy.csv')
            
            # VERIFICATION
            self.assertEqual(mock_datetime.strptime.call_count, 0, "strptime should not be called")
            self.assertEqual(mock_df.iterrows.call_count, 0, "iterrows should not be used")
            self.assertEqual(mock_df.itertuples.call_count, 1, "itertuples should be called")
            self.assertEqual(mock_pd.to_datetime.call_count, 1, "to_datetime should be called")

if __name__ == '__main__':
    unittest.main()
