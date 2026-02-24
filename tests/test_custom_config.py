import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, timedelta

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

# Helper to create mock dataframe
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
        # Fix now to a specific date
        fixed_now = datetime(2023, 1, 1)
        mock_date.now.return_value = fixed_now
        yield mock_date

def test_custom_config_discount(mock_datetime_now):
    # Default: 7 <= days_left <= 14
    # Custom: 5 <= days_left <= 25

    custom_config = {
        "discount_min_days": 5,
        "discount_max_days": 25
    }

    agent = StockSenseAgent(config=custom_config)

    current_date = datetime(2023, 1, 1)

    # Item 1: Expires in 6 days (2023-01-07). Default: No discount. Custom: Discount.
    expiry_1 = current_date + timedelta(days=6)

    # Item 2: Expires in 20 days (2023-01-21). Default: No discount. Custom: Discount.
    expiry_2 = current_date + timedelta(days=20)

    data = {
        'name': ['Item1', 'Item2'],
        'stock': [100, 100],
        'expiry_date': [expiry_1, expiry_2],
        'daily_sales': [1, 1] # Low sales to trigger discount if days match
    }

    mock_df = create_mock_df(data)

    with patch('agent.pd') as mock_pd:
        mock_pd.read_csv.return_value = mock_df

        recs = agent.scan_inventory("dummy.csv")

        discounts = [d['medicine'] for d in recs['discount_recommendations']]

        assert 'Item1' in discounts, "Item1 should be discounted with min_days=5 (days_left=6)"
        assert 'Item2' in discounts, "Item2 should be discounted with max_days=25 (days_left=20)"

def test_custom_config_restock(mock_datetime_now):
    # Default threshold: 20
    # Custom threshold: 60

    custom_config = {
        "restock_threshold": 60
    }

    agent = StockSenseAgent(config=custom_config)

    # Item 1: Stock 50. Default: No restock (<20). Custom: Restock (<60).
    expiry = datetime(2023, 6, 1) # Far future

    data = {
        'name': ['Item1'],
        'stock': [50],
        'expiry_date': [expiry],
        'daily_sales': [1]
    }

    mock_df = create_mock_df(data)

    with patch('agent.pd') as mock_pd:
        mock_pd.read_csv.return_value = mock_df

        recs = agent.scan_inventory("dummy.csv")

        restocks = [d['medicine'] for d in recs['restock_orders']]

        assert 'Item1' in restocks, "Item1 should be restocked with threshold=60 (stock=50)"
