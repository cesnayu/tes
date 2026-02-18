import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Smooth Stock Dashboard")

# --- AUTO REFRESH (Penyebab ModuleNotFoundError diatasi dengan try-except) ---
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, key="datarefresh")
except:
    pass

# --- FUNGSI AMBIL DATA ---
def get_stock_data(ticker):
    try:
        # Ambil data intraday 1 menit
        data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        
        # Jika hari ini libur/tutup, ambil hari terakhir yang ada datanya
        if data.empty:
            data = yf.download(ticker, period="5d", interval="1m", progress=False, auto_adjust=True)
            if not data.empty:
                last_date = data.index[-1].date()
                data = data[data.index.date == last_date]
        
        # Menghapus data NaN agar grafik tidak terputus atau drop ke 0
        data = data.dropna(subset=['Close'])
        return data
    except:
        return None

# --- UI ---
st.title("📈 Real-Time Stock Monitoring")
search_input = st.text_input("Ketik Kode Saham (Pisahkan Spasi):", "BBCA.JK BBRI.JK BMRI.JK")
tickers = [t.strip().upper() for t in search_input.split() if t.strip()]

if tickers:
    for i in range(0, len(tickers), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(tickers):
                ticker = tickers[idx]
                with cols[j]:
                    df = get_stock_data(ticker)
                    
                    if df is not None and not df.empty:
                        # Handle Multi-index kolom yfinance
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                        
                        prices = df['Close'].astype(float)
                        last_price = prices.iloc[-1]
                        open_price = prices.iloc[0]
                        change = last_price - open_price
                        pct_change = (change / open_price) * 100
                        
                        # Warna Grafik
                        color = "#00FF41" if change >= 0 else "#FF4B4B"

                        # --- PLOTLY CHART ---
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df.index, 
                            y=prices,
                            mode='lines',
                            line=dict(color=color, width=2),
                            fill='tozeroy',
                            fillcolor=f"rgba({ '0,255,65' if change >= 0 else '255,75,75' }, 0.1)",
                            hoverinfo='x+y'
                        ))

                        # PERBAIKAN SUMBU Y (Agar tidak mulai dari 0)
                        # autorange=True dengan rangemode='nonnegative' atau 'normal'
                        fig.update_layout(
                            title=f"<b>{ticker}</b><br><span style='font-size:18px;'>{last_price:,.0f} ({pct_change:+.2f}%)</span>",
                            template="plotly_dark",
                            height=350,
                            margin=dict(l=10, r=10, t=60, b=10),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(
                                showgrid=True, 
                                gridcolor="#333", 
                                side="right",
                                # Ini kuncinya: Memaksa sumbu Y fokus ke range data
                                autorange=True,
                                fixedrange=False 
                            ),
                            hovermode="x unified"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Ticker {ticker} tidak valid.")
