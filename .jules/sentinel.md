## 2024-05-24 - Path Traversal Vulnerability in File Loading
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths in `scan_inventory(inventory_file)` and `save_recommendations(output_file)`, leading to path traversal (e.g., `../../etc/passwd`).
**Learning:** File paths passed as arguments without validation can allow an attacker to read/write outside the intended directory boundary.
**Prevention:** Implement path validation using `os.path.abspath` and `os.path.commonpath` to enforce strict directory restrictions.

## 2024-05-24 - Information Leakage in Error Messages
**Vulnerability:** The application was catching exceptions (`FileNotFoundError`, `ValueError`) and printing their exact string representation (e.g., `print(f"ERROR: {e}")`). This exposed internal state, such as specific internal file paths and system information, to potentially untrusted consumers.
**Learning:** Returning or logging raw exception strings directly can expose critical internal details about the application's environment and architecture.
**Prevention:** Catch specific exceptions and log or return safe, generic error messages (e.g., `Failed to load inventory file`) instead of exposing the raw exception object (`e`).
