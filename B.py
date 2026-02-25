import streamlit as st
import yfinance as yf
import pandas as pd
import calendar
from datetime import datetime, timedelta

st.set_page_config(page_title="Tabel Fluktuasi Saham", layout="wide")

st.title("Tabel Persentase Rentang Harian Saham (High vs Low)")
st.write("Menampilkan persentase selisih harga High dan Low harian: `((High - Low) / Low) * 100%`")

# 1. Input Ticker Saham (Default 10 saham kapitalisasi besar IHSG)
default_tickers = "BBCA.JK, BBRI.JK, BMRI.JK, TLKM.JK, ASII.JK, UNTR.JK, ICBP.JK, INDF.JK, BBNI.JK, AMMN.JK"
tickers_input = st.text_input("Masukkan Ticker Saham (pisahkan dengan koma):", default_tickers)
tickers = [t.strip() for t in tickers_input.split(',')]

# 2. Input Pemilihan Bulan dan Tahun
col1, col2 = st.columns(2)
with col1:
    # Nama bulan untuk display
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    selected_month_name = st.selectbox("Pilih Bulan:", nama_bulan, index=datetime.now().month - 1)
    selected_month = nama_bulan.index(selected_month_name) + 1
with col2:
    selected_year = st.selectbox("Pilih Tahun:", list(range(2020, 2030)), index=list(range(2020, 2030)).index(datetime.now().year))

if st.button("Tarik Data & Buat Tabel"):
    with st.spinner("Mengunduh data saham..."):
        # 3. Menentukan rentang tanggal berdasarkan bulan & tahun yang dipilih
        _, last_day = calendar.monthrange(selected_year, selected_month)
        start_date = f"{selected_year}-{selected_month:02d}-01"
        
        # Tambah 1 hari di end_date agar hari terakhir di bulan tersebut ikut terambil oleh yfinance
        end_date_obj = datetime(selected_year, selected_month, last_day) + timedelta(days=1)
        end_date = end_date_obj.strftime("%Y-%m-%d")

        # 4. Download data menggunakan yfinance
        df = yf.download(tickers, start=start_date, end=end_date, progress=False)

        if df.empty:
            st.warning("Data tidak ditemukan untuk periode tersebut. Pastikan ticker valid atau pasar sedang buka di bulan tersebut.")
        else:
            # 5. Ekstrak kolom High dan Low
            # Jika hanya 1 ticker, strukturnya berbeda dengan banyak ticker, jadi kita handle keduanya
            if len(tickers) == 1:
                high = df[['High']]
                low = df[['Low']]
                # Rename column to match the logic below
                high.columns = tickers
                low.columns = tickers
            else:
                high = df['High']
                low = df['Low']
            
            # 6. Hitung persentase fluktuasi
            spread_pct = ((high - low) / low) * 100
            
            # 7. Pivot tabel (Transpose) agar Baris = Ticker, Kolom = Tanggal
            result_df = spread_pct.T
            
            # Ubah format header kolom menjadi tanggal saja (misal: 01-10-2025)
            result_df.columns = result_df.columns.strftime('%d-%m-%Y')
            
            # Urutkan index (ticker) sesuai abjad
            result_df = result_df.sort_index()

            # 8. Tampilkan ke dalam dataframe Streamlit dengan format 2 angka di belakang koma plus tanda '%'
            st.success(f"Berhasil menarik data untuk {len(tickers)} saham pada {selected_month_name} {selected_year}.")
            st.dataframe(result_df.style.format("{:.2f}%", na_rep="Libur/NaN"), use_container_width=True)
