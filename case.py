import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION & CSS ---
st.set_page_config(page_title="IHSG Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background-color: white; border-radius: 10px; }
    .heatmap-box {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 5px;
        margin: 2px;
        font-weight: bold;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LIST ---
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK", "KLBF.JK"]

# --- FUNCTIONS ---
@st.cache_data(ttl=3600)
def fetch_stock_data(tickers, period="1mo"):
    """Mengambil data historical saham secara batch."""
    data = yf.download(tickers, period=period, group_by='ticker')
    return data

@st.cache_data(ttl=3600)
def get_fundamentals(tickers):
    """Mengambil data fundamental untuk perbandingan."""
    fund_data = []
    for t in tickers:
        info = yf.Ticker(t).info
        fund_data.append({
            "Ticker": t,
            "Price": info.get("currentPrice"),
            "PER": info.get("trailingPE"),
            "PBV": info.get("priceToBook"),
            "MarketCap": info.get("marketCap")
        })
    return pd.DataFrame(fund_data)

# --- SESSION STATE INITIALIZATION ---
if 'data' not in st.session_state:
    with st.spinner("Fetching market data..."):
        st.session_state.data = fetch_stock_data(TICKERS, period="1y")

# --- UI TABS ---
tab_list, tab_compare, tab_recap, tab_winloss, tab_cek = st.tabs([
    "📈 List Saham", "⚖️ Compare", "📊 Recap", "🔥 Win/Loss", "📅 Cek Tanggal"
])

# 1. TAB LIST (Grid View with Pagination)
with tab_list:
    st.header("IHSG Live Monitor")
    cols_per_row = 3
    items_per_page = 6
    total_pages = (len(TICKERS) // items_per_page) + 1
    
    page = st.number_input("Halaman", min_value=1, max_value=total_pages, step=1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    
    current_tickers = TICKERS[start_idx:end_idx]
    rows = [current_tickers[i:i + cols_per_row] for i in range(0, len(current_tickers), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        for i, ticker in enumerate(row):
            df = st.session_state.data[ticker].dropna()
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            pct_change = ((last_price - prev_price) / prev_price) * 100
            
            fig = go.Figure(data=[go.Scatter(x=df.index[-20:], y=df['Close'][-20:], mode='lines+markers')])
            fig.update_layout(title=f"{ticker} ({pct_change:.2f}%)", height=250, margin=dict(l=20, r=20, t=40, b=20))
            cols[i].plotly_chart(fig, use_container_width=True)

# 2. TAB COMPARE (Technical & Fundamental)
with tab_compare:
    st.header("Fundamental Comparison")
    selected_tickers = st.multiselect("Pilih Saham", TICKERS, default=TICKERS[:3])
    if selected_tickers:
        fund_df = get_fundamentals(selected_tickers)
        st.table(fund_df)

# 3. TAB RECAP (Performance Summary)
with tab_recap:
    st.header("Performance Recap")
    recap_list = []
    for t in TICKERS:
        df = st.session_state.data[t]['Close'].dropna()
        recap_list.append({
            "Ticker": t,
            "1D %": ((df.iloc[-1] / df.iloc[-2]) - 1) * 100,
            "1W %": ((df.iloc[-1] / df.iloc[-5]) - 1) * 100,
            "1M %": ((df.iloc[-1] / df.iloc[-21]) - 1) * 100,
            "YTD %": ((df.iloc[-1] / df.iloc[0]) - 1) * 100
        })
    st.dataframe(pd.DataFrame(recap_list).style.format(precision=2))

# 4. TAB WIN/LOSS (Heatmap)
with tab_winloss:
    st.header("20-Day Performance Heatmap")
    for t in TICKERS[:5]: # Contoh 5 saham saja agar tidak terlalu panjang
        st.write(f"**{t}**")
        df = st.session_state.data[t]['Close'].dropna().tail(20)
        changes = df.pct_change() * 100
        
        cols = st.columns(20)
        for i, val in enumerate(changes):
            color = "#2ecc71" if val > 0 else "#e74c3c" if val < 0 else "#bdc3c7"
            cols[i].markdown(f'<div class="heatmap-box" style="background-color:{color}">{i+1}</div>', unsafe_allow_html=True)

# 5. TAB CEK TANGGAL (Date Comparison)
with tab_cek:
    st.header("Price Comparison by Date")
    col1, col2 = st.columns(2)
    date1 = col1.date_input("Tanggal Awal", datetime.now() - timedelta(days=30))
    date2 = col2.date_input("Tanggal Akhir", datetime.now())
    
    selected_t = st.selectbox("Pilih Ticker", TICKERS)
    df_t = st.session_state.data[selected_t]['Close'].dropna()
    
    try:
        p1 = df_t.asof(pd.Timestamp(date1))
        p2 = df_t.asof(pd.Timestamp(date2))
        diff = ((p2 - p1) / p1) * 100
        st.metric(label=f"Performa {selected_t}", value=f"{p2:.2f}", delta=f"{diff:.2f}%")
    except:
        st.error("Data tidak tersedia untuk tanggal tersebut.")
