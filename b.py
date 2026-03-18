import streamlit as st
import pandas as pd
import gc

st.subheader("🎲 Win/Loss Heatmap")

txt = st.text_input("Ketik Kode Saham:", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # 1. LOGIKA PAGINATION (20 Saham per Halaman)
    limit = 20
    total_saham = len(clean_ticks)
    num_pages = (total_saham // limit) + (1 if total_saham % limit > 0 else 0)
    page = st.sidebar.number_input("Halaman", 1, num_pages, 1) if num_pages > 1 else 1
    
    start_idx = (page - 1) * limit
    show_ticks = clean_ticks[start_idx : start_idx + limit]

    if show_ticks:
        with st.spinner(f"Memuat {len(show_ticks)} saham..."):
            d_wl = get_data(show_ticks, period="3mo")

        # 2. LOOPING SETIAP SAHAM
        for t in show_ticks:
            try:
                # Ambil data per ticker
                df_stock = d_wl[t].copy() if len(show_ticks) > 1 else d_wl.copy()
                df_stock = df_stock.dropna(subset=['Close']).sort_index()
                if df_stock.empty: continue
                
                # Hitung Return
                df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                df_stock = df_stock.dropna(subset=['Pct'])
                
                # Hitung Hari Positif (30 Hari Terakhir)
                last_30 = df_stock.tail(30)
                pos_count = (last_30['Pct'] > 0).sum()
                
                # --- BAGIAN A: HEADER (NAMA KIRI, INFO KANAN) ---
                # Menggunakan 2 kolom: Kolom 1 lebar, Kolom 2 sempit untuk angka
                head_col1, head_col2 = st.columns([3, 1])
                with head_col1:
                    st.markdown(f"### **{t.replace('.JK','')}**")
                with head_col2:
                    st.markdown(f"<p style='text-align:right; color:#00C805; font-weight:bold;'>Positif: {pos_count}/30D</p>", unsafe_allow_html=True)
                
                # --- BAGIAN B: HEATMAP (KOTAK KECIL) ---
                # Kita buat 20 kolom kecil untuk 20 hari terakhir
                last_20 = df_stock.tail(20)
                cols = st.columns(20) # Membuat 20 slot kolom sejajar
                
                for i, (date, row) in enumerate(last_20.iterrows()):
                    pct = row['Pct']
                    # Warna kotak
                    bg = "🟢" if pct > 0 else "🔴" if pct < 0 else "⚪"
                    
                    with cols[i]:
                        # Menampilkan Tanggal (atas) dan Persen (bawah) secara vertikal
                        # Menggunakan font size kecil agar muat
                        st.caption(f"{date.strftime('%d/%m')}")
                        st.write(f"{bg}")
                        st.caption(f"{pct:+.1f}%")
                
                st.divider() # Garis pemisah antar saham

            except Exception as e:
                # Jika ada 1 saham error, skip ke saham berikutnya
                continue
        
        gc.collect()
