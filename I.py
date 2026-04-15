import streamlit as st
import yfinance as yf
import json # Modul baru untuk membaca dan menulis file catatan (JSON)
import os   # Modul baru untuk mengecek keberadaan file di komputer

# ==========================================
# 1. PENGATURAN HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Saham", layout="wide")

st.title("📈 Dashboard Saham Pilihanku")
st.markdown("Sumber Data: **Yahoo Finance**")

# ==========================================
# 2. SISTEM PENYIMPANAN DATA (JSON)
# ==========================================
# Nama file tempat kita menyimpan daftar saham
NAMA_FILE = "saham_pilihan.json"

# Daftar bawaan jika file belum pernah dibuat
SAHAM_DEFAULT = [
    {"symbol": "BBCA", "targetPrice": 10500},
    {"symbol": "BBRI", "targetPrice": 6000},
    {"symbol": "GOTO", "targetPrice": 150}
]

# Fungsi untuk memuat (membaca) data dari file
def muat_data():
    if os.path.exists(NAMA_FILE):
        # Jika file ada, buka dan baca isinya
        with open(NAMA_FILE, "r") as file:
            return json.load(file)
    else:
        # Jika file belum ada, buat file baru dengan data bawaan
        with open(NAMA_FILE, "w") as file:
            json.dump(SAHAM_DEFAULT, file)
        return SAHAM_DEFAULT

# Fungsi untuk menyimpan data baru ke dalam file
def simpan_data(data):
    with open(NAMA_FILE, "w") as file:
        json.dump(data, file)

# Muat data saat aplikasi pertama kali dijalankan
my_stocks = muat_data()

# ==========================================
# 3. MENU SAMPING (SIDEBAR) UNTUK PENGATURAN
# ==========================================
st.sidebar.header("⚙️ Pengaturan Saham")

# Form untuk menambahkan saham baru
with st.sidebar.form("form_tambah"):
    st.subheader("Tambah Saham Baru")
    # Menggunakan .upper() agar huruf yang diketik otomatis menjadi kapital (misal: bmri -> BMRI)
    kode_baru = st.text_input("Kode Saham (Tanpa .JK)").upper()
    target_baru = st.number_input("Target Harga (Rp)", min_value=1, step=100)
    tombol_tambah = st.form_submit_button("Tambah Saham")

    if tombol_tambah and kode_baru:
        # Cek apakah kode saham sudah ada di daftar agar tidak ganda
        sudah_ada = False
        for saham in my_stocks:
            if saham["symbol"] == kode_baru:
                sudah_ada = True
                break
        
        if sudah_ada:
            st.sidebar.error("Saham tersebut sudah ada di daftar!")
        else:
            # Masukkan ke daftar, simpan ke file, lalu muat ulang halaman
            my_stocks.append({"symbol": kode_baru, "targetPrice": target_baru})
            simpan_data(my_stocks)
            st.rerun()

st.sidebar.divider()

# Tombol untuk menghapus saham
st.sidebar.subheader("Hapus Saham")
# Membuat daftar nama saham saja untuk dipilih di menu dropdown
daftar_kode = [saham["symbol"] for saham in my_stocks]

if len(daftar_kode) > 0:
    saham_dihapus = st.sidebar.selectbox("Pilih saham yang ingin dihapus:", daftar_kode)
    if st.sidebar.button("Hapus Saham"):
        # Menyaring data: ambil semua saham KECUALI saham yang dipilih untuk dihapus
        my_stocks = [saham for saham in my_stocks if saham["symbol"] != saham_dihapus]
        simpan_data(my_stocks)
        st.rerun()
else:
    st.sidebar.info("Daftar saham kosong.")

# ==========================================
# 4. FUNGSI UNTUK MEMFORMAT RUPIAH
# ==========================================
def format_rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# ==========================================
# 5. MENGGAMBAR DASHBOARD (TAMPILAN UTAMA)
# ==========================================
# Tombol untuk memperbarui data secara manual (Refresh)
if st.button("🔄 Perbarui Data Sekarang"):
    st.rerun()

st.divider()

# Membuat 3 kolom
cols = st.columns(3)

if len(my_stocks) == 0:
    st.info("Belum ada saham yang dipantau. Silakan tambah melalui menu di sebelah kiri.")

for index, stock in enumerate(my_stocks):
    symbol = stock["symbol"]
    target = stock["targetPrice"]
    
    try:
        ticker = yf.Ticker(symbol + ".JK")
        hist = ticker.history(period="2d")
        
        if len(hist) > 0:
            current_price = float(hist['Close'].iloc[-1])
            
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
            else:
                prev_close = current_price
                
            daily_return = ((current_price - prev_close) / prev_close) * 100
            jarak_target = ((target - current_price) / current_price) * 100
            
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
                    
    except Exception as e:
        col = cols[index % 3]
        with col:
            with st.container(border=True):
                st.subheader(f"{symbol}")
                st.error("Gagal memuat data. Pastikan kode benar.")

