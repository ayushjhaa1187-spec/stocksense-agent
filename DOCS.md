# StockSense Agent

An autonomous AI agent that predicts medicine expiry and auto-generates restocking orders for independent pharmacies.

## Problem

Independent pharmacies waste **₹20-30K monthly** on expired medicines. Pharmacy owners spend **4-6 hours/month** manually auditing inventory. Risk of accidentally selling expired drugs.

## Solution

**StockSense Agent** is an autonomous AI agent that:
- 24/7 Monitoring — Continuously scans inventory for expiring medicines
- Demand Prediction — Analyzes sales velocity to predict future stock movement
- Smart Discounting — Recommends optimal discounts to clear near-expiry items
- Auto-Restocking — Generates precise purchase orders based on real demand
- Agentverse Integration — Coordinates with other pharmacy agents for bulk supplier pricing

## Performance

StockSense Agent is optimized for real-world pharmacy inventory sizes:

- ⚡ **10x faster** inventory scanning (vectorized operations)
- 📊 Handles 1,000+ SKUs in ~50ms
- 🔄 Efficient 4-hour monitoring cycles with minimal overhead
- 🎯 Production-ready for large pharmacy chains

See [PERFORMANCE.md](PERFORMANCE.md) for detailed optimization report and benchmarks.

## Quick Start

### Prerequisites
- Python 3.9+
- pip
- Git

### Installation

```bash
git clone https://github.com/ayushjhaa1187-spec/stocksense-agent.git
cd stocksense-agent
pip install -r requirements.txt
```

### Run the Agent

```bash
python src/agent.py
```

Expected output:
```
[14:32:00] Agent initialized. Starting inventory scan...
[14:32:05] Found 5 medicines expiring in 30 days
[14:32:10] Calculated discount recommendations
[14:32:15] Generated 3 restocking orders
[14:32:20] Agent cycle complete. Next run: 14:35:00
```

### Run the Dashboard

```bash
python app/dashboard.py
```

Then open: http://localhost:5000

### Run Performance Benchmark

```bash
python scripts/benchmark.py
```

Benchmarks inventory scanning performance across different dataset sizes (100 to 10,000 items).

## Project Structure

```
stocksense-agent/
├── src/
│   ├── agent.py                 # Main Fetch.ai uAgent (optimized)
│   ├── data_processor.py        # Sales velocity & expiry prediction
│   ├── discount_optimizer.py    # Pricing logic
│   └─ scheduler.py             # 4-hour automation cycle
├── app/
│   ├── dashboard.py             # Flask web dashboard
│   ├── templates/               # HTML files
│   └─ static/                  # CSS, JS, Bootstrap
├── data/
│   ├── sample_inventory.csv     # Test pharmacy data
│   └─ sample_sales.csv         # Test sales history
├── tests/
│   ├── test_agent.py
│   ├── test_expiry_logic.py
│   ├── test_discount_calc.py
│   └─ test_perf_regression.py  # Performance regression tests
├── scripts/
│   └─ benchmark.py             # Performance benchmarking
├── docs/
│   ├── ARCHITECTURE.md          # Agent design docs
│   ├── API_DOCS.md              # REST endpoint documentation
│   └─ DEPLOYMENT.md            # How to deploy
├── PERFORMANCE.md               # Performance optimization report
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└─ README.md                    # This file
```

## How It Works

### Agent Cycle (Every 4 Hours)

1. **Query** — Read inventory database
2. **Analyze** — Identify expiring medicines, predict sales (vectorized, 10x faster)
3. **Decide** — Calculate discounts, determine restock quantities
4. **Recommend** — Display action items to pharmacy owner
5. **Schedule** — Run again in 4 hours

### Example Recommendation

```
Medicine: Aspirin 500mg
Current Stock: 150 units
Days to Expiry: 7 days
Daily Sales: 8 units/day
Expected Sales Before Expiry: 56 units

Recommendation:
- Discount: 15% (clears ~120 units before expiry)
- Restock Order: None (stock sufficient until next month)
- Revenue Recovery: ₹2,800 (vs ₹0 if thrown away)
```

## Business Model

**Tiered Subscription:**
- **Silver** (₹1,500/month) — Expiry alerts only
- **Gold** (₹3,000/month) — + Smart restocking + demand prediction
- **Platinum** (₹5,000/month) — + Supplier negotiation + analytics dashboard

**ROI:** One saved expensive medicine per month covers entire annual cost.

## Technologies Used

- **Agent Framework:** Fetch.ai uAgents, Fetch.ai Agentverse
- **Backend:** Python 3.9+, FastAPI, Flask
- **Data Processing:** Pandas, NumPy, Scikit-learn (vectorized operations)
- **ML:** ARIMA, Linear Programming (PuLP)
- **Database:** SQLite (MVP), PostgreSQL (Production)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Deployment:** Docker, GitHub, Vercel/Heroku
- **Notifications:** SendGrid, Twilio
- **AI Thinking:** ASI: One

## Testing

```bash
# Run all tests
pytest tests/

# Run performance regression tests
pytest tests/test_perf_regression.py -v

# Run benchmark
python scripts/benchmark.py
```

## Roadmap

- [x] v1.0: Expiry monitoring + restocking recommendations
- [x] v1.1: Performance optimization (10x faster inventory scanning)
- [ ] v2.0: Supplier negotiation agents on Fetch.ai Agentverse
- [ ] v3.0: Mobile app + advanced analytics
- [ ] v4.0: Network effects (100+ pharmacies coordinating)

## License

MIT License

## Author

Ayush Jha
ayushjhaa1187@gmail.com

## Acknowledgments

- Fetch.ai for the uAgents framework
- ASI: One for strategic thinking support
- Local pharmacy owners for inspiring this solution
