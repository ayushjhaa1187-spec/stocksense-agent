# StockSense Agent 💊🤖

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Fetch.ai](https://img.shields.io/badge/Fetch.ai-uAgents-purple.svg)
![Status](https://img.shields.io/badge/status-Production--Ready-success.svg)

## Short Description

**StockSense Agent** is an autonomous AI agent powered by Fetch.ai that continuously monitors pharmacy inventory to predict medicine expiry and auto-generate precise restocking orders. It eliminates manual auditing and helps independent pharmacies save ₹20-30K monthly by preventing expired stock wastage.

---

## Demo / Screenshot

*(Placeholder: Add a screenshot of the web dashboard or CLI output here)*

![StockSense Dashboard Preview](https://via.placeholder.com/800x400?text=StockSense+Dashboard+Preview)

---

## Features

- **24/7 Autonomous Monitoring:** Continuously scans inventory for expiring medicines without manual intervention.
- **Demand Prediction:** Analyzes sales velocity and historical data to predict future stock movement and demand.
- **Smart Discounting:** Recommends optimal pricing discounts to clear near-expiry items before they become a total loss.
- **Auto-Restocking:** Generates precise purchase orders based on real demand and stock thresholds.
- **High Performance:** Optimized vectorized scanning handles 1,000+ SKUs in ~50ms (10x faster than traditional row-by-row processing).
- **Agentverse Integration:** Designed to coordinate with other pharmacy agents for bulk supplier pricing negotiation.

---

## Tech Stack

- **Agent Framework:** Fetch.ai uAgents, Fetch.ai Agentverse
- **Language:** Python 3.9+
- **Backend APIs:** FastAPI, Flask
- **Data Processing:** Pandas, NumPy
- **Machine Learning / Optimization:** Scikit-learn, Statsmodels (ARIMA), PuLP (Linear Programming)
- **Database:** SQLAlchemy, PostgreSQL (Production ready), SQLite (MVP)
- **Scheduling:** APScheduler
- **Notifications:** SendGrid, Twilio
- **Frontend / Dashboard:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js

---

## Project Structure

```text
stocksense-agent/
├── src/
│   ├── agent.py                 # Main Fetch.ai uAgent logic (optimized)
│   ├── data_processor.py        # Sales velocity & expiry prediction models
│   ├── discount_optimizer.py    # Pricing and discount logic
│   └── scheduler.py             # 4-hour automation cycle scheduling
├── app/
│   ├── dashboard.py             # Flask web dashboard application
│   ├── templates/               # HTML templates for the dashboard
│   └── static/                  # CSS, JS, and Bootstrap assets
├── data/
│   ├── sample_inventory.csv     # Test pharmacy inventory dataset
│   └── sample_sales.csv         # Test sales history dataset
├── tests/
│   ├── test_agent.py            # Unit tests for the main agent
│   ├── test_expiry_logic.py     # Tests for expiry calculations
│   ├── test_discount_calc.py    # Tests for discount optimization
│   └── test_perf_regression.py  # Performance regression checks
├── scripts/
│   └── benchmark.py             # Performance benchmarking utilities
├── docs/                        # Architecture and deployment documentation
├── PERFORMANCE.md               # Detailed performance optimization report
├── requirements.txt             # Project Python dependencies
└── README.md                    # This documentation file
```

---

## Prerequisites

Before setting up the StockSense Agent, ensure you have the following installed:

- **Python 3.9** or higher
- **pip** (Python package installer)
- **Git**

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayushjhaa1187-spec/stocksense-agent.git
   cd stocksense-agent
   ```

2. **Create and activate a virtual environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Copy the example environment file and configure your API keys (SendGrid, Twilio, etc.):
   ```bash
   cp .env.example .env
   ```
   *(Edit `.env` with your actual credentials)*

---

## Usage

### 1. Run the Autonomous Agent

Start the background agent to monitor inventory and generate recommendations. The agent runs on a 4-hour cycle by default.

```bash
python src/agent.py
```

**Expected Output:**
```text
[StockSense Agent] Starting inventory scan...
[StockSense Agent] ALERT: Aspirin 500mg expires in 7 days
[StockSense Agent] RECOMMEND: 15% discount on Aspirin 500mg
[StockSense Agent] ORDER: Restock Paracetamol
[StockSense Agent] Scan complete!
[StockSense Agent] - Expiry alerts: 5
[StockSense Agent] - Discount recommendations: 2
[StockSense Agent] - Restock orders: 3
[StockSense Agent] Recommendations saved to output/recommendations.json
```

### 2. Run the Web Dashboard

Launch the web dashboard to visualize inventory health, active alerts, and generated recommendations.

```bash
python app/dashboard.py
```
Open your browser and navigate to: `http://localhost:5000`

### 3. Run Performance Benchmarks

Verify the inventory scanning performance for varying dataset sizes.

```bash
python scripts/benchmark.py
```

---

## Environment Variables

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `INVENTORY_FILE` | Path to the inventory CSV file | `data/sample_inventory.csv` | No |
| `FETCH_AI_WALLET_KEY` | Private key for the Fetch.ai wallet | `your_fetch_ai_private_key` | Yes (for Agentverse) |
| `SENDGRID_API_KEY` | API key for sending email alerts | `SG.xxxxxxxxxx` | No |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID for SMS alerts | `ACxxxxxxxxxx` | No |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token for SMS alerts | `xxxxxxxxxx` | No |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db` | No |

---

## Configuration

The agent's behavior can be customized by modifying the `DEFAULT_CONFIG` dictionary in `src/agent.py`, or by passing a configuration object during instantiation.

```python
DEFAULT_CONFIG = {
    "expiry_alert_days": 30,
    "critical_expiry_days": 7,
    "discount": {
        "start_days": 14,
        "max_sales_ratio": 0.5,
        "aggressive_sales_ratio": 0.3,
        "base_pct": 10,
        "aggressive_pct": 15
    },
    "restock": {
        "default_threshold": 20,
        "default_qty": 100
    }
}
```

---

## Testing

The project uses `pytest` for unit, integration, and performance regression testing.

```bash
# Run the full test suite
pytest tests/

# Run specific performance regression tests
pytest tests/test_perf_regression.py -v
```

---

## Contributing

We welcome contributions to improve StockSense Agent!

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.

Please ensure all tests pass (`pytest tests/`) before submitting your PR.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- **Fetch.ai:** For providing the powerful uAgents framework.
- **ASI: One:** For strategic thinking support.
- Local pharmacy owners whose real-world challenges inspired this solution.
