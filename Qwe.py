import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Bulk Stock Analyzer", layout="wide")

st.title("📊 Multi-Stock Performance Analyzer")

# --- SIDEBAR ---
st.sidebar.header("Konfigurasi")

# Contoh input: Kamu bisa paste 600 ticker di sini dipisahkan koma atau spasi
tickers_input = st.sidebar.text_area(
    "Masukkan List Ticker (pisahkan dengan spasi/koma):", 
    value="BBCA.JK, BBRI.JK, TLKM.JK, ASII.JK, UNTR.JK",
    help="Contoh: BBCA.JK BBRI.JK TLKM.JK"
)

start_date = st.sidebar.date_input("Dari Tanggal", value=date(2026, 1, 1))
end_date = st.sidebar.date_input("Sampai Tanggal", value=date.today())

# Bersihkan input ticker menjadi list
ticker_list = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]

if st.sidebar.button("Proses Data"):
    if len(ticker_list) > 0:
        with st.spinner(f"Menarik data {len(ticker_list)} saham... Mohon tunggu."):
            try:
                # 1. BULK DOWNLOAD (Efisien untuk banyak saham)
                # group_by='column' agar formatnya rapi
                raw_data = yf.download(
                    ticker_list, 
                    start=start_date, 
                    end=end_date + timedelta(days=1),
                    group_by='column',
                    threads=True # Mempercepat proses untuk 600 saham
                )

                if not raw_data.empty:
                    # 2. FILTER TANGGAL SPESIFIK
                    st.subheader("🔍 Hasil Analisis Persentase Perubahan")
                    
                    # Ambil daftar tanggal yang valid dari index
                    available_dates = raw_data.index.strftime('%Y-%m-%d').tolist()
                    
                    selected_dates = st.multiselect(
                        "Pilih tanggal kolom (Misal: 2026-01-06, 2026-01-13, 2026-02-02):",
                        options=available_dates,
                        default=available_dates[:5] if len(available_dates) > 5 else available_dates
                    )

                    if selected_dates:
                        # 3. PERHITUNGAN MENGGUNAKAN VEKTOR (Cepat untuk 600 saham)
                        # Rumus: ((Close - Open) / Open) * 100
                        open_prices = raw_data['Open'].loc[selected_dates]
                        close_prices = raw_data['Close'].loc[selected_dates]
                        
                        pct_change_table = ((close_prices - open_prices) / open_prices) * 100
                        
                        # Transpose agar Saham jadi Baris, Tanggal jadi Kolom
                        final_df = pct_change_table.T
                        
                        # Styling
                        def color_logic(val):
                            if val > 0: return 'color: #00ff00; font-weight: bold' # Hijau
                            elif val < 0: return 'color: #ff4b4b' # Merah
                            else: return 'color: white'

                        st.write(f"Menampilkan {len(final_df)} saham untuk {len(selected_dates)} tanggal:")
                        st.dataframe(
                            final_df.style.applymap(color_logic).format("{:.2f}%"),
                            height=600 # Agar enak di-scroll jika ada 600 baris
                        )
                        
                        # Download Button
                        csv = final_df.to_csv().encode('utf-8')
                        st.download_button("Download Hasil ke CSV", csv, "analisis_saham.csv", "text/csv")
                else:
                    st.error("Data kosong. Pastikan simbol ticker benar.")

            except Exception as e:
                st.error(f"Terjadi kesalahan saat menarik data.")
                st.exception(e)
    else:
        st.warning("Masukkan setidaknya satu ticker saham.")

st.info("Tips: Untuk 600 saham, pastikan koneksi internet stabil. Dashboard akan memproses secara massal menggunakan threads.")
