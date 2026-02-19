import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Bulk Stock Analyzer", layout="wide")

# --- INISIALISASI SESSION STATE ---
# Ini penting agar saat refresh, data lama tetap tersimpan di memori browser
if 'start_date' not in st.session_state:
    st.session_state.start_date = date(2026, 1, 1)
if 'end_date' not in st.session_state:
    st.session_state.end_date = date.today()
if 'tickers' not in st.session_state:
    st.session_state.tickers = "BBCA.JK, BBRI.JK, TLKM.JK"

st.title("📊 Multi-Stock Performance Analyzer")

# --- SIDEBAR ---
st.sidebar.header("Konfigurasi")

# Gunakan key= untuk mengikat widget ke session_state
tickers_input = st.sidebar.text_area(
    "Masukkan List Ticker:", 
    value=st.session_state.tickers,
    key="tickers_input"
)

# Gunakan value dari session_state agar tidak balik ke awal
start_date = st.sidebar.date_input("Dari Tanggal", value=st.session_state.start_date, key="input_start")
end_date = st.sidebar.date_input("Sampai Tanggal", value=st.session_state.end_date, key="input_end")

# Simpan pilihan terbaru ke session state
st.session_state.start_date = start_date
st.session_state.end_date = end_date
st.session_state.tickers = tickers_input

ticker_list = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]

# --- TOMBOL PROSES ---
# Pakai container agar hasil tidak hilang saat pilih tanggal di multiselect
if st.sidebar.button("Proses & Kunci Data"):
    st.session_state.load_data = True

if st.session_state.get('load_data'):
    with st.spinner("Menarik data massal..."):
        # Tambahkan caching agar tidak download ulang terus setiap klik
        @st.cache_data(ttl=3600) # Data disimpan selama 1 jam di memori
        def get_data(tickers, start, end):
            return yf.download(tickers, start=start, end=end + timedelta(days=1), threads=True)

        raw_data = get_data(ticker_list, start_date, end_date)

        if not raw_data.empty:
            st.subheader("🔍 Analisis Persentase Perubahan")
            
            available_dates = raw_data.index.strftime('%Y-%m-%d').tolist()
            
            # Gunakan key pada multiselect agar pilihannya tidak hilang saat ganti tanggal lain
            selected_dates = st.multiselect(
                "Pilih tanggal kolom:",
                options=available_dates,
                key="date_selector" 
            )

            if selected_dates:
                # Perhitungan
                open_prices = raw_data['Open'].loc[selected_dates]
                close_prices = raw_data['Close'].loc[selected_dates]
                
                pct_change_table = ((close_prices - open_prices) / open_prices) * 100
                final_df = pct_change_table.T
                
                # Styling
                st.dataframe(
                    final_df.style.highlight_max(axis=0, color='#006400')
                                 .highlight_min(axis=0, color='#8B0000')
                                 .format("{:.2f}%"),
                    height=500
                )
