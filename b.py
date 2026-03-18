import streamlit as st
import pandas as pd
import gc

# --- CSS (Tetap Kompak) ---
st.markdown("""
    <style>
    .stock-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 4px 8px; background: #262730; border-radius: 4px; margin-top: 12px;
    }
    .ticker-name { font-weight: bold; font-size: 14px; color: #FFFFFF; }
    .pos-days { font-size: 12px; color: #00C805; }
    .heatmap-row { display: flex; flex-wrap: wrap; gap: 4px; padding: 8px 0; }
    .mini-box {
        width: 36px; height: 36px; border-radius: 4px;
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; font-size: 8px; color: white; line-height: 1;
    }
    .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

st.subheader("📊 Win/Loss Heatmap (20 Stocks/Page)")

txt = st.text_input("Kode Saham:", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # --- PAGINATION ---
    limit = 20
    total = len(clean_ticks)
    pages = (total // limit) + (1 if total % limit > 0 else 0)
    curr_page = st.sidebar.number_input("Halaman", 1, pages, 1) if pages > 1 else 1
    
    show_ticks = clean_ticks[(curr_page-1)*limit : curr_page*limit]

    if show_ticks:
        with st.spinner("Fetching Data..."):
            # Ambil data baru setiap kali untuk menghindari leak data lama
            raw_data = get_data(show_ticks, period="3mo")

        for t in show_ticks:
            try:
                # SOLUSI DATA LEAK: Gunakan .copy() agar tidak merubah dataframe asli
                if isinstance(raw_data, dict):
                    df_stock = raw_data[t].copy()
                else:
                    df_stock = raw_data[t].copy() if len(show_ticks) > 1 else raw_data.copy()
                
                df_stock = df_stock.dropna()
                if df_stock.empty: continue
                
                # Hitung Return Lokal (Hanya untuk ticker ini)
                df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                df_stock = df_stock.dropna(subset=['Pct'])
                
                # Ambil 30 hari terakhir untuk hitung win rate
                last_30 = df_stock.tail(30)
                win_count = (last_30['Pct'] > 0).sum()
                
                # TAMPILAN HEADER (Nama Kiri | Info Kanan)
                st.markdown(f"""
                    <div class="stock-header">
                        <span class="ticker-name">{t.replace('.JK','')}</span>
                        <span class="pos-days">Positif: {win_count}/30 Hari</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # TAMPILAN HEATMAP (20 Hari Terakhir)
                last_20 = df_stock.tail(20)
                h_html = '<div class="heatmap-row">'
                for date, row in last_20.iterrows():
                    p = row['Pct']
                    bg = "#00C805" if p > 0 else "#FF333A" if p < 0 else "#555"
                    h_html += f"""
                        <div class="mini-box" style="background-color: {bg};">
                            <span>{date.strftime('%d/%m')}</span>
                            <span class="mini-pct">{p:+.1f}%</span>
                        </div>
                    """
                h_html += '</div>'
                st.markdown(h_html, unsafe_allow_html=True)

            except Exception:
                continue # Skip jika ada satu saham yang error agar tidak merusak list
        
        gc.collect()
