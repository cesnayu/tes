import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📈 Stock Daily Return Dashboard")

# Input di Sidebar
st.sidebar.header("Input Data")
tickers_input = st.sidebar.text_input("Kode Saham (koma):", "BBCA.JK, TLKM.JK, ASII.JK")
dates_input = st.sidebar.text_input("Tanggal (YYYY-MM-DD):", "2024-02-01, 2024-02-05, 2024-02-12")

if st.sidebar.button("Proses Data"):
    tickers = [t.strip() for t in tickers_input.split(",")]
    target_dates = [d.strip() for d in dates_input.split(",")]
    
    # Gunakan range yang cukup untuk menghitung return
    df = yf.download(tickers, start="2024-01-20", end="2024-02-20")['Adj Close']
    returns = df.pct_change() * 100
    
    analysis_list = []

    # Perhatikan Indentasi: Loop ini harus bersih dari try yang menggantung
    for d in target_dates:
        if d in df.index:
            for t in tickers:
                # Ambil data per saham per tanggal
                price = df.loc[d, t]
                pct = returns.loc[d, t]
                
                # Baris 91 yang bermasalah sebelumnya:
                analysis_list.append({
                    "Ticker": t.replace('.JK', ''),
                    "Tanggal": d,
                    "Harga": round(price, 2),
                    "Return (%)": round(pct, 2)
                })
        else:
            st.warning(f"Data tanggal {d} tidak ada (Market Libur).")

    if analysis_list:
        df_long = pd.DataFrame(analysis_list)
        
        # Mengubah ke format 1 Baris Per Saham (Wide Format)
        df_pivot = df_long.pivot(index='Ticker', columns='Tanggal', values=['Harga', 'Return (%)'])
        
        # Merapikan kolom agar Harga dan Return berjejer per tanggal
        cols = []
        for d in target_dates:
            if d in df.index:
                cols.append(('Harga', d))
                cols.append(('Return (%)', d))
        
        df_final = df_pivot.reindex(columns=cols)
        df_final.columns = [f"{c[0]} ({c[1]})" for c in df_final.columns]
        
        st.write("### Tabel Performa Saham")
        st.dataframe(df_final.style.highlight_max(axis=0, color='#2e7d32', subset=[c for c in df_final.columns if 'Return' in c]))
