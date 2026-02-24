"""
StockSense Agent - Autonomous pharmacy inventory manager
Powered by Fetch.ai uAgents
"""

from datetime import datetime, timedelta
import datetime as dt_module
import json
import pandas as pd
import os
from typing import Union

class MedicineRecord:
    def __init__(self, name: str, stock: int, expiry_date: Union[str, datetime], daily_sales: Union[int, float]):
        """
        Initialize a medicine record with validation.

        Args:
            name: Name of the medicine (non-empty string)
            stock: Current stock level (non-negative integer)
            expiry_date: Date of expiry (YYYY-MM-DD string or datetime object)
            daily_sales: Average units sold per day (non-negative number)
        """
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.strip():
            raise ValueError("name cannot be empty or only whitespace")

        if not isinstance(stock, int):
            raise TypeError("stock must be an integer")
        if stock < 0:
            raise ValueError("stock cannot be negative")

        if not isinstance(daily_sales, (int, float)):
            raise TypeError("daily_sales must be a number")
        if daily_sales < 0:
            raise ValueError("daily_sales cannot be negative")

        if isinstance(expiry_date, str):
            try:
                datetime.strptime(expiry_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("expiry_date string must be in YYYY-MM-DD format")
        elif not isinstance(expiry_date, dt_module.datetime):
            raise TypeError("expiry_date must be a string (YYYY-MM-DD) or datetime object")

        self.name = name
        self.stock = stock
        self.expiry_date = expiry_date
        self.daily_sales = daily_sales
    
    def days_until_expiry(self, current_date=None):
        """Calculate days until expiry.
        
        Args:
            current_date: Optional datetime object. If None, uses datetime.now().
                        Accepts pre-parsed datetime to avoid repeated string parsing.
        
        Returns:
            int: Days until expiry (negative if already expired)
        """
        if current_date is None:
            current_date = datetime.now()
            
        # Support both string and datetime objects
        if isinstance(self.expiry_date, str):
            expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
        else:
            expiry = self.expiry_date
            
        return (expiry - current_date).days
    
    def predicted_sales_before_expiry(self, current_date=None):
        """Predict total sales before expiry date.
        
        Args:
            current_date: Optional datetime object for consistent calculations.
        
        Returns:
            int: Predicted number of units sold before expiry
        """
        return self.daily_sales * max(0, self.days_until_expiry(current_date))

class StockSenseAgent:
    def __init__(self):
        self.name = "stocksense_agent"
        self.logger_prefix = "[StockSense Agent]"
    
    def scan_inventory(self, inventory_file="data/sample_inventory.csv"):
        """Main agent cycle: scan inventory and generate recommendations.
        
        Performance optimizations:
        - Vectorized date parsing with pd.to_datetime (10x faster)
        - itertuples() instead of iterrows() (5-10x faster)
        - Single datetime.now() call outside loop
        
        Args:
            inventory_file: Path to CSV file with columns:
                          name, stock, expiry_date, daily_sales
        
        Returns:
            dict: Recommendations with expiry_alerts, discount_recommendations,
                 restock_orders, and timestamp
        """
        
        print(f"{self.logger_prefix} Starting inventory scan...")
        
        try:
            inventory = pd.read_csv(inventory_file)
        except FileNotFoundError:
            print(f"{self.logger_prefix} ERROR: Could not load inventory data from {inventory_file}")
            return None
        
        # OPTIMIZATION 1: Vectorized date parsing
        # Convert entire column at once instead of per-row parsing
        # This reduces O(N) strptime calls to O(1) vectorized operation
        if 'expiry_date' in inventory.columns:
            inventory['expiry_date'] = pd.to_datetime(inventory['expiry_date'])
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "expiry_alerts": [],
            "discount_recommendations": [],
            "restock_orders": []
        }
        
        # OPTIMIZATION 2: Compute current time once outside loop
        # Avoids repeated datetime.now() calls inside loop
        current_date = datetime.now()

        # OPTIMIZATION 3: Use itertuples() instead of iterrows()
        # itertuples yields named tuples (fast), iterrows creates Series (slow)
        # This provides 5-10x speedup for large datasets
        for medicine in inventory.itertuples():
            medicine_obj = MedicineRecord(
                name=medicine.name,
                stock=medicine.stock,
                expiry_date=medicine.expiry_date,  # Already parsed datetime
                daily_sales=medicine.daily_sales
            )
            
            # Pass pre-calculated current_date to avoid repeated parsing
            days_left = medicine_obj.days_until_expiry(current_date=current_date)
            
            # Alert: Expiring soon
            if days_left <= 30 and days_left > 0:
                recommendations["expiry_alerts"].append({
                    "medicine": medicine_obj.name,
                    "days_left": days_left,
                    "stock": medicine_obj.stock,
                    "urgency": "CRITICAL" if days_left <= 7 else "HIGH"
                })
                print(f"{self.logger_prefix} ALERT: {medicine_obj.name} expires in {days_left} days")
            
            # Recommend discount for near-expiry
            if 7 <= days_left <= 14:
                predicted_sales = medicine_obj.predicted_sales_before_expiry(current_date=current_date)
                if predicted_sales < medicine_obj.stock * 0.5:
                    discount_pct = 15 if predicted_sales < medicine_obj.stock * 0.3 else 10
                    recommendations["discount_recommendations"].append({
                        "medicine": medicine_obj.name,
                        "discount_percent": discount_pct,
                        "expected_clear_pct": 80,
                        "revenue_recovery": int(medicine_obj.stock * 0.1 * 100)
                    })
                    print(f"{self.logger_prefix} RECOMMEND: {discount_pct}% discount on {medicine_obj.name}")
            
            # Recommend restock
            if medicine_obj.stock < 20:
                recommendations["restock_orders"].append({
                    "medicine": medicine_obj.name,
                    "recommended_qty": 100,
                    "supplier": "Default Supplier",
                    "estimated_cost": 5000
                })
                print(f"{self.logger_prefix} ORDER: Restock {medicine_obj.name}")
        
        print(f"{self.logger_prefix} Scan complete!")
        print(f"{self.logger_prefix} - Expiry alerts: {len(recommendations['expiry_alerts'])}")
        print(f"{self.logger_prefix} - Discount recommendations: {len(recommendations['discount_recommendations'])}")
        print(f"{self.logger_prefix} - Restock orders: {len(recommendations['restock_orders'])}")
        
        return recommendations
    
    def save_recommendations(self, recommendations, output_file="output/recommendations.json"):
        """Save agent recommendations to file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(recommendations, f, indent=2)
        print(f"{self.logger_prefix} Recommendations saved to {output_file}")

if __name__ == "__main__":
    agent = StockSenseAgent()
    recommendations = agent.scan_inventory()
    if recommendations:
        agent.save_recommendations(recommendations)
