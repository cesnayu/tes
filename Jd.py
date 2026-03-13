import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df_fin = stock.financials

        if df_fin is None or df_fin.empty:
            print(f"{ticker} financials kosong")
            return []

        # cari baris Net Income
        if "Net Income" not in df_fin.index:
            print(f"{ticker} tidak ada Net Income")
            return []

        income = df_fin.loc["Net Income"].head(3)

        data = []
        for date, val in income.items():
            data.append({
                "Ticker": ticker,
                "Tahun": pd.to_datetime(date).year,
                "Net Income": val
            })

        print(f"{ticker} berhasil")
        return data

    except Exception as e:
        print(f"Error {ticker}: {e}")
        return []


daftar_saham = ["BREN.JK", "BBCA.JK", "DSSA.JK", "BBRI.JK", "TLKM.JK"]

print(f"Memulai pengambilan data {len(daftar_saham)} saham...")

final_results = []

# paralel tapi tidak terlalu agresif
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_data, t) for t in daftar_saham]

    for future in as_completed(futures):
        result = future.result()
        final_results.extend(result)

df_hasil = pd.DataFrame(final_results)

if not df_hasil.empty:
    print("\n--- BERHASIL ---")
    print(df_hasil.head())

    df_hasil.to_csv("net_income_700.csv", index=False)
    print("Data disimpan ke net_income_700.csv")

else:
    print("Tidak ada data ditemukan")
