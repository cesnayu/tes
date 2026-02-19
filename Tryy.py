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
    target_dates = [d.strip() for d in dates_input.split(",")]

    # Download satu per satu agar lebih stabil
    all_data = {}
    for t in tickers:
        raw = yf.download(t, start="2024-01-20", end="2024-02-20", auto_adjust=True, progress=False)
        
        # Flatten kolom jika MultiIndex
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        
        # Hapus timezone dari index
        raw.index = raw.index.tz_localize(None) if raw.index.tz else raw.index
        
        # Simpan sebagai string YYYY-MM-DD
        raw.index = raw.index.strftime("%Y-%m-%d")
        
        all_data[t] = raw

    # Cek tanggal tersedia dari ticker pertama
    sample_index = list(all_data[tickers[0]].index)

    analysis_list = []

    for d in target_dates:
        if d in sample_index:
            for t in tickers:
                df = all_data[t]
                open_  = float(df.loc[d, "Open"])
                high   = float(df.loc[d, "High"])
                close  = float(df.loc[d, "Close"])

                # Hitung return: ambil close hari sebelumnya
                idx_pos = sample_index.index(d)
                if idx_pos > 0:
                    prev_close = float(df.iloc[idx_pos - 1]["Close"])
                    ret = ((close - prev_close) / prev_close) * 100
                else:
                    ret = 0.0

                hvo = ((high - open_) / open_) * 100

                analysis_list.append({
                    "Ticker"          : t.replace(".JK", ""),
                    "Tanggal"         : d,
                    "Open"            : round(open_, 2),
                    "High"            : round(high, 2),
                    "High vs Open (%)": round(hvo, 2),
                    "Close"           : round(close, 2),
                    "Return (%)"      : round(ret, 2),
                })
        else:
            st.warning(f"⚠️ {d} tidak tersedia (libur/pasar tutup).")

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
