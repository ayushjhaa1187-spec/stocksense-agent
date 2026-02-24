import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# We need to handle module cleanup to avoid polluting other tests
class TestBenchmarkSecurity(unittest.TestCase):
    def setUp(self):
        # Patch sys.modules to mock pandas
        self.patcher = patch.dict(sys.modules, {'pandas': MagicMock()})
        self.mock_pd = self.patcher.start()

        # Add scripts to path
        self.script_path = os.path.abspath('scripts')
        if self.script_path not in sys.path:
            sys.path.append(self.script_path)

    def tearDown(self):
        self.patcher.stop()
        # Remove modules that might have been loaded with the mock
        for module in ['benchmark', 'agent']:
            if module in sys.modules:
                del sys.modules[module]
        if self.script_path in sys.path:
            sys.path.remove(self.script_path)

    @patch('benchmark.StockSenseAgent')
    @patch('benchmark.generate_test_data')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_temp_file_usage(self, mock_remove, mock_exists, mock_gen_data, mock_agent):
        # Import benchmark inside test to ensure it uses the mocked pandas
        import benchmark

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
        # print(f"Filename used: {filename}")

        # Security check: filename should not be a simple relative path
        self.assertNotEqual(filename, 'benchmark_data.csv', "Vulnerable: using fixed filename 'benchmark_data.csv'")

        # It should be an absolute path (tempfile usually returns absolute path)
        self.assertTrue(os.path.isabs(filename), f"Filename {filename} is not absolute")

if __name__ == '__main__':
    unittest.main()
