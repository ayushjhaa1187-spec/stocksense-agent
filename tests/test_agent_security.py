import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

from agent import StockSenseAgent

@pytest.fixture
def agent():
    return StockSenseAgent()

def test_path_traversal_scan_inventory_outside_data(agent):
    """Test that scanning a file outside the data directory raises ValueError."""
    # We patch pd.read_csv to simulate successful file read if the path check was bypassed
    with patch('agent.pd.read_csv') as mock_read_csv:
        mock_read_csv.return_value = MagicMock()

        # This should raise ValueError because ../secret.csv is outside data/
        # Currently it will fail because the code doesn't check
    with pytest.raises(ValueError, match="must be within"):
            agent.scan_inventory(inventory_file="../secret.csv")

def test_path_traversal_scan_inventory_absolute_path(agent):
    """Test that scanning a file using absolute path outside allowed directory raises ValueError."""
    with patch('agent.pd.read_csv') as mock_read_csv:
        mock_read_csv.return_value = MagicMock()

        # Use an absolute path that is definitely not in data/
        # e.g., /etc/passwd or C:\Windows\System32
        # We'll use a platform independent way
        abs_path = os.path.abspath("/etc/passwd")

        with pytest.raises(ValueError, match="must be within"):
            agent.scan_inventory(inventory_file=abs_path)

def test_path_traversal_save_recommendations_outside_output(agent):
    """Test that saving to a file outside the output directory raises ValueError."""
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        with patch('os.makedirs') as mock_makedirs:
            # This should raise ValueError because ../critical_system_file.json is outside output/
            with pytest.raises(ValueError, match="must be within"):
                agent.save_recommendations({}, output_file="../critical_system_file.json")
