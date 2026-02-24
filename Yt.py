import pandas as pd
import requests
import io

# List saham
tickers = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK']

def fetch_data_direct(ticker):
    # Menggunakan endpoint Yahoo Finance versi lama yang seringkali lebih stabil
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=1672531200&period2=9999999999&interval=1d&events=history&includeAdjustedClose=true"
    
    # Menambahkan 'User-Agent' agar tidak disangka bot/leak
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return pd.read_csv(io.StringIO(response.text))
    else:
        return None

results = []

print("Sedang memproses data...")
for t in tickers:
    df = fetch_data_direct(t)
    if df is not None and len(df) >= 200:
        # Ambil kolom Close
        close = df['Close']
        last_price = close.iloc[-1]
        
        row = {'Ticker': t, 'Price': round(last_price, 2)}
        
        # Hitung MA
        for ma in [20, 60, 120, 200]:
            ma_val = close.rolling(window=ma).mean().iloc[-1]
            dist = ((last_price - ma_val) / ma_val) * 100
            
            row[f'MA{ma}'] = round(ma_val, 2)
            row[f'% Dist {ma}'] = f"{dist:+.2f}%"
            
        results.append(row)
        print(f"Berhasil: {t}")
    else:
        print(f"Gagal/Data kurang: {t}")

if results:
    final_df = pd.DataFrame(results)
    print("\n--- STOCK DASHBOARD ---")
    print(final_df.to_string(index=False))
else:
    print("Tetap gagal. Sepertinya IP internet Anda sedang diblokir sementara oleh Yahoo.")
