import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Dynamic Stock Dashboard", layout="wide")

st.title("📈 Stock Data Explorer")

# --- SIDEBAR: INPUT DINAMIS ---
st.sidebar.header("Filter Pencarian")

ticker = st.sidebar.text_input("Simbol Saham", value="BBCA.JK")

# Mengatur default start_date ke 1 bulan lalu dan end_date ke hari ini
default_start = date.today() - timedelta(days=60) 
today = date.today()

# User bebas memilih tanggal kapanpun lewat kalender
start_date = st.sidebar.date_input("Dari Tanggal", value=default_start)
end_date = st.sidebar.date_input("Sampai Tanggal", value=today)

# --- PROSES DATA ---
# Logic: Ambil data berdasarkan input kalender user
if start_date <= end_date:
    # Kita tarik datanya (End date +1 agar hari terakhir masuk hitungan)
    data = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1))
    
    if not data.empty:
        # --- TABEL DATA ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📍 Data Open & Close")
            # Menampilkan data yang ditarik
            display_df = data[['Open', 'Close']].copy()
            # Format agar tanggal lebih enak dibaca
            display_df.index = display_df.index.strftime('%d %B %Y')
            st.dataframe(display_df, use_container_width=True)

        with col2:
            st.subheader("📊 Pergerakan Harga")
            st.line_chart(data['Close'])

        # --- FITUR PICKER TANGGAL SPESIFIK ---
        st.divider()
        st.subheader("🔍 Cari Tanggal Tertentu")
        
        # Ambil semua list tanggal yang ada di data yang sudah di-download
        all_dates = data.index.strftime('%Y-%m-%d').tolist()
        
        selected = st.multiselect(
            "Pilih tanggal spesifik (bisa pilih banyak):",
            options=all_dates,
            help="Ketik atau pilih tanggal, misal 2026-01-06 atau 2026-02-02"
        )

        if selected:
            # Filter hanya yang dipilih user
            filtered = data.loc[data.index.isin(selected)]
            st.write(f"Hasil untuk {len(selected)} tanggal terpilih:")
            st.table(filtered[['Open', 'Close']])
            
    else:
        st.warning("Data tidak tersedia untuk rentang tanggal ini. Coba cek apakah bursa sedang libur.")
else:
    st.error("Error: Tanggal 'Mulai' tidak boleh lebih besar dari tanggal 'Selesai'.")
