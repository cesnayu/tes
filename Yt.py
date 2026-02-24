import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("IHSG Stock MA Scanner")

# 1. List Saham (Bisa kamu tambah sampai ratusan)
tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "ADRO.JK", "UNVR.JK", "ICBP.JK", "AMMN.JK"] 
# Tips: Untuk ratusan saham, kamu bisa load dari file CSV atau list lengkap IHSG

@st.cache_data
def get_stock_data(list_ticker):
    all_results = []
    # Ambil data 1.5 tahun agar MA200 aman terhitung
    data = yf.download(list_ticker, period="2y", group_by='ticker', progress=False)
    
    for ticker in list_ticker:
        try:
            df = data[ticker].dropna()
            current_price = df['Close'].iloc[-1]
            
            # Hitung Moving Average
            ma_list = [20, 60, 120, 200]
            row = {'Ticker': ticker.replace('.JK', ''), 'Price': current_price}
            
            for ma in ma_list:
                ma_val = df['Close'].rolling(window=ma).mean().iloc[-1]
                # Hitung Persentase Jarak
                dist = ((current_price - ma_val) / ma_val) * 100
                row[f'MA {ma}'] = round(ma_val, 2)
                row[f'% Dist MA{ma}'] = round(dist, 2)
            
            all_results.append(row)
        except:
            continue
    return pd.DataFrame(all_results)

# 2. Proses Data
with st.spinner('Mengambil data dari Yahoo Finance...'):
    df_result = get_stock_data(tickers)

# 3. Tampilkan Tabel
st.write(f"Menampilkan {len(df_result)} saham")

# Tambahkan fitur coloring: Hijau jika di atas MA, Merah jika di bawah MA
def color_dist(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

# Tampilkan tabel dengan sorting & highlight
st.dataframe(
    df_result.style.applymap(color_dist, subset=[col for col in df_result.columns if '% Dist' in col]),
    use_container_width=True,
    height=600
)
