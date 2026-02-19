import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Professional Real-Time Dashboard")

# --- KONFIGURASI SAHAM ---
# List saham yang ingin dipantau di tab 5-Minute Analysis (bisa ditambah)
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK"]

def get_stock_data(ticker_input):
    # Auto-suffix .JK untuk saham Indonesia 4 huruf
    ticker = f"{ticker_input.upper()}.JK" if len(ticker_input) == 4 and "." not in ticker_input else ticker_input.upper()
    
    try:
        # Ambil data intraday 1 menit
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if df.empty:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df.dropna(subset=['Close']), ticker
    except:
        return None, ticker

# --- DASHBOARD UI ---
st.title("📊 Real-Time 5-Minute Pulse Dashboard")

tab1, tab2 = st.tabs(["🔍 Search & Monitor", "⚡ 5-Min Gainers/Losers"])

# --- TAB 1: SEARCH CUSTOM ---
with tab1:
    search_input = st.text_input("Ketik kode saham (misal: bbca bbri tlkm):", "BBCA BBRI BMRI")
    tickers_to_show = [t.strip() for t in search_input.split() if t.strip()]
    
    if tickers_to_show:
        for i in range(0, len(tickers_to_show), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(tickers_to_show):
                    with cols[j]:
                        df, full_name = get_stock_data(tickers_to_show[idx])
                        if df is not None and len(df) > 1:
                            latest_p = df['Close'].iloc[-1]
                            
                            # Hitung perubahan 5 menit terakhir
                            # Jika data kurang dari 5 menit, ambil data pertama yang tersedia
                            idx_5m = -6 if len(df) >= 6 else 0
                            price_5m_ago = df['Close'].iloc[idx_5m]
                            change_5m = ((latest_p - price_5m_ago) / price_5m_ago) * 100
                            
                            color = "#00FF41" if change_5m >= 0 else "#FF4B4B"
                            
                            fig = go.Figure(go.Scatter(
                                x=df.index, y=df['Close'],
                                mode='lines', line=dict(color=color, width=3, shape='spline')
                            ))
                            fig.update_layout(
                                title=f"<b>{full_name}</b><br>5-Min Change: {change_5m:+.2f}%",
                                template="plotly_dark", height=300,
                                yaxis=dict(autorange=True, side="right", fixedrange=False),
                                margin=dict(l=10, r=10, t=60, b=10)
                            )
                            st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: 5-MINUTE GAINERS & LOSERS ---
with tab2:
    st.subheader("Perubahan Harga dalam 5 Menit Terakhir (Real-Time)")
    
    analysis_data = []
    with st.spinner("Menganalisis watchlist..."):
        for t in WATCHLIST:
            df, full_name = get_stock_data(t)
            if df is not None and len(df) >= 2:
                latest_p = df['Close'].iloc[-1]
                idx_5m = -6 if len(df) >= 6 else 0
                p_old = df['Close'].iloc[idx_5m]
                pct = ((latest_p - p_old) / p_old) * 100
                analysis_data.append({"Ticker": t, "Price": latest_p, "5m %": pct})
    
    if analysis_data:
        res_df = pd.DataFrame(analysis_data).sort_values(by="5m %", ascending=False)
        
        col_g, col_l = st.columns(2)
        
        with col_g:
            st.success("🚀 TOP 5-MIN GAINERS")
            st.dataframe(res_df.head(5), use_container_width=True)
            
        with col_l:
            st.error("📉 TOP 5-MIN LOSERS")
            st.dataframe(res_df.tail(5).sort_values(by="5m %"), use_container_width=True)
            
    st.caption(f"Update terakhir: {datetime.now().strftime('%H:%M:%S')} (Interval data 1 menit)")
