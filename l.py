import streamlit as st
import pandas as pd

st.title("📈 Grafik Return Harian Saham")

# ==========================================
# 1. MEMBACA FILE CSV
# ==========================================
# Pastikan nama file ini sama persis dengan file yang ada di foldermu
NAMA_FILE = '2026-04-15T11-07_export.csv'

try:
    df = pd.read_csv(NAMA_FILE)
    
    # ==========================================
    # 2. MENYARING (FILTER) HANYA KOLOM RETURN
    # ==========================================
    # Kita menyuruh Python: "Cari semua nama kolom yang ada tulisan 'Ret%'"
    kolom_return = [col for col in df.columns if 'Ret%' in col]
    
    # Kita gabungkan kolom 'Ticker' dengan kolom-kolom return yang sudah ketemu
    df_return = df[['Ticker'] + kolom_return]
    
    # Menjadikan 'Ticker' sebagai label baris (index) agar namanya tidak ikut terhitung sebagai data grafik
    df_return.set_index('Ticker', inplace=True)
    
    st.subheader("1. Tabel Data Return (Sudah Disaring)")
    st.dataframe(df_return)
    
    st.divider()

    # ==========================================
    # 3. MEMUTAR TABEL DAN MEMBUAT GRAFIK
    # ==========================================
    st.subheader("2. Grafik Pergerakan Return")
    st.markdown("Pilih saham yang ingin kamu bandingkan pergerakannya.")
    
    # Memutar tabel (Transpose) menggunakan .T
    # Ini WAJIB dilakukan agar hari (H1, H2, dll) berada di sumbu X (bawah), 
    # dan nama saham berada di sumbu Y (sebagai warna garis grafik)
    df_grafik = df_return.T
    
    # Membuat filter pilihan (Multiselect) agar grafik tidak tumpang tindih berantakan
    pilihan_saham = st.multiselect(
        "Pilih Saham:",
        options=df_grafik.columns,
        default=df_grafik.columns[:3].tolist() # Menampilkan 3 saham pertama secara otomatis
    )
    
    # Jika ada saham yang dipilih, gambar grafiknya
    if pilihan_saham:
        st.line_chart(df_grafik[pilihan_saham])
    else:
        st.warning("Silakan pilih minimal 1 saham untuk menampilkan grafik.")

except FileNotFoundError:
    st.error(f"File {NAMA_FILE} tidak ditemukan. Pastikan file berada di folder yang sama dengan aplikasi.")
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
