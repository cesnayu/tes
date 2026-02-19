import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock Monitor")

# List saham untuk Tab 2
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

def ambil_data(ticker_raw):
    # Logika penamaan ticker
    nama = ticker_raw.strip().upper()
    if len(nama) == 4 and "." not in nama:
        ticker = f"{nama}.JK"
    else:
        ticker = nama
        
    # Download data
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    # Cek jika data kosong, ambil backup
    if df is None or df.empty:
        df = yf.download(ticker, period="5d", interval="1m", progress=False)
        
    # Validasi akhir data
    if df is not None and not df.empty:
        # Perbaiki kolom Multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ambil kolom Close dan pastikan angka
        prices = df['Close'].astype(float).dropna()
        return prices, ticker
        
    return None, ticker

st.title("📊 Real-Time Stock Pulse")

t1, t2 = st.tabs(["🔍 Search", "⚡ Movers 5 Menit"])

with t1:
    q = st.text_input("Ketik kode saham:", "BBCA BBRI")
    for i, t_input in enumerate(q.split()):
        # Baris baru setiap 3 saham
        if i % 3 == 0:
            cols = st.columns(3)
        
        with cols[i % 3]:
            p, name = ambil_data(t_input)
            if p is not None and len(p) >= 2:
                # Ambil nilai harga
                val_now = float(p.iloc[-1])
                idx_old = -6 if len(p) >= 6 else 0
                val_old = float(p.iloc[idx_old])
                
                # Hitung skor perubahan
                skor = ((val_now - val_old) / val_old) * 100
                warna = "#00FF41" if skor >= 0 else "#FF4B4B"
                
                fig = go.Figure(go.Scatter(x=p.index, y=p.values, line=dict(color=warna, width=2)))
                fig.update_layout(
                    title=f"<b>{name}</b>: {val_now:,.0f} ({skor:+.2f}%)",
                    template="plotly_dark", height=250, margin=dict(l=5,r=5,t=40,b=5),
                    yaxis=dict(autorange=True, side="right")
                )
                st.plotly_chart(fig, use_container_width=True)

with t2:
    if st.button("Refresh Data"):
        st.rerun()
    
    hasil = []
    for s in WATCHLIST:
        p_data, s_name = ambil_data(s)
        
        # Gunakan IF murni, tidak boleh ada TRY di sini
        if p_data is not None:
            if len(p_data) >= 2:
                v_skrg = float(p_data.iloc[-1])
                idx_lalu = -6 if len(p_data) >= 6 else 0
                v_lalu = float(p_data.iloc[idx_lalu])
                
                # Kalkulasi langsung
                perubahan = ((v_skrg - v_lalu) / v_lalu) * 100
                
                # Simpan data
                item = {"Ticker": s_name, "Harga": v_skrg, "Change_5m": perubahan}
                hasil.append(item)
            
    if len(hasil) > 0:
        df_res = pd.DataFrame(hasil).sort_values("Change_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS")
            st.table(df_res.head(5))
        with c2:
            st.error("📉 TOP LOSERS")
            st.table(df_res.tail(5))
