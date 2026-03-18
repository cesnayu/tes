import streamlit as st
import pandas as pd
import gc

# --- 1. CSS (Dibuat Global agar tidak dipanggil berulang kali) ---
st.markdown("""
    <style>
    .stock-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 5px 10px; background: #262730; border-radius: 4px; margin-top: 15px;
    }
    .ticker-name { font-weight: bold; font-size: 14px; color: #FFFFFF; }
    .pos-days { font-size: 12px; color: #00C805; font-weight: bold; }
    .heatmap-row { 
        display: flex; flex-wrap: wrap; gap: 4px; padding: 10px 0; 
        min-height: 40px;
    }
    .mini-box {
        width: 38px; height: 38px; border-radius: 4px;
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; font-size: 8px; color: white; line-height: 1.1;
    }
    .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Win/Loss Heatmap")

# --- 2. INPUT & PAGINATION LOGIC ---
txt = st.text_input("Kode Saham (Pisahkan dengan koma):", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    # Bersihkan list
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # HITUNG PAGINATION
    limit = 20
    total_saham = len(clean_ticks)
    num_pages = (total_saham // limit) + (1 if total_saham % limit > 0 else 0)
    
    # Navigasi Halaman
    if num_pages > 1:
        page = st.sidebar.number_input(f"Halaman (Total {num_pages})", 1, num_pages, 1)
    else:
        page = 1
    
    # POTONG LIST (PENTING: Agar hanya 20 yang muncul)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    ticks_to_show = clean_ticks[start_idx:end_idx]

    # --- 3. FETCH & RENDER ---
    if ticks_to_show:
        with st.spinner(f"Loading page {page}..."):
            d_wl = get_data(ticks_to_show, period="3mo")

        for t in ticks_to_show:
            try:
                # Isolasi Data (Anti Leak)
                if isinstance(d_wl, dict):
                    df_stock = d_wl[t].copy()
                else:
                    df_stock = d_wl[t].copy() if len(ticks_to_show) > 1 else d_wl.copy()
                
                df_stock = df_stock.dropna(subset=['Close'])
                if df_stock.empty: continue
                
                # Hitung Return
                df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                df_stock = df_stock.dropna(subset=['Pct'])
                
                # Info Hari Positif (30 Hari Terakhir)
                last_30 = df_stock.tail(30)
                win_count = (last_30['Pct'] > 0).sum()
                
                # HEADER: Rata Kiri & Rata Kanan
                st.markdown(f"""
                    <div class="stock-header">
                        <span class="ticker-name">{t.replace('.JK','')}</span>
                        <span class="pos-days">Positif: {win_count} / {len(last_30)} Hari</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # HEATMAP: Render dalam satu blok markdown per saham
                last_20 = df_stock.tail(20)
                heatmap_html = '<div class="heatmap-row">'
                
                for date, row in last_20.iterrows():
                    p = row['Pct']
                    bg = "#00C805" if p > 0 else "#FF333A" if p < 0 else "#555"
                    heatmap_html += f"""
                        <div class="mini-box" style="background-color: {bg};">
                            <span>{date.strftime('%d/%m')}</span>
                            <span class="mini-pct">{p:+.1f}%</span>
                        </div>
                    """
                heatmap_html += '</div>'
                
                # TAMPILKAN SEBAGAI SATU KESATUAN ELEMEN
                st.markdown(heatmap_html, unsafe_allow_html=True)
                st.divider() # Pemisah antar saham agar rapi

            except Exception:
                continue
        
        gc.collect()
