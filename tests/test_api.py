import unittest
import sys
import os
import asyncio
from unittest.mock import MagicMock

# Mock fastapi BEFORE importing app
# We need to ensure we don't clobber the real fastapi if it's there
# But for tests without env, we need to mock it.
# The previous attempt failed because app.get decorator wrapped the function and returned a MagicMock instead of the original function.

# Let's mock FastAPI app.get decorator to return the original function.
mock_fastapi = MagicMock()
mock_app = MagicMock()

def mock_get(path):
    def decorator(func):
        return func
    return decorator

mock_app.get = mock_get
mock_fastapi.FastAPI.return_value = mock_app

sys.modules['fastapi'] = mock_fastapi

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import AFTER mocking
from app.main import app, read_root

class TestApp(unittest.TestCase):
    def test_import_app(self):
        """Verify that the FastAPI app object exists."""
        self.assertIsNotNone(app)

    def test_read_root(self):
        """Verify the root endpoint logic."""
        # read_root should be the original function now because of our decorator mock

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if it's awaitable
            if asyncio.iscoroutinefunction(read_root):
                result = loop.run_until_complete(read_root())
            else:
                result = read_root()
            self.assertEqual(result, {"message": "StockSense Agent API is running"})
        finally:
            loop.close()

if __name__ == '__main__':
    unittest.main()
