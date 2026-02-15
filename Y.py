import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="PRO Stock Screener", layout="wide")

st.title("📊 PRO MA20/MA200 + RSI Screener")

# =============================
# INPUT
# =============================
default_tickers = "BBRI.JK,BBCA.JK,BMRI.JK,ADRO.JK,PTBA.JK,TLKM.JK,ASII.JK,UNTR.JK,ITMG.JK"
ticker_input = st.text_area("Masukkan List Saham (pisahkan koma):", default_tickers)

tickers = [x.strip().upper() for x in ticker_input.split(",") if x.strip()]

only_yes = st.checkbox("Tampilkan hanya yang Above MA20 & MA200 (YES)")
min_volume = st.number_input("Minimum Volume (harian)", value=0)
sort_by = st.selectbox("Sort By", ["Trend Strength", "RSI", "Volume", "Last Price"])
page_size = 50

# =============================
# CACHE DATA
# =============================
@st.cache_data(ttl=600)
def fetch_data(tickers):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=400)

    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        group_by='ticker',
        auto_adjust=True,
        threads=True
    )
    return data

# =============================
# RSI FUNCTION
# =============================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# =============================
# MAIN SCAN
# =============================
if st.button("🚀 Scan Market"):

    with st.spinner("Mengambil data pasar..."):
        data = fetch_data(tickers)

    results = []

    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 200:
                continue

            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA200"] = df["Close"].rolling(200).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            last = df.iloc[-1]

            trend_strength = (last["Close"] / last["MA200"]) - 1

            status = "YES" if last["Close"] > last["MA20"] and last["Close"] > last["MA200"] else "NO"

            if last["Volume"] < min_volume:
                continue

            results.append({
                "Ticker": ticker,
                "Last Price": round(last["Close"], 2),
                "MA20": round(last["MA20"], 2),
                "MA200": round(last["MA200"], 2),
                "RSI": round(last["RSI"], 2),
                "Volume": int(last["Volume"]),
                "Trend Strength": round(trend_strength, 4),
                "Above MA20 & MA200": status
            })

        except:
            continue

    df_result = pd.DataFrame(results)

    if df_result.empty:
        st.warning("Tidak ada data valid.")
    else:

        if only_yes:
            df_result = df_result[df_result["Above MA20 & MA200"] == "YES"]

        df_result = df_result.sort_values(by=sort_by, ascending=False)

        # =============================
        # PAGINATION
        # =============================
        total_pages = int(np.ceil(len(df_result) / page_size))
        page = st.number_input("Page", min_value=1, max_value=max(total_pages,1), value=1)

        start = (page - 1) * page_size
        end = start + page_size

        st.write(f"Menampilkan {start+1} - {min(end,len(df_result))} dari {len(df_result)} saham")
        st.dataframe(df_result.iloc[start:end], use_container_width=True)
