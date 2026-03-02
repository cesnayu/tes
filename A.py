import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests_cache

# Membuat session cache agar tidak kena rate limit terus menerus
# Cache akan disimpan selama 1 jam (3600 detik)
session = requests_cache.CachedSession('yfinance.cache')
session.expire_after = 3600

def get_stock_data(tickers):
    all_data = []
    for ticker_symbol in tickers:
        try:
            # Gunakan session cache
            stock = yf.Ticker(ticker_symbol, session=session)
            
            # Gunakan fast_info untuk data harga dan kapitalisasi
            f_info = stock.fast_info
            # Untuk fundamental detail, kita terpaksa pakai info tapi dengan proteksi
            info = stock.info 
            
            price = f_info.get('last_price', 1)
            eps = info.get('trailingEps', 0)
            
            all_data.append({
                'Ticker': ticker_symbol.replace('.JK', ''),
                'EPS': eps,
                'PER': info.get('trailingPE', 0),
                'PBV': info.get('priceToBook', 0),
                'ROA (%)': info.get('returnOnAssets', 0) * 100,
                'ROE (%)': info.get('returnOnEquity', 0) * 100,
                'DER': info.get('debtToEquity', 0),
                'RPS': info.get('totalRevenue', 0) / f_info.get('shares', 1),
                'EY (%)': (eps / price * 100) if price > 0 else 0
            })
        except Exception:
            st.error(f"Gagal mengambil data {ticker_symbol}. Coba lagi nanti.")
            
    return pd.DataFrame(all_data)

# --- UI STREAMLIT ---
st.title("📈 Stock Dashboard Pro")
user_input = st.text_input("Masukkan Kode (contoh: BBCA.JK, ASII.JK)", "BBCA.JK, ASII.JK")
daftar_saham = [t.strip().upper() for t in user_input.split(",")]

if st.button("Jalankan Dashboard"):
    df = get_stock_data(daftar_saham)
    if not df.empty:
        # Tampilkan Tabel
        st.dataframe(df.style.highlight_max(axis=0, color='#1e40af'))
        
        # Visualisasi
        metrics = ['EPS', 'PER', 'PBV', 'ROA (%)', 'ROE (%)', 'DER', 'RPS', 'EY (%)']
        fig, axes = plt.subplots(4, 2, figsize=(12, 18))
        axes = axes.flatten()
        
        for i, m in enumerate(metrics):
            sns.barplot(x='Ticker', y=m, data=df, ax=axes[i], hue='Ticker', palette='viridis', legend=False)
            axes[i].set_title(m, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
