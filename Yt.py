import yfinance as yf
import pandas as pd

# List Saham
tickers = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'ASII.JK', 'GOTO.JK']

def create_dashboard():
    all_data = []
    
    print("Sedang mengambil data, mohon tunggu...")
    
    for t in tickers:
        try:
            # Menggunakan period 2 tahun supaya MA200 pasti muncul
            # auto_adjust=True membantu menormalkan kolom Close
            df = yf.download(t, period='2y', auto_adjust=True, progress=False)
            
            if df.empty:
                print(f"Data untuk {t} kosong (Check koneksi/ticker)")
                continue

            # Perbaikan krusial: Meratakan kolom jika ada multi-index
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Menghitung MA
            ma_windows = [20, 60, 120, 200]
            last_close = float(df['Close'].iloc[-1])
            
            res = {'Ticker': t, 'Price': round(last_close, 2)}
            
            for window in ma_windows:
                ma_val = df['Close'].rolling(window=window).mean().iloc[-1]
                
                if pd.isna(ma_val):
                    res[f'MA{window}'] = "N/A"
                    res[f'% Dist {window}'] = "N/A"
                else:
                    dist = ((last_close - ma_val) / ma_val) * 100
                    res[f'MA{window}'] = round(ma_val, 2)
                    res[f'% Dist {window}'] = f"{dist:+.2f}%"
            
            all_data.append(res)
            print(f"Berhasil mengambil data: {t}")
            
        except Exception as e:
            print(f"Gagal mengambil {t}: {str(e)}")

    # Membuat DataFrame
    if not all_data:
        print("\nFATAL: Semua data gagal diambil. Coba ganti koneksi internet/Hotspot.")
    else:
        df_final = pd.DataFrame(all_data)
        print("\n--- STOCK MA DASHBOARD ---")
        print(df_final.to_string(index=False))

if __name__ == "__main__":
    create_dashboard()
