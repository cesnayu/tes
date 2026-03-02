import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Fundamental Stock Dashboard", layout="wide")

st.title("📊 Financial Ratio Dashboard")
st.write("Masukkan kode saham (misal: BBCA.JK atau AAPL) untuk melihat ROE dan ROA.")

# Sidebar untuk input user
ticker_symbol = st.sidebar.text_input("Ticker Saham", value="BBCA.JK")

if ticker_symbol:
    try:
        # Fetch data dari Yahoo Finance
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # Ambil data spesifik
        name = info.get('longName', 'N/A')
        current_price = info.get('currentPrice', 'N/A')
        currency = info.get('currency', 'USD')
        
        # Fundamental Metrics (ROE & ROA dalam desimal, jadi dikali 100)
        roe = info.get('returnOnEquity', 0) * 100
        roa = info.get('returnOnAssets', 0) * 100
        net_margin = info.get('profitMargins', 0) * 100

        # Menampilkan Informasi Utama
        st.subheader(f"{name} ({ticker_symbol})")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Harga Terakhir", f"{current_price} {currency}")
        col2.metric("ROE", f"{roe:.2f}%")
        col3.metric("ROA", f"{roa:.2f}%")

        # Visualisasi sederhana dengan Bar Chart
        st.write("---")
        st.subheader("Perbandingan Profitabilitas")
        
        df_metrics = pd.DataFrame({
            'Metrik': ['ROE', 'ROA', 'Profit Margin'],
            'Persentase (%)': [roe, roa, net_margin]
        })
        
        st.bar_chart(df_metrics.set_index('Metrik'))

        # Menampilkan data mentah di expander
        with st.expander("Lihat Data Fundamental Lainnya"):
            st.write(info)

    except Exception as e:
        st.error(f"Gagal mengambil data. Pastikan ticker benar. Error: {e}")
