## 2025-03-07 - Path Traversal Vulnerability in File Methods
**Vulnerability:** The `StockSenseAgent` in `src/agent.py` was directly passing the user-provided `inventory_file` and `output_file` arguments to `pd.read_csv` and `open()` without proper validation.
**Learning:** This allowed paths like `../malicious.csv` to be read or written to, posing a serious path traversal risk.
**Prevention:** Implement an internal `_validate_path(filepath, allowed_dir)` method using `os.path.realpath` and `os.path.commonpath` to ensure file operations are strictly confined to their intended `data` and `output` directories. Ensure path traversal raises `ValueError` that is safely caught without leaking error specifics.
