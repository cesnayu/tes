import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Safe Stock Dashboard")

# --- KONFIGURASI SAHAM ---
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK"]

def get_stock_data(ticker_input):
    # Auto-suffix .JK
    ticker = f"{ticker_input.upper()}.JK" if len(ticker_input) == 4 and "." not in ticker_input else ticker_input.upper()
    
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        # Backup jika market hari ini tutup
        if df.empty:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        if df.empty:
            return None, ticker

        # --- FIX MULTI-INDEX & DATA TYPE ---
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Pastikan kolom Close adalah angka (float)
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df = df.dropna(subset=['Close'])
            
        return df, ticker
    except:
        return None, ticker

# --- UI DASHBOARD ---
st.title("📊 5-Minute Pulse Monitor")

tab1, tab2 = st.tabs(["🔍 Search Custom", "⚡ 5-Min Gainers/Losers"])

with tab1:
    search_input = st.text_input("Ketik kode saham (misal: bbca bbri):", "BBCA BBRI")
    tickers_to_show = [t.strip() for t in search_input.split() if t.strip()]
    
    if tickers_to_show:
        for i in range(0, len(tickers_to_show), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(tickers_to_show):
                    with cols[j]:
                        df, full_name = get_stock_data(tickers_to_show[idx])
                        if df is not None and len(df) >= 2:
                            current_p = float(df['Close'].iloc[-1])
                            # Perubahan 5 menit
                            old_idx = -6 if len(df) >= 6 else 0
                            old_p = float(df['Close'].iloc[old_idx])
                            change_5m = ((current_p - old_p) / old_p) * 100
                            
                            color = "#00FF41" if change_5m >= 0 else "#FF4B4B"
                            
                            fig = go.Figure(go.Scatter(
                                x=df.index, y=df['Close'],
                                mode='lines', line=dict(color=color, width=2.5, shape='spline')
                            ))
                            fig.update_layout(
                                title=f"<b>{full_name}</b>: {current_p:,.0f} ({change_5m:+.2f}%)",
                                template="plotly_dark", height=300,
                                yaxis=dict(autorange=True, side="right"),
                                margin=dict(l=5, r=5, t=50, b=5)
                            )
                            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Real-Time Movers (Last 5 Minutes)")
    analysis_data = []
    
    with st.spinner("Crunching data..."):
        for t in WATCHLIST:
            df, full_name = get_stock_data(t)
            if df is not None and len(df) >= 2:
                # Ambil nilai skalar (bukan Series) menggunakan float()
                curr = float(df['Close'].iloc[-1])
                prev_idx = -6 if len(df) >= 6 else 0
                prev = float(df['Close'].iloc[prev_idx])
                diff_pct = ((curr - prev) / prev) * 100
                
                analysis_data.append({
                    "Ticker": full_name,
                    "Price": round(curr, 2),
                    "5m_Pct": round(diff_pct, 4) # Gunakan nama kolom tanpa spasi/simbol agar aman
                })
    
    if analysis_data:
        # Konversi ke DataFrame
        res_df = pd.DataFrame(analysis_data)
        
        # Pastikan tipe data kolom sorting adalah float
        res_df["5m_Pct"] = res_df["5m_Pct"].astype(float)
        
        # Urutkan
        res_df = res_df.sort_values(by="5m_Pct", ascending=False)
        
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP 5-MIN GAINERS")
            # Styling agar lebih rapi
            st.table(res_df.head(5).style.format({"5m_Pct": "{:+.2f}%", "Price": "{:,.0f}"}))
        with c2:
            st.error("📉 TOP 5-MIN LOSERS")
            st.table(res_df.tail(5).sort_values(by="5m_Pct").style.format({"5m_Pct": "{:+.2f}%", "Price": "{:,.0f}"}))
    else:
        st.warning("Tidak ada data yang bisa dianalisis.")
