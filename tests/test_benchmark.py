import sys
import os
from unittest.mock import MagicMock, patch

# Mock pandas globally
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Add scripts to path
sys.path.append(os.path.abspath('scripts'))

# Import benchmark
# We need to ensure agent can be imported too.
# benchmark.py adds ../src to sys.path, so that should handle agent import.
import benchmark

import unittest

class TestBenchmarkSecurity(unittest.TestCase):
    @patch('benchmark.StockSenseAgent')
    @patch('benchmark.generate_test_data')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_temp_file_usage(self, mock_remove, mock_exists, mock_gen_data, mock_agent):
        # Setup mocks
        mock_df = MagicMock()
        mock_gen_data.return_value = mock_df

        # Run benchmark with small size
        benchmark.benchmark_scan_inventory(sizes=[10])

        # Check that to_csv was called
        self.assertTrue(mock_df.to_csv.called)

        # Check the filename passed to to_csv
        args, _ = mock_df.to_csv.call_args
        filename = args[0]
        print(f"Filename used: {filename}")

        # Security check: filename should not be a simple relative path
        self.assertNotEqual(filename, 'benchmark_data.csv', "Vulnerable: using fixed filename 'benchmark_data.csv'")

        # It should be an absolute path (tempfile usually returns absolute path)
        self.assertTrue(os.path.isabs(filename), f"Filename {filename} is not absolute")

if __name__ == '__main__':
    unittest.main()
