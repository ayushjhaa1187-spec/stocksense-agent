import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
import pandas as pd

from agent import StockSenseAgent

def create_mock_df(data):
    df = MagicMock()
    df.columns = list(data.keys())
    rows = []
    num_rows = len(next(iter(data.values())))
    for i in range(num_rows):
        row = MagicMock()
        for col, values in data.items():
            setattr(row, col, values[i])
        rows.append(row)
    df.itertuples.return_value = rows
    return df

@pytest.fixture
def mock_datetime_now():
    with patch('agent.datetime') as mock_date:
        real_datetime = datetime
        mock_date.strptime.side_effect = real_datetime.strptime
        fixed_now = datetime(2023, 1, 1)
        mock_date.now.return_value = fixed_now
        yield mock_date

def test_custom_discount_config(mock_datetime_now):
    # Custom config: min_days = 5 (default is 7)
    custom_config = {
        "discount": {
            "min_days": 5,
            "max_days": 14,
            "stock_threshold_ratio": 0.5,
            "high_discount_threshold_ratio": 0.3,
            "high_discount_percent": 15,
            "low_discount_percent": 10,
            "expected_clear_pct": 80,
            "recovery_factor": 0.1
        }
    }

    agent = StockSenseAgent(config=custom_config)

    # Item expiring in 6 days
    # Default config (min 7) -> No discount
    # Custom config (min 5) -> Discount

    current_date = datetime(2023, 1, 1)
    expiry_date = current_date + timedelta(days=6)

    data = {
        'name': ['Item1'],
        'stock': [50],
        'expiry_date': [expiry_date],
        'daily_sales': [1] # predicted sales = 6 < 25 (50*0.5). Fits logic.
    }

    mock_df = create_mock_df(data)

    with patch('agent.pd') as mock_pd:
        mock_pd.read_csv.return_value = mock_df

        recs = agent.scan_inventory("dummy.csv")

        discounts = recs['discount_recommendations']
        assert len(discounts) == 1
        assert discounts[0]['medicine'] == 'Item1'

def test_default_discount_config(mock_datetime_now):
    # Verify default config behavior (min 7)
    agent = StockSenseAgent() # Default config

    current_date = datetime(2023, 1, 1)
    expiry_date = current_date + timedelta(days=6)

    data = {
        'name': ['Item1'],
        'stock': [50],
        'expiry_date': [expiry_date],
        'daily_sales': [1]
    }

    mock_df = create_mock_df(data)

    with patch('agent.pd') as mock_pd:
        mock_pd.read_csv.return_value = mock_df

        recs = agent.scan_inventory("dummy.csv")

        discounts = recs['discount_recommendations']
        assert len(discounts) == 0

if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__])

def test_partial_config_update(mock_datetime_now):
    # Verify that partial update doesn't delete other keys
    custom_config = {
        "discount": {
            "min_days": 5
        }
    }

    agent = StockSenseAgent(config=custom_config)

    # Check that min_days is updated
    assert agent.config["discount"]["min_days"] == 5

    # Check that other keys are preserved
    assert agent.config["discount"]["max_days"] == 14
    assert agent.config["discount"]["stock_threshold_ratio"] == 0.5
