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
    min_rebound = st.number_input("Minimal Rebound dari Low (%)", value=0.0, step=0.5)
    btn_refresh = st.button("🔄 Jalankan Scan")

def get_pro_data(tickers_str):
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    results = []
    
    p_bar = st.progress(0)
    for idx, ticker in enumerate(tickers):
        try:
            # Menggunakan auto_adjust=True untuk menghindari MultiIndex yang membingungkan
            data = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
            
            if not data.empty and len(data) > 1:
                # Memastikan kita mengambil nilai skalar tunggal
                open_p = float(data['Open'].iloc[0])
                curr_p = float(data['Close'].iloc[-1])
                high_p = float(data['High'].max())
                low_p = float(data['Low'].min())
                
                chg_from_open = ((curr_p - open_p) / open_p) * 100
                rebound_from_low = ((curr_p - low_p) / low_p) * 100
                drop_from_high = ((curr_p - high_p) / high_p) * 100
                
                results.append({
                    'Ticker': ticker,
                    'Current': round(curr_p, 2),
                    'Chg vs Open (%)': round(chg_from_open, 2),
                    'Rebound from Low (%)': round(rebound_from_low, 2),
                    'Drop from High (%)': round(drop_from_high, 2),
                    'High Harian': round(high_p, 2),
                    'Low Harian': round(low_p, 2)
                })
        except Exception as e:
            # st.write(f"Debug: {ticker} error {e}") # Aktifkan jika ingin melihat error per saham
            continue
        p_bar.progress((idx + 1) / len(tickers))
    return pd.DataFrame(results)

if btn_refresh:
    df_raw = get_pro_data(input_saham)
    
    # Perbaikan: Cek apakah DataFrame kosong atau tidak
    if not df_raw.empty:
        # Memastikan tipe data kolom adalah float
        df_raw['Rebound from Low (%)'] = pd.to_numeric(df_raw['Rebound from Low (%)'])
        
        # Filter data
        df_filtered = df_raw[df_raw['Rebound from Low (%)'] >= min_rebound].copy()
        
        if not df_filtered.empty:
            df_display = df_filtered.sort_values(by='Rebound from Low (%)', ascending=False)
            
            st.subheader("Analisa Pergerakan Harga (Intraday)")
            
            def style_logic(val, col):
                if col == 'Rebound from Low (%)': return 'color: #2ecc71; font-weight: bold'
                if col == 'Drop from High (%)': return 'color: #e74c3c; font-weight: bold'
                if col == 'Chg vs Open (%)':
                    return f"color: {'#2ecc71' if val > 0 else '#e74c3c'}"
                return ''

            st.dataframe(
                df_display.style.apply(lambda x: [style_logic(v, x.name) for v in x], axis=0),
                use_container_width=True
            )
        else:
            st.info("Tidak ada saham yang memenuhi kriteria filter.")
    else:
        st.warning("Data tidak ditemukan. Pastikan market sudah buka.")
