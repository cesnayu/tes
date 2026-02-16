import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Advanced Day Trading Scanner", layout="wide")

st.title("📊 Intraday Momentum & 5-Day History")
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
            # 1. Ambil data menit untuk REAL-TIME hari ini
            data_live = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
            
            # 2. Ambil data harian untuk HISTORI 5 hari terakhir
            data_hist = yf.download(ticker, period="7d", interval="1d", progress=False, auto_adjust=True)
            
            if not data_live.empty and not data_hist.empty:
                # Logika Real-time
                open_p = float(data_live['Open'].iloc[0])
                curr_p = float(data_live['Close'].iloc[-1])
                high_p = float(data_live['High'].max())
                low_p = float(data_live['Low'].min())
                
                chg_from_open = ((curr_p - open_p) / open_p) * 100
                rebound_from_low = ((curr_p - low_p) / low_p) * 100
                drop_from_high = ((curr_p - high_p) / high_p) * 100
                
                # Logika Histori 5 Hari (Return harian Close to Close)
                # Ambil 6 data terakhir untuk dapat 5 selisih return harian
                returns_5d = data_hist['Close'].pct_change() * 100
                last_5_returns = returns_5d.dropna().tail(5)
                
                row = {
                    'Ticker': ticker,
                    'Current': round(curr_p, 2),
                    'Chg vs Open (%)': round(chg_from_open, 2),
                    'Rebound from Low (%)': round(rebound_from_low, 2),
                    'Drop from High (%)': round(drop_from_high, 2)
                }

                # Tambahkan kolom histori tanggal secara dinamis
                for date, val in last_5_returns.items():
                    row[date.strftime('%d/%m')] = round(val, 2)
                
                results.append(row)
        except Exception as e:
            continue
        p_bar.progress((idx + 1) / len(tickers))
    return pd.DataFrame(results)

if btn_refresh:
    df_raw = get_pro_data(input_saham)
    
    if not df_raw.empty:
        df_raw['Rebound from Low (%)'] = pd.to_numeric(df_raw['Rebound from Low (%)'])
        df_filtered = df_raw[df_raw['Rebound from Low (%)'] >= min_rebound].copy()
        
        if not df_filtered.empty:
            # Urutkan berdasarkan performa hari ini
            df_display = df_filtered.sort_values(by='Chg vs Open (%)', ascending=False)
            
            st.subheader("Analisa Intraday (Real-time) & Histori 5 Hari")
            
            def style_logic(val, col):
                if not isinstance(val, (int, float)): return ''
                # Kolom Rebound selalu hijau jika positif
                if col == 'Rebound from Low (%)': return 'color: #2ecc71; font-weight: bold'
                # Kolom Drop selalu merah jika negatif
                if col == 'Drop from High (%)': return 'color: #e74c3c; font-weight: bold'
                # Kolom dinamis tanggal & Chg vs Open mengikuti nilai +/-
                return f"color: {'#2ecc71' if val > 0 else '#e74c3c'}; font-weight: bold"

            # Tentukan kolom mana yang akan diberi warna (kecuali Ticker dan Current)
            styled_cols = [c for c in df_display.columns if c not in ['Ticker', 'Current']]
            
            st.dataframe(
                df_display.style.apply(lambda x: [style_logic(v, x.name) for v in x], axis=0, subset=styled_cols),
                use_container_width=True
            )
        else:
            st.info("Tidak ada saham yang memenuhi kriteria filter.")
    else:
        st.warning("Data tidak ditemukan. Pastikan market sudah buka.")
