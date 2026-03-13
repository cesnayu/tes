import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 1. List saham kamu (saya ringkas contohnya, masukkan list 700+ milikmu di sini)
daftar_saham = ["BREN.JK", "BBCA.JK", "DSSA.JK", "BBRI.JK", "TLKM.JK"] # ... masukkan sisanya

def ambil_data_tunggal(ticker):
    """Fungsi kecil untuk mengambil net income satu saham"""
    try:
        tko = yf.Ticker(ticker)
        # Ambil financials dengan periode tahunan
        df_fin = tko.get_financials(freq='yearly')
        
        if not df_fin.empty and 'Net Income' in df_fin.index:
            # Ambil 3 kolom teratas (3 tahun terakhir)
            income_data = df_fin.loc['Net Income'].head(3)
            res = []
            for date, val in income_data.items():
                res.append({
                    'Ticker': ticker,
                    'Tahun': date.year,
                    'Net Income': val
                })
            return res
    except Exception:
        return None
    return None

def main():
    print(f"Memulai proses {len(daftar_saham)} saham...")
    start_time = time.time()
    
    final_data = []
    
    # Menggunakan ThreadPool untuk menjalankan banyak request sekaligus
    # max_workers=20 adalah angka aman agar tidak langsung di-ban
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(ambil_data_tunggal, t): t for t in daftar_saham}
        
        counter = 0
        for future in as_completed(future_to_ticker):
            result = future.result()
            if result:
                final_data.extend(result)
            
            counter += 1
            if counter % 50 == 0:
                print(f"Selesai memproses {counter} saham...")

    # Simpan hasil
    if final_data:
        df = pd.DataFrame(final_data)
        df.to_csv("hasil_net_income_700.csv", index=False)
        print(f"\n--- SELESAI dalam {round(time.time() - start_time, 2)} detik ---")
        print(f"Data disimpan di: hasil_net_income_700.csv")
        print(df.head())
    else:
        print("Gagal mengambil data sama sekali. Cek koneksi atau coba 10 saham dulu.")

if __name__ == "__main__":
    main()
