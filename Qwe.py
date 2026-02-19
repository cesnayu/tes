import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Stock Analyzer", layout="wide")

st.title("📈 Stock Performance Analyzer")

# --- SIDEBAR ---
st.sidebar.header("Filter")
ticker_input = st.sidebar.text_input("Simbol Saham", value="BBCA.JK").upper()
start_date = st.sidebar.date_input("Dari Tanggal", value=date(2026, 1, 1))
end_date = st.sidebar.date_input("Sampai Tanggal", value=date.today())

# Tombol Refresh Manual
if st.sidebar.button("Tarik Data Terbaru"):
    st.rerun()

# --- PROSES AMBIL DATA DENGAN ERROR HANDLING ---
try:
    # Menarik data
    data = yf.download(ticker_input, start=start_date, end=end_date + timedelta(days=1))
    
    if data.empty:
        st.warning(f"Data untuk {ticker_input} kosong. Coba cek koneksi internet atau simbol saham (pastikan pakai .JK untuk saham Indonesia).")
    else:
        # --- FITUR ANALISIS TANGGAL ---
        st.subheader("🔍 Analisis Persentase Perubahan")
        
        available_dates = data.index.strftime('%Y-%m-%d').tolist()
        selected = st.multiselect(
            "Pilih tanggal (bisa ketik tgl di sini):",
            options=available_dates,
            default=available_dates[:3] if len(available_dates) >= 3 else available_dates
        )

        if selected:
            # Ambil data spesifik & hitung % Change
            sub_data = data.loc[data.index.isin(selected)].copy()
            
            # Rumus (Close - Open) / Open * 100
            # Kita gunakan .iloc untuk memastikan mengambil kolom yang benar jika data multi-index
            pct_change = ((sub_data['Close'] - sub_data['Open']) / sub_data['Open']) * 100
            
            # Buat DataFrame Transpose
            final_df = pd.DataFrame(pct_change).T
            final_df.index = [ticker_input]
            final_df.columns = selected # Pastikan nama kolom adalah tanggalnya
            
            # Tampilan Tabel dengan Warna (Hijau untuk +, Merah untuk -)
            def color_negative_red(val):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'

            st.write("Tabel Persentase Perubahan:")
            st.dataframe(final_df.style.applymap(color_negative_red).format("{:.2f}%"))
            
            # Grafik pendukung
            st.divider()
            st.line_chart(data['Close'])
        else:
            st.info("Pilih tanggal di atas untuk melihat tabel.")

except Exception as e:
    st.error("Terjadi kesalahan teknis:")
    st.exception(e) # Ini akan memunculkan detail error daripada layar putih
