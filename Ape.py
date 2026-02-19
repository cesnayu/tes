import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock 5-Min Monitor")

# Daftar Watchlist
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

def ambil_data_aman(ticker_raw):
    """Ambil data tanpa menggunakan try-except"""
    t = ticker_raw.strip().upper()
    full_t = f"{t}.JK" if len(t) == 4 and "." not in t else t
    
    # Download data
    df = yf.download(full_t, period="1d", interval="1m", progress=False)
    
    # Jika kosong, coba tarik 5 hari terakhir
    if df is None or df.empty:
        df = yf.download(full_t, period="5d", interval="1m", progress=False)
    
    # Jika masih kosong setelah dicoba lagi, stop di sini
    if df is None or df.empty:
        return None, full_t
        
    # Perbaiki struktur tabel (Multi-index fix)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Pastikan kolom Close ada dan ubah ke angka float
    if 'Close' in df.columns:
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        return df['Close'].dropna(), full_t
        
    return None, full_t

st.title("📈 5-Minute Pulse Dashboard (Stable Version)")

tab1, tab2 = st.tabs(["🔍 Search Monitor", "⚡ 5-Min Movers"])

with tab1:
    q = st.text_input("Cari Saham (Contoh: bbca bbri):", "BBCA BBRI")
    tickers = q.split()
    
    if tickers:
        for i in range(0, len(tickers), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(tickers):
                    with cols[j]:
                        p, name = ambil_data_aman(tickers[idx])
                        
                        # Validasi data dengan IF, bukan TRY
                        if p is not None and len(p) >= 2:
                            now = float(p.iloc[-1])
                            old = float(p.iloc[-6]) if len(p) >= 6 else float(p.iloc[0])
                            pct = ((now - old) / old) * 100
                            
                            color = "#00FF41" if pct >= 0 else "#FF4B4B"
                            
                            fig = go.Figure(go.Scatter(
                                x=p.index, y=p.values,
                                mode='lines', line=dict(color=color, width=2.5, shape='spline')
                            ))
                            fig.update_layout(
                                title=f"<b>{name}</b>: {now:,.0f} ({pct:+.2f}%)",
                                template="plotly_dark", height=280, margin=dict(l=5,r=5,t=50,b=5),
                                yaxis=dict(autorange=True, side="right")
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"{tickers[idx]} tidak tersedia.")

with tab2:
    if st.button("Refresh Analisis"):
        st.rerun()
    
    analysis = []
    with st.spinner("Menghitung data..."):
        for saham in WATCHLIST:
            p, name = ambil_data_aman(saham)
            
            # Gunakan pengecekan manual IF
            if p is not None and len(p) >= 2:
                val_now = float(p.iloc[-1])
                val_old = float(p.iloc[-6]) if len(p) >= 6 else float(p.iloc[0])
                diff_pct = ((val_now - val_old) / val_old) * 100
                
                analysis.append({
                    "Ticker": name,
                    "Price": val_now,
                    "Change_5m": diff_pct
                })
    
    if analysis:
        res = pd.DataFrame(analysis).sort_values("Change_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP 5-MIN GAINERS")
            st.table(res.head(5))
        with c2:
            st.error("📉 TOP 5-MIN LOSERS")
            st.table(res.tail(5).sort_values("Change_5m"))
    else:
        st.info("Data belum tersedia. Klik refresh.")
