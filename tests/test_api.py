import unittest
import sys
import os
import asyncio
from unittest.mock import MagicMock

# Define a function to patch sys.modules while preserving original state if possible
# But in this environment, simple is better.

# 1. Create Mock Objects
mock_fastapi = MagicMock()
mock_app = MagicMock()
mock_staticfiles = MagicMock()
mock_responses = MagicMock()
mock_files_response = MagicMock()
mock_json_response = MagicMock()

# 2. Configure Mock Attributes
# Decorator mock
def mock_get(path):
    def decorator(func):
        return func
    return decorator

mock_app.get = mock_get
mock_app.mount = MagicMock()

# FastAPI constructor returns the mock app
mock_fastapi.FastAPI.return_value = mock_app

# 3. Patch sys.modules
# We need 'fastapi', 'fastapi.staticfiles', 'fastapi.responses' to be importable
sys.modules['fastapi'] = mock_fastapi
sys.modules['fastapi.staticfiles'] = mock_staticfiles
sys.modules['fastapi.responses'] = mock_responses

# 4. Ensure specific classes/functions are available on the mocks
# from fastapi.staticfiles import StaticFiles
mock_staticfiles.StaticFiles = MagicMock()

# from fastapi.responses import FileResponse, JSONResponse
mock_responses.FileResponse = mock_files_response
mock_responses.JSONResponse = mock_json_response

# 5. Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 6. Import app
# Use try/except to catch import errors and fail test gracefully
try:
    from app.main import app, read_root
except ImportError as e:
    app = None
    read_root = None
    print(f"DEBUG: Import failed: {e}")

class TestApp(unittest.TestCase):
    def test_import_app(self):
        """Verify that the FastAPI app object exists."""
        self.assertIsNotNone(app, "Failed to import app from app.main")

    def test_read_root(self):
        """Verify the root endpoint logic."""
        self.assertIsNotNone(read_root, "Failed to import read_root from app.main")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Check if it's awaitable
            if asyncio.iscoroutinefunction(read_root):
                result = loop.run_until_complete(read_root())
            else:
                result = read_root()

            # We expect a FileResponse (which is mocked)
            # Since FileResponse is a class, the result is an instance of the mock
            self.assertIsNotNone(result)
        finally:
            loop.close()

if __name__ == '__main__':
    unittest.main()
