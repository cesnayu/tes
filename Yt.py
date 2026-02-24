import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="Ultimate Stock Scanner")
st.title("IHSG Multi-Range High/Low & MA Scanner")

# List Ticker (Bisa ditambah sesuai kebutuhan)
tickers = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "ADRO.JK", "UNVR.JK", "ICBP.JK", "AMMN.JK", "BRIS.JK", "MEDC.JK"]

@st.cache_data
def get_comprehensive_data(list_ticker):
    all_results = []
    # Tarik data 2 tahun untuk memastikan semua range terhitung
    data = yf.download(list_ticker, period="2y", group_by='ticker', progress=False)
    
    for ticker in list_ticker:
        try:
            df = data[ticker].dropna()
            if len(df) < 250: continue
            
            current_price = df['Close'].iloc[-1]
            
            # Definisi Range (Minggu ke Hari Bursa)
            ranges = {
                '4W': 20,
                '12W': 60,
                '24W': 120,
                '52W': 250
            }
            
            row = {'Ticker': ticker.replace('.JK', ''), 'Price': current_price}
            
            # --- Hitung High/Low & % Distance ---
            for label, days in ranges.items():
                high_val = df['High'].tail(days).max()
                low_val = df['Low'].tail(days).min()
                
                # % Jarak ke High (diskon dari puncak range tersebut)
                dist_high = ((current_price - high_val) / high_val) * 100
                # % Jarak ke Low (kenaikan dari dasar range tersebut)
                dist_low = ((current_price - low_val) / low_val) * 100
                
                row[f'{label} High'] = round(high_val, 0)
                row[f'{label} Low'] = round(low_val, 0)
                row[f'% High {label}'] = round(dist_high, 2)
                row[f'% Low {label}'] = round(dist_low, 2)

            # --- Hitung Moving Averages ---
            for ma in [20, 60, 120, 200]:
                ma_val = df['Close'].rolling(window=ma).mean().iloc[-1]
                dist_ma = ((current_price - ma_val) / ma_val) * 100
                row[f'% Dist MA{ma}'] = round(dist_ma, 2)
            
            all_results.append(row)
        except:
            continue
    return pd.DataFrame(all_results)

with st.spinner('Menghitung data High/Low dan MA...'):
    df_result = get_comprehensive_data(tickers)

# Styling Warna
def color_logic(val):
    if isinstance(val, (int, float)):
        if val > 0: return 'color: #2ecc71' # Hijau
        if val < 0: return 'color: #e74c3c' # Merah
    return ''

# Tampilkan Tabel
st.dataframe(
    df_result.style.applymap(color_logic, subset=[col for col in df_result.columns if '%' in col]),
    use_container_width=True,
    height=650
)
