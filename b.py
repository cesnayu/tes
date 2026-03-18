import streamlit as st
import pandas as pd
import gc

# --- 1. CSS CUSTOM UNTUK TAMPILAN PADAT ---
st.markdown("""
    <style>
    /* Baris nama saham rata kiri-kanan */
    .stock-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 2px 5px;
        margin-top: 10px;
        border-bottom: 1px solid #444;
    }
    .ticker-name { font-weight: bold; font-size: 15px; color: #FAFAFA; }
    .pos-days { font-size: 13px; color: #00C805; font-weight: bold; }

    /* Container untuk kotak heatmap kecil */
    .heatmap-row {
        display: flex;
        flex-wrap: wrap;
        gap: 3px;
        padding: 5px 0 15px 0;
    }

    /* Kotak return mini */
    .mini-box {
        width: 35px;
        height: 35px;
        border-radius: 3px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 8px;
        color: white;
        line-height: 1;
    }
    .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Quick Win/Loss Tracker")

# --- 2. INPUT & DATA ---
txt = st.text_input("Ketik Kode Saham (pisahkan dengan koma):", value="BBCA, GOTO, ASII, TLKM, BMRI, AMRT, UNVR, BBNI, ADRO, PTBA")

if txt:
    # Membersihkan list ticker
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # Pagination: 20 Saham per Halaman
    limit = 20
    total_saham = len(clean_ticks)
    num_pages = (total_saham // limit) + (1 if total_saham % limit > 0 else 0)
    
    # Navigasi halaman di sidebar
    page = st.sidebar.selectbox("Pilih Halaman", range(1, num_pages + 1)) if num_pages > 1 else 1
    
    start_idx = (page - 1) * limit
    ticks_to_show = clean_ticks[start_idx : start_idx + limit]

    if ticks_to_show:
        with st.spinner(f"Mengambil data halaman {page}..."):
            # Ambil data sedikit lebih banyak untuk perhitungan pct_change
            d_wl = get_data(ticks_to_show, period="3mo")

        for t in ticks_to_show:
            try:
                # Handling jika d_wl adalah single dataframe atau dict
                dt = d_wl[t] if isinstance(d_wl, dict) else d_wl
                dt = dt.dropna().copy()
                if dt.empty: continue
                
                # Kalkulasi Persentase
                dt['Pct'] = dt['Close'].pct_change() * 100
                
                # Hitung jumlah hari positif dlm 30 hari terakhir
                last_30_days = dt.tail(30)
                pos_count = len(last_30_days[last_30_days['Pct'] > 0])
                
                # TAMPILAN HEADER: Nama (Kiri) | Positif Days (Kanan)
                st.markdown(f"""
                    <div class="stock-header">
                        <span class="ticker-name">{t.replace('.JK', '')}</span>
                        <span class="pos-days">+{pos_count} Hari Positif (30D)</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # TAMPILAN HEATMAP: Kotak-kotak kecil (20 hari terakhir)
                last_20_display = dt.tail(20)
                heatmap_html = '<div class="heatmap-row">'
                
                for date, row in last_20_display.iterrows():
                    if pd.isna(row['Pct']): continue
                    pct = row['Pct']
                    # Warna: Hijau jika positif, Merah jika negatif, Abu jika flat
                    bg = "#00C805" if pct > 0 else "#FF333A" if pct < 0 else "#555"
                    
                    heatmap_html += f"""
                        <div class="mini-box" style="background-color: {bg};" title="{date.strftime('%Y-%m-%d')}">
                            <span>{date.strftime('%d/%m')}</span>
                            <span class="mini-pct">{pct:+.1f}%</span>
                        </div>
                    """
                heatmap_html += '</div>'
                st.markdown(heatmap_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Gagal memproses {t}")
        
        gc.collect()
