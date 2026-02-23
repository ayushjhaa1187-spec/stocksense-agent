## 2026-02-17 - Path Traversal in File Operations
**Vulnerability:** The `StockSenseAgent` allowed arbitrary file access via unvalidated input paths in `scan_inventory` and `save_recommendations`, leading to potential data leakage or system compromise.
**Learning:** Python's `open()` and `pd.read_csv()` do not restrict file access by default. Trusting user input for file paths without validation is a critical security risk.
**Prevention:** Always validate file paths against an allowlist of directories using `os.path.abspath` and `os.path.commonpath` before performing file operations. Enforce strict directory boundaries (e.g., `data/` for input, `output/` for output).
