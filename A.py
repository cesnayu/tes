import yfinance as yf
import pandas as pd

def ambil_data_aman(ticker_list):
    hasil = []
    # Menambahkan Header agar terlihat seperti Browser Manusia
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for t in ticker_list:
        try:
            stock = yf.Ticker(t)
            # Ambil info dengan proteksi
            info = stock.info
            
            # Ambil data satu per satu dengan default 0 jika tidak ada
            data = {
                'Ticker': t,
                'Price': info.get('currentPrice', 0),
                'EPS': info.get('trailingEps', 0),
                'ROE': info.get('returnOnEquity', 0),
                'PBV': info.get('priceToBook', 0)
            }
            hasil.append(data)
            print(f"✅ {t} Berhasil diambil.")
        except Exception as e:
            print(f"❌ {t} Gagal: {e}")
            
    return pd.DataFrame(hasil)

# Coba tes 1 atau 2 saham dulu
df = ambil_data_aman(['BBCA.JK', 'ASII.JK'])
print(df)
