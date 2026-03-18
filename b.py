import streamlit as st
import pandas as pd
import yfinance as yf # Asumsi fungsi get_data menggunakan yfinance
import gc

# --- 1. FUNGSI PENGAMBIL DATA (Jika belum ada atau bermasalah) ---
def get_data_safe(tickers, period="3mo"):
    """Mengambil data saham dengan penanganan error per ticker."""
    try:
        # Download massal (lebih cepat)
        data = yf.download(tickers, period=period, group_by='ticker', progress=False)
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data massal: {e}")
        return None

# --- 2. CSS (Tampilan Kompak & Rata Kiri-Kanan) ---
st.markdown("""
    <style>
    .stock-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 5px 10px; background: #262730; border-radius: 4px; margin-top: 10px;
    }
    .ticker-name { font-weight: bold; font-size: 14px; color: #FFFFFF; }
    .pos-days { font-size: 12px; color: #00C805; font-weight: bold; }
    .heatmap-row { display: flex; flex-wrap: wrap; gap: 4px; padding: 5px 0 10px 0; }
    .mini-box {
        width: 36px; height: 36px; border-radius: 4px;
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; font-size: 8px; color: white; line-height: 1.1;
    }
    .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN UI ---
st.subheader("📊 Win/Loss Heatmap")
txt = st.text_input("Kode Saham (Pisahkan dengan koma):", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # Pagination 20 per halaman
    limit = 20
    total = len(clean_ticks)
    pages = (total // limit) + (1 if total % limit > 0 else 0)
    page = st.sidebar.selectbox("Halaman", range(1, pages + 1)) if pages > 1 else 1
    
    show_ticks = clean_ticks[(page-1)*limit : page*limit]

    if show_ticks:
        with st.spinner(f"Memuat {len(show_ticks)} saham..."):
            # Menggunakan fungsi safe download
            raw_data = get_data_safe(show_ticks)

        if raw_data is not None:
            for t in show_ticks:
                try:
                    # Ambil data spesifik ticker dari hasil download massal
                    if len(show_ticks) > 1:
                        df_stock = raw_data[t].copy()
                    else:
                        df_stock = raw_data.copy()
                    
                    df_stock = df_stock.dropna(subset=['Close'])
                    if df_stock.empty: continue
                    
                    # Hitung Return & Hari Positif 30 hari terakhir
                    df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                    df_stock = df_stock.dropna(subset=['Pct'])
                    
                    last_30 = df_stock.tail(30)
                    win_count = (last_30['Pct'] > 0).sum()
                    
                    # RENDER HEADER (Kiri: Nama | Kanan: Hari Positif)
                    st.markdown(f"""
                        <div class="stock-header">
                            <span class="ticker-name">{t.replace('.JK','')}</span>
                            <span class="pos-days">Positif: {win_count} / {len(last_30)} Hari</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # RENDER HEATMAP KOTAK KECIL (20 Hari Terakhir)
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
                    continue 
        
        gc.collect()
