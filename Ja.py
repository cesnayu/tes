import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Stock Fundamental Table", layout="wide")

st.title("📊 Stock Fundamental Comparison")

# Fungsi untuk mengambil data dengan Cache agar tidak berat/limit API
@st.cache_data(ttl=3600)  # Data disimpan selama 1 jam
def get_stock_data(tickers_list):
    data_list = []
    for ticker_symbol in tickers_list:
        ticker_symbol = ticker_symbol.strip().upper()
        if not ticker_symbol:
            continue
            
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            # Ekstraksi data spesifik sesuai permintaan
            row = {
                "Ticker": ticker_symbol,
                "Nama Saham": info.get('longName', 'N/A'),
                "ROA (%)": info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                "ROE (%)": info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                "Revenue Per Share": info.get('revenuePerShare', 0),
                "Total Cash Per Share": info.get('totalCashPerShare', 0),
                "Total Debt/Equity": info.get('debtToEquity', 0),
                "Book Value Per Share": info.get('bookValue', 0),
                "Beta": info.get('beta', 0),
                "% Held by Insiders": info.get('heldPercentInsiders', 0) * 100 if info.get('heldPercentInsiders') else 0,
                "Annual Div Yield (%)": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            }
            data_list.append(row)
        except Exception as e:
            st.warning(f"Gagal mengambil data untuk {ticker_symbol}: {e}")
            
    return pd.DataFrame(data_list)

# Form Input (Mencegah Auto-Refresh setiap mengetik)
with st.sidebar.form(key='my_form'):
    st.header("Input Ticker")
    # User bisa memasukkan banyak ticker dipisah koma
    input_tickers = st.text_area("Masukkan Ticker (pisahkan dengan koma):", 
                                value="BBCA.JK, ASII.JK, AAPL, MSFT")
    submit_button = st.form_submit_button(label='Ambil Data')

# Logika Penampilan Data
if submit_button or 'df_result' in st.session_state:
    ticker_list = input_tickers.split(',')
    
    with st.spinner('Sedang mengambil data dari Yahoo Finance...'):
        df = get_stock_data(ticker_list)
        
    if not df.empty:
        # Menampilkan tabel dengan format angka agar rapi
        st.subheader("Tabel Perbandingan Fundamental")
        
        # Formatting untuk tampilan tabel
        styled_df = df.style.format({
            "ROA (%)": "{:.2f}%",
            "ROE (%)": "{:.2f}%",
            "Revenue Per Share": "{:.2f}",
            "Total Cash Per Share": "{:.2f}",
            "Total Debt/Equity": "{:.2f}",
            "Book Value Per Share": "{:.2f}",
            "Beta": "{:.2f}",
            "% Held by Insiders": "{:.2f}%",
            "Annual Div Yield (%)": "{:.2f}%"
        })
        
        st.table(styled_df) # Menggunakan st.table agar statis dan bersih
    else:
        st.info("Silahkan masukkan ticker dan tekan tombol 'Ambil Data'.")

