## 2026-02-18 - [Path Traversal in CSV Input]
**Vulnerability:** The `StockSenseAgent.scan_inventory` method accepted arbitrary file paths directly into `pd.read_csv`, allowing attackers to read sensitive system files (e.g., `/etc/passwd`) or files outside the intended `data/` directory.
**Learning:** Functions that accept file paths as input must never assume the input is safe, even if it defaults to a local file. Library functions like `pd.read_csv` perform no validation on the path's safety.
**Prevention:** Always sanitize and validate file paths using `os.path.realpath` and `os.path.commonpath` to ensure the resolved path resides within a specific, allowed directory (sandbox) before opening it.
