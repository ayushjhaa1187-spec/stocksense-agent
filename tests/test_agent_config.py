import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from collections import namedtuple
import sys
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
import pandas as pd

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent, MedicineRecord

class TestAgentConfig:
    def test_custom_expiry_threshold(self):
        """Test that the agent respects custom expiry threshold configuration."""

        # Define custom config
        custom_config = {
            "expiry_alert_days": 60,  # Changed from default 30
            "critical_expiry_days": 7,
            "discount": {
                "min_days": 7,
                "max_days": 14,
                "stock_ratio_threshold": 0.5,
                "high_discount_pct": 15,
                "low_discount_pct": 10,
                "high_discount_stock_ratio": 0.3,
                "expected_clear_pct": 80,
                "revenue_recovery_ratio": 0.1
            },
            "restock": {
                "threshold": 20,
                "qty": 100,
                "cost": 5000
            }
        }

        # Setup mock data
        # Medicine expires in 45 days
        # Default (30 days): No alert
        # Custom (60 days): Alert

        mock_df = MagicMock()
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        # expiry_date doesn't matter much as we mock days_until_expiry, but let's be consistent
        expiry_dt = datetime(2023, 2, 15) # 45 days from 2023-01-01

        rows = [
            Row(0, 'MedA', 100, expiry_dt, 5)
        ]

        mock_df.itertuples.return_value = rows
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        pd.read_csv = MagicMock(return_value=mock_df)
        pd.to_datetime = MagicMock()

        with patch('agent.datetime') as mock_datetime:
            real_datetime = datetime
            mock_datetime.strptime.side_effect = real_datetime.strptime
            # Mock current time to 2023-01-01
            mock_datetime.now.return_value = datetime(2023, 1, 1)

            # Test with custom config
            agent = StockSenseAgent(config=custom_config)
            recommendations = agent.scan_inventory('dummy.csv')

            # Should have an alert because 45 <= 60
            assert len(recommendations['expiry_alerts']) == 1
            assert recommendations['expiry_alerts'][0]['medicine'] == 'MedA'

    def test_default_expiry_threshold(self):
        """Test that the agent uses default expiry threshold (30 days) when no config is provided."""

        # Setup mock data
        # Medicine expires in 45 days
        # Default (30 days): No alert

        mock_df = MagicMock()
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        expiry_dt = datetime(2023, 2, 15) # 45 days from 2023-01-01

        rows = [
            Row(0, 'MedA', 100, expiry_dt, 5)
        ]

        mock_df.itertuples.return_value = rows
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        pd.read_csv = MagicMock(return_value=mock_df)
        pd.to_datetime = MagicMock()

        with patch('agent.datetime') as mock_datetime:
            real_datetime = datetime
            mock_datetime.strptime.side_effect = real_datetime.strptime
            mock_datetime.now.return_value = datetime(2023, 1, 1)

            # Test with default config
            agent = StockSenseAgent()
            recommendations = agent.scan_inventory('dummy.csv')

            # Should NOT have an alert because 45 > 30
            assert len(recommendations['expiry_alerts']) == 0

if __name__ == '__main__':
    pytest.main([__file__])
