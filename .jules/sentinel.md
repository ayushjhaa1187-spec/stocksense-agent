# Sentinel's Journal - Critical Security Learnings

## 2024-05-22 - Initial Setup
**Note:** Initializing Sentinel's journal.

## 2025-05-22 - Path Traversal in File Operations
**Vulnerability:** The `StockSenseAgent.save_recommendations` and `scan_inventory` methods blindly accepted user-provided file paths, allowing path traversal (e.g., `../exploit.json`) to write or read files outside the intended directories.
**Learning:** Python's `open()` and `pd.read_csv()` do not inherently validate that a path is within a specific directory. Relying on relative paths without validation is insecure.
**Prevention:** Implemented a `_validate_path` helper method using `os.path.abspath` and `os.path.commonpath`. This ensures that all file operations are strictly contained within their respective `data/` and `output/` directories. This pattern should be applied to all future file I/O operations.
