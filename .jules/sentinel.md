## 2025-02-24 - Path Traversal Vulnerability in I/O Methods
**Vulnerability:** Found a path traversal vulnerability in `StockSenseAgent.scan_inventory` and `save_recommendations` where user-provided file paths were not restricted to intended `data/` and `output/` directories.
**Learning:** Hardcoded default values do not implicitly prevent overriding with directory traversal sequences like `../`, which could lead to arbitrary file reads/writes on the filesystem and potential remote code execution or data leakage.
**Prevention:** Implement secure path validation using `os.path.realpath` to resolve symbolic links and relative paths alongside `os.path.commonpath` to ensure the resolved target path resides strictly within the intended base directory.
