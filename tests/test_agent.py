import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import MedicineRecord

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

def test_medicine_record_init_validation():
    # Valid string date
    MedicineRecord(name="Test", stock=10, expiry_date="2023-01-01", daily_sales=5)
    # Valid datetime date
    MedicineRecord(name="Test", stock=10, expiry_date=datetime(2023, 1, 1), daily_sales=5.5)

    # Invalid name type
    with pytest.raises(TypeError, match="name must be a string"):
        MedicineRecord(name=123, stock=10, expiry_date="2023-01-01", daily_sales=5)

    # Empty name
    with pytest.raises(ValueError, match="name cannot be empty"):
        MedicineRecord(name="   ", stock=10, expiry_date="2023-01-01", daily_sales=5)

    # Negative stock
    with pytest.raises(ValueError, match="stock cannot be negative"):
        MedicineRecord(name="Test", stock=-1, expiry_date="2023-01-01", daily_sales=5)

    # Invalid stock type
    with pytest.raises(TypeError, match="stock must be an integer"):
        MedicineRecord(name="Test", stock=10.5, expiry_date="2023-01-01", daily_sales=5)

    # Invalid daily_sales type
    with pytest.raises(TypeError, match="daily_sales must be a number"):
        MedicineRecord(name="Test", stock=10, expiry_date="2023-01-01", daily_sales="5")

    # Negative daily_sales
    with pytest.raises(ValueError, match="daily_sales cannot be negative"):
        MedicineRecord(name="Test", stock=10, expiry_date="2023-01-01", daily_sales=-1.0)

    # Invalid expiry_date format
    with pytest.raises(ValueError, match="expiry_date string must be in YYYY-MM-DD format"):
        MedicineRecord(name="Test", stock=10, expiry_date="11-01-2023", daily_sales=5)

    # Invalid expiry_date type
    with pytest.raises(TypeError, match="expiry_date must be a string"):
        MedicineRecord(name="Test", stock=10, expiry_date=123, daily_sales=5)
