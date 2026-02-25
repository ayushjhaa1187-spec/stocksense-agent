## 2024-05-22 - [Path Traversal in Agent File Operations]
**Vulnerability:** `StockSenseAgent.scan_inventory` and `save_recommendations` accepted user-provided file paths without validation, allowing reading and writing arbitrary files outside intended directories.
**Learning:** Even in internal agents or scripts, file operations must be sandboxed to prevent accidental or malicious data leakage, especially when file paths might be influenced by external configuration.
**Prevention:** Use `os.path.realpath` and `os.path.commonpath` to strictly enforce directory boundaries for all file I/O operations.
