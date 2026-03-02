import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import seaborn as sns
import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===============================
# CONFIG STREAMLIT
# ===============================
st.set_page_config(
    page_title="Fundamental Stock Dashboard",
    layout="wide"
)

st.title("📊 Dashboard Analisis Fundamental Saham")

# ===============================
# CACHE SESSION + USER AGENT
# ===============================
requests_cache.install_cache("yfinance_cache", expire_after=3600)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

# ===============================
# INPUT USER
# ===============================
tickers_input = st.text_input(
    "Masukkan kode saham (pisahkan dengan koma)",
    value="ASII.JK, BBCA.JK, TLKM.JK"
)

if st.button("Analisa"):

    tickers = [ticker.strip().upper() for ticker in tickers_input.split(",")]

    data_list = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker, session=session)
            info = stock.info

            price = info.get("currentPrice", 0) or 0
            eps = info.get("trailingEps", 0) or 0
            book_value = info.get("bookValue", 0) or 0
            roe = info.get("returnOnEquity", 0) or 0
            roa = info.get("returnOnAssets", 0) or 0
            debt_to_equity = info.get("debtToEquity", 0) or 0
            revenue = info.get("totalRevenue", 0) or 0
            shares = info.get("sharesOutstanding", 0) or 0

            # ===============================
            # HITUNG METRIK
            # ===============================
            per = price / eps if eps != 0 else 0
            pbv = price / book_value if book_value != 0 else 0
            rps = revenue / shares if shares != 0 else 0
            earning_yield = (eps / price) * 100 if price != 0 else 0

            data_list.append({
                "Ticker": ticker,
                "EPS": eps,
                "PER": per,
                "PBV": pbv,
                "ROE (%)": roe * 100,
                "ROA (%)": roa * 100,
                "DER": debt_to_equity,
                "RPS": rps,
                "Earning Yield (%)": earning_yield
            })

        except Exception:
            st.warning(f"⚠️ Data {ticker} gagal diambil. Diisi default 0.")
            data_list.append({
                "Ticker": ticker,
                "EPS": 0,
                "PER": 0,
                "PBV": 0,
                "ROE (%)": 0,
                "ROA (%)": 0,
                "DER": 0,
                "RPS": 0,
                "Earning Yield (%)": 0
            })

    df = pd.DataFrame(data_list)

    # ===============================
    # TABEL RINGKASAN
    # ===============================
    st.subheader("📋 Ringkasan Fundamental")
    st.dataframe(df, use_container_width=True)

    # ===============================
    # VISUAL STYLE
    # ===============================
    sns.set_style("whitegrid")

    metrics = [
        "EPS",
        "PER",
        "PBV",
        "ROE (%)",
        "ROA (%)",
        "DER",
        "RPS",
        "Earning Yield (%)"
    ]

    st.subheader("📊 Perbandingan Visual")

    cols = st.columns(2)

    for i, metric in enumerate(metrics):

        fig = px.bar(
            df,
            x="Ticker",
            y=metric,
            text_auto='.2f',
            color=metric,
            color_continuous_scale="Viridis"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            title=f"Perbandingan {metric}",
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            plot_bgcolor="white"
        )

        cols[i % 2].plotly_chart(fig, use_container_width=True)
