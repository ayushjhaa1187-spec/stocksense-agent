## 2024-05-23 - Path Traversal in Agent File Operations
**Vulnerability:** The `StockSenseAgent` accepted arbitrary file paths for `inventory_file` and `output_file`, allowing an attacker to read from or write to any location on the filesystem accessible by the process (Path Traversal).
**Learning:** File operations in autonomous agents often default to "trusted" inputs, but if these inputs can be influenced by external configurations or users, strict path validation is mandatory to enforce sandboxing.
**Prevention:** Implement a helper method like `_validate_path` that resolves absolute paths and uses `os.path.commonpath` to ensure the target file resides strictly within an allowed directory (e.g., `data/` or `output/`).
