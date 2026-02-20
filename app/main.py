import sys
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add src to sys.path to allow importing StockSenseAgent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.agent import StockSenseAgent
except ImportError:
    # Fallback for environments where src isn't importable (though sys.path should fix it)
    print("WARNING: Could not import StockSenseAgent. Using mock data.")
    StockSenseAgent = None

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('app/static/index.html')

@app.get("/api/recommendations")
async def get_recommendations():
    if StockSenseAgent:
        try:
            agent = StockSenseAgent()
            # In a real app, we might want to cache this or run it asynchronously
            # For now, we'll scan the sample inventory
            # We need to make sure the path to inventory file is correct relative to execution
            inventory_path = os.path.join(os.path.dirname(__file__), '../data/sample_inventory.csv')
            recommendations = agent.scan_inventory(inventory_path)
            if recommendations:
                return recommendations
            else:
                return {"error": "Failed to scan inventory or file not found"}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Agent module not available"}
