import sys
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from collections import namedtuple

# Mock pandas
mock_pandas = MagicMock()
sys.modules["pandas"] = mock_pandas

Medicine = namedtuple('Medicine', ['name', 'stock', 'expiry_date', 'daily_sales'])

N_ITEMS = 100000
SCALE = 10 # Scale up from 10k to 100k

def mock_itertuples():
    now = datetime.now()
    # 1. Critical Expiry (<= 7 days)
    for i in range(1000 * SCALE):
        yield Medicine(f"Crit_{i}", 100, now + timedelta(days=5), 10)

    # 2. High Urgency Expiry (8-30 days)
    for i in range(1000 * SCALE):
        yield Medicine(f"High_{i}", 100, now + timedelta(days=20), 10)

    # 3. Discount (7-14 days, low predicted sales)
    for i in range(1000 * SCALE):
        yield Medicine(f"Disc_{i}", 100, now + timedelta(days=10), 2)

    # 4. Restock (stock < 20)
    for i in range(1000 * SCALE):
        yield Medicine(f"Restock_{i}", 10, now + timedelta(days=100), 10)

    # 5. Normal items
    for i in range(6000 * SCALE):
        yield Medicine(f"Norm_{i}", 100, now + timedelta(days=100), 10)

mock_df = MagicMock()
mock_df.itertuples = mock_itertuples
mock_df.columns = ['name', 'stock', 'expiry_date', 'daily_sales']

mock_pandas.read_csv.return_value = mock_df
mock_pandas.to_datetime.side_effect = lambda x: x

sys.path.append('src')
from agent import StockSenseAgent

print(f"Benchmarking with {N_ITEMS} items...")

agent = StockSenseAgent()

start_time = time.time()
# Use /dev/null to measure print overhead without disk I/O cost masking it?
# Actually, we want to measure the overhead of the python print call itself + formatting.
# Writing to file includes OS calls.
agent.scan_inventory("dummy.csv")
end_time = time.time()

print(f"\nExecution time: {end_time - start_time:.4f} seconds")
