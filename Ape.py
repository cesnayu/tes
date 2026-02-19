import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock Monitor")

# List saham untuk dipantau
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

st.title("📈 Real-Time Stock Pulse")

t1, t2 = st.tabs(["🔍 Search", "⚡ Movers 5 Menit"])

with t1:
    q = st.text_input("Ketik kode saham:", "BBCA BBRI")
    list_saham = q.split()
    
    if list_saham:
        for i, s_input in enumerate(list_saham):
            # Layouting 3 kolom
            if i % 3 == 0:
                cols = st.columns(3)
            
            with cols[i % 3]:
                # Logika Ticker
                t_raw = s_input.upper()
                nama_saham = f"{t_raw}.JK" if len(t_raw) == 4 and "." not in t_raw else t_raw
                
                # Tarik Data
                df = yf.download(nama_saham, period="1d", interval="1m", progress=False)
                if df is None or df.empty:
                    df = yf.download(nama_saham, period="5d", interval="1m", progress=False)

                if df is not None and not df.empty:
                    # Fix kolom jika bertumpuk
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    p = df['Close'].astype(float).dropna()
                    
                    if len(p) >= 2:
                        now_val = float(p.iloc[-1])
                        old_idx = -6 if len(p) >= 6 else 0
                        old_val = float(p.iloc[old_idx])
                        
                        # Hitung perubahan
                        hasil_ubah = ((now_val - old_val) / old_val) * 100
                        warna = "#00FF41" if hasil_ubah >= 0 else "#FF4B4B"
                        
                        fig = go.Figure(go.Scatter(x=p.index, y=p.values, line=dict(color=warna, width=2)))
                        fig.update_layout(
                            title=f"<b>{nama_saham}</b>: {now_val:,.0f} ({hasil_ubah:+.2f}%)",
                            template="plotly_dark", height=250, margin=dict(l=5,r=5,t=40,b=5),
                            yaxis=dict(autorange=True, side="right")
                        )
                        st.plotly_chart(fig, use_container_width=True)

with t2:
    if st.button("Refresh Data"):
        st.rerun()
    
    list_hasil = []
    for s in WATCHLIST:
        df_w = yf.download(s, period="1d", interval="1m", progress=False)
        if df_w is None or df_w.empty:
            df_w = yf.download(s, period="5d", interval="1m", progress=False)
            
        if df_w is not None and not df_w.empty:
            if isinstance(df_w.columns, pd.MultiIndex):
                df_w.columns = df_w.columns.get_level_values(0)
            
            pw = df_w['Close'].astype(float).dropna()
            
            if len(pw) >= 2:
                v_now = float(pw.iloc[-1])
                v_old = float(pw.iloc[-6]) if len(pw) >= 6 else float(pw.iloc[0])
                v_ubah = ((v_now - v_old) / v_old) * 100
                
                # Masukkan ke list
                list_hasil.append({"Ticker": s, "Harga": v_now, "Ubah_5m": v_ubah})
            
    if len(list_hasil) > 0:
        res_df = pd.DataFrame(list_hasil).sort_values("Ubah_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS")
            st.table(res_df.head(5))
        with c2:
            st.error("📉 TOP LOSERS")
            st.table(res_df.tail(5))
