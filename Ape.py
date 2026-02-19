import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Konfigurasi Dasar
st.set_page_config(layout="wide", page_title="Safe Stock Dash")

# Daftar Watchlist untuk Tab 2
WATCHLIST = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

def get_single_stock(ticker_input):
    """Fungsi paling stabil untuk ambil data saham tunggal"""
    # Auto-suffix .JK
    t = ticker_input.upper()
    full_t = f"{t}.JK" if len(t) == 4 and "." not in t else t
    
    try:
        # Ambil data 1 menit
        df = yf.download(full_t, period="1d", interval="1m", progress=False)
        
        # Jika hari ini kosong, ambil hari terakhir buka
        if df.empty:
            df = yf.download(full_t, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        if df.empty:
            return None, full_t

        # --- BERSIHKAN DATA (Kunci Utama Anti-Error) ---
        # 1. Jika kolomnya bertumpuk (Multi-index), ratakan jadi satu lapis
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # 2. Pastikan kolom 'Close' ada
        if 'Close' not in df.columns:
            return None, full_t
            
        # 3. Ambil data Close dan pastikan jadi angka (float)
        prices = df['Close'].astype(float).dropna()
        return prices, full_t
    except Exception:
        return None, full_t

# --- Tampilan Dashboard ---
st.title("📈 Stock Pulse Dashboard")

tab1, tab2 = st.tabs(["🔍 Monitor Saham", "⚡ Perubahan 5 Menit"])

# TAB 1: SEARCH
with tab1:
    search_q = st.text_input("Cari saham (misal: bbca bbri tlkm):", "BBCA BBRI")
    tickers = search_q.split()
    
    if tickers:
        for i in range(0, len(tickers), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(tickers):
                    with cols[j]:
                        prices, name = get_single_stock(tickers[idx])
                        if prices is not None and len(prices) > 1:
                            curr = float(prices.iloc[-1])
                            # Hitung perubahan 5 menit
                            prev = float(prices.iloc[-6]) if len(prices) >= 6 else float(prices.iloc[0])
                            pct = ((curr - prev) / prev) * 100
                            
                            color = "#00FF41" if pct >= 0 else "#FF4B4B"
                            
                            fig = go.Figure(go.Scatter(
                                x=prices.index, y=prices.values,
                                mode='lines', line=dict(color=color, width=2, shape='spline')
                            ))
                            fig.update_layout(
                                title=f"<b>{name}</b>: {curr:,.0f} ({pct:+.2f}%)",
                                template="plotly_dark", height=250,
                                yaxis=dict(autorange=True, side="right"),
                                margin=dict(l=5, r=5, t=40, b=5)
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning(f"Data {tickers[idx]} tidak tersedia")

# TAB 2: ANALYSIS
with tab2:
    st.subheader("Top Movers (5 Menit Terakhir)")
    if st.button("Refresh Analisis"):
        st.rerun()

    results = []
    # Menggunakan spinner supaya user tahu sedang proses
    with st.spinner("Mengambil data..."):
        for t in WATCHLIST:
            prices, name = get_single_stock(t)
            if prices is not None and len(prices) >= 2:
                curr = float(prices.iloc[-1])
                prev = float(prices.iloc[-6]) if len(prices) >= 6 else float(prices.iloc[0])
                diff = ((curr - prev) / prev) * 100
                results.append({"Ticker": name, "Price": curr, "Chg_5m": diff})

    if results:
        res_df = pd.DataFrame(results).sort_values(by="Chg_5m", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS (5m)")
            st.table(res_df.head(5).style.format({"Chg_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
        with c2:
            st.error("📉 TOP LOSERS (5m)")
            st.table(res_df.tail(5).sort_values(by="Chg_5m").style.format({"Chg_5m": "{:+.2f}%", "Price": "{:,.0f}"}))
    else:
        st.info("Tidak ada data. Pastikan market sedang buka atau gunakan saham yang valid.")
