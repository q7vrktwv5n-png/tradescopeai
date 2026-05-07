from openai import OpenAI
import time
import json
import os
from datetime import datetime

# 🔐 USE ENV VARIABLE (safer)
client = OpenAI()

symbols = ["ETH-USD", "BTC-USD", "SOL-USD", "ADA-USD"]

def analyze_market(symbol):
    data_file = symbol.lower().replace("-", "_") + "_data.json"
    decision_file = symbol.lower().replace("-", "_") + "_decisions.json"

    if not os.path.exists(data_file):
        print(f"❌ Missing {data_file}")
        return

    with open(data_file, "r") as f:
        data = json.load(f)

    if len(data) < 2:
        print(f"⏳ Not enough data for {symbol}")
        return

    latest = data[-1]

    open_price = latest["open"]
    close_price = latest["close"]
    high = latest["high"]
    low = latest["low"]
    volume = latest["volume"]

    price_change = close_price - open_price
    volatility = high - low

    candle_strength = price_change / volatility if volatility != 0 else 0

    print(f"\n📊 {symbol} Analysis")
    print("Price Change:", price_change)
    print("Volatility:", volatility)
    print("Candle Strength:", candle_strength)

    # 🔥 AI PROMPT (slightly strengthened for consistency)
    prompt = f"""
You are a professional crypto market analyst.

Analyze the following 5-minute candle data for {symbol}.

Return ONLY valid JSON.

Rules:
- decision MUST be exactly "BUY", "SELL", or "HOLD"
- confidence MUST be a float between 0 and 1
- NO extra text, ONLY JSON

{{
  "decision": "BUY or SELL or HOLD",
  "confidence": 0.0,
  "trend": "UP or DOWN or SIDEWAYS",
  "momentum": "WEAK or STRONG",
  "risk": "LOW or MEDIUM or HIGH"
}}

Data:
{data}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(result)

        # ===============================
        # ✅ FIX 1: NORMALIZE OUTPUT
        # ===============================
        decision = str(parsed["decision"]).strip().upper()

        try:
            confidence = float(parsed["confidence"])
        except:
            confidence = 0.0

        # ===============================
        # FIXED OUTPUT STRUCTURE
        # ===============================
        output = {
            "decision": decision,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

        # Load history
        if os.path.exists(decision_file):
            with open(decision_file, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(output)
        history = history[-20:]

        with open(decision_file, "w") as f:
            json.dump(history, f, indent=4)

        print(f"✅ Saved {decision_file}")

    except Exception as e:
        print(f"❌ AI Error for {symbol}: {e}")


print("🧠 Multi-Crypto AI Running...")

while True:
    for symbol in symbols:
        analyze_market(symbol)

    print("\n⏳ Waiting 5 minutes...\n")
    time.sleep(300)
