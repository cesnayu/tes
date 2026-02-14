import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# CSS Kustom (Hanya untuk styling text, bukan layout grid)
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    div[data-testid="stMetricValue"] {font-size: 1rem;}
    .stPlotlyChart {height: 280px;}
    
    /* Styling Sederhana untuk Box Win/Loss */
    .wl-box-content {
        padding: 10px;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin-bottom: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .wl-date { font-size: 11px; margin-bottom: 2px; opacity: 0.9; }
    .wl-price { font-size: 14px; font-weight: bold; margin-bottom: 2px; }
    .wl-pct { font-size: 12px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA STATIC ---
LIST_SAHAM_IHSG = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "GOTO.JK", "KLBF.JK",
    "AMRT.JK", "MDKA.JK", "ADRO.JK", "UNTR.JK", "CPIN.JK", "INCO.JK", "PGAS.JK", "ITMG.JK", "PTBA.JK", "ANTM.JK",
    "BRPT.JK", "INDF.JK", "INKP.JK", "TPIA.JK", "EXCL.JK", "ISAT.JK", "TOWR.JK", "TBIG.JK", "MTEL.JK", "BUKA.JK",
    "ARTO.JK", "EMTK.JK", "SCMA.JK", "MNCN.JK", "MEDIA.JK", "JPFA.JK", "SMGR.JK", "INTP.JK", "JSMR.JK", "WIKA.JK",
    "PTPP.JK", "ADHI.JK", "WSKT.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPPF.JK", "RALS.JK",
    "ACES.JK", "MAPI.JK", "MAPA.JK", "ERAA.JK", "SIDO.JK", "KAEF.JK", "HEAL.JK", "MIKA.JK", "SILO.JK", "SAME.JK"
]

# --- 3. STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'sim_balance' not in st.session_state: st.session_state.sim_balance = 100000000
if 'sim_portfolio' not in st.session_state: st.session_state.sim_portfolio = {}
if 'sim_history' not in st.session_state: st.session_state.sim_history = []

# --- 4. FUNGSI BACKEND ---
@st.cache_data(ttl=3600)
def get_fundamental_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('priceToBook', 0), info.get('trailingPE', 0)
    except: return 0, 0

@st.cache_data(ttl=900)
def get_data_bulk(tickers, period="3mo", interval="1d", start=None, end=None):
    if not tickers: return pd.DataFrame()
    try:
        if start and end:
            data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, threads=True, auto_adjust=True)
        else:
            data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, threads=True, auto_adjust=True)
        return data
    except: return pd.DataFrame()

def format_rupiah(value):
    if pd.isna(value): return "0"
    return f"{value:,.0f}"

def format_volume(value):
    if pd.isna(value): return "0"
    if value >= 1000000000: return f"{value/1000000000:.1f}B"
    if value >= 1000000: return f"{value/1000000:.1f}M"
    if value >= 1000: return f"{value/1000:.1f}K"
    return f"{value:.0f}"

# --- 5. FUNGSI VISUALISASI CHART ---
def create_chart(df, ticker, ma20=True, chart_type="Candle"):
    fig = go.Figure()
    
    # Line Chart
    if chart_type == "Line":
        color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', 
            line=dict(color=color_line, width=2), name="Price"
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], fill='tozeroy', mode='none',
            fillcolor=f"rgba{tuple(int(color_line.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
            showlegend=False
        ))
        xaxis_config = dict(showgrid=False, showticklabels=False, type="date")
    
    # Candle Chart
    else:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
            name="Price", showlegend=False
        ))
        xaxis_config = dict(showgrid=False, showticklabels=False, rangeslider=dict(visible=False))

    # MA20
    if ma20 and len(df) > 20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), showlegend=False, name="MA20"))
    
    last_price = df['Close'].iloc[-1]
    color_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    
    fig.update_layout(
        title=dict(text=f"{ticker} ({format_rupiah(last_price)})", font=dict(size=14, color=color_title), x=0.5, y=0.95),
        margin=dict(l=10, r=10, t=30, b=10), 
        height=250,
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=xaxis_config
    )
    return fig

def create_advanced_chart(df, ticker, style='candle', pbv=0, per=0):
    fig = make
