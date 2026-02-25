import pandas as pd
import yfinance as yf
import streamlit as st
import concurrent.futures
import gc
from datetime import datetime

# --- KONFIGURASI DASHBOARD ---
st.set_page_config(page_title="Liquidity Screener", layout="wide")

@st.cache_data(ttl=3600)
def get_ticker_list():
    # Daftar contoh, silakan ganti dengan list 800+ saham kamu
    return ["ASII.JK", "BBCA.JK", "BBRI.JK", "TLKM.JK", "GOTO.JK", 
            "BUMI.JK", "BRMS.JK", "MEDC.JK", "ANTM.JK", "PGAS.JK", 
            "ADRO.JK", "ITMG.JK", "UNTR.JK", "AMRT.JK", "CPIN.JK"]

def fetch_data(ticker):
    try:
        # Ambil 30 hari data agar perhitungan rata-rata volume (RVOL) 20 hari akurat
        df = yf.download(ticker, period="30d", interval="1d", progress=False, auto_adjust=False)
        
        if df.empty or len(df) < 21:
            return None

        # Perbaikan kolom jika MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Data Terbaru (H) & Kemarin (H-1)
        last_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        vol_raw = float(df['Volume'].iloc[-1])
        
        # Hitung Rata-rata Volume 20 hari (untuk RVOL)
        avg_vol_20d = df['Volume'].iloc[-21:-1].mean()

        # Kalkulasi Metrik
        ret_pct = ((last_close - prev_close) / prev_close) * 100
        vol_lot = vol_raw / 100
        value_turnover = last_close * vol_raw
        rvol = vol_raw / avg_vol_20d if avg_vol_20d > 0 else 0

        return {
            "Ticker": ticker.replace(".JK", ""),
            "Price Close": last_close,
            "Return (%)": round(ret_pct, 2),
            "Volume (Lot)": int(vol_lot),
            "Value (IDR)": value_turnover,
            "RVOL": round(rvol, 2)
        }
    except:
        return None

# --- UI INTERFACE ---
st.title("📊 Dashboard Filter Likuiditas Saham")
st.markdown("---")

# Sidebar untuk Filter User-Defined
st.sidebar.header("🔧 Pengaturan Filter")
min_lot = st.sidebar.number_input("Min Volume (Lot)", value=10000, step=1000)
min_value = st.sidebar.number_input("Min Value / Turnover (IDR)", value=5_000_000_000, step=1_000_000_000)
min_rvol = st.sidebar.slider("Min RVOL (Relative Volume)", 0.0, 5.0, 1.0)
min_return = st.sidebar.slider("Min Return (%)", -10.0, 10.0, 0.0)

if st.button("🚀 Jalankan Scan Saham"):
    tickers = get_ticker_list()
    raw_data = []
    
    status = st.empty()
    bar = st.progress(0)

    # Proses Multi-threading (Cepat)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_data, t): t for t in tickers}
        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            res = f.result()
            if res: raw_data.append(res)
            bar.progress((i + 1) / len(tickers))
            status.text(f"Menganalisis {i+1}/{len(tickers)} saham...")

    if raw_data:
        df_result = pd.DataFrame(raw_data)
        
        # PROSES FILTERING (Berdasarkan Pilihan User)
        mask = (df_result['Volume (Lot)'] >= min_lot) & \
               (df_result['Value (IDR)'] >= min_value) & \
               (df_result['RVOL'] >= min_rvol) & \
               (df_result['Return (%)'] >= min_return)
        
        final_df = df_result[mask].sort_values(by="Value (IDR)", ascending=False)

        # TAMPILAN DATA
        st.subheader(f"✅ Hasil Screening: {len(final_df)} Saham Likuid")
        
        st.dataframe(
            final_df.style.format({
                "Value (IDR)": "{:,.0f}",
                "Volume (Lot)": "{:,.0f}",
                "Price Close": "{:,.0f}",
                "Return (%)": "{:+.2f}%",
                "RVOL": "{:.2f}x"
            }).background_gradient(subset=['Return (%)'], cmap='RdYlGn'),
            use_container_width=True
        )

        # Hapus memori agar tidak berat
        del df_result, final_df
        gc.collect()
    else:
        st.error("Gagal menarik data. Cek koneksi internet atau list ticker.")

st.sidebar.markdown("---")
st.sidebar.caption(f"Update: {datetime.now().strftime('%H:%M:%S')} WIB")
