## 2024-05-24 - Path Traversal Vulnerability in File Loading
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths in `scan_inventory(inventory_file)` and `save_recommendations(output_file)`, leading to path traversal (e.g., `../../etc/passwd`).
**Learning:** File paths passed as arguments without validation can allow an attacker to read/write outside the intended directory boundary.
**Prevention:** Implement path validation using `os.path.abspath` and `os.path.commonpath` to enforce strict directory restrictions.
## 2026-03-11 - Prevent path leakage in error messages
**Vulnerability:** Information Leakage via Exception Messages
**Learning:** Returning or printing raw exceptions (`e`) caught during file operations or validation can expose internal file paths or system information to logs or users.
**Prevention:** Always use generic error messages when catching exceptions related to file access or validation, avoiding direct logging or exposure of the exception object's message.
