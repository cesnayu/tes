import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def get_daily_dashboard(tickers, target_date):
    # Mengonversi string tanggal ke objek datetime
    date_obj = datetime.strptime(target_date, '%Y-%m-%d')
    
    # Mengambil data beberapa hari sebelumnya untuk mendapatkan harga 'Previous Close'
    start_fetch = (date_obj - timedelta(days=7)).strftime('%Y-%m-%d')
    end_fetch = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
    
    summary_data = []

    print(f"Fetching data untuk tanggal: {target_date}...\n")

    for ticker in tickers:
        try:
            # Download data historis
            df = yf.download(ticker, start=start_fetch, end=end_fetch, progress=False)
            
            # Memastikan data pada tanggal target tersedia
            if target_date in df.index.strftime('%Y-%m-%d'):
                # Mengambil baris untuk hari H dan hari bursa sebelumnya
                target_idx = df.index.get_loc(df.loc[target_date:target_date].index[0])
                
                price_today = df['Close'].iloc[target_idx]
                price_prev = df['Close'].iloc[target_idx - 1]
                
                # Menghitung Return
                daily_return = ((price_today - price_prev) / price_prev) * 100
                
                summary_data.append({
                    'Ticker': ticker,
                    'Prev Close': round(float(price_prev), 2),
                    'Target Close': round(float(price_today), 2),
                    'Return (%)': round(float(daily_return), 2)
                })
            else:
                print(f"Peringatan: Data {ticker} tidak tersedia pada {target_date} (Mungkin pasar tutup).")
        except Exception as e:
            print(f"Error pada {ticker}: {e}")

    return pd.DataFrame(summary_data)

# --- KONFIGURASI ---
# Tambahkan kode .JK untuk saham Indonesia (BEI)
list_saham = ['BBCA.JK', 'TLKM.JK', 'ASII.JK', 'BBRI.JK', 'UNVR.JK', 'GOTO.JK']
tanggal_target = '2025-04-08' 

# Jalankan Dashboard
df_result = get_daily_dashboard(list_saham, tanggal_target)

if not df_result.empty:
    # 1. Tampilkan Tabel
    print("\n" + "="*50)
    print(f" DASHBOARD RETURN SAHAM - {tanggal_target}")
    print("="*50)
    print(df_result.to_string(index=False))
    print("="*50)

    # 2. Visualisasi Sederhana
    df_result = df_result.sort_values(by='Return (%)')
    colors = ['green' if x > 0 else 'red' for x in df_result['Return (%)']]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(df_result['Ticker'], df_result['Return (%)'], color=colors)
    plt.axvline(0, color='black', linewidth=0.8)
    plt.xlabel('Return (%)')
    plt.title(f'Performance Saham pada {tanggal_target}')
    
    # Tambah label angka di ujung bar
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{width}%', 
                 va='center', ha='left' if width > 0 else 'right', fontweight='bold')

    plt.tight_layout()
    plt.show()
else:
    print("Tidak ada data untuk ditampilkan.")

