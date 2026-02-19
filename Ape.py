import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock 5-Min Monitor")

# Konfigurasi Watchlist
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

def get_clean_data(ticker_input):
    """Fungsi stabil untuk ambil data dan bersihkan Multi-Index"""
    t = ticker_input.strip().upper()
    full_t = f"{t}.JK" if len(t) == 4 and "." not in t else t
    try:
        df = yf.download(full_t, period="1d", interval="1m", progress=False)
        if df.empty:
            df = yf.download(full_t, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        if not df.empty:
            # Fix Multi-index Columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Pastikan kolom Close ada dan berbentuk angka
            df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
            prices = df['Close'].dropna()
            return prices, full_t
    except Exception:
        pass
    return None, full_t

st.title("📈 5-Minute Pulse Dashboard")

tab1, tab2 = st.tabs(["🔍 Search Monitor", "⚡ 5-Min Movers"])

with tab1:
    q = st.text_input("Cari Saham (Contoh: bbca bbri):", "BBCA BBRI")
    tickers = q.split()
    if tickers:
        for i in range(0, len(tickers), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(tickers):
                    with cols[j]:
                        p, name = get_clean_data(tickers[idx])
                        if p is not None and len(p) >= 2:
                            now = float(p.iloc[-1])
                            # Ambil data 5 menit lalu (index -6 karena interval 1m)
                            old = float(p.iloc[-6]) if len(p) >= 6 else float(p.iloc[0])
                            pct = ((now - old) / old) * 100
                            
                            fig = go.Figure(go.Scatter(
                                x=p.index, y=p.values,
                                mode='lines', line=dict(color="#00FF41" if pct >= 0 else "#FF4B4B", width=2.5, shape='spline')
                            ))
                            fig.update_layout(
                                title=f"<b>{name}</b>: {now:,.0f} ({pct:+.2f}%)",
                                template="plotly_dark", height=280, margin=dict(l=5,r=5,t=50,b=5),
                                yaxis=dict(autorange=True, side="right")
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"{tickers[idx]} tidak ditemukan.")

with tab2:
    if st.button("Refresh Analisis"):
        st.rerun()
    
    analysis = []
    with st.spinner("Menghitung data..."):
        for saham in WATCHLIST:
            p, name = get_clean_data(saham)
            if p is not None and len(p) >= 2:
                try:
                    now = float(p.iloc[-1])
                    old = float(p.iloc[-6]) if len(p) >= 6 else float(p.iloc[0])
                    analysis.append({
                        "Ticker": name,
                        "Price": now,
                        "Chg_5m": ((now - old) / old) * 100
                    })
                except Exception:
                    continue
    
    if analysis:
        res = pd.DataFrame(analysis).sort_values("Chg_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP 5-MIN GAINERS")
            st.table(res.head(5).style.format({"Chg_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
        with c2:
            st.error("📉 TOP 5-MIN LOSERS")
            st.table(res.tail(5).sort_values("Chg_5m").style.format({"Chg_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
