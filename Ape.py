import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Stock Dashboard")

# Daftar saham untuk Tab 2 (Bisa kamu tambah sendiri)
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK"]

def get_data(tickers):
    try:
        # Download data secara bulk
        df = yf.download(tickers, period="1d", interval="1m", group_by='ticker', progress=False)
        if df.empty:
            df = yf.download(tickers, period="5d", interval="1m", group_by='ticker', progress=False)
        return df
    except Exception as e:
        st.error(f"Koneksi gagal: {e}")
        return None

st.title("📊 Real-Time Stock Dashboard")

tab1, tab2 = st.tabs(["🔍 Search Saham", "⚡ 5-Min Movers"])

# --- TAB 1: SEARCH ---
with tab1:
    user_input = st.text_input("Ketik kode saham (misal: bbca bbri):", "BBCA BBRI")
    tickers_search = []
    for t in user_input.split():
        t = t.strip().upper()
        if len(t) == 4 and "." not in t:
            tickers_search.append(f"{t}.JK")
        else:
            tickers_search.append(t)
    
    if tickers_search:
        df_search = get_data(tickers_search)
        if df_search is not None:
            for i in range(0, len(tickers_search), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(tickers_search):
                        t = tickers_search[idx]
                        with cols[j]:
                            try:
                                # Ambil data per saham
                                if len(tickers_search) > 1:
                                    data_t = df_search[t].dropna(subset=['Close'])
                                else:
                                    data_t = df_search.dropna(subset=['Close'])
                                
                                if not data_t.empty:
                                    curr = float(data_t['Close'].iloc[-1])
                                    prev = float(data_t['Close'].iloc[-6]) if len(data_t) >= 6 else float(data_t['Close'].iloc[0])
                                    pct = ((curr - prev) / prev) * 100
                                    
                                    fig = go.Figure(go.Scatter(
                                        x=data_t.index, y=data_t['Close'],
                                        mode='lines', line=dict(color="#00FF41" if pct >= 0 else "#FF4B4B", width=2, shape='spline')
                                    ))
                                    fig.update_layout(title=f"<b>{t}</b>: {curr:,.0f} ({pct:+.2f}%)", 
                                                    template="plotly_dark", height=250, margin=dict(l=5,r=5,t=40,b=5))
                                    st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                st.warning(f"Gagal memuat {t}")

# --- TAB 2: 5-MIN GAINERS/LOSERS ---
with tab2:
    st.subheader("Movers dlm 5 Menit Terakhir")
    if st.button("Refresh Data"):
        st.rerun()
        
    df_bulk = get_data(WATCHLIST)
    analysis = []
    
    if df_bulk is not None:
        for t in WATCHLIST:
            try:
                # Ambil data individu dari hasil download massal
                t_df = df_bulk[t].dropna(subset=['Close'])
                if len(t_df) >= 2:
                    curr_p = float(t_df['Close'].iloc[-1])
                    # Bandingkan dengan 5 baris sebelumnya (5 menit)
                    old_p = float(t_df['Close'].iloc[-6]) if len(t_df) >= 6 else float(t_df['Close'].iloc[0])
                    diff = ((curr_p - old_p) / old_p) * 100
                    analysis.append({"Ticker": t, "Price": curr_p, "Change_5m": diff})
            except Exception:
                continue # Abaikan jika satu saham error

    if analysis:
        res_df = pd.DataFrame(analysis).sort_values(by="Change_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS (5m)")
            st.table(res_df.head(5).style.format({"Change_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
        with c2:
            st.error("📉 TOP LOSERS (5m)")
            st.table(res_df.tail(5).sort_values(by="Change_5m").style.format({"Change_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
    else:
        st.info("Klik refresh atau tunggu market buka.")
