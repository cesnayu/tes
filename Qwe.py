import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")
st.title("📈 Stock Performance Analyzer")

# --- SIDEBAR ---
st.sidebar.header("Filter")
ticker = st.sidebar.text_input("Simbol Saham", value="BBCA.JK").upper()
start_date = st.sidebar.date_input("Dari Tanggal", value=date(2026, 1, 1))
end_date = st.sidebar.date_input("Sampai Tanggal", value=date(2026, 2, 19)) # Update ke Feb 2026

# --- AMBIL DATA ---
data = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1))

if not data.empty:
    # 1. Tampilan Grafik Utama
    st.subheader(f"Pergerakan Harga {ticker}")
    st.line_chart(data['Close'])

    st.divider()

    # --- FITUR ANALISIS TANGGAL (CUSTOM TABLE) ---
    st.subheader("🔍 Analisis Persentase Perubahan Per Tanggal")
    
    available_dates = data.index.strftime('%Y-%m-%d').tolist()
    selected = st.multiselect(
        "Pilih tanggal untuk dihitung (Contoh: 2026-01-06, 2026-02-02):",
        options=available_dates,
        default=available_dates[:3] if len(available_dates) > 3 else available_dates
    )

    if selected:
        # Filter data berdasarkan pilihan
        sub_data = data.loc[data.index.isin(selected)].copy()
        
        # HITUNG: ((Close - Open) / Open) * 100
        # Menggunakan rumus: (sub_data['Close'] - sub_data['Open']) / sub_data['Open'] * 100
        sub_data['Pct_Change'] = ((sub_data['Close'] - sub_data['Open']) / sub_data['Open']) * 100
        
        # Siapkan DataFrame untuk Transpose
        # Kita ambil kolom 'Pct_Change' saja, index-nya adalah Tanggal
        final_df = sub_data[['Pct_Change']].T 
        
        # Ubah nama index baris menjadi Nama Saham (Ticker)
        final_df.index = [ticker]
        
        # Tampilkan Tabel
        st.write("Tabel Persentase Perubahan ($ \Delta \% $):")
        
        # Beri styling agar angka terlihat lebih rapi (2 desimal + %)
        st.dataframe(final_df.style.format("{:.2f}%"))
        
        st.caption("Rumus: $((Close - Open) / Open) * 100$")
    else:
        st.info("Pilih tanggal pada kotak di atas untuk memunculkan tabel analisis.")

else:
    st.error("Data tidak ditemukan. Cek kembali ticker atau rentang tanggal.")

