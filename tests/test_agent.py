import sys
from unittest.mock import MagicMock

# Mock pandas before importing src.agent
mock_pd = MagicMock()
sys.modules["pandas"] = mock_pd

from src.agent import StockSenseAgent, MedicineRecord

def test_agent_initialization():
    """Test that StockSenseAgent initializes with correct default values."""
    agent = StockSenseAgent()
    assert agent.name == "stocksense_agent"
    assert agent.logger_prefix == "[StockSense Agent]"

def test_medicine_record_initialization():
    """Test that MedicineRecord initializes with correct attributes."""
    name = "Paracetamol"
    stock = 100
    expiry_date = "2026-12-31"
    daily_sales = 5

    medicine = MedicineRecord(name, stock, expiry_date, daily_sales)

    assert medicine.name == name
    assert medicine.stock == stock
    assert medicine.expiry_date == expiry_date
    assert medicine.daily_sales == daily_sales
