from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from dotenv import load_dotenv

from client import BinanceTestClient
from models import AccountInfo, OrderRequest, AssetBalance


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = BinanceTestClient(api_key, api_secret)


@app.get("/api/health")
async def health():
    return {"message": "OK"}

@app.get("/api/account")
async def get_account() -> AccountInfo:
    try:
        data = client.get_account_info()
        balances = {b['asset']: b for b in data['balances']}
        return AccountInfo(
            account_type=data["accountType"],
            btc_balance=AssetBalance(asset="BTC", balance=balances.get("BTC", {"free": "0"})["free"]),
            usdt_balance=AssetBalance(asset="USDT", balance=balances.get("USDT", {"free": "0"})["free"]),
            eth_balance=AssetBalance(asset="ETH", balance=balances.get("ETH", {"free": "0"})["free"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price")
async def get_price(symbol: str):
    try:
        data = client.get_price(symbol)
        return {"symbol": data["symbol"], "price": data["price"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/price-history")
async def get_price_history(symbol: str, interval: str = '1h'):
    try:
        raw_data = client.get_candlesticks(symbol, interval)
        return [
            {
                "open_time": c[0],
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
                "close_time": c[6],
                "quote_asset_volume": float(c[7]),
                "number_of_trades": c[8],
                "taker_buy_base_asset_volume": float(c[9]),
                "taker_buy_quote_asset_volume": float(c[10]),
                "ignore": c[11]
            } for c in raw_data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/order")
async def create_order(order: OrderRequest):
    try:
        data = client.create_order(order.dict())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
