import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Daftar ratusan saham IHSG (Top 200+ Liquid & Market Cap)
tickers = [
    "AALI.JK", "ABMM.JK", "ACES.JK", "ADCP.JK", "ADES.JK", "ADHI.JK", "ADMR.JK", "ADRO.JK",
    "AGII.JK", "AKRA.JK", "AMMN.JK", "AMRT.JK", "ANTM.JK", "ARTO.JK", "ASII.JK", "ASRI.JK",
    "AVIA.JK", "BBCA.JK", "BBNI.JK", "BBRI.JK", "BBTN.JK", "BDMN.JK", "BFIN.JK", "BIRD.JK",
    "BMRI.JK", "BMTR.JK", "BNGA.JK", "BRIS.JK", "BRMS.JK", "BRPT.JK", "BSDE.JK", "BTPS.JK",
    "BUKA.JK", "BUMI.JK", "BYAN.JK", "CPIN.JK", "CTRA.JK", "CUAN.JK", "DMAS.JK", "DOID.JK",
    "DSNG.JK", "DSSA.JK", "ELSA.JK", "EMTK.JK", "ENRG.JK", "ERAA.JK", "ESSA.JK", "EXCL.JK",
    "GGRM.JK", "GOTO.JK", "HEAL.JK", "HMSP.JK", "HRUM.JK", "ICBP.JK", "INCO.JK", "INDF.JK",
    "INDY.JK", "INKP.JK", "INTP.JK", "ISAT.JK", "ITMG.JK", "JPFA.JK", "JSMR.JK", "KLBF.JK",
    "LPKR.JK", "LSIP.JK", "MAPI.JK", "MBMA.JK", "MDKA.JK", "MEDC.JK", "MIKA.JK", "MNCN.JK",
    "MTEL.JK", "MYOR.JK", "PGAS.JK", "PGEO.JK", "PNLF.JK", "PTBA.JK", "PTPP.JK", "PWON.JK",
    "SCMA.JK", "SIDO.JK", "SMGR.JK", "SMRA.JK", "TINS.JK", "TLKM.JK", "TOWR.JK", "TPIA.JK",
    "UNTR.JK", "UNVR.JK", "WIKA.JK", "WSKT.JK" 
    # Anda bisa menambahkan kode saham lainnya di sini dengan akhiran .JK
]

def calculate_ma_dashboard(ticker_list):
    print(f"Sedang mengambil data untuk {len(ticker_list)} saham...")
    
    # Ambil data historis 1 tahun terakhir (agar cukup untuk MA 200)
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = yf.download(ticker_list, start=start_date, group_by='ticker', progress=True)
    
    results = []
    
    for ticker in ticker_list:
        try:
            # Pastikan ticker ada di data dan tidak kosong
            if ticker not in data.columns.levels[0]: continue
            df = data[ticker].dropna()
            if len(df) < 200: continue
            
            # Harga Terakhir
            current_price = df['Close'].iloc[-1]
            
            # Hitung MA
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma60 = df['Close'].rolling(window=60).mean().iloc[-1]
            ma120 = df['Close'].rolling(window=120).mean().iloc[-1]
            ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
            
            # Hitung % Jarak (Distance)
            dist20 = ((current_price - ma20) / ma20) * 100
            dist60 = ((current_price - ma60) / ma60) * 100
            dist120 = ((current_price - ma120) / ma120) * 100
            dist200 = ((current_price - ma200) / ma200) * 100
            
            results.append({
                'Ticker': ticker.replace('.JK', ''),
                'Price': round(current_price, 0),
                'MA 20': round(ma20, 2),
                'MA 60': round(ma60, 2),
                'MA 120': round(ma120, 2),
                'MA 200': round(ma200, 2),
                '% Dist MA20': round(dist20, 2),
                '% Dist MA60': round(dist60, 2),
                '% Dist MA120': round(dist120, 2),
                '% Dist MA200': round(dist200, 2)
            })
        except Exception as e:
            continue

    return pd.DataFrame(results)

# Eksekusi
df_dashboard = calculate_ma_dashboard(tickers)

# Sorting berdasarkan saham yang paling dekat dengan MA 200 (misalnya)
df_dashboard = df_dashboard.sort_values(by='% Dist MA200', ascending=True)

# Simpan ke Excel/CSV
df_dashboard.to_csv('Dashboard_MA_IHSG.csv', index=False)

# Tampilkan 20 teratas
print("\n=== DASHBOARD JARAK HARGA KE MOVING AVERAGE ===")
print(df_dashboard.head(20).to_string(index=False))
