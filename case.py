import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="IHSG Pro Dashboard", layout="wide")

# Custom CSS untuk mempercantik UI
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .heatmap-box {
        display: inline-block;
        width: 35px; height: 35px; line-height: 35px;
        text-align: center; border-radius: 4px;
        margin: 2px; font-size: 10px; font-weight: bold; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIST TICKER IHSG (Contoh) ---
TICKERS = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", 
    "GOTO.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK", "KLBF.JK",
    "CPIN.JK", "UNTR.JK", "ICBP.JK", "AMRT.JK", "PGAS.JK"
]

# --- HELPER FUNCTIONS ---

@st.cache_data(ttl=3600)
def fetch_historical_batch(tickers):
    """Mengambil data harga penutupan secara massal (efisien)."""
    # Gunakan period 2 tahun agar data YTD dan Weekly aman
    data = yf.download(tickers, period="2y", interval="1d", group_by='ticker')
    return data

@st.cache_data(ttl=3600)
def get_fundamental_safe(selected_tickers):
    """Mengambil data fundamental satu per satu dengan delay untuk menghindari blokir."""
    results = []
    progress_text = "Mengambil data fundamental... Mohon tunggu."
    my_bar = st.progress(0, text=progress_text)
    
    # Headers agar request terlihat seperti browser asli
    headers = {'User-agent': 'Mozilla/5.0'}
    
    for i, t in enumerate(selected_tickers):
        try:
            ticker_obj = yf.Ticker(t)
            # Menambahkan sedikit delay (0.7 detik) tiap request
            time.sleep(0.7) 
            info = ticker_obj.info
            
            results.append({
                "Ticker": t,
                "Nama": info.get("shortName", "N/A"),
                "Price": info.get("currentPrice", 0),
                "PER": info.get("trailingPE", "N/A"),
                "PBV": info.get("priceToBook", "N/A"),
                "Market Cap": f"{info.get('marketCap', 0):,}"
            })
        except Exception:
            results.append({"Ticker": t, "Nama": "Limit/Error", "Price": 0, "PER": "N/A", "PBV": "N/A", "Market Cap": 0})
        
        my_bar.progress((i + 1) / len(selected_tickers))
    
    my_bar.empty()
    return pd.DataFrame(results)

# --- INITIALIZATION ---
if 'stock_data' not in st.session_state:
    with st.spinner("Mengunduh data pasar IHSG..."):
        st.session_state.stock_data = fetch_historical_batch(TICKERS)

# --- UI LAYOUT ---
st.title("🇮🇩 IHSG Market Dashboard")
st.caption("Data real-time via Yahoo Finance API dengan optimasi Rate Limit")

tabs = st.tabs(["📈 Halaman List", "⚖️ Bandingkan", "📊 Rekap Performa", "🔥 Win/Loss", "📅 Cek Tanggal"])

# --- 1. TAB LIST (Pagination & Grid) ---
with tabs[0]:
    st.subheader("Grid Monitoring Saham")
    items_per_page = 6
    total_pages = (len(TICKERS) // items_per_page) + (1 if len(TICKERS) % items_per_page > 0 else 0)
    
    col_p1, col_p2 = st.columns([1, 4])
    page = col_p1.number_input("Halaman", min_value=1, max_value=total_pages, step=1)
    
    idx_start = (page - 1) * items_per_page
    idx_end = idx_start + items_per_page
    current_batch = TICKERS[idx_start:idx_end]
    
    cols = st.columns(3)
    for i, t in enumerate(current_batch):
        with cols[i % 3]:
            df = st.session_state.stock_data[t]['Close'].dropna()
            if not df.empty:
                last_p = df.iloc[-1]
                prev_p = df.iloc[-2]
                change = ((last_p - prev_p) / prev_p) * 100
                
                fig = go.Figure(data=[go.Scatter(x=df.index[-30:], y=df[-30:], fill='tozeroy', line_color='green' if change >= 0 else 'red')])
                fig.update_layout(title=f"{t} ({change:.2f}%)", height=200, margin=dict(l=0,r=0,t=30,b=0), 
                                 xaxis_visible=False, yaxis_visible=True)
                st.plotly_chart(fig, use_container_width=True)

# --- 2. TAB COMPARE ---
with tabs[1]:
    st.subheader("Analisis Fundamental & Teknikal")
    selected = st.multiselect("Pilih maksimal 5 saham untuk dibandingkan:", TICKERS, default=TICKERS[:3])
    
    if st.button("Proses Perbandingan"):
        if len(selected) > 5:
            st.error("Maksimal 5 saham untuk menjaga kestabilan koneksi.")
        else:
            fund_df = get_fundamental_safe(selected)
            st.dataframe(fund_df, use_container_width=True)

# --- 3. TAB RECAP ---
with tabs[2]:
    st.subheader("Tabel Ringkasan Performa")
    recap_data = []
    for t in TICKERS:
        df = st.session_state.stock_data[t]['Close'].dropna()
        if len(df) > 250:
            recap_data.append({
                "Ticker": t,
                "Harian %": ((df.iloc[-1] / df.iloc[-2]) - 1) * 100,
                "Mingguan %": ((df.iloc[-1] / df.iloc[-5]) - 1) * 100,
                "Bulanan %": ((df.iloc[-1] / df.iloc[-21]) - 1) * 100,
                "YTD %": ((df.iloc[-1] / df.loc[f"{datetime.now().year}-01-02":].iloc[0]) - 1) * 100
            })
    st.table(pd.DataFrame(recap_data).set_index("Ticker").style.format("{:.2f}%"))

# --- 4. TAB WIN/LOSS (Heatmap) ---
with tabs[3]:
    st.subheader("20-Day Win/Loss Heatmap")
    st.info("Hijau: Naik, Merah: Turun, Abu-abu: Tetap")
    
    for t in TICKERS[:10]: # Batasi 10 agar UI tidak terlalu panjang
        df_hl = st.session_state.stock_data[t]['Close'].dropna().tail(21)
        changes = df_hl.pct_change().dropna() * 100
        
        st.write(f"**{t}**")
        html_line = ""
        for val in changes:
            color = "#2ecc71" if val > 0.1 else "#e74c3c" if val < -0.1 else "#bdc3c7"
            html_line += f'<div class="heatmap-box" style="background-color:{color}">{val:.1f}</div>'
        st.markdown(html_line, unsafe_allow_html=True)
        st.divider()

# --- 5. TAB CEK TANGGAL ---
with tabs[4]:
    st.subheader("Bandingkan Harga antar Tanggal")
    c1, c2, c3 = st.columns(3)
    target_t = c1.selectbox("Pilih Saham", TICKERS, key="cek_t")
    d1 = c2.date_input("Dari", datetime.now() - timedelta(days=60))
    d2 = c3.date_input("Sampai", datetime.now())
    
    if d1 < d2:
        df_target = st.session_state.stock_data[target_t]['Close'].dropna()
        try:
            val1 = df_target.asof(pd.Timestamp(d1))
            val2 = df_target.asof(pd.Timestamp(d2))
            diff_pct = ((val2 - val1) / val1) * 100
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(f"Harga {d1}", f"{val1:,.2f}")
            col_m2.metric(f"Harga {d2}", f"{val2:,.2f}", delta=f"{diff_pct:.2f}%")
        except:
            st.warning("Data tidak ditemukan pada rentang tanggal tersebut.")
