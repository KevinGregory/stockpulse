import solara
import httpx
from typing import Dict
import asyncio

"""To run, run 
`poetry run uvicorn stockpulse.api.routes:app --reload in terminal 1
`poetry run solara run stockpulse.frontend.app:Page in terminal 2"""

@solara.component
def StockCard(symbol: str, data: dict | None, on_remove=None):
    """A component for displaying a single stock card with enhanced visuals"""
    card_style = "min-width: 250px; padding: 1rem;"
    
    def get_change_color(change: float) -> str:
        return "color: #22c55e;" if change >= 0 else "color: #ef4444;"
    
    with solara.Card(f"{symbol} Stock", style=card_style):
        if data is None:
            with solara.Column(align="center"):
                solara.Text("Loading...")
        
        elif "error" in data:
            with solara.Column(gap="0.5rem", align="center"):
                solara.Text("Error: Invalid Symbol", style="color: #ef4444;")
                solara.Button(
                    "Remove", 
                    on_click=lambda: on_remove(symbol),
                    style="background-color: #fee2e2; color: #ef4444;"
                )
        
        else:
            try:
                with solara.Column(gap="1rem"):
                    # Symbol and Price
                    with solara.Row(gap="1rem"):  # Removed justify
                        solara.Text(symbol, style="font-size: 1.5rem; font-weight: bold;")
                        # Add a spacer
                        solara.Text("", style="flex-grow: 1;")
                        solara.Text(
                            f"${data['price']:,.2f}", 
                            style="font-size: 1.5rem; font-weight: bold;"
                        )
                    
                    # Change percentage
                    change_style = get_change_color(data['change'])
                    with solara.Column(align="center"):  # Changed to Column
                        solara.Text(
                            f"{'↑' if data['change'] >= 0 else '↓'} {abs(data['change']):.2f}%",
                            style=f"font-weight: bold; {change_style}"
                        )
                    
                    # Volume with label
                    with solara.Row(gap="1rem"):  # Removed justify
                        solara.Text("Volume:", style="color: #6b7280;")
                        solara.Text("", style="flex-grow: 1;")  # Spacer
                        solara.Text(f"{data['volume']:,}")
                    
                    # Bottom buttons
                    with solara.Row(gap="1rem"):  # Removed justify and align
                        solara.Button(
                            "Details",
                            on_click=lambda: None,
                            style="background-color: #e0f2fe; color: #0284c7;"
                        )
                        solara.Text("", style="flex-grow: 1;")  # Spacer
                        solara.Button(
                            "Remove",
                            on_click=lambda: on_remove(symbol),
                            style="background-color: #fee2e2; color: #ef4444;"
                        )
            except Exception as e:
                with solara.Column(gap="0.5rem", align="center"):
                    solara.Text(f"Error displaying {symbol}", style="color: #ef4444;")
                    solara.Text(str(e), style="font-size: 0.8rem; color: #6b7280;")
                    solara.Button(
                        "Remove", 
                        on_click=lambda: on_remove(symbol),
                        style="background-color: #fee2e2; color: #ef4444;"
                    )
                    
                    
                    
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