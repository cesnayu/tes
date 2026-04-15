import streamlit as st
import yfinance as yf 
import pandas as pd 
import json 
import os

DATA_FILE = "stocks.json"



def load_data():
    if os.path.exists(DATA_FILE): 
        with open(DATA_FILE, "r") as f: 
           return json.load(f) 
           return []

def save_data(data): 
   with open(DATA_FILE, "w") as f: json.dump(data, f)

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.history(period="2d")
    
    if len(info) < 2:
        return None
        
    return info

current_price = info["Close"].iloc[-1]
prev_close = info["Close"].iloc[-2]
daily_return = ((current_price - prev_close) / prev_close) * 100
def hitung_harga_saham(ticker):
    # ... (kode lainnya di sini) ...
    daily_return = ((current_price - prev_close) / prev_close) * 100
    
    # Baris return INI harus lurus dengan tulisan daily_return di atasnya
    return current_price, daily_return

st.set_page_config(page_title="Stock Target Dashboard", layout="wide")

st.title("📈 Stock Target Dashboard (Yahoo Finance)")

stocks = load_data()


st.subheader("➕ Add / Update Stock") 
col1, col2 = st.columns(2)

with col1: ticker_input = st.text_input("Ticker (e.g., AAPL, BBCA.JK)")

with col2: target_price_input = st.number_input("Target Price", min_value=0.0, step=0.1)

if st.button("Save Stock"):
    if ticker_input: updated = False 
    for s in stocks: 
        if s["ticker"].upper() == ticker_input.upper(): s["target"] = target_price_input 
        updated = True
        if not updated: stocks.append({"ticker": ticker_input.upper(), "target": target_price_input}) 
        save_data(stocks) 
        st.success("Saved!")


st.subheader("📊 Your Portfolio")

if stocks: table_data = []

# Membuat 3 kolom untuk tampilan
cols = st.columns(3)

if len(my_stocks) == 0:
    st.info("Belum ada saham yang dipantau. Silakan tambah melalui menu di sebelah kiri.")

# Perulangan untuk mengecek satu per satu saham di daftarmu
for index, stock in enumerate(my_stocks):
    symbol = stock["symbol"]
    target = stock["targetPrice"]
    
    try:
        # 1. PANGGIL FUNGSI DI SINI: Kita suruh fungsi mengambil data
        info = get_stock_data(symbol + ".JK")
        
        # 2. Cek apakah fungsi berhasil mengembalikan data (tidak None)
        if info is not None:
            # 3. Sekarang 'info' sudah ada dan bisa kita ambil harganya
            current_price = float(info['Close'].iloc[-1])
            
            if len(info) > 1:
                prev_close = float(info['Close'].iloc[-2])
            else:
                prev_close = current_price
                
            daily_return = ((current_price - prev_close) / prev_close) * 100
            jarak_target = ((target - current_price) / current_price) * 100
            
            # Memasukkan ke dalam kolom yang tepat
            col = cols[index % 3]
            
            with col:
                with st.container(border=True):
                    st.subheader(f"{symbol}")
                    st.metric(
                        label="Harga Asli Saat Ini", 
                        value=format_rupiah(current_price), 
                        delta=f"{daily_return:.2f}% Hari Ini"
                    )
                    st.markdown(f"🎯 **Target Harga:** {format_rupiah(target)}")
                    
                    warna = "green" if jarak_target > 0 else "red"
                    st.markdown(
                        f"📏 **Jarak ke Target:** <span style='color:{warna}; font-weight:bold;'>{jarak_target:.2f}%</span>", 
                        unsafe_allow_html=True
                    )
        else:
            # Jika data dari Yahoo Finance kurang dari 2 hari / kosong
            col = cols[index % 3]
            with col:
                with st.container(border=True):
                    st.subheader(f"{symbol}")
                    st.warning("Data belum lengkap di Yahoo Finance.")
                    
    except Exception as e:
        col = cols[index % 3]
        with col:
            with st.container(border=True):
                st.subheader(f"{symbol}")
                st.error("Gagal memuat data. Pastikan kode benar.")

df = pd.DataFrame(table_data)

st.dataframe(df, use_container_width=True)

st.subheader("🔥 Insights")
if not df.empty:
    best = df.loc[df["% to Target"].idxmax()]
    worst = df.loc[df["Daily Return %"].idxmin()]

    st.write(f"🚀 Most Upside: {best['Ticker']} ({best['% to Target']}%)")
    st.write(f"📉 Worst Today: {worst['Ticker']} ({worst['Daily Return %']}%)")

else: st.info("No stocks added yet.")


st.subheader("❌ Remove Stock") 
remove_ticker = st.text_input("Ticker to remove")

if st.button("Delete"): stocks = [s for s in stocks if s["ticker"] != remove_ticker.upper()] 
save_data(stocks) 
st.success("Deleted!")
