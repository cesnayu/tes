import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Real-Time Stock Dashboard")

# --- AUTO REFRESH ---
# Refresh otomatis setiap 60.000 ms (1 menit)
# Jika belum install: pip install streamlit-autorefresh
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, key="datarefresh")
except ImportWarning:
    st.info("Tips: Install 'streamlit-autorefresh' untuk update otomatis.")

# --- UI HEADER ---
st.title("📊 Multi-Stock Intraday Dashboard")
st.markdown("Masukkan kode saham dipisahkan dengan spasi (Contoh: `BBCA.JK BBRI.JK TLKM.JK AAPL TSLA`)")

# Input pencarian (Default: BBCA, BBRI, BMRI)
search_input = st.text_input("Search Tickers:", "BBCA.JK BBRI.JK BMRI.JK")
tickers = [t.strip().upper() for t in search_input.split() if t.strip()]

# --- FUNGSI AMBIL DATA ---
def get_stock_data(ticker):
    try:
        # Mengambil data 1 menit untuk hari ini
        # auto_adjust=True membantu menormalkan kolom
        data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        
        # Jika hari ini kosong (market belum buka/libur), ambil data hari terakhir buka
        if data.empty:
            data = yf.download(ticker, period="5d", interval="1m", progress=False, auto_adjust=True)
            # Ambil hanya hari terakhir yang tersedia datanya
            last_date = data.index[-1].date()
            data = data[data.index.date == last_date]
            
        return data
    except Exception as e:
        return None

# --- RENDER DASHBOARD ---
if tickers:
    # Membuat baris (rows) secara dinamis, tiap baris maksimal 3 kolom
    for i in range(0, len(tickers), 3):
        cols = st.columns(3)
        
        # Loop untuk mengisi 3 kolom dalam 1 baris
        for j in range(3):
            index_ticker = i + j
            if index_ticker < len(tickers):
                ticker = tickers[index_ticker]
                
                with cols[j]:
                    df = get_stock_data(ticker)
                    
                    if df is not None and not df.empty:
                        # Menangani potensi Multi-Index pada kolom yfinance terbaru
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)

                        try:
                            # Ambil harga terakhir dan harga pembukaan
                            latest_price = float(df['Close'].iloc[-1])
                            open_price = float(df['Close'].iloc[0])
                            price_change = latest_price - open_price
                            pct_change = (price_change / open_price) * 100
                            
                            # Tentukan warna (Hijau jika naik, Merah jika turun)
                            line_color = '#00ff41' if price_change >= 0 else '#ff4b4b'

                            # Plotly Chart (Smooth Rendering)
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df.index, 
                                y=df['Close'], 
                                mode='lines',
                                line=dict(width=2, color=line_color),
                                fill='tozeroy', # Memberikan efek area di bawah garis
                                fillcolor=f"rgba({ '0,255,65' if price_change >= 0 else '255,75,75' }, 0.1)",
                                name=ticker,
                                hoverinfo='x+y'
                            ))

                            fig.update_layout(
                                title=f"<b>{ticker}</b> <br><span style='font-size:20px;'>{latest_price:,.2f} ({pct_change:+.2f}%)</span>",
                                template="plotly_dark",
                                height=350,
                                margin=dict(l=10, r=10, t=60, b=10),
                                xaxis=dict(showgrid=False, title="Time"),
                                yaxis=dict(showgrid=True, gridcolor="#333", side="right"),
                                hovermode="x unified",
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                            )

                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Gagal memproses data {ticker}")
                    else:
                        st.warning(f"Data {ticker} tidak tersedia.")
else:
    st.info("Masukkan kode ticker untuk memulai.")

# --- FOOTER ---
st.caption(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data by Yahoo Finance")
