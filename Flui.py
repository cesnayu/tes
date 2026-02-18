import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Real-Time Stock Dashboard")

# --- HEADER ---
st.title("📈 Quick Stock Dashboard (Intraday)")
search_input = st.text_input("Search Ticker (misal: BBCA.JK, BBRI.JK, AAPL)", "BBCA.JK")

# Memisahkan input menjadi list (mendukung satu atau banyak saham)
tickers = [t.strip().upper() for t in search_input.split() if t.strip()]

# --- FUNGSI AMBIL DATA ---
def get_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m")
        if data.empty:
            # Jika hari ini belum ada data (market belum buka), ambil 2 hari terakhir
            data = yf.download(ticker, period="2d", interval="1m")
        return data
    except:
        return None

# --- LAYOUTING ---
# Menampilkan dalam baris (1 row = 3 kolom)
cols = st.columns(3)

for i, ticker in enumerate(tickers):
    with cols[i % 3]:
        df = get_stock_data(ticker)
        
        if df is not None and not df.empty:
            # Mengambil harga terakhir dan perubahan
            latest_price = df['Close'].iloc[-1]
            price_change = latest_price - df['Open'].iloc[0]
            pct_change = (price_change / df['Open'].iloc[0]) * 100

            # Membuat Grafik Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['Close'], 
                mode='lines',
                line=dict(width=2, color='#00ff41'),
                fill='tozeroy', # Efek gradient bawah
                name=ticker
            ))

            fig.update_layout(
                title=f"<b>{ticker}</b>: {latest_price:,.2f} ({pct_change:+.2f}%)",
                template="plotly_dark",
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis=dict(showgrid=False, rangeslider=dict(visible=False)),
                yaxis=dict(showgrid=True, gridcolor="#333"),
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Ticker {ticker} tidak ditemukan.")

# Auto-refresh tiap 60 detik
st.empty() 

