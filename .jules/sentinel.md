## 2025-03-05 - Path Traversal Vulnerability in File Handling
**Vulnerability:** StockSenseAgent lacked validation on input and output file paths in `scan_inventory` and `save_recommendations`, allowing arbitrary read/write access to the filesystem (e.g. `../../../etc/passwd`).
**Learning:** Functions that accept file paths as arguments without checking if they remain within expected bounds open up critical path traversal vulnerabilities.
**Prevention:** Always validate file paths by resolving them to absolute paths using `os.path.realpath` and verifying they share a common base directory using `os.path.commonpath` against the intended root before performing file I/O operations.
