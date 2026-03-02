## 2025-03-02 - Path Traversal in Agent I/O
**Vulnerability:** The `scan_inventory` and `save_recommendations` methods in `StockSenseAgent` accepted arbitrary file paths (like `../../etc/passwd` or `/absolute/paths`) and processed/wrote to them without validation.
**Learning:** File paths passed to an agent must never be trusted. Even if defaults are safe (e.g., `data/sample_inventory.csv`), an attacker modifying the arguments could read sensitive local files via pandas or write arbitrary files via JSON serialization.
**Prevention:** Always validate file paths against an allowed base directory using `os.path.realpath()` and `os.path.commonpath()`. Catch exceptions and fail securely without leaking stack traces.
