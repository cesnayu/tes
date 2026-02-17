import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- 1. DAFTAR SAHAM (Langsung di dalam kode) ---
TICKERS_IDX = [
    "BREN.JK", "BBCA.JK", "BBRI.JK", "TLKM.JK", "GOTO.JK", 
    "AMMN.JK", "BRIS.JK", "ASII.JK", "UNVR.JK", "ADRO.JK",
    "PTBA.JK", "ITMG.JK", "CPIN.JK", "ICBP.JK", "MDKA.JK",
    "BUKA.JK", "ANTM.JK", "HRUM.JK", "TPIA.JK", "INKP.JK"
    # Anda bisa copy-paste sampai 800 saham di sini
]

# --- 2. LOGIKA SWING (Sesuai Code Anda) ---
def calculate_current_swing(prices, threshold=0.02):
    if len(prices) < 2: return 0, "N/A", 0
    
    last_pivot = prices[0]
    direction = 0 
    
    for p in prices:
        diff = (p - last_pivot) / last_pivot
        
        if direction <= 0 and diff >= threshold:
            last_pivot = p
            direction = 1
        elif direction >= 0 and diff <= -threshold:
            last_pivot = p
            direction = -1
        elif (direction <= 0 and p < last_pivot) or (direction >= 0 and p > last_pivot):
            last_pivot = p
            
    current_price = prices[-1]
    current_diff = (current_price - last_pivot) / last_pivot
    
    if direction == 1: status = "UP TREND"
    elif direction == -1: status = "DOWN TREND"
    else: status = "WAITING"
    
    return current_diff, status, last_pivot

# --- 3. UI DASHBOARD STREAMLIT ---
st.set_page_config(page_title="Real-time IDX Scanner", layout="wide")
st.title("📈 IDX Live Swing Scanner")

# Informasi Waktu Run
current_time = datetime.now().strftime("%H:%M:%S")
st.write(f"Waktu sistem saat ini: **{current_time}** (Data ditarik dari jam 09:00 s/d sekarang)")

# Sidebar Konfigurasi
st.sidebar.header("Konfigurasi")
threshold_pct = st.sidebar.slider("Threshold Swing (%)", 0.5, 5.0, 2.0)
threshold = threshold_pct / 100

# Input Manual Saham Tambahan
manual_input = st.sidebar.text_input("Tambah Saham Lain (pisahkan koma, misal: ANTM.JK, PTBA.JK)")
if manual_input:
    extra_tickers = [x.strip().upper() for x in manual_input.split(",")]
    all_tickers = list(set(TICKERS_IDX + extra_tickers))
else:
    all_tickers = TICKERS_IDX

# Multi-select untuk monitoring spesifik
watchlist = st.sidebar.multiselect(
    "Monitor Saham Pilihan (Kosongkan untuk Scan Semua):", 
    options=all_tickers
)

# Tombol Run
if st.button("🔄 SCAN SEKARANG"):
    target_list = watchlist if watchlist else all_tickers
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Batching 20 saham per request agar aman dari rate limit
    batch_size = 20
    for i in range(0, len(target_list), batch_size):
        batch = target_list[i:i+batch_size]
        status_text.text(f"Menganalisis {i} dari {len(target_list)} saham...")
        
        # Mengambil data intraday menit ke menit untuk HARI INI saja
        # period='1d' & interval='1m' akan selalu mengambil data dari jam 09:00 s/d saat ini
        data = yf.download(batch, period="1d", interval="1m", group_by='ticker', progress=False)
        
        for ticker in batch:
            try:
                # Ambil data Close dan buang baris kosong
                df = data[ticker].dropna() if len(batch) > 1 else data.dropna()
                
                if not df.empty:
                    prices = df['Close'].values
                    diff, status, pivot = calculate_current_swing(prices, threshold)
                    
                    results.append({
                        "Ticker": ticker,
                        "Current Price": f"{prices[-1]:,.0f}",
                        "Status": status,
                        "Swing vs Pivot (%)": round(diff * 100, 2),
                        "Last Pivot Price": f"{pivot:,.0f}",
                        "Last Update": df.index[-1].strftime('%H:%M')
                    })
            except:
                continue
        
        progress_bar.progress(min((i + batch_size) / len(target_list), 1.0))
        time.sleep(1) # Jeda aman rate limit

    status_text.text("✅ Scan Selesai!")

    # Tampilkan Hasil
    if results:
        df_results = pd.DataFrame(results)
        
        # Memberi warna pada teks Status
        def color_status(val):
            if val == "DOWN TREND": return 'color: red; font-weight: bold'
            if val == "UP TREND": return 'color: green; font-weight: bold'
            return ''

        st.subheader(f"Tabel Monitoring Keseluruhan")
        st.dataframe(
            df_results.style.applymap(color_status, subset=['Status']),
            use_container_width=True
        )

        # Highlight yang sedang turun (Peluang Buy on Weakness)
        st.divider()
        st.subheader("⚠️ Saham Sedang Drop (Mencari Pantulan)")
        df_drop = df_results[df_results['Status'] == "DOWN TREND"].sort_values(by="Swing vs Pivot (%)")
        if not df_drop.empty:
            st.table(df_drop)
        else:
            st.success("Belum ada saham yang menyentuh threshold penurunan.")
    else:
        st.error("Gagal mendapatkan data. Pastikan bursa sudah buka dan koneksi internet stabil.")
