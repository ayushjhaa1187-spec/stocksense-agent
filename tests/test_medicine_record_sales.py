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
    # Patch datetime in the agent module
    with patch('agent.datetime') as mock_date:
        # Wire up strptime to the real implementation
        real_datetime = datetime
        mock_date.strptime.side_effect = real_datetime.strptime

        # Mock datetime.now()
        fixed_now = datetime(2023, 1, 1)
        mock_date.now.return_value = fixed_now

        yield mock_date

def test_predicted_sales_before_expiry(mock_datetime_now):
    """Test predicted_sales_before_expiry with various scenarios."""

    # 1. Future expiry (Implicit current_date via mock)
    # Expiry 2023-01-11 (10 days from 2023-01-01), daily_sales 5 -> 50
    record = MedicineRecord(name="Med A", stock=100, expiry_date="2023-01-11", daily_sales=5)
    assert record.predicted_sales_before_expiry() == 50

    # 2. Future expiry (Explicit current_date)
    # Expiry 2023-01-06, current_date 2023-01-01 -> 5 days * 5 = 25
    explicit_date = datetime(2023, 1, 1)
    record = MedicineRecord(name="Med B", stock=100, expiry_date="2023-01-06", daily_sales=5)
    assert record.predicted_sales_before_expiry(current_date=explicit_date) == 25

    # 3. Expired (Past date)
    # Expiry 2022-12-31, current_date 2023-01-01 -> -1 days * 5 -> 0 (max(0, -1))
    record = MedicineRecord(name="Med C", stock=100, expiry_date="2022-12-31", daily_sales=5)
    assert record.predicted_sales_before_expiry(current_date=explicit_date) == 0

    # 4. Expiring Today
    # Expiry 2023-01-01, current_date 2023-01-01 -> 0 days * 5 -> 0
    record = MedicineRecord(name="Med D", stock=100, expiry_date="2023-01-01", daily_sales=5)
    assert record.predicted_sales_before_expiry(current_date=explicit_date) == 0

    # 5. Zero Daily Sales
    # Expiry 2023-01-11 (10 days), daily_sales 0 -> 0
    record = MedicineRecord(name="Med E", stock=100, expiry_date="2023-01-11", daily_sales=0)
    assert record.predicted_sales_before_expiry(current_date=explicit_date) == 0
