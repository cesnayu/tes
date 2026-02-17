import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. LOGIKA INTI (MODIFIKASI DARI KODE ANDA) ---
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
    status = "UP" if direction == 1 else "DOWN" if direction == -1 else "SIDE"
    return current_diff, status, last_pivot

# --- 2. FUNGSI DOWNLOAD (ANTI RATE LIMIT) ---
@st.cache_data(ttl=300) # Data disimpan selama 5 menit
def scan_stocks(ticker_list, threshold):
    results = []
    batch_size = 20 # Download 20 saham per kelompok
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(0, len(ticker_list), batch_size):
        batch = ticker_list[i:i+batch_size]
        status_text.text(f"Scanning batch {i//batch_size + 1}...")
        
        # Download batch sekaligus untuk efisiensi
        data = yf.download(batch, period="1d", interval="1m", group_by='ticker', progress=False)
        
        for ticker in batch:
            try:
                # Handle jika data cuma 1 saham vs banyak saham (format df berbeda)
                df = data[ticker] if len(batch) > 1 else data
                df = df.dropna()
                
                if not df.empty:
                    prices = df['Close'].values
                    diff, status, pivot = calculate_current_swing(prices, threshold)
                    
                    results.append({
                        "Ticker": ticker,
                        "Price": round(prices[-1], 2),
                        "Status": status,
                        "Swing %": round(diff * 100, 2),
                        "Last Pivot": round(pivot, 2)
                    })
            except:
                continue
        
        # Jeda tipis untuk menghindari rate limit jika list sangat panjang
        time.sleep(0.5) 
        progress_bar.progress((i + batch_size) / len(ticker_list) if (i + batch_size) < len(ticker_list) else 1.0)
    
    status_text.text("Scan Selesai!")
    return pd.DataFrame(results)

# --- 3. UI STREAMLIT ---
st.set_page_config(page_title="IDX Swing Scanner", layout="wide")
st.title("📊 Real-time Stock Swing Scanner")

# Sidebar
st.sidebar.header("Settings")
threshold_pct = st.sidebar.slider("Swing Threshold (%)", 0.5, 5.0, 2.0)
threshold = threshold_pct / 100

# List 800 Saham (Contoh 10, silakan isi lengkap atau load dari CSV)
all_idx_stocks = [f"{s}.JK" for s in ["BBCA", "BBRI", "TLKM", "ASII", "GOTO", "AMMN", "BRIS", "ADRO", "UNVR", "ICBP"]] # Tambahkan sampai 800

# Pilihan Mode
mode = st.radio("Pilih Mode Scan:", ["Watchlist Spesifik", "Scan Semua (800 Saham)"])

selected_stocks = []
if mode == "Watchlist Spesifik":
    selected_stocks = st.multiselect("Pilih saham yang mau di-monitor:", all_idx_stocks, default=all_idx_stocks[:5])
else:
    selected_stocks = all_idx_stocks

if st.button("Mulai Scan"):
    with st.spinner("Sedang mengambil data..."):
        df_final = scan_stocks(selected_stocks, threshold)
        
        if not df_final.empty:
            # Highlight yang sedang turun banyak
            def color_negative_red(val):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'

            st.subheader(f"Hasil Analisis (Threshold {threshold_pct}%)")
            st.dataframe(
                df_final.style.applymap(color_negative_red, subset=['Swing %']),
                use_container_width=True
            )
            
            # Ringkasan
            col1, col2 = st.columns(2)
            col1.metric("Saham DOWN Trend", len(df_final[df_final['Status'] == "DOWN"]))
            col2.metric("Saham UP Trend", len(df_final[df_final['Status'] == "UP"]))
        else:
            st.warning("Data tidak ditemukan atau pasar sedang tutup.")
