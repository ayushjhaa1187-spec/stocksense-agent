import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os
from collections import namedtuple

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import MedicineRecord, StockSenseAgent

@pytest.fixture
def mock_datetime_now():
    # We patch the datetime class in the agent module
    with patch('agent.datetime') as mock_date:
        # We need to ensure strptime works as expected.
        # Since we are mocking the class, we need to wire up strptime to the real implementation
        real_datetime = datetime
        mock_date.strptime.side_effect = real_datetime.strptime

        # We also need to mock datetime.now()
        fixed_now = datetime(2023, 1, 1)
        mock_date.now.return_value = fixed_now

        yield mock_date

def test_days_until_expiry_valid(mock_datetime_now):
    # expiry_date is 10 days after fixed_now (2023-01-01)
    record = MedicineRecord(name="Test Med", stock=10, expiry_date="2023-01-11", daily_sales=1)

    # expected: (2023-01-11 - 2023-01-01).days = 10
    # Note: we need to be careful. agent.py uses (expiry - datetime.now()).days
    # If datetime.now() returns a datetime object, and expiry is a datetime object,
    # subtraction returns a timedelta. timedelta.days is an integer.

    # Verify the mock is working as expected
    from agent import datetime as agent_datetime
    assert agent_datetime.now() == datetime(2023, 1, 1)

    assert record.days_until_expiry() == 10

def test_days_until_expiry_invalid_format(mock_datetime_now):
    # Invalid date format
    # Even if mock_datetime_now is used, strptime should still raise ValueError
    # because we wired it to real_datetime.strptime

    record = MedicineRecord(name="Test Med", stock=10, expiry_date="11-01-2023", daily_sales=1)

    with pytest.raises(ValueError):
        record.days_until_expiry()

def test_scan_inventory_restock(mock_datetime_now):
    # Setup mock dataframe rows
    # itertuples yields namedtuples where the first element is Index
    Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

    # Item 1: Stock 10 (< 20), should trigger restock
    # Expiry far in future (2024-01-01 is > 30 days from 2023-01-01)
    row1 = Row(Index=0, name="Low Stock Med", stock=10, expiry_date="2024-01-01", daily_sales=5)

    # Item 2: Stock 50 (> 20), should NOT trigger restock
    row2 = Row(Index=1, name="High Stock Med", stock=50, expiry_date="2024-01-01", daily_sales=5)

    mock_df = MagicMock()
    mock_df.itertuples.return_value = [row1, row2]
    # Configure columns so 'expiry_date' in inventory.columns check works
    mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

    # We need to access the pandas mock that agent uses
    # Since sys.modules['pandas'] is mocked, agent.pd is that mock
    from agent import pd as agent_pd

    # Configure read_csv to return our mock_df
    agent_pd.read_csv.return_value = mock_df

    # Instantiate agent
    agent = StockSenseAgent()

    # Run scan
    recommendations = agent.scan_inventory(inventory_file="dummy.csv")

    # Assertions
    assert recommendations is not None
    restock_orders = recommendations["restock_orders"]

    # Check that we have exactly 1 restock order
    assert len(restock_orders) == 1

    # Check it's the correct medicine
    assert restock_orders[0]["medicine"] == "Low Stock Med"
    assert restock_orders[0]["recommended_qty"] == 100
