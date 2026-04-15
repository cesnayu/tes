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
# 2. PROSES DAN TAMPILAN GRID (VERSI PALING AMAN)
# ==========================================
n_cols = 2 
rows = [st.columns(n_cols) for _ in range((len(my_stocks) + n_cols - 1) // n_cols)]
cols = [col for row in rows for col in row]

for i, ticker_symbol in enumerate(my_stocks):
    with cols[i]:
        try:
            # 1. Menggunakan .history() karena formatnya lebih stabil dari .download()
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period=yf_period)
            
            if not data.empty and 'Close' in data.columns:
                
                # 2. OBAT ANTI ERROR GRAFIK: Menghilangkan zona waktu (timezone) dari penanggalan
                data.index = data.index.tz_localize(None)
                
                close_prices = data['Close'].dropna()
                
                if len(close_prices) >= 2:
                    # Menghitung persentase return kumulatif
                    return_pct = (close_prices / close_prices.iloc[0] - 1) * 100
                    
                    current_val = float(close_prices.iloc[-1])
                    change = float(return_pct.iloc[-1])
                    
                    st.subheader(f"📈 {ticker_symbol.replace('.JK', '')}")
                    st.caption(f"Harga: Rp {current_val:,.0f} | Total Return: {change:.2f}%")
                    
                    # Menggambar grafik
                    st.area_chart(return_pct, height=300, use_container_width=True)
                else:
                    st.warning(f"⚠️ Data {ticker_symbol} kurang dari 2 hari.")
            else:
                st.warning(f"⚠️ Data {ticker_symbol} tidak ditemukan di Yahoo Finance.")
                
        except Exception as e:
            # Pesan error disederhanakan agar tidak menakutkan
            st.error(f"Grafik {ticker_symbol.replace('.JK', '')} gagal dimuat.")

st.divider()
st.info("💡 Tip: Gunakan 2 kolom (n_cols = 2) agar grafik memiliki ruang vertikal yang cukup dan tidak terlihat gepeng.")
