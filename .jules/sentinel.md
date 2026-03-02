## 2025-02-18 - Path Traversal Vulnerability in StockSense Agent
**Vulnerability:** Arbitrary file read and write access in `scan_inventory` and `save_recommendations` due to lack of path validation.
**Learning:** `pd.read_csv` and `open` operations were directly processing user-supplied file paths (`inventory_file` and `output_file`) without ensuring they resided within their intended directories (`data/` and `output/`).
**Prevention:** Always validate user-provided file paths against allowed base directories using `os.path.realpath` and `os.path.commonpath` before executing file I/O operations.
