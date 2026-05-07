import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import requests
import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# ===============================
# 🔁 AUTO REFRESH (LIVE UPDATE)
# ===============================
st_autorefresh(interval=5000, key="refresh")  # refresh every 5 seconds

# ===============================
# 🎨 DARK MODE STYLE
# ===============================
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# 🔥 SIDEBAR
# ===============================
st.sidebar.title("TradeScope AI")
page = st.sidebar.radio("Navigate", ["Home", "Dashboard"])

# ===============================
# 🏠 HOME PAGE
# ===============================
if page == "Home":

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("tradescope_ai_logo.svg", use_container_width=True)

    st.markdown("<h3 style='text-align: center;'>AI-Powered Crypto Trading Intelligence</h3>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        "<p style='text-align: center; font-size:18px;'>"
        "Analyze markets. Track performance. Make smarter decisions."
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align: center; color: gray; font-size:14px;'>"
        "“I can do all things through Christ who strengthens me.” — Philippians 4:13"
        "</p>",
        unsafe_allow_html=True
    )

# ===============================
# 📊 DASHBOARD
# ===============================
elif page == "Dashboard":

    st.title("📊 Trading Dashboard")

    selected_asset = st.selectbox(
        "Select Asset",
        ["ETH-USD", "BTC-USD", "SOL-USD", "ADA-USD"]
    )

    # ===============================
    # 🔴 LIVE BINANCE PRICE
    # ===============================
    symbol_map = {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "ADA-USD": "ADAUSDT"
    }

    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_map[selected_asset]}"
        response = requests.get(url)
        live_price = float(response.json()["price"])
        st.metric("💰 Live Price (Binance)", f"${live_price:,.2f}")
    except:
        st.warning("Live price unavailable")

    # ===============================
    # 📂 LOAD DATA
    # ===============================
    data_file = selected_asset.lower().replace("-", "_") + "_data.json"
    decision_file = selected_asset.lower().replace("-", "_") + "_decisions.json"

    try:
        with open(data_file, "r") as f:
            data = json.load(f)
    except:
        data = []

    try:
        with open(decision_file, "r") as f:
            decisions = json.load(f)
    except:
        decisions = []

    balance = 1000
    position = 0
    last_buy_price = 0
    wins = 0
    losses = 0

    buy_x, buy_y = [], []
    sell_x, sell_y = [], []

    # ===============================
    # 🔁 PROCESS TRADES (FIXED)
    # ===============================
    for i in range(min(len(data), len(decisions))):

        price = data[i]["close"]

        # ✅ FIX 1: SAFE NORMALIZATION
        decision = str(decisions[i].get("decision", "")).strip().upper()

        # ✅ FIX 2: SAFE CONVERSION
        try:
            confidence = float(decisions[i].get("confidence", 0))
        except:
            confidence = 0.0

        # ❌ FILTER DISABLED (was causing 0 win rate)
        # if confidence < 0.6:
        #     continue

        if position == 0 and decision == "BUY":
            position = balance / price
            last_buy_price = price
            buy_x.append(i)
            buy_y.append(price)

        elif position > 0 and decision == "SELL":

            if price > last_buy_price:
                wins += 1
            else:
                losses += 1

            balance = position * price
            position = 0
            sell_x.append(i)
            sell_y.append(price)

    if data:
        final_value = balance if position == 0 else balance + (position * data[-1]["close"])
    else:
        final_value = balance

    profit = final_value - 1000

    # ===============================
    # 📊 CHART
    # ===============================
    if data:
        df = pd.DataFrame(data)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            df["timestamp"] = pd.date_range(start="2024-01-01", periods=len(df), freq="H")

        df["MA_5"] = df["close"].rolling(5).mean()
        df = df.dropna().reset_index(drop=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["MA_5"],
            mode="lines",
            name="MA 5"
        ))

        fig.add_trace(go.Scatter(
            x=[df["timestamp"].iloc[i] for i in buy_x if i < len(df)],
            y=buy_y,
            mode="markers",
            marker=dict(size=12, symbol="triangle-up"),
            name="BUY"
        ))

        fig.add_trace(go.Scatter(
            x=[df["timestamp"].iloc[i] for i in sell_x if i < len(df)],
            y=sell_y,
            mode="markers",
            marker=dict(size=12, symbol="triangle-down"),
            name="SELL"
        ))

        st.subheader(f"📊 {selected_asset} Chart")
        st.plotly_chart(fig, use_container_width=True)

        last_price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-2]

        if last_price > prev_price:
            st.success("🟢 Market Trending Up")
        else:
            st.error("🔴 Market Trending Down")

    # ===============================
    # 🤖 AI DECISION
    # ===============================
    st.subheader("🤖 Latest AI Decision")

    if decisions:
        latest = decisions[-1]

        decision = str(latest.get("decision", "")).upper()
        confidence = float(latest.get("confidence", 0))

        if decision == "BUY":
            st.success(f"BUY 🚀 (Confidence: {confidence:.2f})")
        elif decision == "SELL":
            st.error(f"SELL ⚠️ (Confidence: {confidence:.2f})")
        else:
            st.info("HOLD 🤝")

        st.subheader("🧠 AI Explanation")

        if decision == "BUY":
            st.write("The AI detected upward momentum and strong probability of price increase.")
        elif decision == "SELL":
            st.write("The AI detected potential reversal or downward pressure.")
        else:
            st.write("The AI is uncertain and waiting for clearer signals.")

    # ===============================
    # 💰 PERFORMANCE
    # ===============================
    st.subheader("💰 Performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Balance", f"${final_value:.2f}")
    col2.metric("Profit", f"${profit:.2f}")

    win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
    col3.metric("Win Rate", f"{win_rate:.2f}%")

    st.caption(f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")

    # ===============================
    # 📜 HISTORY
    # ===============================
    st.subheader("📜 Decision History")
    st.write(decisions)
