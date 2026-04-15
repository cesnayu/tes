import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Return Harian Saham", layout="wide")

st.title("📊 Grafik Return Harian Saham")
st.markdown("Menampilkan fluktuasi persentase keuntungan/kerugian **setiap harinya**.")

# ==========================================
# 1. PENGATURAN DATA
# ==========================================
my_stocks = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BMRI.JK"]

col_config1, col_config2 = st.columns([1, 2])
with col_config1:
    periode = st.select_slider(
        "Pilih Rentang Waktu:",
        options=["1 Bulan", "3 Bulan", "6 Bulan"],
        value="1 Bulan"
    )
    mapping = {"1 Bulan": "1mo", "3 Bulan": "3mo", "6 Bulan": "6mo"}
    yf_period = mapping[periode]

st.divider()

# ==========================================
# 2. PROSES DAN MENGGAMBAR GRAFIK RETURN HARIAN
# ==========================================
n_cols = 2 
rows = [st.columns(n_cols) for _ in range((len(my_stocks) + n_cols - 1) // n_cols)]
cols = [col for row in rows for col in row]

for i, ticker_symbol in enumerate(my_stocks):
    with cols[i]:
        try:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period=yf_period)
            
            if not data.empty and 'Close' in data.columns:
                
                # Menghilangkan zona waktu (timezone) dari tanggal
                data.index = data.index.tz_localize(None)
                
                # RUMUS BENAR: Menghitung Return Harian (Selisih % dari hari sebelumnya)
                daily_return = data['Close'].pct_change() * 100
                
                # Membuang hari pertama karena tidak ada data hari sebelumnya untuk dihitung
                daily_return = daily_return.dropna()
                
                if len(daily_return) > 0:
                    
                    st.subheader(f"📉 {ticker_symbol.replace('.JK', '')}")
                    
                    # Menggunakan Bar Chart agar return plus/minus terlihat jelas ke atas dan ke bawah
                    st.bar_chart(daily_return, height=300, use_container_width=True)
                    
                else:
                    st.warning(f"⚠️ Data {ticker_symbol} kurang dari 2 hari.")
            else:
                st.warning(f"⚠️ Data {ticker_symbol} tidak ditemukan di Yahoo Finance.")
                
        except Exception as e:
            st.error(f"Grafik {ticker_symbol.replace('.JK', '')} gagal dimuat.")

st.divider()
