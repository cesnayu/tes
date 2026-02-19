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

    st.write("#### 🔍 Debug Info")
    st.write(f"Tickers: `{tickers}`")
    st.write(f"Target Dates: `{target_dates}`")

    try:
        raw = yf.download(tickers, start="2024-01-20", end="2024-02-20", auto_adjust=True, progress=False)

        st.write(f"Kolom raw: `{list(raw.columns)}`")
        st.write(f"Shape raw: `{raw.shape}`")

        # Ambil kolom Close
        if isinstance(raw.columns, pd.MultiIndex):
            df = raw["Close"]
        else:
            df = raw[["Close"]]
            df.columns = tickers

        st.write("#### Preview data Close (sebelum format index):")
        st.dataframe(df.tail(10))
        st.write(f"Tipe index: `{type(df.index[0])}`")
        st.write(f"Contoh nilai index: `{df.index[:3].tolist()}`")

        # Normalisasi index
        df.index = pd.to_datetime(df.index).strftime("%Y-%m-%d")
        returns = df.pct_change() * 100

        st.write("#### Index setelah normalisasi (5 terakhir):")
        st.write(df.index[-5:].tolist())

        st.write("#### Cek apakah target_dates ada di index:")
        for d in target_dates:
            ada = d in df.index
            st.write(f"- `{d}` → {'✅ Ada' if ada else '❌ Tidak Ada'}")

        # Proses analisis
        analysis_list = []
        for d in target_dates:
            if d in df.index:
                for t in tickers:
                    try:
                        price = df.loc[d, t]
                        pct = returns.loc[d, t]
                        analysis_list.append({
                            "Ticker": t.replace(".JK", ""),
                            "Tanggal": d,
                            "Harga": round(float(price), 2),
                            "Return (%)": round(float(pct), 2)
                        })
                    except Exception as e:
                        st.warning(f"Error ambil data {t} pada {d}: {e}")
            else:
                st.warning(f"⚠️ Tanggal {d} tidak ada di data (libur/pasar tutup).")

        if analysis_list:
            df_long = pd.DataFrame(analysis_list)

            df_pivot = df_long.pivot(index="Ticker", columns="Tanggal", values=["Harga", "Return (%)"])

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

            st.write("### 📉 Grafik Return (%)")
            return_data = df_long.pivot(index="Tanggal", columns="Ticker", values="Return (%)")
            st.bar_chart(return_data)

        else:
            st.error("Tidak ada data yang berhasil diproses.")

    except Exception as e:
        st.error(f"❌ Error saat download data: {e}")
        st.write("Pastikan koneksi internet aktif dan kode saham benar (contoh: BBCA.JK)")
