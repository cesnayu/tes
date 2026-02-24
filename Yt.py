import yfinance as yf
import pandas as pd

# Daftar saham (Pastikan pakai .JK)
tickers = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK']

def get_ma_dashboard(stock_list):
    summary = []
    
    for ticker in stock_list:
        try:
            # Ambil data 2 tahun (supaya MA200 pasti terhitung)
            df = yf.download(ticker, period='2y', interval='1d', progress=False)
            
            if df.empty or len(df) < 200:
                print(f"Data {ticker} tidak cukup atau tidak ditemukan.")
                continue
            
            # Memastikan kolom adalah satu lapis (Menghindari Multi-Index)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Ambil kolom Close
            close_prices = df['Close']
            last_price = float(close_prices.iloc[-1])
            
            # Hitung MA
            ma_list = [20, 60, 120, 200]
            row = {'Ticker': ticker, 'Price': round(last_price, 2)}
            
            for ma in ma_list:
                ma_val = float(close_prices.rolling(window=ma).mean().iloc[-1])
                dist = ((last_price - ma_val) / ma_val) * 100
                
                row[f'MA{ma}'] = round(ma_val, 2)
                row[f'% Dist {ma}'] = f"{dist:+.2f}%"
                
            summary.append(row)
            
        except Exception as e:
            print(f"Error pada {ticker}: {e}")
            
    return pd.DataFrame(summary)

# Jalankan
df_hasil = get_ma_dashboard(tickers)

if df_hasil.empty:
    print("Dashboard Kosong. Cek koneksi internet atau simbol ticker.")
else:
    print(df_hasil.to_string(index=False))
