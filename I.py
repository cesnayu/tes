import streamlit as st
import yfinance as yf 
import pandas as pd 
import json 
import os

DATA_FILE = "stocks.json"



def load_data():
    if os.path.exists(DATA_FILE): 
    with open(DATA_FILE, "r") 
    as f: 
        return json.load(f) 
        return []

def save_data(data): 
with open(DATA_FILE, "w") 
as f: json.dump(data, f)

def get_stock_data(ticker): stock = yf.Ticker(ticker) info = stock.history(period="2d")

if len(info) < 2:
    return None

current_price = info["Close"].iloc[-1]
prev_close = info["Close"].iloc[-2]
daily_return = ((current_price - prev_close) / prev_close) * 100

return current_price, daily_return

---------- UI ----------

st.set_page_config(page_title="Stock Target Dashboard", layout="wide")

st.title("📈 Stock Target Dashboard (Yahoo Finance)")

Load saved stocks

stocks = load_data()

---------- Add Stock ----------

st.subheader("➕ Add / Update Stock") col1, col2 = st.columns(2)

with col1: ticker_input = st.text_input("Ticker (e.g., AAPL, BBCA.JK)")

with col2: target_price_input = st.number_input("Target Price", min_value=0.0, step=0.1)

if st.button("Save Stock"):
    if ticker_input: updated = False 
        for s in stocks: 
if s["ticker"].upper() == ticker_input.upper(): s["target"] = target_price_input updated = True
if not updated: stocks.append({"ticker": ticker_input.upper(), "target": target_price_input}) save_data(stocks) st.success("Saved!")

---------- Display Dashboard ----------

st.subheader("📊 Your Portfolio")

if stocks: table_data = []

for s in stocks:
    data = get_stock_data(s["ticker"])
    if data:
        current_price, daily_return = data
        target_price = s["target"]

        diff_percent = ((target_price - current_price) / current_price) * 100

        table_data.append({
            "Ticker": s["ticker"],
            "Current Price": round(current_price, 2),
            "Target Price": target_price,
            "% to Target": round(diff_percent, 2),
            "Daily Return %": round(daily_return, 2)
        })

df = pd.DataFrame(table_data)

st.dataframe(df, use_container_width=True)

# ---------- Highlight ----------
st.subheader("🔥 Insights")
if not df.empty:
    best = df.loc[df["% to Target"].idxmax()]
    worst = df.loc[df["Daily Return %"].idxmin()]

    st.write(f"🚀 Most Upside: {best['Ticker']} ({best['% to Target']}%)")
    st.write(f"📉 Worst Today: {worst['Ticker']} ({worst['Daily Return %']}%)")

else: st.info("No stocks added yet.")

---------- Delete ----------

st.subheader("❌ Remove Stock") remove_ticker = st.text_input("Ticker to remove")

if st.button("Delete"): stocks = [s for s in stocks if s["ticker"] != remove_ticker.upper()] save_data(stocks) st.success("Deleted!")
