import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Fast Stock Dashboard")

# --- LIST SAHAM (Boleh letak banyak tanpa masalah) ---
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", 
             "BBNI.JK", "UNVR.JK", "ADRO.JK", "ASSA.JK", "CPIN.JK", "ICBP.JK"]

# --- FUNGSI DOWNLOAD SEKALIGUS (BULK) ---
def get_bulk_data(tickers):
    try:
        # Download semua saham dalam 1 request (sangat laju)
        data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', progress=False)
        
        # Jika hari ini cuti, ambil data 5 hari lepas
        if data.empty:
            data = yf.download(tickers, period="5d", interval="1m", group_by='ticker', progress=False)
            
        return data
    except:
        return None

# --- UI ---
st.title("⚡ Fast 5-Min Pulse Dashboard")

tab1, tab2 = st.tabs(["🔍 Search Custom", "⚡ 5-Min Gainers/Losers"])

with tab1:
    search_input = st.text_input("Ketik kode saham (contoh: bbca bbri):", "BBCA BBRI")
    u_tickers = [f"{t.strip().upper()}.JK" if len(t.strip())==4 and "." not in t else t.strip().upper() for t in search_input.split()]
    
    if u_tickers:
        # Download data untuk search secara bulk juga
        df_search = get_bulk_data(u_tickers)
        
        if df_search is not None:
            for i in range(0, len(u_tickers), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(u_tickers):
                        t = u_tickers[idx]
                        with cols[j]:
                            try:
                                # Ambil data spesifik ticker dari bulk data
                                if len(u_tickers) > 1:
                                    t_data = df_search[t].dropna(subset=['Close'])
                                else:
                                    t_data = df_search.dropna(subset=['Close'])

                                curr_p = float(t_data['Close'].iloc[-1])
                                old_idx = -6 if len(t_data) >= 6 else 0
                                old_p = float(t_data['Close'].iloc[old_idx])
                                chg = ((curr_p - old_p) / old_p) * 100
                                
                                fig = go.Figure(go.Scatter(
                                    x=t_data.index, y=t_data['Close'],
                                    mode='lines', line=dict(color="#00FF41" if chg >=0 else "#FF4B4B", width=2, shape='spline')
                                ))
                                fig.update_layout(title=f"<b>{t}</b>: {curr_p:,.0f} ({chg:+.2f}%)", 
                                                template="plotly_dark", height=250, margin=dict(l=5,r=5,t=40,b=5))
                                st.plotly_chart(fig, use_container_width=True)
                            except:
                                st.error(f"Data {t} error")

with tab2:
    st.subheader("Real-Time Movers (Last 5 Minutes)")
    
    if st.button("Refresh Analysis"):
        st.rerun()

    analysis_list = []
    # Download semua saham watchlist dalam satu masa
    df_bulk = get_bulk_data(WATCHLIST)
    
    if df_bulk is not None:
        for t in WATCHLIST:
            try:
                # Ambil data per ticker
                t_df = df_bulk[t].dropna(subset=['Close'])
                if len(t_df) >= 2:
                    c_p = float(t_df['Close'].iloc[-1])
                    p_idx = -6 if len(t_df) >= 6 else 0
                    p_p = float(t_df['Close'].iloc[p_idx])
                    pct = ((c_p - p_p) / p_p) * 100
                    
                    analysis_list.append({"Ticker": t, "Price": c_p, "5m_Pct": pct})
            except:
                continue

    if analysis_list:
        res_df = pd.DataFrame(analysis_list).sort_values(by="5m_Pct", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS (5m)")
            st.table(res_df.head(5).style.format({"5m_Pct": "{:+.2f}%", "Price": "{:,.0f}"}))
        with c2:
            st.error("📉 TOP LOSERS (5m)")
            st.table(res_df.tail(5).sort_values(by="5m_Pct").style.format({"5m_Pct": "{:+.2f}%", "Price": "{:,.0f}"}))

