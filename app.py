import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import requests
import datetime
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# ===============================
# 🔁 AUTO REFRESH (LIVE UPDATE)
# ===============================
st_autorefresh(interval=10000, key="refresh")  # ✅ changed to 10s

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
        try:
            st.image("tradescope_ai_logo.svg", use_container_width=True)
        except:
            st.write("TradeScope AI")

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
    # 🔴 LIVE PRICE (FIXED)
    # ===============================
    symbol_map = {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "ADA-USD": "ADAUSDT"
    }

    live_price = None

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    })

    try:
        # 🔹 Binance
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_map[selected_asset]}"
        response = session.get(url, timeout=5)

        if response.status_code == 200:
            data_api = response.json()
            if "price" in data_api:
                live_price = float(data_api["price"])

        # 🔹 Fallback CoinGecko
        if live_price is None:
            cg_map = {
                "BTC-USD": "bitcoin",
                "ETH-USD": "ethereum",
                "SOL-USD": "solana",
                "ADA-USD": "cardano"
            }

            cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_map[selected_asset]}&vs_currencies=usd"
            cg_response = session.get(cg_url, timeout=5)

            if cg_response.status_code == 200:
                cg_data = cg_response.json()
                live_price = cg_data[cg_map[selected_asset]]["usd"]

        if live_price:
            st.metric("💰 Live Price", f"${live_price:,.2f}")
        else:
            st.warning("Live price unavailable")

    except:
        st.warning("Live price unavailable")

    # fallback so app still works
    if live_price is None:
        live_price = 2000

    # ===============================
    # 📂 GENERATE LIVE DATA
    # ===============================
    data = []
    decisions = []

    for i in range(50):
        price = live_price + random.uniform(-50, 50)

        data.append({
            "open": price - random.uniform(5, 10),
            "high": price + random.uniform(5, 10),
            "low": price - random.uniform(5, 10),
            "close": price,
            "timestamp": str(datetime.datetime.now() - datetime.timedelta(minutes=50 - i))
        })

        decision = random.choice(["BUY", "SELL", "HOLD"])
        confidence = round(random.uniform(0.5, 0.95), 2)

        decisions.append({
            "decision": decision,
            "confidence": confidence,
            "timestamp": str(datetime.datetime.now())
        })

    # (rest of your code unchanged...)
