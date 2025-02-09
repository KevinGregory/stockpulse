import solara
import httpx
from typing import Dict

@solara.component
def StockDisplay():
    # State to store our stock data
    stock_data = solara.use_state(None)
    
    @solara.memoize
    async def fetch_stock():
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/stock/AAPL")
            if response.status_code == 200:
                stock_data.set(response.json())

    # Fetch data when component mounts and every 5 seconds after
    solara.use_interval(fetch_stock, 5000)  

    with solara.Column(align="center", gap="2rem"):
        solara.Title("StockPulse Dashboard")
        
        if stock_data.value is None:
            solara.Text("Loading...")
        else:
            with solara.Card("Apple Stock"):
                solara.Markdown(f"""
                    **Price:** ${stock_data.value['price']}  
                    **Change:** {stock_data.value['change']}%  
                    **Volume:** {stock_data.value['volume']:,}
                """)

# This is important - make sure this is defined at the module level
@solara.component
def Page():
    return StockDisplay()