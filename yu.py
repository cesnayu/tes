import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Stock Performance Dashboard")
st.title("📈 Dashboard Performa Saham (%)")

# 1. Sidebar untuk Input
st.sidebar.header("Pengaturan")
list_saham = st.sidebar.text_input("Masukkan Kode Saham (pisahkan dengan koma)", "BBCA.JK, BBRI.JK, ASII.JK, TLKM.JK")
tickers = [t.strip() for t in list_saham.split(",")]

rentang = st.sidebar.selectbox("Rentang Waktu", ["1 bln", "6 bln", "1 thn"])

# Logika penentuan tanggal
end_date = datetime.now()
if rentang == "1 bln":
    start_date = end_date - timedelta(days=30)
elif rentang == "6 bln":
    start_date = end_date - timedelta(days=180)
else:
    start_date = end_date - timedelta(days=365)

# 2. Fungsi untuk Mengambil dan Mengolah Data
def get_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    if data.empty:
        return None
    
    # Ambil harga penutupan (Close)
    close_prices = data['Close']
    # Hitung persentase perubahan dari harga awal periode
    first_price = close_prices.iloc[0]
    pct_change = ((close_prices / first_price) - 1) * 100
    return pct_change, close_prices.iloc[-1]

# 3. Menampilkan Grid Grafik
cols = st.columns(3) # Membuat 3 kolom kotak

for i, ticker in enumerate(tickers):
    with cols[i % 3]: # Memasukkan grafik ke kolom secara bergantian
        data_pct, last_price = get_stock_data(ticker, start_date, end_date)
        
        if data_pct is not None:
            # Hitung statistik sederhana
            min_pct = data_pct.min()
            max_pct = data_pct.max()
            jarak_persen = max_pct - min_pct

            # Membuat Grafik Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data_pct.index, 
                y=data_pct, 
                mode='lines', 
                name=ticker,
                line=dict(width=2)
            ))

            fig.update_layout(
                title=f"<b>{ticker}</b>",
                xaxis_title="Tanggal",
                yaxis_title="Perubahan (%)",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                template="plotly_dark"
            )

            # Menampilkan Grafik dan Info
            st.plotly_chart(fig, use_container_width=True)
            st.write(f"Harga Terakhir: **Rp {last_price:,.0f}**")
            st.write(f"Rentang Perubahan: **{jarak_persen:.2f}%**")
            st.divider()
        else:
            st.error(f"Data {ticker} tidak ditemukan.")
