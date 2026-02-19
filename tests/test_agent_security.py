import unittest
import os
import sys
from unittest.mock import MagicMock

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestAgentSecurity(unittest.TestCase):
    def setUp(self):
        self.agent = StockSenseAgent()

    def test_scan_inventory_path_traversal(self):
        """Test path traversal detection in scan_inventory."""
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Valid path
        valid_path = "data/valid.csv"

        # We expect no exception for valid path
        # Mocking pandas.read_csv to avoid FileNotFoundError or other issues
        # But even if it fails, we only care about ValueError from validation
        try:
            self.agent.scan_inventory(valid_path)
        except ValueError:
            self.fail("scan_inventory raised ValueError for valid path!")
        except Exception:
            # Other exceptions (like FileNotFoundError) are expected if file doesn't exist
            pass

        # Invalid path: Parent directory traversal
        # Assuming we are running from root or somewhere where ../ exists
        invalid_path = "../etc/passwd"
        with self.assertRaises(ValueError):
            self.agent.scan_inventory(invalid_path)

        # Invalid path: Absolute path outside allowed
        if os.name == 'posix':
            invalid_abs_path = "/etc/passwd"
            with self.assertRaises(ValueError):
                self.agent.scan_inventory(invalid_abs_path)

    def test_save_recommendations_path_traversal(self):
        """Test path traversal detection in save_recommendations."""
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)

        # Valid path
        valid_path = "output/valid.json"
        recommendations = {}

        # We expect no exception for valid path
        try:
            self.agent.save_recommendations(recommendations, valid_path)
        except ValueError:
            self.fail("save_recommendations raised ValueError for valid path!")
        except Exception:
            pass

        # Invalid path
        invalid_path = "../pwned.txt"
        with self.assertRaises(ValueError):
            self.agent.save_recommendations(recommendations, invalid_path)

    def test_partial_path_match(self):
        """Test that partial directory name matches are rejected."""
        # output_backup vs output
        invalid_path = "output_backup/test.json"

        with self.assertRaises(ValueError):
             self.agent.save_recommendations({}, invalid_path)

if __name__ == '__main__':
    unittest.main()
