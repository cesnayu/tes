import streamlit as st
import pandas as pd
import yfinance as yf
import gc

# --- 1. DEFINISI FUNGSI get_data (WAJIB ADA) ---
def get_data(tickers, period="3mo"):
    try:
        # Download data saham dari Yahoo Finance
        data = yf.download(tickers, period=period, group_by='ticker', progress=False)
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

# --- 2. CSS UNTUK TAMPILAN KOMPAK ---
st.markdown("""
    <style>
    .stock-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 5px 10px; background: #262730; border-radius: 4px; margin-top: 15px;
    }
    .ticker-name { font-weight: bold; font-size: 14px; color: #FFFFFF; }
    .pos-days { font-size: 12px; color: #00C805; font-weight: bold; }
    .heatmap-row { display: flex; flex-wrap: wrap; gap: 4px; padding: 10px 0; }
    .mini-box {
        width: 38px; height: 38px; border-radius: 4px;
        display: flex; flex-direction: column; justify-content: center;
        align-items: center; font-size: 8px; color: white; line-height: 1.1;
    }
    .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Win/Loss Heatmap")

# --- 3. INPUT & PAGINATION ---
txt = st.text_input("Ketik Kode Saham:", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # Pagination: 20 Saham per Halaman
    limit = 20
    total_saham = len(clean_ticks)
    num_pages = (total_saham // limit) + (1 if total_saham % limit > 0 else 0)
    
    # Pilih halaman di sidebar
    page = st.sidebar.number_input("Halaman", 1, num_pages, 1) if num_pages > 1 else 1
    
    # Potong list biar cuma muncul 20 per halaman
    start_idx = (page - 1) * limit
    ticks_to_show = clean_ticks[start_idx : start_idx + limit]

    if ticks_to_show:
        with st.spinner("Fetching data..."):
            d_wl = get_data(ticks_to_show) # Memanggil fungsi yang sudah didefinisikan di atas

        if d_wl is not None:
            for t in ticks_to_show:
                try:
                    # Ambil data per saham
                    if len(ticks_to_show) > 1:
                        df_stock = d_wl[t].copy()
                    else:
                        df_stock = d_wl.copy()
                    
                    df_stock = df_stock.dropna(subset=['Close'])
                    if df_stock.empty: continue
                    
                    # Hitung Return
                    df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                    df_stock = df_stock.dropna(subset=['Pct'])
                    
                    # Hitung Hari Positif (30 Hari Terakhir)
                    last_30 = df_stock.tail(30)
                    win_count = (last_30['Pct'] > 0).sum()
                    
                    # HEADER (Nama Kiri | Info Kanan)
                    st.markdown(f"""
                        <div class="stock-header">
                            <span class="ticker-name">{t.replace('.JK','')}</span>
                            <span class="pos-days">+{win_count} Hari Positif (30D)</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # HEATMAP KOTAK KECIL (20 Hari Terakhir)
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
                    st.divider()

                except:
                    continue
        
        gc.collect()
