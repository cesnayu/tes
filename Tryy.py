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

    try:
        raw = yf.download(tickers, start="2024-01-20", end="2024-02-20", auto_adjust=True, progress=False)

        # Ambil masing-masing kolom
        if isinstance(raw.columns, pd.MultiIndex):
            df_close  = raw["Close"]
            df_open   = raw["Open"]
            df_high   = raw["High"]
        else:
            df_close  = raw[["Close"]].rename(columns={"Close": tickers[0]})
            df_open   = raw[["Open"]].rename(columns={"Open": tickers[0]})
            df_high   = raw[["High"]].rename(columns={"High": tickers[0]})

        # Hitung daily return (Close hari ini vs Close kemarin)
        returns = df_close.pct_change() * 100

        # Hitung persentase High vs Open: ((High - Open) / Open) * 100
        high_vs_open = ((df_high - df_open) / df_open) * 100

        # Normalisasi index ke string YYYY-MM-DD
        for frame in [df_close, df_open, df_high, returns, high_vs_open]:
            frame.index = pd.to_datetime(frame.index).strftime("%Y-%m-%d")

        analysis_list = []

        for d in target_dates:
            if d in df_close.index:
                for t in tickers:
                    try:
                        close    = float(df_close.loc[d, t])
                        open_    = float(df_open.loc[d, t])
                        high     = float(df_high.loc[d, t])
                        ret      = float(returns.loc[d, t])
                        hvo_pct  = float(high_vs_open.loc[d, t])

                        analysis_list.append({
                            "Ticker"         : t.replace(".JK", ""),
                            "Tanggal"        : d,
                            "Open"           : round(open_, 2),
                            "High"           : round(high, 2),
                            "High vs Open (%)": round(hvo_pct, 2),
                            "Close"          : round(close, 2),
                            "Return (%)"     : round(ret, 2),
                        })
                    except Exception as e:
                        st.warning(f"Error ambil data {t} pada {d}: {e}")
            else:
                st.warning(f"⚠️ Tanggal {d} tidak tersedia (hari libur/pasar tutup).")

        if analysis_list:
            df_long = pd.DataFrame(analysis_list)

            # === Tampilan Long Format (per baris = 1 saham 1 tanggal) ===
            st.write("### 📊 Tabel Detail per Saham per Tanggal")
            pct_cols = ["High vs Open (%)", "Return (%)"]
            st.dataframe(
                df_long.style
                    .highlight_max(axis=0, color="#1b5e20", subset=pct_cols)
                    .highlight_min(axis=0, color="#b71c1c", subset=pct_cols)
                    .format({
                        "Open"             : "{:.2f}",
                        "High"             : "{:.2f}",
                        "Close"            : "{:.2f}",
                        "High vs Open (%)": "{:.2f}%",
                        "Return (%)"       : "{:.2f}%",
                    }),
                use_container_width=True
            )

            # === Grafik High vs Open (%) ===
            st.write("### 📉 Grafik High vs Open (%)")
            chart_hvo = df_long.pivot_table(index="Tanggal", columns="Ticker", values="High vs Open (%)")
            st.bar_chart(chart_hvo)

            # === Grafik Return (%) ===
            st.write("### 📉 Grafik Daily Return (%)")
            chart_ret = df_long.pivot_table(index="Tanggal", columns="Ticker", values="Return (%)")
            st.bar_chart(chart_ret)

        else:
            st.error("Tidak ada data yang berhasil diproses. Cek tanggal atau kode saham.")

    except Exception as e:
        st.error(f"❌ Error saat download data: {e}")
        st.write("Pastikan koneksi internet aktif dan kode saham benar (contoh: BBCA.JK)")
