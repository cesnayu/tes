import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Advanced Day Trading Scanner", layout="wide")

st.title("📊 Intraday Momentum Scanner")
st.write(f"Update: {datetime.now().strftime('%H:%M:%S')} WIB")

with st.sidebar:
    st.header("Konfigurasi")
    default_list = "GOTO.JK, ANTM.JK, ADRO.JK, BRPT.JK, MEDC.JK, BBRI.JK, TLKM.JK, ASII.JK"
    input_saham = st.text_area("List Saham:", value=default_list)
    
    st.markdown("---")
    # Filter tambahan untuk mencari yang sedang 'mantul' (rebound)
    min_rebound = st.number_input("Minimal Rebound dari Low (%)", value=0.0, step=0.5)
    btn_refresh = st.button("🔄 Jalankan Scan")

def get_pro_data(tickers_str):
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    results = []
    
    p_bar = st.progress(0)
    for idx, ticker in enumerate(tickers):
        try:
            # Tarik data intraday 1 menit (Batching 1 day)
            data = yf.download(ticker, period="1d", interval="1m", progress=False)
            
            if not data.empty:
                open_p = data['Open'].iloc[0]
                curr_p = data['Close'].iloc[-1]
                high_p = data['High'].max()
                low_p = data['Low'].min()
                
                # Kalkulasi perbedaan 'Untung' vs 'Rugi' secara intraday
                chg_from_open = ((curr_p - open_p) / open_p) * 100
                rebound_from_low = ((curr_p - low_p) / low_p) * 100  # "Berapa persen naiknya dari bawah?"
                drop_from_high = ((curr_p - high_p) / high_p) * 100 # "Berapa persen turunnya dari atas?"
                
                results.append({
                    'Ticker': ticker,
                    'Current': round(curr_p, 2),
                    'Chg vs Open (%)': round(chg_from_open, 2),
                    'Rebound from Low (%)': round(rebound_from_low, 2), # UNTUNG (Hijau)
                    'Drop from High (%)': round(drop_from_high, 2),   # RUGI (Merah)
                    'High Harian': round(high_p, 2),
                    'Low Harian': round(low_p, 2)
                })
        except:
            continue
        p_bar.progress((idx + 1) / len(tickers))
    return pd.DataFrame(results)

if btn_refresh:
    df_pro = get_pro_data(input_saham)
    
    if not df_pro.empty:
        # Filter hanya yang punya rebound sesuai input user
        df_filtered = df_pro[df_pro['Rebound from Low (%)'] >= min_rebound]
        
        # Urutkan berdasarkan Rebound terbesar (Mencari saham yang paling kuat mantul)
        df_display = df_filtered.sort_values(by='Rebound from Low (%)', ascending=False)
        
        st.subheader("Analisa Pergerakan Harga (Intraday)")
        
        # Styling Tabel
        def style_logic(val, col):
            if col == 'Rebound from Low (%)':
                return 'color: #2ecc71; font-weight: bold' # Hijau untuk Untung/Mantul
            if col == 'Drop from High (%)':
                return 'color: #e74c3c; font-weight: bold' # Merah untuk Rugi/Drop
            if col == 'Chg vs Open (%)':
                color = '#2ecc71' if val > 0 else '#e74c3c'
                return f'color: {color}'
            return ''

        # Tampilkan DataFrame dengan style per kolom
        st.dataframe(
            df_display.style.apply(lambda x: [style_logic(v, x.name) for v in x], axis=0),
            use_container_width=True
        )
        
        # Penjelasan Strategi
        st.info("""
        💡 **Cara Baca:**
        - **Rebound from Low (%):** Jika angkanya besar, berarti saham ini sedang ditarik naik oleh pembeli setelah sempat jatuh. (Peluang Buy on Reversal).
        - **Drop from High (%):** Jika angkanya mendekati 0%, berarti harga sekarang sedang di pucuk (Breakout). Jika angkanya besar (misal -3%), berarti ada aksi ambil untung (Profit Taking).
        """)
    else:
        st.info("Tidak ada data yang memenuhi kriteria.")
