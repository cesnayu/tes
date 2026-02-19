import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Set konfigurasi halaman
st.set_page_config(layout="wide", page_title="Stock Return Dashboard")
st.title("📊 Custom Stock Return Dashboard")

# --- SIDEBAR: INPUT ---
st.sidebar.header("Pengaturan")

# Input List Saham
tickers_input = st.sidebar.text_input("Masukkan Kode Saham (pisahkan dengan koma):", 
                                     "BBCA.JK, TLKM.JK, ASII.JK, GOTO.JK")
tickers = [t.strip() for t in tickers_input.split(",")]

# Input List Tanggal
dates_input = st.sidebar.text_input("Masukkan Tanggal (YYYY-MM-DD):", 
                                   "2024-02-01, 2024-02-05, 2024-02-12")
target_dates = [d.strip() for d in dates_input.split(",")]

if st.sidebar.button("Run Analysis"):
    try:
        # Penentuan range data agar aman untuk perhitungan return
        all_dates = sorted([datetime.strptime(d, '%Y-%m-%d') for d in target_dates])
        start_fetch = (all_dates[0] - timedelta(days=10)).strftime('%Y-%m-%d')
        end_fetch = (all_dates[-1] + timedelta(days=2)).strftime('%Y-%m-%d')
        
        # 1. Download Data
        with st.spinner('Mengambil data dari Yahoo Finance...'):
            df_raw = yf.download(tickers, start=start_fetch, end=end_fetch)['Adj Close']
        
        # 2. Hitung Return
        df_returns = df_raw.pct_change() * 100
        
        # 3. Kumpulkan Data (Revisi bagian yang error tadi)
        analysis_list = []
        
        for date_str in target_dates:
            # Gunakan try-except di dalam loop agar jika 1 tanggal error, yang lain tetap jalan
            try:
                if date_str in df_raw.index:
                    for t in tickers:
                        c_p = df_raw.loc[date_str, t]
                        pct = df_returns.loc[date_str, t]
                        
                        # Baris yang tadi menyebabkan error sudah masuk ke list di sini
                        analysis_list.append({
                            "Ticker": t.replace('.JK', ''),
                            "Tanggal": date_str,
                            "Harga": round(c_p, 2),
                            "Return (%)": round(pct, 2)
                        })
                else:
                    st.warning(f"Tanggal {date_str} adalah hari libur bursa.")
            except Exception as e:
                st.error(f"Gagal memproses tanggal {date_str}: {e}")

        # 4. Transformasi ke Tabel Lebar (Wide Format)
        if analysis_list:
            df_long = pd.DataFrame(analysis_list)
            df_pivot = df_long.pivot(index='Ticker', columns='Tanggal', values=['Harga', 'Return (%)'])
            
            # Mengurutkan kolom: Harga (Tgl A), Return (Tgl A), Harga (Tgl B), dst.
            final_columns = []
            for d in target_dates:
                if any(df_long['Tanggal'] == d):
                    final_columns.append(('Harga', d))
                    final_columns.append(('Return (%)', d))
            
            df_final = df_pivot.reindex(columns=final_columns)
            df_final.columns = [f"{col[0]} ({col[1]})" for col in df_final.columns]
            df_final.reset_index(inplace=True)

            # 5. Styling dan Tampilkan
            st.subheader("Hasil Analisis Performa")
            
            def color_return(val):
                if isinstance(val, (int, float)):
                    if val > 0: return 'color: #00ff00; font-weight: bold'
                    if val < 0: return 'color: #ff4b4b; font-weight: bold'
                return ''

            st.dataframe(df_final.style.applymap(color_return, 
                         subset=[c for c in df_final.columns if 'Return' in c]),
                         use_container_width=True)
            
            # Fitur tambahan: Download Excel
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("Download Tabel (CSV)", csv, "data_saham.csv", "text/csv")
            
    except Exception as e:
        st.error(f"Error Utama: {e}. Pastikan format tanggal benar (YYYY-MM-DD).")
else:
    st.info("Masukkan kode saham & tanggal di kiri, lalu klik 'Run Analysis'")
