from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import yfinance as yf
from typing import Dict, Any
from redis import asyncio as aioredis

app = FastAPI(title="StockPulse")

# Initialize cache on startup
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="stockpulse-cache")

async def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
            
        latest_price = data['Close'].iloc[-1]
        latest_volume = data['Volume'].iloc[-1]
        previous_close = data['Open'].iloc[0]
        percent_change = ((latest_price - previous_close) / previous_close) * 100

        return {
            "symbol": symbol,
            "price": round(latest_price, 2),
            "change": round(percent_change, 2),
            "volume": int(latest_volume)
        }
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Error fetching stock {symbol}: {str(e)}"
        )

@app.get("/stock/{symbol}")
@cache(expire=30)  # Cache results for 30 seconds
async def get_stock(symbol: str):
    return await fetch_stock_data(symbol)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}