import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import gc

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# --- 2. CSS ---
st.markdown("""
<style>
    .wl-box {
        border-radius: 5px; padding: 10px; text-align: center; color: white;
        margin-bottom: 10px; font-family: sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .wl-date { font-size: 11px; opacity: 0.9; margin-bottom: 4px; }
    .wl-price { font-size: 14px; font-weight: bold; margin-bottom: 2px; }
    .wl-pct { font-size: 12px; font-weight: bold; }
    thead tr th:first-child {display:none}
    tbody th {display:none}
    div.stButton > button {width: 100%;}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LIST SAHAM ---
RAW_TICKERS = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "BREN", "AMMN", "TPIA"] # Disederhanakan untuk contoh, pakai list lengkap Anda di lokal
LIST_SAHAM_IHSG = [f"{t}.JK" for t in RAW_TICKERS]

# --- 4. STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'recap_data' not in st.session_state: st.session_state.recap_data = None
if 'date_check_data' not in st.session_state: st.session_state.date_check_data = None

# --- 5. FUNGSI DATA ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_fundamental(ticker):
    try:
        i = yf.Ticker(ticker).info
        return i.get('priceToBook', 0), i.get('trailingPE', 0)
    except: return 0, 0

@st.cache_data(ttl=600, show_spinner=False)
def get_data(tickers, period="3mo", interval="1d", start=None, end=None):
    if not tickers: return pd.DataFrame()
    try:
        # Note: 1h interval limited to last 730 days
        d = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=True, threads=True)
        return d
    except: return pd.DataFrame()
    finally: gc.collect()

def fetch_data_chunked(ticker_list, period="2y", chunk_size=50):
    full_data = pd.DataFrame()
    prog_bar = st.progress(0)
    for i in range(0, len(ticker_list), chunk_size):
        chunk = ticker_list[i:i+chunk_size]
        try:
            temp_data = get_data(chunk, period=period)
            if not temp_data.empty:
                full_data = temp_data if full_data.empty else pd.concat([full_data, temp_data], axis=1)
        except: pass
        prog_bar.progress(min((i + chunk_size) / len(ticker_list), 1.0))
    prog_bar.empty()
    return full_data

def fmt_idr(val):
    return f"{val:,.0f}" if not pd.isna(val) else "0"

# --- 6. VISUALISASI ---
def chart_grid(df, ticker, ma20=True, chart_type="Candle"):
    # Hitung MACD jika dipilih
    if chart_type == "MACD":
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.6, 0.4], vertical_spacing=0.03)
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='gray', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=macd, name='MACD', line=dict(color='blue', width=1)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=signal, name='Signal', line=dict(color='orange', width=1)), row=2, col=1)
        fig.add_trace(go.Bar(x=df.index, y=hist, name='Hist'), row=2, col=1)
        xaxis_cfg = dict(showgrid=False, showticklabels=False)
    else:
        fig = go.Figure()
        if chart_type == "Line":
            clr = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=clr, width=2)))
            xaxis_cfg = dict(showgrid=False, showticklabels=False)
        else: # Candle
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
            xaxis_cfg = dict(showgrid=False, showticklabels=False, rangeslider=dict(visible=False))
        
        if ma20 and len(df)>20:
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1)))

    clr_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    fig.update_layout(
        title=dict(text=f"{ticker} ({fmt_idr(df['Close'].iloc[-1])})", font=dict(size=12, color=clr_title), x=0.5, y=0.9),
        margin=dict(l=5, r=5, t=30, b=5), height=280, showlegend=False, 
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=xaxis_cfg
    )
    return fig

# --- 7. MAIN UI ---
tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Recap", "🎲 Win/Loss", "🗓️ Cek Tanggal"])

# === TAB 1: LIST ===
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1.5, 1])
    with c1: 
        tf = st.selectbox("Waktu", ["1h", "5d", "1mo", "3mo", "1y"], 3)
    with c2: min_p = st.number_input("Min Rp", 0, step=50)
    with c3: max_p = st.number_input("Max Rp", 100, value=100000, step=50)
    with c4: c_type = st.radio("Grafik", ["Candle", "Line", "MACD"], horizontal=True)
    with c5: show_ma = st.checkbox("MA20", True)

    # Logika Interval & Period
    interval = "1d"
    period = tf
    if tf == "1h":
        interval = "1h"
        period = "2y" # Maksimum untuk 1h adalah 730 hari

    per_page = 20
    total_pages = math.ceil(len(LIST_SAHAM_IHSG)/per_page)
    
    b1, b2, b3 = st.columns([1, 8, 1])
    if b1.button("⬅️") and st.session_state.page > 1: st.session_state.page -= 1; st.rerun()
    b2.markdown(f"<div style='text-align:center; margin-top:5px'><b>Page {st.session_state.page}/{total_pages}</b></div>", unsafe_allow_html=True)
    if b3.button("➡️") and st.session_state.page < total_pages: st.session_state.page += 1; st.rerun()

    start_idx = (st.session_state.page-1)*per_page
    batch = LIST_SAHAM_IHSG[start_idx:start_idx+per_page]
    
    if batch:
        with st.spinner("Loading Grid..."):
            df_b = get_data(batch, period=period, interval=interval)
        
        cols = st.columns(4)
        idx = 0
        for t in batch:
            try:
                dft = df_b[t].dropna() if len(batch) > 1 else df_b.dropna()
                if dft.empty: continue
                if not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                
                with cols[idx % 4]:
                    st.plotly_chart(chart_grid(dft, t, show_ma, c_type), use_container_width=True)
                idx += 1
            except: continue
        gc.collect()

# [Teks sisa Tab 2-5 tetap sama seperti kode awal Anda...]

