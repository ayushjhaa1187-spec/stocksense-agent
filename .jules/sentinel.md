## 2024-05-24 - Path Traversal Vulnerability in File Loading
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths in `scan_inventory(inventory_file)` and `save_recommendations(output_file)`, leading to path traversal (e.g., `../../etc/passwd`).
**Learning:** File paths passed as arguments without validation can allow an attacker to read/write outside the intended directory boundary.
**Prevention:** Implement path validation using `os.path.abspath` and `os.path.commonpath` to enforce strict directory restrictions.

## 2026-03-10 - Information Leakage in Error Messages
**Vulnerability:** The `StockSenseAgent` logged specific exception variables (e.g., `ValueError` containing internal paths) when scanning inventory or saving recommendations.
**Learning:** Detailed error messages that expose internal file paths or state can leak sensitive information to users or logs.
**Prevention:** Catch generic exceptions and display/log generic error messages (e.g., "Failed to scan inventory file") to prevent information leakage, rather than exposing the exact error string.
