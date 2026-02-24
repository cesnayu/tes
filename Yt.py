import pandas as pd
from pandas_datareader import data as pdr
import datetime

# Daftar saham (Stooq menggunakan format Ticker.ID untuk Indonesia)
# Contoh: BBCA.ID, BBRI.ID
tickers = ['BBCA.ID', 'BBRI.ID', 'BMRI.ID', 'TLKM.ID', 'ASII.ID', 'GOTO.ID']

def create_stooq_dashboard():
    all_data = []
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365*2) # Ambil 2 tahun
    
    print("Mengambil data dari Stooq...")

    for t in tickers:
        try:
            # Mengambil data dari Stooq
            df = pdr.DataReader(t, 'stooq', start_date, end_date)
            
            if df.empty:
                print(f"Data {t} tidak ditemukan.")
                continue
            
            # Stooq mengembalikan data terbalik (terbaru di atas), kita balik dulu
            df = df.sort_index(ascending=True)
            
            # Ambil harga closing
            close_prices = df['Close']
            last_price = float(close_prices.iloc[-1])
            
            row = {'Ticker': t.replace('.ID', '.JK'), 'Price': round(last_price, 2)}
            
            # Hitung MA
            for ma in [20, 60, 120, 200]:
                ma_val = close_prices.rolling(window=ma).mean().iloc[-1]
                
                if pd.isna(ma_val):
                    row[f'MA{ma}'] = "N/A"
                    row[f'% Dist {ma}'] = "N/A"
                else:
                    dist = ((last_price - ma_val) / ma_val) * 100
                    row[f'MA{ma}'] = round(ma_val, 2)
                    row[f'% Dist {ma}'] = f"{dist:+.2f}%"
            
            all_data.append(row)
            print(f"Berhasil: {t}")
            
        except Exception as e:
            print(f"Gagal di {t}: {e}")

    if all_data:
        df_final = pd.DataFrame(all_data)
        print("\n--- STOCK DASHBOARD (SOURCE: STOOQ) ---")
        print(df_final.to_string(index=False))
    else:
        print("Gagal mengambil semua data. Cek koneksi internet.")

if __name__ == "__main__":
    create_stooq_dashboard()
