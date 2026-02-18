import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure pandas is mocked so agent can be imported
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Add src path to import agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import agent
from agent import StockSenseAgent
from collections import namedtuple

def test_scan_inventory_missing_columns():
    """Test that scan_inventory raises AttributeError when required columns (like 'stock') are missing."""

    # Setup mock dataframe
    mock_df = MagicMock()
    mock_df.columns = ['name', 'expiry_date', 'daily_sales']

    # Define a row structure missing 'stock'
    Row = namedtuple('Row', ['name', 'expiry_date', 'daily_sales'])
    row1 = Row(name="Medicine A", expiry_date="2023-12-31", daily_sales=10)

    mock_df.itertuples.return_value = [row1]

    # Patch agent.pd to ensure we control the pandas used by agent
    with patch('agent.pd') as mock_pd:
        mock_pd.read_csv.return_value = mock_df
        mock_pd.to_datetime.return_value = ["2023-12-31"]

        agent_instance = StockSenseAgent()

        with pytest.raises(AttributeError) as excinfo:
            agent_instance.scan_inventory("dummy.csv")

        assert "object has no attribute 'stock'" in str(excinfo.value)
