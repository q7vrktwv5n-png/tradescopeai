import yfinance as yf
import json
import time
import os

# 🔥 MULTI-CRYPTO LIST
symbols = ["ETH-USD", "BTC-USD", "SOL-USD", "ADA-USD"]

def fetch_data(symbol):
    print(f"\n📊 Fetching data for {symbol}...")

    data = yf.download(symbol, period="1d", interval="5m")

    # Fix multi-index columns (sometimes yfinance does this)
    if isinstance(data.columns, type(data.columns)):
        try:
            data.columns = data.columns.get_level_values(0)
        except:
            pass

    latest = data.iloc[-1]

    candle = {
        "timestamp": str(data.index[-1]),
        "open": float(latest["Open"]),
        "high": float(latest["High"]),
        "low": float(latest["Low"]),
        "close": float(latest["Close"]),
        "volume": float(latest["Volume"])
    }

    # 🔥 Dynamic file name per coin
    file_name = symbol.lower().replace("-", "_") + "_data.json"

    # Load existing data
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            dataset = json.load(f)
    else:
        dataset = []

    dataset.append(candle)

    # Keep only last 20 candles
    if len(dataset) > 20:
        dataset.pop(0)

    # Save back
    with open(file_name, "w") as f:
        json.dump(dataset, f, indent=4)

    print(f"✅ Saved {file_name}")


print("🚀 Multi-Crypto Data Collector Running...")

while True:
    for symbol in symbols:
        try:
            fetch_data(symbol)
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

    print("\n⏳ Waiting 5 minutes for next update...\n")
    time.sleep(300)
