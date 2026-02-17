import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. DAFTAR SAHAM (Masukkan di sini) ---
# Anda bisa menambah sampai 800 saham dengan format "KODE.JK"
TICKERS_IDX = [
    "BREN.JK", "BBCA.JK", "BBRI.JK", "TLKM.JK", "GOTO.JK", 
    "AMMN.JK", "BRIS.JK", "ASII.JK", "UNVR.JK", "ADRO.JK",
    "PTBA.JK", "ITMG.JK", "CPIN.JK", "ICBP.JK", "MDKA.JK"
    # ... tambahkan terus ke bawah
]

# --- 2. LOGIKA SWING ---
def calculate_current_swing(prices, threshold=0.02):
    if len(prices) < 2: return 0, "N/A", 0
    
    last_pivot = prices[0]
    direction = 0 # 0=mencari, 1=up, -1=down
    
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

# --- 3. UI DASHBOARD ---
st.set_page_config(page_title="IDX Real-time Scanner", layout="wide")
st.title("🔍 IDX Swing Scanner (Anti-Rate Limit)")

st.sidebar.header("Konfigurasi")
threshold_pct = st.sidebar.slider("Threshold Swing (%)", 0.5, 5.0, 2.0)
threshold = threshold_pct / 100

# Fitur Watchlist Custom (Bisa pilih manual dari list di atas)
watchlist = st.sidebar.multiselect(
    "Monitor Spesifik (Watchlist):", 
    options=TICKERS_IDX, 
    default=["BREN.JK", "BBCA.JK"]
)

# Tombol Eksekusi
if st.button("🚀 Jalankan Scan Sekarang"):
    results = []
    
    # Pilih list mana yang mau di-scan
    target_list = TICKERS_IDX if not watchlist else watchlist
    
    st.info(f"Memulai scan untuk {len(target_list)} saham...")
    progress_bar = st.progress(0)
    
    # BATCHING: Download 20 saham per sesi agar tidak kena blokir
    batch_size = 20
    for i in range(0, len(target_list), batch_size):
        batch = target_list[i:i+batch_size]
        
        # Download data 1 menit (Intraday)
        data = yf.download(batch, period="1d", interval="1m", group_by='ticker', progress=False)
        
        for ticker in batch:
            try:
                # Ambil kolom Close
                df = data[ticker].dropna() if len(batch) > 1 else data.dropna()
                
                if not df.empty:
                    prices = df['Close'].values
                    diff, status, pivot = calculate_current_swing(prices, threshold)
                    
                    results.append({
                        "Ticker": ticker,
                        "Price": f"{prices[-1]:,.0f}",
                        "Status": status,
                        "Swing Current %": round(diff * 100, 2),
                        "Last Pivot Price": f"{pivot:,.0f}",
                        "Time": df.index[-1].strftime('%H:%M')
                    })
            except Exception as e:
                continue
        
        # Update progress bar
        progress_bar.progress(min((i + batch_size) / len(target_list), 1.0))
        time.sleep(1) # Jeda 1 detik antar batch agar aman dari rate limit

    # Tampilkan Tabel Hasil
    if results:
        df_results = pd.DataFrame(results)
        
        # Styling Tabel
        def highlight_status(val):
            color = 'red' if val == "DOWN TREND" else 'green' if val == "UP TREND" else 'white'
            return f'color: {color}; font-weight: bold'

        st.subheader(f"Hasil Analisis (Update: {time.strftime('%H:%M:%S')})")
        st.dataframe(
            df_results.style.applymap(highlight_status, subset=['Status']),
            use_container_width=True
        )
        
        # Filter Saham yang sedang turun (mencari diskon)
        st.divider()
        st.subheader("⚠️ Saham Sedang Drop (Down Trend)")
        df_drop = df_results[df_results['Status'] == "DOWN TREND"].sort_values(by="Swing Current %")
        st.table(df_drop)
    else:
        st.warning("Tidak ada data. Pastikan jam bursa sedang buka.")
