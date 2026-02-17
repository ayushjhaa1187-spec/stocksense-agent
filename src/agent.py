"""
StockSense Agent - Autonomous pharmacy inventory manager
Powered by Fetch.ai uAgents
"""

from datetime import datetime, timedelta
import json
import pandas as pd
import os
from dotenv import load_dotenv

class MedicineRecord:
    def __init__(self, name, stock, expiry_date, daily_sales):
        self.name = name
        self.stock = stock
        self.expiry_date = expiry_date
        self.daily_sales = daily_sales
    
    def days_until_expiry(self):
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
        return (expiry - datetime.now()).days
    
    def predicted_sales_before_expiry(self):
        return self.daily_sales * max(0, self.days_until_expiry())

class StockSenseAgent:
    def __init__(self):
        load_dotenv()
        self.name = "stocksense_agent"
        self.logger_prefix = "[StockSense Agent]"
    
    def scan_inventory(self, inventory_file=None):
        """Main agent cycle: scan inventory and generate recommendations"""
        if inventory_file is None:
            inventory_file = os.getenv("INVENTORY_FILE", "data/sample_inventory.csv")
        
        print(f"{self.logger_prefix} Starting inventory scan...")
        
        try:
            inventory = pd.read_csv(inventory_file)
        except FileNotFoundError:
            print(f"{self.logger_prefix} ERROR: Could not load inventory data from {inventory_file}")
            return None
        
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "expiry_alerts": [],
            "discount_recommendations": [],
            "restock_orders": []
        }
        
        # Analyze each medicine
        for _, medicine in inventory.iterrows():
            medicine_obj = MedicineRecord(
                name=medicine['name'],
                stock=medicine['stock'],
                expiry_date=medicine['expiry_date'],
                daily_sales=medicine['daily_sales']
            )
            
            days_left = medicine_obj.days_until_expiry()
            
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
                predicted_sales = medicine_obj.predicted_sales_before_expiry()
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
    
    def save_recommendations(self, recommendations, output_file=None):
        """Save agent recommendations to file"""
        if output_file is None:
            output_file = os.getenv("OUTPUT_FILE", "output/recommendations.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(recommendations, f, indent=2)
        print(f"{self.logger_prefix} Recommendations saved to {output_file}")

if __name__ == "__main__":
    agent = StockSenseAgent()
    recommendations = agent.scan_inventory()
    if recommendations:
        agent.save_recommendations(recommendations)
