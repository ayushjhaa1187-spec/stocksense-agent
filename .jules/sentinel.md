## 2024-05-24 - Path Traversal Vulnerability in File Loading
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths in `scan_inventory(inventory_file)` and `save_recommendations(output_file)`, leading to path traversal (e.g., `../../etc/passwd`).
**Learning:** File paths passed as arguments without validation can allow an attacker to read/write outside the intended directory boundary.
**Prevention:** Implement path validation using `os.path.abspath` and `os.path.commonpath` to enforce strict directory restrictions.

## 2024-05-24 - Information Leakage via Error Messages
**Vulnerability:** The error handling blocks printed the exact exception message (`e`), which could leak sensitive information such as file paths or internal state. Additionally, `save_recommendations` did not handle general exceptions (like `OSError`), potentially leading to unhandled exceptions and full stack trace leakage.
**Learning:** Unhandled exceptions or overly descriptive error messages can be exploited to gain insights into the application's environment or logic.
**Prevention:** Catch general exceptions in critical path file operations and use generic error messages that do not expose internal details.
