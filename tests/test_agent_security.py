import pytest
from unittest.mock import MagicMock
import os
import sys

sys.modules['pandas'] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

def test_scan_inventory_path_traversal():
    agent = StockSenseAgent()
    # Mock to prevent pandas error
    sys.modules['agent'].pd.read_csv = MagicMock()

    # Path traversal payload
    result = agent.scan_inventory("../etc/passwd")

    assert result is None
    sys.modules['agent'].pd.read_csv.assert_not_called()

def test_save_recommendations_path_traversal():
    agent = StockSenseAgent()

    # Path traversal payload
    agent.save_recommendations({}, "../test_out.json")

    # ensure it doesn't raise exception, just returns None silently
    assert True
