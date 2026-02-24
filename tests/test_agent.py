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

def test_days_until_expiry_invalid_format(mock_datetime_now):
    # Invalid date format
    # Even if mock_datetime_now is used, strptime should still raise ValueError
    # because we wired it to real_datetime.strptime

    record = MedicineRecord(name="Test Med", stock=10, expiry_date="11-01-2023", daily_sales=1)

    with pytest.raises(ValueError):
        record.days_until_expiry()

def test_predicted_sales_before_expiry(mock_datetime_now):
    # Setup
    # Mocked now is 2023-01-01

    # Case 1: Future expiry
    # Expiry 2023-01-11 (10 days away)
    # Daily sales 5
    # Expected: 10 * 5 = 50
    record = MedicineRecord(name="Future Med", stock=100, expiry_date="2023-01-11", daily_sales=5)
    assert record.predicted_sales_before_expiry() == 50

    # Case 2: Past expiry (expired)
    # Expiry 2022-12-31 (1 day ago)
    # Expected: 0 (max(0, -1) * 5)
    record_expired = MedicineRecord(name="Expired Med", stock=100, expiry_date="2022-12-31", daily_sales=5)
    assert record_expired.predicted_sales_before_expiry() == 0

    # Case 3: Explicit current_date
    # Override current date to 2023-01-05
    # Expiry 2023-01-11 -> 6 days left
    # Expected: 6 * 5 = 30
    explicit_date = datetime(2023, 1, 5)
    assert record.predicted_sales_before_expiry(current_date=explicit_date) == 30
