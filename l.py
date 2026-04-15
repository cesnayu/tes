import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Gallery Saham", layout="wide")

st.title("📊 Monitoring Semua Saham")
st.markdown("Menampilkan semua portfolio saham secara otomatis.")

# ==========================================
# 1. PENGATURAN DATA
# ==========================================
# Daftar saham yang ingin langsung ditampilkan semua
my_stocks = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BMRI.JK"]

col_config1, col_config2 = st.columns([1, 2])
with col_config1:
    periode = st.select_slider(
        "Pilih Rentang Waktu:",
        options=["1 Bulan", "3 Bulan", "6 Bulan"],
        value="1 Bulan"
    )
    # Konversi ke kode Yahoo Finance
    mapping = {"1 Bulan": "1mo", "3 Bulan": "3mo", "6 Bulan": "6mo"}
    yf_period = mapping[periode]

st.divider()

# ==========================================
# 2. PROSES DAN TAMPILAN GRID
# ==========================================
# Kita buat grid: 2 grafik per baris agar tidak terlihat gepeng dan kecil
n_cols = 2 
rows = [st.columns(n_cols) for _ in range((len(my_stocks) + n_cols - 1) // n_cols)]

# Meratakan list kolom agar mudah di-loop
cols = [col for row in rows for col in row]

for i, ticker_symbol in enumerate(my_stocks):
    with cols[i]:
        try:
            # Mengambil data
            data = yf.download(ticker_symbol, period=yf_period)
            
            if not data.empty:
                # Menghitung return kumulatif untuk grafik yang lebih cantik
                # (Harga / Harga Awal - 1) * 100
                close_prices = data['Close']
                return_pct = (close_prices / close_prices.iloc[0] - 1) * 100
                
                # Tampilan Header Kecil
                current_val = float(close_prices.iloc[-1])
                change = float(return_pct.iloc[-1])
                
                st.subheader(f"📈 {ticker_symbol.replace('.JK', '')}")
                st.caption(f"Harga: Rp {current_val:,.0f} | Total Return: {change:.2f}%")
                
                # MENGGAMBAR GRAFIK
                # Parameter height=300 atau 350 biasanya paling proporsional
                st.area_chart(return_pct, height=300, use_container_width=True)
                
            else:
                st.warning(f"Data {ticker_symbol} tidak ditemukan.")
                
        except Exception as e:
            st.error(f"Error pada {ticker_symbol}")

st.divider()
st.info("💡 Tip: Gunakan 2 kolom (n_cols = 2) agar grafik memiliki ruang vertikal yang cukup dan tidak terlihat gepeng.")
