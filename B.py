import pandas as pd
import yfinance as yf
import streamlit as st
import concurrent.futures
import gc
from datetime import datetime

# --- SETTING PAGE ---
st.set_page_config(page_title="Accurate Liquidity Screener", layout="wide")

@st.cache_data(ttl=300) # Cache 5 menit saja agar data tetap segar
def get_ticker_list():
    # Contoh list, pastikan pakai .JK
    return ["MDIY.JK", "ASII.JK", "BBCA.JK", "BBRI.JK", "TLKM.JK", "GOTO.JK", "BUMI.JK", "BRMS.JK"]

def fetch_accurate_data(ticker):
    try:
        # PENTING: auto_adjust=False & back_adjust=False agar harga TIDAK dimanipulasi API
        df = yf.download(ticker, period="30d", interval="1d", progress=False, 
                         auto_adjust=False, back_adjust=False)
        
        if df.empty or len(df) < 20:
            return None

        # Menghapus Multi-Index jika ada
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Ambil baris terakhir dan kemarin
        # Gunakan 'Close' murni, bukan 'Adj Close'
        price_now = float(df['Close'].iloc[-1])
        price_prev = float(df['Close'].iloc[-2])
        volume_now = float(df['Volume'].iloc[-1])
        
        # Rata-rata volume 20 hari untuk RVOL
        avg_vol_20d = df['Volume'].iloc[-21:-1].mean()

        # Kalkulasi
        ret = ((price_now - price_prev) / price_prev) * 100
        vol_lot = volume_now / 100
        turnover = price_now * volume_now
        rvol = volume_now / avg_vol_20d if avg_vol_20d > 0 else 0

        # PROTEKSI: Jika harga tidak masuk akal (misal tiba-tiba jadi ribuan)
        # Saham MDIY aslinya di bawah 1000, jika API kirim > 5000 itu data error
        if price_now > 5000 and ticker == "MDIY.JK":
            return None

        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price": price_now,
            "Prev": price_prev,
            "Return (%)": round(ret, 2),
            "Vol (Lot)": int(vol_lot),
            "Value (IDR)": turnover,
            "RVOL": round(rvol, 2)
        }
    except:
        return None

# --- UI ---
st.title("🚀 Accurate Professional Screener")

st.sidebar.header("Filter Likuiditas")
target_val = st.sidebar.number_input("Min Value (IDR)", value=1_000_000_000)
target_lot = st.sidebar.number_input("Min Lot", value=5000)

if st.button("Mulai Screening"):
    tickers = get_ticker_list()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_accurate_data, t): t for t in tickers}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: results.append(res)

    if results:
        df = pd.DataFrame(results)
        
        # Filtering berdasarkan input user
        final_df = df[
            (df['Value (IDR)'] >= target_val) & 
            (df['Vol (Lot)'] >= target_lot)
        ].sort_values(by="Return (%)", ascending=False)

        st.dataframe(final_df.style.format({
            "Price": "{:,.0f}",
            "Prev": "{:,.0f}",
            "Value (IDR)": "{:,.0f}",
            "Vol (Lot)": "{:,.0f}"
        }))
        
        gc.collect()
