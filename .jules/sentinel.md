## 2024-05-24 - Path Traversal Vulnerability in File Loading
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths in `scan_inventory(inventory_file)` and `save_recommendations(output_file)`, leading to path traversal (e.g., `../../etc/passwd`).
**Learning:** File paths passed as arguments without validation can allow an attacker to read/write outside the intended directory boundary.
**Prevention:** Implement path validation using `os.path.abspath` and `os.path.commonpath` to enforce strict directory restrictions.

## 2024-05-25 - Information Leakage via Exception Stringification
**Vulnerability:** The `StockSenseAgent` printed the raw exception object `e` to the console on file validation errors, exposing internal file paths like the expected base directory and the rejected absolute path.
**Learning:** Even if an application securely handles a path traversal attempt by raising an error, logging or printing the raw error message can leak the server's directory structure to an attacker or user.
**Prevention:** Fail securely by catching specific exceptions and returning generic error messages (e.g., "Failed to load file") without including the internal exception string representation.
