import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation")

# CSS Kustom untuk tampilan lebih padat & menghilangkan padding berlebih
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    div[data-testid="stMetricValue"] {font-size: 1rem;}
    .stPlotlyChart {height: 250px;}
    button[kind="secondary"] {margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA STATIC (LIST SAHAM) ---
# Pastikan BBCA.JK dan BBRI.JK ada di sini jika ingin dijadikan default
LIST_SAHAM_IHSG = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "GOTO.JK", "KLBF.JK",
    "AMRT.JK", "MDKA.JK", "ADRO.JK", "UNTR.JK", "CPIN.JK", "INCO.JK", "PGAS.JK", "ITMG.JK", "PTBA.JK", "ANTM.JK",
    "BRPT.JK", "INDF.JK", "INKP.JK", "TPIA.JK", "EXCL.JK", "ISAT.JK", "TOWR.JK", "TBIG.JK", "MTEL.JK", "BUKA.JK",
    "ARTO.JK", "EMTK.JK", "SCMA.JK", "MNCN.JK", "MEDIA.JK", "JPFA.JK", "SMGR.JK", "INTP.JK", "JSMR.JK", "WIKA.JK",
    "PTPP.JK", "ADHI.JK", "WSKT.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPPF.JK", "RALS.JK",
    "ACES.JK", "MAPI.JK", "MAPA.JK", "ERAA.JK", "SIDO.JK", "KAEF.JK", "HEAL.JK", "MIKA.JK", "SILO.JK", "SAME.JK"
]

# --- 3. STATE MANAGEMENT (PAGINATION) ---
if 'page' not in st.session_state:
    st.session_state.page = 1

# --- 4. FUNGSI BACKEND (CACHING) ---

@st.cache_data(ttl=3600)
def get_fundamental_info(ticker):
    """Mengambil data PBV dan PER dengan Error Handling"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        pbv = info.get('priceToBook', 0)
        per = info.get('trailingPE', 0)
        return pbv, per
    except:
        return 0, 0

@st.cache_data(ttl=900)
def get_data_bulk(tickers, period="3mo", interval="1d", start=None, end=None):
    """Download data bulk dengan penanganan MultiIndex"""
    if not tickers: return pd.DataFrame()
    try:
        if start and end:
            data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, threads=True)
        else:
            data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, threads=True)
        return data
    except Exception:
        return pd.DataFrame()

def format_rupiah(value):
    if pd.isna(value): return "0"
    return f"{value:,.0f}"

# --- 5. FUNGSI VISUALISASI ---

def create_compact_candle(df, ticker, ma20=True, ma200=False):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Price", showlegend=False
    ))
    if ma20 and len(df) > 20:
        ma_20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_20, line=dict(color='orange', width=1), name="MA20", showlegend=False))
    if ma200 and len(df) > 200:
        ma_200 = df['Close'].rolling(window=200).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_200, line=dict(color='blue', width=1), name="MA200", showlegend=False))

    last_price = df['Close'].iloc[-1]
    color_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    
    fig.update_layout(
        title=dict(text=f"{ticker} ({format_rupiah(last_price)})", font=dict(size=12, color=color_title), x=0.5, y=0.95),
        margin=dict(l=10, r=10, t=30, b=10),
        height=200,
        xaxis_rangeslider_visible=False,
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

def create_advanced_chart(df, ticker, style='candle', pbv=0, per=0):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # Chart Harga
    if style == 'candle':
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="OHLC"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='green', width=2), name="Close"), row=1, col=1)

    # MA20
    if len(df) > 20:
        ma_20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_20, line=dict(color='orange', width=1.5), name="MA20"), row=1, col=1)

    # Volume
    colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

    title_text = f"{ticker} | Price: {format_rupiah(df['Close'].iloc[-1])} | PBV: {pbv:.2f}x | PER: {per:.2f}x"
    fig.update_layout(title=dict(text=title_text, font=dict(size=16), x=0), height=500, margin=dict(l=10, r=10, t=40, b=10), xaxis_rangeslider_visible=False, showlegend=False)
    return fig

# --- 6. UI DASHBOARD ---
st.title("📈 Observation")

tabs = st.tabs(["📋 List (Grid)", "⚖️ Compare & Watchlist", "📅 Weekly Recap", "🚀 Performa", "🎲 Win/Loss", "🎯 Simulator"])

# ==========================
# TAB 1: LIST (GRID SYSTEM)
# ==========================
with tabs[0]:
    # --- Filter Bar ---
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        timeframe_list = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y", "ytd"], index=2, key="tf_grid")
    with c2:
        min_price = st.number_input("Min Harga", value=0, step=50)
    with c3:
        max_price = st.number_input("Max Harga", value=100000, step=50)
    with c4:
        show_ma20_list = st.checkbox("Show MA20", value=True)
        show_ma200_list = st.checkbox("Show MA200", value=False)

    # --- Pagination Logic ---
    ITEMS_PER_PAGE = 50
    total_pages = math.ceil(len(LIST_SAHAM_IHSG) / ITEMS_PER_PAGE)
    
    # Navigasi Halaman
    col_p1, col_p2, col_p3 = st.columns([1, 8, 1])
    with col_p1:
        if st.button("⬅️ Prev", key="prev_btn"):
            if st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()
    with col_p2:
        st.markdown(f"<div style='text-align: center; padding-top: 10px; font-weight: bold;'>Page {st.session_state.page} of {total_pages}</div>", unsafe_allow_html=True)
    with col_p3:
        if st.button("Next ➡️", key="next_btn"):
            if st.session_state.page < total_pages:
                st.session_state.page += 1
                st.rerun()

    # --- Slicing & Rendering ---
    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    batch_tickers = LIST_SAHAM_IHSG[start_idx:end_idx]

    if batch_tickers:
        with st.spinner("Loading Grid Data..."):
            df_batch = get_data_bulk(batch_tickers, period=timeframe_list)
        
        # Menggunakan Container Grid
        cols = st.columns(5) # 5 Kolom per baris
        idx_counter = 0

        # Loop berdasarkan list batch agar URUT
        for t in batch_tickers:
            try:
                # Logika ekstraksi data yfinance (MultiIndex handling)
                if len(batch_tickers) > 1:
                    if t in df_batch.columns.levels[0]: # Cek apakah ticker ada di kolom
                        df_t = df_batch[t].dropna()
                    else:
                        continue
                else:
                    df_t = df_batch.dropna() # Jika cuma 1 saham

                if df_t.empty: continue
                
                last_price = df_t['Close'].iloc[-1]
                
                # Terapkan Filter Harga
                if not (min_price <= last_price <= max_price):
                    continue

                # Render Grafik
                with cols[idx_counter % 5]:
                    st.plotly_chart(
                        create_compact_candle(df_t, t, ma20=show_ma20_list, ma200=show_ma200_list),
                        use_container_width=True
                    )
                idx_counter += 1
            except Exception:
                continue

# ====================================
# TAB 2: COMPARE & WATCHLIST
# ====================================
with tabs[1]:
    st.markdown("### 🔍 Analisis & Perbandingan")
    
    # --- PERBAIKAN UTAMA: SAFETY CHECK DEFAULT VALUE ---
    default_tickers = ["BBCA.JK", "BBRI.JK"]
    # Hanya masukkan default jika ada di LIST_SAHAM_IHSG untuk mencegah Crash
    safe_defaults = [t for t in default_tickers if t in LIST_SAHAM_IHSG]

    col_w1, col_w2, col_w3 = st.columns([3, 1, 1])
    with col_w1:
        selected_stocks = st.multiselect(
            "Cari / Pilih Saham (Watchlist):", 
            options=LIST_SAHAM_IHSG, 
            default=safe_defaults # Menggunakan variable aman
        )
    with col_w2:
        chart_style = st.radio("Style:", ["Candle", "Line"], horizontal=True)
        style_code = 'candle' if chart_style == "Candle" else 'line'
    with col_w3:
        mode_waktu = st.radio("Mode:", ["Preset", "Cycle"], horizontal=True)

    # Timeframe
    start_date, end_date = None, None
    period_sel = "3mo"
    
    if mode_waktu == "Preset":
        period_sel = st.select_slider("Rentang:", options=["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], value="6mo")
    else:
        c_d1, c_d2 = st.columns(2)
        with c_d1: start_input = st.date_input("Mulai", value=datetime.now() - timedelta(days=60))
        with c_d2: end_input = st.date_input("Sampai", value=datetime.now())
        start_date = start_input.strftime("%Y-%m-%d")
        end_date = end_input.strftime("%Y-%m-%d")

    st.divider()

    if selected_stocks:
        data_compare = get_data_bulk(selected_stocks, period=period_sel, start=start_date, end=end_date)
        
        for ticker in selected_stocks:
            try:
                # Logika ekstraksi data aman
                if len(selected_stocks) > 1:
                    if ticker in data_compare.columns.levels[0]:
                        df_c = data_compare[ticker].dropna()
                    else: continue
                else:
                    df_c = data_compare.dropna()

                if df_c.empty: continue

                # Info Fundamental (Lazy Load)
                pbv, per = get_fundamental_info(ticker)
                
                st.plotly_chart(
                    create_advanced_chart(df_c, ticker, style=style_code, pbv=pbv, per=per), 
                    use_container_width=True
                )
                st.markdown("---")
            except Exception:
                continue

# ==========================
# TAB 3: WEEKLY RECAP
# ==========================
with tabs[2]:
    st.header("📅 Weekly Performance")
    
    wr_col1, wr_col2 = st.columns([3, 1])
    with wr_col1:
        # Safety check untuk default multiselect juga
        default_weekly = LIST_SAHAM_IHSG[:10] if len(LIST_SAHAM_IHSG) >= 10 else LIST_SAHAM_IHSG
        weekly_search = st.multiselect("Cari Saham:", options=LIST_SAHAM_IHSG, default=default_weekly)
    with wr_col2:
        if st.button("Reset"):
            st.rerun()

    if weekly_search:
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        w_start = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        w_data = yf.download(weekly_search, start=w_start, group_by='ticker', progress=False, threads=True)
        
        weekly_rows = []
        for t in weekly_search:
            try:
                if len(weekly_search) > 1:
                    if t in w_data.columns.levels[0]: df_w = w_data[t].dropna()
                    else: continue
                else: df_w = w_data.dropna()

                if df_w.empty: continue
                
                df_w["Return"] = df_w["Close"].pct_change() * 100
                
                row = {
                    "Ticker": t, 
                    "Price": format_rupiah(df_w["Close"].iloc[-1]), 
                    "Today (%)": round(df_w["Return"].iloc[-1], 2)
                }
                
                acc_weekly = 0
                for i in range(5):
                    target_date = (start_of_week + timedelta(days=i)).date()
                    val = 0.0
                    if target_date in df_w.index.date:
                         # Ambil return pada tanggal tersebut
                         locs = df_w.index[df_w.index.date == target_date]
                         if not locs.empty:
                             val = df_w.loc[locs[0], "Return"]
                    
                    row[days_names[i]] = round(val, 2)
                    acc_weekly += val
                
                row["Weekly Acc (%)"] = round(acc_weekly, 2)
                weekly_rows.append(row)
            except: continue
        
        if weekly_rows:
            def color_returns(val):
                if isinstance(val, (int, float)):
                    return f'color: {"#00C805" if val > 0 else "#FF333A" if val < 0 else ""}'
                return ''
            
            st.dataframe(
                pd.DataFrame(weekly_rows).style.applymap(color_returns, subset=['Today (%)', 'Weekly Acc (%)'] + days_names),
                use_container_width=True, hide_index=True
            )

# Placeholder Tabs
with tabs[3]: st.info("Maintenance: Performa")
with tabs[4]: st.info("Maintenance: Win/Loss")
with tabs[5]: st.info("Maintenance: Simulator")

st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

