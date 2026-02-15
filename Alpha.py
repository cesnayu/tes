import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BEI Full Scanner", layout="wide")

st.title("🚀 BEI Full Market Volatility Scanner")
st.write("Menganalisa seluruh saham di Bursa Efek Indonesia untuk mencari peluang Day Trading.")

# 1. Fungsi Mengambil Daftar Semua Saham BEI
@st.cache_data # Cache agar tidak download ulang terus menerus
def get_all_idx_tickers():
    try:
        # Mengambil daftar dari Wikipedia (Daftar perusahaan di BEI)
        url = "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Indonesia_Stock_Exchange"
        tables = pd.read_html(url)
        # Biasanya ada di tabel tertentu, kita ambil kolom 'Ticker' atau 'Code'
        df_tickers = tables[1] # Tabel perusahaan
        tickers = df_tickers['Code'].tolist()
        return [str(t) + ".JK" for t in tickers]
    except:
        # Fallback list manual jika wiki gagal (sebagai contoh beberapa)
        return ["ASII.JK", "BBCA.JK", "GOTO.JK", "TLKM.JK", "ADRO.JK", "BRPT.JK", "ANTM.JK"]

# 2. Sidebar Konfigurasi
with st.sidebar:
    st.header("Filter Scanner")
    all_tickers = get_all_idx_tickers()
    st.write(f"Total Saham Ditemukan: {len(all_tickers)}")
    
    threshold = st.slider("Minimal Volatilitas Harian (%)", 1.0, 15.0, 3.0)
    min_freq = st.slider("Minimal Frekuensi (dalam 5 hari)", 1, 5, 3)
    min_volume_jt = st.number_input("Minimal Volume (Juta Lembar)", value=1.0)
    
    scan_button = st.button("Mulai Scan Seluruh Market")

# 3. Fungsi Pemrosesan Data
def scan_market(tickers, threshold, min_vol):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        try:
            # Update Progress
            if i % 10 == 0:
                progress_bar.progress((i + 1) / len(tickers))
                status_text.text(f"Memeriksa: {ticker}")
            
            # Ambil data singkat
            df = yf.download(ticker, period="7d", interval="1d", progress=False)
            if len(df) < 5: continue
            
            last_5 = df.tail(5).copy()
            last_5['HL_Pct'] = (last_5['High'] - last_5['Low']) / last_5['Low'] * 100
            
            # Hitung Frekuensi
            freq = (last_5['HL_Pct'] >= threshold).sum()
            avg_vol_jt = (last_5['Volume'].mean() / 1_000_000)
            
            # Filter Awal: Hanya masukkan yang frekuensinya masuk kriteria
            if freq >= min_freq and avg_vol_jt >= min_vol:
                dates = last_5.index.strftime('%d/%m').tolist()
                ranges = last_5['HL_Pct'].tolist()
                
                row = {'Ticker': ticker, 'Avg Vol (M)': round(avg_vol_jt, 2)}
                for j in range(5):
                    row[dates[j]] = round(ranges[j], 2)
                
                row['Freq'] = freq
                results.append(row)
        except:
            continue
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)

# 4. Tampilan Hasil
if scan_button:
    with st.spinner('Sedang memindai seluruh bursa... (Mungkin butuh 1-2 menit)'):
        final_df = scan_market(all_tickers, threshold, min_volume_jt)
    
    if not final_df.empty:
        st.subheader(f"✅ Saham yang Memenuhi Kriteria (Freq >= {min_freq} kali)")
        
        # Urutkan berdasarkan frekuensi tertinggi dan volatilitas terbaru
        kolom_tgl = final_df.columns[-2]
        final_df = final_df.sort_values(by=['Freq', kolom_tgl], ascending=False)
        
        # Tampilkan Tabel
        st.dataframe(final_df.style.background_gradient(subset=['Freq'], cmap='Greens'), 
                     use_container_width=True)
        
        # Fitur Download
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Hasil Scan (.csv)", csv, "scan_result.csv", "text/csv")
    else:
        st.warning("Tidak ada saham yang memenuhi kriteria saat ini.")
