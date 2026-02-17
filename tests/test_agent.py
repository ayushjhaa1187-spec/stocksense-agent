import sys
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    import pandas as pd
except ImportError:
    # Create a mock pandas module
    mock_pd = MagicMock()
    sys.modules['pandas'] = mock_pd

from agent import MedicineRecord, StockSenseAgent

class TestMedicineRecord:
    def test_days_until_expiry(self):
        # Mock datetime.now() to return a fixed date: 2024-01-01
        with patch('agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1)
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            # Case 1: 9 days left
            med1 = MedicineRecord("Med1", 100, "2024-01-10", 5)
            assert med1.days_until_expiry() == 9

            # Case 2: 31 days left
            med2 = MedicineRecord("Med2", 100, "2024-02-01", 5)
            assert med2.days_until_expiry() == 31

            # Case 3: Expired (-1 days)
            med3 = MedicineRecord("Med3", 100, "2023-12-31", 5)
            assert med3.days_until_expiry() == -1

    def test_predicted_sales_before_expiry(self):
        with patch('agent.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1)
            mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

            # 10 days left, 5 sales/day -> 50 sales
            med = MedicineRecord("Med1", 100, "2024-01-11", 5)
            assert med.days_until_expiry() == 10
            assert med.predicted_sales_before_expiry() == 50

            # Expired -> 0 sales
            med_expired = MedicineRecord("Med2", 100, "2023-12-31", 5)
            assert med_expired.predicted_sales_before_expiry() == 0

class TestStockSenseAgent:
    @pytest.fixture
    def agent(self):
        return StockSenseAgent()

    @patch('agent.pd.read_csv')
    @patch('agent.datetime')
    def test_scan_inventory(self, mock_datetime, mock_read_csv, agent):
        mock_datetime.now.return_value = datetime(2024, 1, 1)
        mock_datetime.strptime.side_effect = lambda *args, **kwargs: datetime.strptime(*args, **kwargs)

        # Create mock dataframe
        data = {
            'name': ['ExpiringSoon', 'DiscountCandidate', 'RestockNeeded', 'SafeMed'],
            'stock': [50, 100, 10, 100],
            'expiry_date': ['2024-01-06', '2024-01-10', '2025-01-01', '2025-01-01'],
            'daily_sales': [5, 2, 5, 5]
        }

        if 'pandas' in sys.modules and isinstance(sys.modules['pandas'], MagicMock):
            mock_df = MagicMock()
            rows = []
            for i in range(len(data['name'])):
                row = {k: data[k][i] for k in data}
                rows.append((i, row))
            mock_df.iterrows.return_value = rows
            mock_read_csv.return_value = mock_df
        else:
            import pandas as pd
            mock_read_csv.return_value = pd.DataFrame(data)

        recommendations = agent.scan_inventory()

        # Verify Expiry Alerts
        # ExpiringSoon: 5 days left -> Alert
        # DiscountCandidate: 9 days left -> Alert (since < 30)
        alerts = recommendations['expiry_alerts']
        assert len(alerts) == 2

        alert_names = [a['medicine'] for a in alerts]
        assert 'ExpiringSoon' in alert_names
        assert 'DiscountCandidate' in alert_names

        expiring_soon = next(a for a in alerts if a['medicine'] == 'ExpiringSoon')
        assert expiring_soon['days_left'] == 5
        assert expiring_soon['urgency'] == 'CRITICAL'

        discount_candidate = next(a for a in alerts if a['medicine'] == 'DiscountCandidate')
        assert discount_candidate['days_left'] == 9
        assert discount_candidate['urgency'] == 'HIGH'

        # Verify Discount Recommendations (DiscountCandidate: 9 days left)
        discounts = recommendations['discount_recommendations']
        assert len(discounts) == 1
        assert discounts[0]['medicine'] == 'DiscountCandidate'
        assert discounts[0]['discount_percent'] == 15

        # Verify Restock Orders (RestockNeeded: stock 10 < 20)
        orders = recommendations['restock_orders']
        assert len(orders) == 1
        assert orders[0]['medicine'] == 'RestockNeeded'

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_recommendations(self, mock_makedirs, mock_file, agent):
        recommendations = {"test": "data"}
        agent.save_recommendations(recommendations, "output/test.json")

        mock_makedirs.assert_called_with("output", exist_ok=True)
        mock_file.assert_called_with("output/test.json", "w")
