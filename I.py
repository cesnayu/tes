import streamlit as st
import yfinance as yf
import json
import os

# ==========================================
# 1. PENGATURAN HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Saham", layout="wide")

st.title("📈 Dashboard Saham Pilihanku")
st.markdown("Sumber Data: **Yahoo Finance**")

# ==========================================
# 2. SISTEM PENYIMPANAN DATA (JSON)
# ==========================================
DATA_FILE = "saham_pilihan.json"

SAHAM_DEFAULT = [
    {"symbol": "BBCA", "targetPrice": 10500},
    {"symbol": "BBRI", "targetPrice": 6000},
    {"symbol": "GOTO", "targetPrice": 150}
]

def load_data():
    if os.path.exists(DATA_FILE): 
        with open(DATA_FILE, "r") as f: 
            return json.load(f) 
    return SAHAM_DEFAULT

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

my_stocks = load_data()

# ==========================================
# 3. FUNGSI PENGAMBIL DATA & FORMAT ANGKA
# ==========================================
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.history(period="2d")
        if len(info) < 2:
            return None
        return info
    except Exception:
        return None

def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# ==========================================
# 4. MENU SAMPING (SIDEBAR) UNTUK PENGATURAN
# ==========================================
st.sidebar.header("⚙️ Pengaturan Saham")

with st.sidebar.form("form_tambah"):
    st.subheader("➕ Tambah Saham Baru")
    kode_baru = st.text_input("Kode Saham (Tanpa .JK)").upper()
    target_baru = st.number_input("Target Harga (Rp)", min_value=1, step=100)
    tombol_tambah = st.form_submit_button("Tambah Saham")

    if tombol_tambah and kode_baru:
        sudah_ada = False
        for saham in my_stocks:
            if saham["symbol"] == kode_baru:
                sudah_ada = True
                break
        
        if sudah_ada:
            st.sidebar.error("Saham tersebut sudah ada di daftar!")
        else:
            my_stocks.append({"symbol": kode_baru, "targetPrice": target_baru})
            save_data(my_stocks)
            st.rerun()

st.sidebar.divider()

st.sidebar.subheader("🗑️ Hapus Saham")
daftar_kode = [saham["symbol"] for saham in my_stocks]

if len(daftar_kode) > 0:
    saham_dihapus = st.sidebar.selectbox("Pilih saham yang ingin dihapus:", daftar_kode)
    if st.sidebar.button("Hapus Saham"):
        my_stocks = [saham for saham in my_stocks if saham["symbol"] != saham_dihapus]
        save_data(my_stocks)
        st.rerun()
else:
    st.sidebar.info("Daftar saham kosong.")

# ==========================================
# 5. MENGGAMBAR DASHBOARD (TAMPILAN UTAMA)
# ==========================================
if st.button("🔄 Perbarui Data Sekarang"):
    st.rerun()

st.divider()

cols = st.columns(3)

if len(my_stocks) == 0:
    st.info("Belum ada saham yang dipantau. Silakan tambah melalui menu di sebelah kiri.")

for index, stock in enumerate(my_stocks):
    symbol = stock["symbol"]
    target = stock["targetPrice"]
    
    # Memanggil fungsi untuk mengambil data
    info = get_stock_data(symbol + ".JK")
    
    # Memilih kolom tempat kartu akan digambar
    col = cols[index % 3]
    
    with col:
        with st.container(border=True):
            st.subheader(f"{symbol}")
            
            # Cek apakah data berhasil diambil dan tidak kosong
            if info is not None and not info.empty:
                try:
                    current_price = float(info['Close'].iloc[-1])
                    prev_close = float(info['Close'].iloc[-2])
                    
                    daily_return = ((current_price - prev_close) / prev_close) * 100
                    jarak_target = ((target - current_price) / current_price) * 100
                    
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
                except Exception as e:
                    # Jika ada error spesifik pada perhitungan
                    st.error("Gagal menghitung harga.")
            else:
                # Jika data belum tersedia di Yahoo Finance
                st.warning("Menunggu data pasar / Libur.")
