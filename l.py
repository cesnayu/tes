import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Grafik Saham Live", layout="wide")

st.title("📈 Grafik Return Saham Otomatis")
st.markdown("Data diambil langsung dari **Yahoo Finance** tanpa perlu file Excel!")

st.divider()

# ==========================================
# 1. MENU PILIHAN (WAKTU DAN SAHAM)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    # Membuat tombol pilihan rentang waktu
    pilihan_waktu = st.radio(
        "⏳ Pilih Rentang Waktu:", 
        options=["1 Bulan", "3 Bulan"], 
        horizontal=True
    )
    
    # Mengubah teks pilihan menjadi kode yang dimengerti Yahoo Finance
    if pilihan_waktu == "1 Bulan":
        periode_yf = "1mo"
    else:
        periode_yf = "3mo"

with col2:
    # Membuat daftar saham bawaan (jangan lupa tambah .JK untuk saham Indonesia)
    daftar_saham_tersedia = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]
    
    # Membuat menu pilihan saham (bisa pilih lebih dari satu)
    saham_dipilih = st.multiselect(
        "📊 Pilih Saham yang Ingin Dibandingkan:",
        options=daftar_saham_tersedia,
        default=["BBCA.JK", "BBRI.JK"] # Otomatis menampilkan 2 saham ini saat web dibuka
    )

st.divider()

# ==========================================
# 2. MENGAMBIL DATA DAN MENGGAMBAR GRAFIK
# ==========================================
if len(saham_dipilih) > 0:
    with st.spinner('Sedang mengambil data dari Yahoo Finance...'):
        try:
            # Mengambil data harga penutupan (Close) dari saham yang dipilih
            # Fitur ajaib yfinance: kita bisa beri banyak saham sekaligus!
            data_harga = yf.download(saham_dipilih, period=periode_yf)['Close']
            
            # Jika user hanya memilih 1 saham, bentuk datanya sedikit berbeda, jadi kita rapikan
            if len(saham_dipilih) == 1:
                data_harga = pd.DataFrame(data_harga)
                data_harga.columns = saham_dipilih
            
            # Menghitung Return Harian Otomatis
            # Fungsi .pct_change() akan menghitung selisih persentase harga hari ini vs kemarin
            data_return_harian = data_harga.pct_change() * 100
            
            # --- MENGGAMBAR GRAFIK RETURN ---
            st.subheader(f"Pergerakan Return Harian ({pilihan_waktu})")
            st.markdown("Grafik ini menunjukkan persentase kenaikan/penurunan harga setiap harinya.")
            st.line_chart(data_return_harian)
            
            # --- MENGGAMBAR GRAFIK HARGA ASLI (Sebagai Tambahan) ---
            with st.expander("Klik di sini jika ingin melihat grafik Harga Asli (Rupiah)"):
                st.line_chart(data_harga)
                
        except Exception as e:
            st.error("Terjadi kesalahan saat mengambil data. Pastikan koneksi internetmu lancar.")
else:
    st.warning("Silakan pilih minimal 1 saham pada menu di atas untuk menampilkan grafik.")
