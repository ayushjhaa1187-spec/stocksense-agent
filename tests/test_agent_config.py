import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import os

# Mock pandas before importing agent
sys.modules['pandas'] = MagicMock()
import pandas as pd

# Add src to python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agent import StockSenseAgent

class TestAgentConfig(unittest.TestCase):
    def test_custom_expiry_threshold(self):
        """Test that custom expiry threshold is respected."""

        custom_config = {
            "expiry_alert_days": 60,
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

        mock_df = MagicMock()

        from collections import namedtuple
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        expiry_dt = datetime(2023, 2, 15)

        rows = [
            Row(0, 'TestMed_45Days', 100, expiry_dt, 5)
        ]

        mock_df.itertuples.return_value = rows
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        with patch('agent.pd') as mock_pd:
            mock_pd.read_csv.return_value = mock_df
            mock_pd.to_datetime.return_value = mock_df['expiry_date']

            with patch('agent.datetime') as mock_datetime:
                real_datetime = datetime
                mock_datetime.strptime.side_effect = real_datetime.strptime
                mock_datetime.now.return_value = real_datetime(2023, 1, 1)

                agent = StockSenseAgent(config=custom_config)
                recommendations = agent.scan_inventory('dummy.csv')

                alerts = recommendations['expiry_alerts']
                self.assertEqual(len(alerts), 1, "Should alert for item expiring in 45 days with 60-day threshold")
                self.assertEqual(alerts[0]['medicine'], 'TestMed_45Days')

    def test_default_expiry_threshold(self):
        """Test that default expiry threshold (30 days) is respected when no config is provided."""

        mock_df = MagicMock()

        from collections import namedtuple
        Row = namedtuple('Row', ['Index', 'name', 'stock', 'expiry_date', 'daily_sales'])

        expiry_dt = datetime(2023, 2, 15)

        rows = [
            Row(0, 'TestMed_45Days', 100, expiry_dt, 5)
        ]

        mock_df.itertuples.return_value = rows
        mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

        with patch('agent.pd') as mock_pd:
            mock_pd.read_csv.return_value = mock_df
            mock_pd.to_datetime.return_value = mock_df['expiry_date']

            with patch('agent.datetime') as mock_datetime:
                real_datetime = datetime
                mock_datetime.strptime.side_effect = real_datetime.strptime
                mock_datetime.now.return_value = real_datetime(2023, 1, 1)

                agent = StockSenseAgent()
                recommendations = agent.scan_inventory('dummy.csv')

                alerts = recommendations['expiry_alerts']
                self.assertEqual(len(alerts), 0, "Should NOT alert for item expiring in 45 days with default 30-day threshold")

if __name__ == '__main__':
    unittest.main()
