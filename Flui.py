import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Professional Stock Dashboard")

# --- AUTO REFRESH (Try-Except agar tidak error jika lib tidak ada) ---
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60000, key="datarefresh")
except:
    pass

# --- FUNGSI AMBIL DATA (DIPERBAIKI) ---
def get_stock_data(ticker):
    try:
        # 1. Download data 1 hari dengan interval 1 menit
        # Menggunakan group_by='column' untuk struktur data yang lebih konsisten
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        # 2. Jika hari ini kosong (market tutup), ambil data 5 hari terakhir
        if df.empty:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if not df.empty:
                # Ambil hanya hari perdagangan terakhir yang tersedia
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        # 3. Pembersihan Multi-Index (Penyebab utama "Ticker tidak valid" atau Grafik Flat)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        return None

# --- UI DASHBOARD ---
st.title("📊 Real-Time Intraday Dashboard")
st.markdown("Gunakan akhiran `.JK` untuk saham Indonesia (Contoh: `BBCA.JK BBNI.JK`).")

# Input pencarian
search_input = st.text_input("Ketik Kode Saham (Pisahkan dengan Spasi):", "BBCA.JK BBRI.JK BMRI.JK")
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
                    
                    # Validasi apakah data ada dan kolom 'Close' tersedia
                    if df is not None and not df.empty and 'Close' in df.columns:
                        try:
                            # Ambil data harga
                            prices = df['Close'].dropna()
                            latest_price = float(prices.iloc[-1])
                            open_price = float(prices.iloc[0])
                            change = latest_price - open_price
                            pct_change = (change / open_price) * 100
                            
                            color = "#00FF41" if change >= 0 else "#FF4B4B"

                            # --- PLOTLY CHART ---
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df.index, 
                                y=prices,
                                mode='lines',
                                line=dict(color=color, width=2),
                                fill='tonexty', # Mengisi area di bawah garis
                                fillcolor=f"rgba({ '0,255,65' if change >= 0 else '255,75,75' }, 0.1)",
                                hoverinfo='x+y'
                            ))

                            fig.update_layout(
                                title=f"<b>{ticker}</b><br><span style='font-size:20px;'>{latest_price:,.0f} ({pct_change:+.2f}%)</span>",
                                template="plotly_dark",
                                height=350,
                                margin=dict(l=10, r=10, t=60, b=10),
                                xaxis=dict(showgrid=False),
                                yaxis=dict(
                                    showgrid=True, 
                                    gridcolor="#333", 
                                    side="right",
                                    autorange=True, # AGAR TIDAK FLAT DARI 0
                                    fixedrange=False 
                                ),
                                hovermode="x unified"
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Gagal merender grafik {ticker}")
                    else:
                        st.error(f"Ticker '{ticker}' tidak ditemukan atau tidak ada data.")
else:
    st.info("Masukkan kode ticker untuk memulai.")
