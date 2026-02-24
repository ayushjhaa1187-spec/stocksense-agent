## 2026-02-24 - Path Traversal in StockSenseAgent
**Vulnerability:** Path Traversal in `scan_inventory` and `save_recommendations` allowed arbitrary file read/write.
**Learning:** Python's `os.path.commonpath` can behave differently on different OSes (Windows vs Linux). Specifically, on Windows it raises `ValueError` if paths are on different drives, but on Linux it simply returns the common path prefix.  Validating paths by catching `ValueError` from `commonpath` is insufficient on Linux; one must explicitly compare the return value against the allowed directory.
**Prevention:** Use `os.path.realpath` to resolve all paths to absolute paths, and then use `os.path.commonpath` to verify containment, explicitly checking the result.
