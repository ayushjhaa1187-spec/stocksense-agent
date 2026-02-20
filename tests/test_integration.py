import unittest
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Mock pandas before importing agent
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = MagicMock()

# Mock fastapi before importing app
if 'fastapi' not in sys.modules:
    mock_fastapi = MagicMock()
    mock_app = MagicMock()

    def mock_get(path):
        def decorator(func):
            return func
        return decorator

    mock_app.get = mock_get
    mock_app.mount = MagicMock()
    mock_fastapi.FastAPI.return_value = mock_app
    mock_fastapi.staticfiles = MagicMock()
    mock_fastapi.responses = MagicMock()

    sys.modules['fastapi'] = mock_fastapi
    sys.modules['fastapi.staticfiles'] = MagicMock()
    sys.modules['fastapi.responses'] = MagicMock()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to ensure src.agent uses the mock pandas
import src.agent
from app.main import get_recommendations

class TestIntegration(unittest.TestCase):
    def test_api_recommendations_mocked(self):
        """Test that /api/recommendations calls agent scan_inventory."""

        # We need to mock StockSenseAgent instance inside app.main
        # app.main does: from src.agent import StockSenseAgent

        # Define return value
        expected_data = {
            "timestamp": "2023-01-01T00:00:00",
            "expiry_alerts": [],
            "discount_recommendations": [],
            "restock_orders": []
        }

        # Patch StockSenseAgent class where it is used in app.main
        with patch('app.main.StockSenseAgent') as MockAgent:
            # Configure the mock instance returned by constructor
            mock_instance = MockAgent.return_value
            mock_instance.scan_inventory.return_value = expected_data

            # Execute the async handler
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if asyncio.iscoroutinefunction(get_recommendations):
                    result = loop.run_until_complete(get_recommendations())
                else:
                    result = get_recommendations()

                # Verify result
                self.assertEqual(result, expected_data)

                # Verify it called scan_inventory
                mock_instance.scan_inventory.assert_called_once()

            finally:
                loop.close()

if __name__ == '__main__':
    unittest.main()
