import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Day Trading Scanner", layout="wide")

st.title("📈 Day Trading Volatility Scanner")
st.write("Menganalisa rentang High-Low harian untuk mencari saham yang 'licin'.")

# Sidebar untuk Input
with st.sidebar:
    st.header("Konfigurasi")
    input_saham = st.text_area("Masukkan Kode Saham (pisahkan dengan koma):", 
                                "GOTO.JK, ANTM.JK, ADRO.JK, BRPT.JK, MEDC.JK, BBRI.JK, TLKM.JK, ASII.JK")
    threshold = st.slider("Ambang Batas Volatilitas (%)", 1.0, 10.0, 3.0)
    tombol_proses = st.button("Scan Saham")

# Fungsi untuk memproses data
def get_data(tickers_str, threshold):
    tickers = [t.strip() for t in tickers_str.split(",")]
    final_data = []
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="10d", interval="1d", progress=False)
            if len(data) < 5: continue
                
            last_5 = data.tail(5).copy()
            # Hitung Rentang High-Low
            last_5['HL_Pct'] = (last_5['High'] - last_5['Low']) / last_5['Low'] * 100
            
            dates = last_5.index.strftime('%d/%m').tolist()
            ranges = last_5['HL_Pct'].tolist()
            count_met = (last_5['HL_Pct'] >= threshold).sum()
            
            row = {'Ticker': ticker}
            for i in range(5):
                row[dates[i]] = round(ranges[i], 2)
            
            row['Freq'] = count_met
            final_data.append(row)
        except:
            continue
            
    return pd.DataFrame(final_data)

# Logika Tampilan
if tombol_proses:
    df = get_data(input_saham, threshold)
    
    if not df.empty:
        # Mengurutkan berdasarkan tanggal terbaru secara default
        kolom_terbaru = df.columns[-2]
        df = df.sort_values(by=kolom_terbaru, ascending=False)
        
        # Fungsi styling untuk memberi warna
        def highlight_volatility(val):
            if isinstance(val, (int, float)) and val >= threshold:
                return 'background-color: #2ecc71; color: white'
            return ''

        # Tampilkan Tabel dengan Style
        st.subheader(f"Hasil Analisa (Urutan Berdasarkan Tgl Terakhir: {kolom_terbaru})")
        st.dataframe(df.style.applymap(highlight_volatility, subset=df.columns[1:-1]), 
                     use_container_width=True, height=400)
        
        st.success(f"Tips: Fokus pada saham dengan 'Freq' tinggi dan sel berwarna hijau.")
    else:
        st.error("Data tidak ditemukan. Pastikan format ticker benar (contoh: ASII.JK).")

