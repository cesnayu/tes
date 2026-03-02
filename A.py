import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import seaborn as sns
import requests
import requests_cache
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================
# CONFIG STREAMLIT
# ==============================
st.set_page_config(page_title="Fundamental Dashboard PRO", layout="wide")
st.title("📊 Fundamental Stock Analysis Dashboard")

# ==============================
# CACHE & SESSION (ANTI RATE LIMIT)
# ==============================
requests_cache.install_cache("yf_cache", expire_after=3600)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

retry = Retry(total=5, backoff_factor=1,
              status_forcelist=[429, 500, 502, 503, 504])

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

# ==============================
# INPUT USER
# ==============================
tickers_input = st.text_input(
    "Masukkan kode saham (pisahkan koma)",
    value="BBCA.JK, TLKM.JK, ASII.JK"
)

analyze = st.button("Analisa")

if analyze:

    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    results = []

    progress = st.progress(0)

    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker, session=session)

            # ==========================
            # FAST INFO (HARGA & SHARES)
            # ==========================
            fast = stock.fast_info
            price = fast.get("lastPrice", 0) or 0
            shares = fast.get("sharesOutstanding", 0) or 0

            # ==========================
            # FINANCIAL STATEMENTS
            # ==========================
            income = stock.get_income_stmt()
            balance = stock.get_balance_sheet()

            if not income.empty:
                net_income = income.loc["Net Income"][0] if "Net Income" in income.index else 0
                revenue = income.loc["Total Revenue"][0] if "Total Revenue" in income.index else 0
            else:
                net_income = 0
                revenue = 0

            if not balance.empty:
                equity = balance.loc["Total Stockholder Equity"][0] if "Total Stockholder Equity" in balance.index else 0
                assets = balance.loc["Total Assets"][0] if "Total Assets" in balance.index else 0
                total_debt = balance.loc["Total Debt"][0] if "Total Debt" in balance.index else 0
            else:
                equity = 0
                assets = 0
                total_debt = 0

            # ==========================
            # HITUNG METRIK
            # ==========================
            eps = net_income / shares if shares != 0 else 0
            per = price / eps if eps != 0 else 0
            pbv = price / (equity / shares) if shares != 0 and equity != 0 else 0
            roe = (net_income / equity) * 100 if equity != 0 else 0
            roa = (net_income / assets) * 100 if assets != 0 else 0
            der = total_debt / equity if equity != 0 else 0
            rps = revenue / shares if shares != 0 else 0
            earning_yield = (eps / price) * 100 if price != 0 else 0

            results.append({
                "Ticker": ticker,
                "EPS": eps,
                "PER": per,
                "PBV": pbv,
                "ROE (%)": roe,
                "ROA (%)": roa,
                "DER": der,
                "RPS": rps,
                "Earning Yield (%)": earning_yield
            })

        except Exception:
            st.warning(f"⚠️ Data {ticker} gagal diambil. Diisi default 0.")
            results.append({
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

        progress.progress((i + 1) / len(tickers))
        time.sleep(0.5)  # Anti rate limit

    df = pd.DataFrame(results)

    # ==============================
    # TABEL RINGKASAN
    # ==============================
    st.subheader("📋 Ringkasan Fundamental")
    st.dataframe(df.sort_values("ROE (%)", ascending=False),
                 use_container_width=True)

    # ==============================
    # VISUAL STYLE
    # ==============================
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
            plot_bgcolor="white",
            uniformtext_minsize=8,
            uniformtext_mode="hide"
        )

        cols[i % 2].plotly_chart(fig, use_container_width=True)
