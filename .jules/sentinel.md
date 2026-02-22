## 2024-05-22 - Performance Test Mocking Patterns
**Vulnerability:** Flaky tests in `test_perf_regression.py` due to module caching.
**Learning:** `sys.modules['pandas']` mocking is fragile when `agent` module is already imported/cached by other tests (`test_agent.py`). Subsequent tests modifying `sys.modules` won't update `agent.pd`.
**Prevention:** Use `patch('agent.pd')` in tests to ensure you are configuring the exact object instance used by the code under test, rather than relying on global `sys.modules` state.
