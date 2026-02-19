# Sentinel's Security Journal 🛡️

## 2024-05-22 - Path Traversal in Agent Methods
**Vulnerability:** `StockSenseAgent` methods accepted unvalidated file paths, allowing read/write access outside the intended `data/` and `output/` directories.
**Learning:** Even internal agent classes need input validation if their methods might be exposed to external input (e.g., via API wrappers).
**Prevention:** Enforce strict path validation using `os.path.realpath` and `os.path.commonpath` to ensure file operations stay within sandbox directories.
