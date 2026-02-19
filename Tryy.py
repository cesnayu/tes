import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("📈 Stock Daily Return Dashboard")

st.sidebar.header("Input Data")
tickers_input = st.sidebar.text_input("Kode Saham (koma):", "BBCA.JK, TLKM.JK, ASII.JK")
dates_input   = st.sidebar.text_input("Tanggal (YYYY-MM-DD):", "2024-02-01, 2024-02-05, 2024-02-12")

if st.sidebar.button("Proses Data"):
    tickers      = [t.strip() for t in tickers_input.split(",")]
    target_dates = [pd.Timestamp(d.strip()) for d in dates_input.split(",")]

    raw = yf.download(tickers, start="2024-01-20", end="2024-02-20", auto_adjust=True, progress=False)

    # Hapus timezone agar bisa dicocokkan
    raw.index = raw.index.tz_localize(None) if raw.index.tz else raw.index

    if isinstance(raw.columns, pd.MultiIndex):
        df_open  = raw["Open"]
        df_high  = raw["High"]
        df_close = raw["Close"]
    else:
        df_open  = raw[["Open"]].rename(columns={"Open": tickers[0]})
        df_high  = raw[["High"]].rename(columns={"High": tickers[0]})
        df_close = raw[["Close"]].rename(columns={"Close": tickers[0]})

    df_return    = df_close.pct_change() * 100
    df_hvo       = ((df_high - df_open) / df_open) * 100

    analysis_list = []

    for d in target_dates:
        if d in raw.index:
            for t in tickers:
                analysis_list.append({
                    "Ticker"          : t.replace(".JK", ""),
                    "Tanggal"         : d.strftime("%Y-%m-%d"),
                    "Open"            : round(float(df_open.loc[d, t]), 2),
                    "High"            : round(float(df_high.loc[d, t]), 2),
                    "High vs Open (%)": round(float(df_hvo.loc[d, t]), 2),
                    "Close"           : round(float(df_close.loc[d, t]), 2),
                    "Return (%)"      : round(float(df_return.loc[d, t]), 2),
                })
        else:
            st.warning(f"⚠️ {d.strftime('%Y-%m-%d')} tidak tersedia (libur/pasar tutup).")

    if analysis_list:
        df_long  = pd.DataFrame(analysis_list)
        pct_cols = ["High vs Open (%)", "Return (%)"]

        st.write("### 📊 Tabel Performa Saham")
        st.dataframe(
            df_long.style
                .highlight_max(axis=0, color="#1b5e20", subset=pct_cols)
                .highlight_min(axis=0, color="#b71c1c", subset=pct_cols)
                .format({
                    "Open"            : "{:.2f}",
                    "High"            : "{:.2f}",
                    "Close"           : "{:.2f}",
                    "High vs Open (%)": "{:.2f}%",
                    "Return (%)"      : "{:.2f}%",
                }),
            use_container_width=True
        )

        st.write("### 📉 Grafik High vs Open (%)")
        st.bar_chart(df_long.pivot_table(index="Tanggal", columns="Ticker", values="High vs Open (%)"))

        st.write("### 📉 Grafik Daily Return (%)")
        st.bar_chart(df_long.pivot_table(index="Tanggal", columns="Ticker", values="Return (%)"))

    else:
        st.error("Tidak ada data. Cek kode saham atau tanggal.")
