import streamlit as st
import pandas as pd
import yfinance as yf
import gc

# --- 1. DEFINISI FUNGSI AMBIL DATA ---
# Fungsi ini harus ada di atas sebelum dipanggil
def get_data(tickers, period="3mo"):
    try:
        # Download data dari Yahoo Finance
        data = yf.download(tickers, period=period, group_by='ticker', progress=False)
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

# --- 2. KONFIGURASI TAMPILAN ---
st.set_page_config(layout="wide") # Agar kolom bisa muat banyak menyamping
st.title("🎲 Win/Loss Heatmap")

# --- 3. INPUT & LOGIKA PAGINATION ---
txt = st.text_input("Ketik Kode Saham (Pisahkan dengan koma):", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    # Bersihkan input
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # Atur 20 Saham per Halaman
    limit = 20
    total_saham = len(clean_ticks)
    num_pages = (total_saham // limit) + (1 if total_saham % limit > 0 else 0)
    
    # Sidebar untuk ganti halaman
    if num_pages > 1:
        page = st.sidebar.number_input(f"Halaman (Total {num_pages})", 1, num_pages, 1)
    else:
        page = 1
    
    # Potong list saham sesuai halaman
    start_idx = (page - 1) * limit
    show_ticks = clean_ticks[start_idx : start_idx + limit]

    if show_ticks:
        with st.spinner(f"Memproses {len(show_ticks)} saham..."):
            d_wl = get_data(show_ticks)

        if d_wl is not None:
            for t in show_ticks:
                try:
                    # Ambil data per ticker secara aman
                    if len(show_ticks) > 1:
                        df_stock = d_wl[t].copy()
                    else:
                        df_stock = d_wl.copy()
                    
                    df_stock = df_stock.dropna(subset=['Close']).sort_index()
                    if df_stock.empty: continue
                    
                    # Hitung Return
                    df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                    df_stock = df_stock.dropna(subset=['Pct'])
                    
                    # Hitung Hari Positif (30 Hari Terakhir)
                    last_30 = df_stock.tail(30)
                    win_count = (last_30['Pct'] > 0).sum()
                    
                    # --- RENDER BAGIAN A: HEADER (RATA KIRI & KANAN) ---
                    # Col 1 untuk Nama (Lebar), Col 2 untuk Info Positif (Sempit)
                    h_col1, h_col2 = st.columns([4, 1])
                    with h_col1:
                        st.markdown(f"### **{t.replace('.JK','')}**")
                    with h_col2:
                        # Rata kanan menggunakan Markdown sederhana
                        st.markdown(f"<div style='text-align:right; color:#00C805; font-size:18px; font-weight:bold;'>Positif: {win_count}/30D</div>", unsafe_allow_html=True)
                    
                    # --- RENDER BAGIAN B: HEATMAP (20 HARI TERAKHIR) ---
                    # Gunakan 20 kolom kecil bawaan streamlit
                    last_20 = df_stock.tail(20)
                    cols = st.columns(20)
                    
                    for i, (date, row) in enumerate(last_20.iterrows()):
                        p = row['Pct']
                        # Warna Emoji sebagai indikator yang stabil
                        color_icon = "🟢" if p > 0 else "🔴" if p < 0 else "⚪"
                        
                        with cols[i]:
                            # Tampilkan Tanggal, Icon, dan Persen secara vertikal
                            st.caption(f"{date.strftime('%d/%m')}")
                            st.write(color_icon)
                            st.caption(f"{p:+.1f}%")
                    
                    st.divider() # Garis pemisah antar saham

                except Exception:
                    continue
        
        gc.collect()
