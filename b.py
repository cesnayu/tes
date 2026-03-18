import streamlit as st
import pandas as pd
import streamlit.components.v1 as components # Tambahkan ini
import gc

# --- 1. FUNGSI RENDER HTML (Dibuat terpisah agar bersih) ---
def render_stock_card(ticker, win_count, total_days, daily_data):
    # CSS Internal untuk komponen HTML
    css = """
    <style>
        body { font-family: sans-serif; background-color: #0e1117; color: white; margin: 0; }
        .stock-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 5px 10px; background: #262730; border-radius: 4px; margin-top: 10px;
        }
        .ticker-name { font-weight: bold; font-size: 14px; }
        .pos-days { font-size: 12px; color: #00C805; font-weight: bold; }
        .heatmap-row { display: flex; flex-wrap: wrap; gap: 4px; padding: 10px 0; }
        .mini-box {
            width: 38px; height: 38px; border-radius: 4px;
            display: flex; flex-direction: column; justify-content: center;
            align-items: center; font-size: 8px; color: white; line-height: 1.1;
            text-align: center;
        }
        .mini-pct { font-weight: bold; font-size: 9px; }
    </style>
    """
    
    # Header Saham
    header_html = f"""
    <div class="stock-header">
        <span class="ticker-name">{ticker.replace('.JK','')}</span>
        <span class="pos-days">Positif: {win_count}/{total_days} Hari (30D)</span>
    </div>
    """
    
    # Heatmap Kotak
    boxes_html = '<div class="heatmap-row">'
    for date, pct in daily_data:
        bg = "#00C805" if pct > 0 else "#FF333A" if pct < 0 else "#555"
        boxes_html += f"""
            <div class="mini-box" style="background-color: {bg};">
                <span>{date}</span>
                <span class="mini-pct">{pct:+.1f}%</span>
            </div>
        """
    boxes_html += '</div>'
    
    # Gabungkan semua
    full_html = f"<html><body>{css}{header_html}{boxes_html}</body></html>"
    
    # Hitung tinggi dinamis (agar tidak ada scrollbar di dalam box)
    # Biasanya 100px - 120px cukup untuk 1 baris kotak
    components.html(full_html, height=110, scrolling=False)

# --- 2. LOGIKA DASHBOARD ---
st.title("🎲 Win/Loss Heatmap")
txt = st.text_input("Ketik Kode Saham:", value="BBCA, GOTO, ASII, TLKM, BMRI")

if txt:
    ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
    clean_ticks = [f"{t}.JK" if not t.endswith(".JK") else t for t in ticks]
    
    # Pagination 20
    limit = 20
    pages = (len(clean_ticks) // limit) + (1 if len(clean_ticks) % limit > 0 else 0)
    page = st.sidebar.number_input("Halaman", 1, pages, 1) if pages > 1 else 1
    show_ticks = clean_ticks[(page-1)*limit : page*limit]

    if show_ticks:
        with st.spinner("Fetching Data..."):
            d_wl = get_data(show_ticks)

        if d_wl is not None:
            for t in show_ticks:
                try:
                    # Ambil data per saham secara aman (Copy)
                    df_stock = d_wl[t].copy() if len(show_ticks) > 1 else d_wl.copy()
                    df_stock = df_stock.dropna(subset=['Close']).sort_index()
                    
                    if df_stock.empty: continue
                    
                    # Hitung Return
                    df_stock['Pct'] = df_stock['Close'].pct_change() * 100
                    df_stock = df_stock.dropna(subset=['Pct'])
                    
                    # Ambil data 30 hari & 20 hari terakhir
                    last_30 = df_stock.tail(30)
                    win_count = (last_30['Pct'] > 0).sum()
                    
                    # Siapkan list tuple untuk di-render (Tanggal, Persen)
                    last_20 = df_stock.tail(20)
                    daily_list = [(d.strftime('%d/%m'), r) for d, r in zip(last_20.index, last_20['Pct'])]
                    
                    # PANGGIL FUNGSI RENDER
                    render_stock_card(t, win_count, len(last_30), daily_list)
                    
                except Exception as e:
                    continue
        
        gc.collect()
