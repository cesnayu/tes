import yfinance as yf
import pandas as pd

saham_list = ['GOTO.JK', 'ANTM.JK', 'ADRO.JK', 'BRPT.JK', 'MEDC.JK', 'BBRI.JK', 'TLKM.JK', 'ASII.JK']
threshold_persen = 3.0

def generate_sorted_dashboard(tickers, threshold):
    final_data = []
    
    for ticker in tickers:
        data = yf.download(ticker, period="10d", interval="1d", progress=False)
        if len(data) < 5: continue
            
        last_5 = data.tail(5).copy()
        last_5['HL_Pct'] = (last_5['High'] - last_5['Low']) / last_5['Low'] * 100
        
        dates = last_5.index.strftime('%d/%m').tolist()
        ranges = last_5['HL_Pct'].tolist()
        vols = (last_5['Volume'] / 1_000_000).tolist()
        count_met = (last_5['HL_Pct'] >= threshold).sum()
        
        row = {'Ticker': ticker}
        for i in range(5):
            # Simpan angka murni (float) dulu agar bisa diurutkan
            row[dates[i]] = round(ranges[i], 2)
            # Opsional: Jika ingin tetap ada info Volume, kita buat kolom terpisah atau simpan di list
            
        row['Freq'] = count_met
        final_data.append(row)
        
    df = pd.DataFrame(final_data)
    
    # MENGURUTKAN: Berdasarkan kolom tanggal terakhir (indeks -2 karena kolom terakhir adalah 'Freq')
    kolom_terbaru = df.columns[-2] 
    df_sorted = df.sort_values(by=kolom_terbaru, ascending=False)
    
    return df_sorted, kolom_terbaru

# Jalankan
df_hasil, tgl_acuan = generate_sorted_dashboard(saham_list, threshold_persen)

print(f"\n--- Dashboard Diurutkan Berdasarkan Tanggal Terupdate ({tgl_acuan}) ---")
print(df_hasil.to_string(index=False))

