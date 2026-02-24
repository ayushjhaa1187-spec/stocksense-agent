#!/usr/bin/env python3
"""Benchmark script for StockSense Agent performance testing."""

import time
import tempfile
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from agent import StockSenseAgent

def generate_test_data(n_items=1000):
    """Generate synthetic inventory data."""
    today = datetime.now()
    data = {
        'name': [f'Medicine_{i}' for i in range(n_items)],
        'expiry_date': [(today + timedelta(days=i % 365)).strftime('%Y-%m-%d') 
                        for i in range(n_items)],
        'stock': [100 + (i % 200) for i in range(n_items)],
        'daily_sales': [5 + (i % 10) for i in range(n_items)],
    }
    return pd.DataFrame(data)

def benchmark_scan_inventory(sizes=[100, 500, 1000, 5000, 10000]):
    """Run benchmark for different inventory sizes."""
    print("StockSense Agent - Inventory Scanning Benchmark")
    print("=" * 60)
    
    agent = StockSenseAgent()

    # Use secure temporary file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        for size in sizes:
            df = generate_test_data(size)
            df.to_csv(temp_file, index=False)
            
            # Warm-up run
            _ = agent.scan_inventory(temp_file)
            
            # Timed run
            start = time.perf_counter()
            result = agent.scan_inventory(temp_file)
            elapsed = (time.perf_counter() - start) * 1000  # ms
            
            # Count expiring items
            n_expiring = len(result.get('expiry_alerts', []))
            
            print(f"{size:>6} items | {elapsed:>8.2f} ms | "
                  f"{n_expiring} expiring | {elapsed/size:.3f} ms/item")
    except Exception as e:
        print(f"Benchmark failed: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("=" * 60)

if __name__ == '__main__':
    benchmark_scan_inventory()
