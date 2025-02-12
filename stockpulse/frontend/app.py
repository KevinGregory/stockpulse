import solara
import httpx
from typing import Dict
import asyncio

"""To run, run 
`poetry run uvicorn stockpulse.api.routes:app --reload in terminal 1
`poetry run solara run stockpulse.frontend.app:Page in terminal 2"""


@solara.component
def StockCard(symbol: str, data: dict | None, on_remove=None):
    """A component for displaying a single stock card"""
    with solara.Card(f"{symbol} Stock"):
        if data is None:
            solara.Text("Loading...")
        elif "error" in data:
            with solara.Column(gap="0.5rem"):
                solara.Text("Error: Invalid Symbol", style="color: red")
                solara.Button("Remove", on_click=lambda: on_remove(symbol))
        else:
            solara.Markdown(f"""
                **Price:** ${data['price']}  
                **Change:** {data['change']}%  
                **Volume:** {data['volume']:,}
            """)
            
@solara.component
def StockDisplay():
    symbols, set_symbols = solara.use_state(["AAPL"])
    stocks_data, set_stocks_data = solara.use_state({})
    new_symbol, set_new_symbol = solara.use_state("")
    
    async def fetch_data():
        async with httpx.AsyncClient() as client:
            for symbol in symbols:
                try:
                    response = await client.get(f"http://localhost:8000/stock/{symbol}")
                    new_data = dict(stocks_data)
                    if response.status_code == 200:
                        new_data[symbol] = response.json()
                    else:
                        new_data[symbol] = {"error": response.json()["detail"]}
                    set_stocks_data(new_data)
                except Exception as e:
                    new_data = dict(stocks_data)
                    new_data[symbol] = {"error": str(e)}
                    set_stocks_data(new_data)

    def remove_symbol(symbol: str):
        set_symbols([s for s in symbols if s != symbol])
        new_data = dict(stocks_data)
        if symbol in new_data:
            del new_data[symbol]
        set_stocks_data(new_data)

    def start_fetching():
        # Create a task that we can cancel
        should_run = True
        
        async def periodic_fetch():
            while should_run:
                try:
                    await fetch_data()
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"Error in periodic fetch: {str(e)}")
                    await asyncio.sleep(5)  # Still wait before retrying
        
        task = asyncio.create_task(periodic_fetch())
        
        # Return cleanup function
        def cleanup():
            nonlocal should_run
            should_run = False
            task.cancel()
        
        return cleanup

    solara.use_effect(start_fetching)

    def add_symbol(*_):
        if new_symbol and new_symbol not in symbols:
            set_symbols([*symbols, new_symbol.upper()])
            set_new_symbol("")

    with solara.Column(align="center", gap="2rem"):
        solara.Title("StockPulse Dashboard")
        
        with solara.Row(gap="1rem"):
            solara.InputText(
                label="Add Stock Symbol",
                value=new_symbol,
                on_value=set_new_symbol
            )
            solara.Button("Add", on_click=add_symbol)
        
        with solara.Column(gap="1rem"):
            for i in range(0, len(symbols), 3):
                with solara.Row(gap="1rem"):
                    for symbol in symbols[i:i+3]:
                        StockCard(symbol, stocks_data.get(symbol), remove_symbol)

@solara.component
def Page():
    return StockDisplay()