import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Day Trading + 5D History", layout="wide")

st.title("📈 Dashboard Intraday & Histori 5 Hari")

with st.sidebar:
    st.header("Konfigurasi")
    default_list = "GOTO.JK, ANTM.JK, ADRO.JK, BRPT.JK, MEDC.JK, BBRI.JK, TLKM.JK, ASII.JK"
    input_saham = st.text_area("List Saham:", value=default_list)
    btn_refresh = st.button("🔄 Jalankan Scan")

def get_combined_data(tickers_str):
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]
    results = []
    
    p_bar = st.progress(0)
    for idx, ticker in enumerate(tickers):
        try:
            # 1. Ambil data harian untuk histori 5 hari
            hist = yf.download(ticker, period="10d", interval="1d", progress=False, auto_adjust=True)
            # 2. Ambil data menit untuk real-time hari ini
            live = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
            
            if not hist.empty and not live.empty:
                # Perhitungan Real-time
                open_p = float(live['Open'].iloc[0])
                curr_p = float(live['Close'].iloc[-1])
                diff_open = round(((curr_p - open_p) / open_p) * 100, 2)
                
                # Perhitungan Histori 5 Hari (Daily Return)
                # Ambil 6 hari terakhir untuk dapat 5 selisih (Return)
                last_6_days = hist.tail(6).copy()
                last_6_days['Return'] = last_6_days['Close'].pct_change() * 100
                returns = last_6_days['Return'].dropna().tail(5)
                
                row = {
                    'Ticker': ticker,
                    'Last Price': round(curr_p, 2),
                    'vs Open (%)': diff_open,
                }
                
                # Tambahkan kolom tanggal untuk 5 hari terakhir
                for date, val in returns.items():
                    row[date.strftime('%d/%m')] = round(val, 2)
                
                # Tambahkan Rata-rata Return 5 hari
                row['Avg 5D (%)'] = round(returns.mean(), 2)
                
                results.append(row)
        except:
            continue
        p_bar.progress((idx + 1) / len(tickers))
    return pd.DataFrame(results)

if btn_refresh:
    df_final = get_combined_data(input_saham)
    
    if not df_final.empty:
        # Urutkan berdasarkan performa hari ini (vs Open)
        df_display = df_final.sort_values(by='vs Open (%)', ascending=False)
        
        st.subheader("Tabel Pergerakan: Real-time vs Histori 5 Hari")
        
        # Styling: Hijau untuk untung, Merah untuk rugi
        def color_picker(val):
            if isinstance(val, (int, float)):
                color = '#2ecc71' if val > 0 else '#e74c3c' if val < 0 else 'white'
                return f'color: {color}; font-weight: bold'
            return ''

        # Terapkan styling ke kolom persentase
        target_cols = [c for c in df_display.columns if c not in ['Ticker', 'Last Price']]
        st.dataframe(
            df_display.style.applymap(color_picker, subset=target_cols),
            use_container_width=True
        )
        
        st.info("💡 Kolom tanggal menunjukkan return harian (Close vs Prev Close). Kolom 'vs Open' menunjukkan performa hari ini saja.")
    else:
        st.warning("Data tidak ditemukan. Pastikan list saham benar.")
