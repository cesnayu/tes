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

    # Download data dengan range yang cukup untuk menghitung return
    raw = yf.download(tickers, start="2024-01-20", end="2024-02-20", auto_adjust=True)

    # Ambil kolom Close (kompatibel yfinance versi lama & baru)
    if isinstance(raw.columns, pd.MultiIndex):
        df = raw["Close"]
    else:
        df = raw[["Close"]]
        df.columns = tickers

    # Hitung daily return
    returns = df.pct_change() * 100

    # Normalisasi index ke string YYYY-MM-DD
    df.index = df.index.strftime("%Y-%m-%d")
    returns.index = returns.index.strftime("%Y-%m-%d")

    analysis_list = []

    for d in target_dates:
        if d in df.index:
            for t in tickers:
                price = df.loc[d, t]
                pct = returns.loc[d, t]
                analysis_list.append({
                    "Ticker": t.replace(".JK", ""),
                    "Tanggal": d,
                    "Harga": round(float(price), 2),
                    "Return (%)": round(float(pct), 2)
                })
        else:
            st.warning(f"⚠️ Data tanggal {d} tidak tersedia (kemungkinan hari libur/pasar tutup).")

    if analysis_list:
        df_long = pd.DataFrame(analysis_list)

        # Pivot ke format wide: 1 baris per saham
        df_pivot = df_long.pivot(index="Ticker", columns="Tanggal", values=["Harga", "Return (%)"])

        # Susun kolom agar Harga & Return berjejer per tanggal
        cols = []
        for d in target_dates:
            if d in df.index:
                cols.append(("Harga", d))
                cols.append(("Return (%)", d))

        df_final = df_pivot.reindex(columns=cols)
        df_final.columns = [f"{c[0]} ({c[1]})" for c in df_final.columns]

        st.write("### 📊 Tabel Performa Saham")
        return_cols = [c for c in df_final.columns if "Return" in c]
        st.dataframe(
            df_final.style.highlight_max(axis=0, color="#2e7d32", subset=return_cols)
                          .highlight_min(axis=0, color="#c62828", subset=return_cols)
                          .format("{:.2f}")
        )

        # Tampilkan grafik return
        st.write("### 📉 Grafik Return (%)")
        return_data = df_long.pivot(index="Tanggal", columns="Ticker", values="Return (%)")
        st.bar_chart(return_data)

    else:
        st.error("Tidak ada data yang berhasil diproses. Coba periksa tanggal atau kode saham.")

