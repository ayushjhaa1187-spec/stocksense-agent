## 2024-05-14 - Prevent Path Traversal in File Operations
**Vulnerability:** The `StockSenseAgent` accepted arbitrary paths for `inventory_file` and `output_file`, leading to potential directory traversal (`../`) allowing reading or writing arbitrary files.
**Learning:** Hardcoded default file paths don't inherently prevent users from supplying malicious inputs. We must validate user-supplied file paths strictly against allowed directories.
**Prevention:** Implement a robust validation helper using `os.path.realpath` and `os.path.commonpath` to ensure resolved paths reside strictly within allowed base directories.
