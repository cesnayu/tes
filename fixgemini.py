import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# CSS Kustom
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    div[data-testid="stMetricValue"] {font-size: 1rem;}
    .stPlotlyChart {height: 280px;}
    
    /* CSS BARU UNTUK WIN/LOSS HEATMAP */
    .wl-wrapper {
        display: grid;
        grid-template-columns: repeat(5, 1fr); /* 5 Kolom */
        gap: 8px;
        margin-bottom: 20px;
    }
    .wl-card {
        border-radius: 6px;
        padding: 8px 4px;
        text-align: center;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.1s;
    }
    .wl-card:hover {
        transform: scale(1.05);
    }
    .wl-date { font-size: 10px; opacity: 0.9; margin-bottom: 2px; }
    .wl-price { font-size: 13px; font-weight: bold; margin-bottom: 2px; }
    .wl-pct { font-size: 11px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA STATIC ---
LIST_SAHAM_IHSG = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "GOTO.JK", "KLBF.JK",
    "AMRT.JK", "MDKA.JK", "ADRO.JK", "UNTR.JK", "CPIN.JK", "INCO.JK", "PGAS.JK", "ITMG.JK", "PTBA.JK", "ANTM.JK",
    "BRPT.JK", "INDF.JK", "INKP.JK", "TPIA.JK", "EXCL.JK", "ISAT.JK", "TOWR.JK", "TBIG.JK", "MTEL.JK", "BUKA.JK",
    "ARTO.JK", "EMTK.JK", "SCMA.JK", "MNCN.JK", "MEDIA.JK", "JPFA.JK", "SMGR.JK", "INTP.JK", "JSMR.JK", "WIKA.JK",
    "PTPP.JK", "ADHI.JK", "WSKT.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPPF.JK", "RALS.JK",
    "ACES.JK", "MAPI.JK", "MAPA.JK", "ERAA.JK", "SIDO.JK", "KAEF.JK", "HEAL.JK", "MIKA.JK", "SILO.JK", "SAME.JK"
]

# --- 3. STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'sim_balance' not in st.session_state: st.session_state.sim_balance = 100000000
if 'sim_portfolio' not in st.session_state: st.session_state.sim_portfolio = {}
if 'sim_history' not in st.session_state: st.session_state.sim_history = []

# --- 4. FUNGSI BACKEND ---
@st.cache_data(ttl=3600)
def get_fundamental_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('priceToBook', 0), info.get('trailingPE', 0)
    except: return 0, 0

@st.cache_data(ttl=900)
def get_data_bulk(tickers, period="3mo", interval="1d", start=None, end=None):
    if not tickers: return pd.DataFrame()
    try:
        if start and end:
            data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, threads=True, auto_adjust=True)
        else:
            data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, threads=True, auto_adjust=True)
        return data
    except: return pd.DataFrame()

def format_rupiah(value):
    if pd.isna(value): return "0"
    return f"{value:,.0f}"

def format_volume(value):
    if pd.isna(value): return "0"
    if value >= 1000000000: return f"{value/1000000000:.1f}B"
    if value >= 1000000: return f"{value/1000000:.1f}M"
    if value >= 1000: return f"{value/1000:.1f}K"
    return f"{value:.0f}"

# --- 5. FUNGSI VISUALISASI CHART ---
def create_chart(df, ticker, ma20=True, chart_type="Candle"):
    fig = go.Figure()
    
    # Line Chart
    if chart_type == "Line":
        color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', 
            line=dict(color=color_line, width=2), name="Price"
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], fill='tozeroy', mode='none',
            fillcolor=f"rgba{tuple(int(color_line.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
            showlegend=False
        ))
        xaxis_config = dict(showgrid=False, showticklabels=False, type="date")
    
    # Candle Chart
    else:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
            name="Price", showlegend=False
        ))
        xaxis_config = dict(showgrid=False, showticklabels=False, rangeslider=dict(visible=False))

    # MA20
    if ma20 and len(df) > 20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), showlegend=False, name="MA20"))
    
    last_price = df['Close'].iloc[-1]
    color_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    
    fig.update_layout(
        title=dict(text=f"{ticker} ({format_rupiah(last_price)})", font=dict(size=14, color=color_title), x=0.5, y=0.95),
        margin=dict(l=10, r=10, t=30, b=10), 
        height=250,
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=xaxis_config
    )
    return fig

def create_advanced_chart(df, ticker, style='candle', pbv=0, per=0):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    if style == 'candle':
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="OHLC"), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='green', width=2), name="Close"), row=1, col=1)
    
    if len(df) > 20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1.5), name="MA20"), row=1, col=1)

    colors = ['red' if r['Open'] - r['Close'] >= 0 else 'green' for i, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

    fig.update_layout(
        title=dict(text=f"{ticker} | PBV: {pbv:.2f}x | PER: {per:.2f}x", font=dict(size=14), x=0),
        height=500, margin=dict(l=10, r=10, t=30, b=10), xaxis_rangeslider_visible=False, showlegend=False
    )
    return fig

# --- 6. UI DASHBOARD ---
st.title("📈 Observation Pro")

tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Market Recap", "🎲 Win/Loss", "🎯 Simulator"])

# ==========================
# TAB 1: LIST (GRID 4 KOLOM)
# ==========================
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5])
    with c1: tf_grid = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=2, key="tg")
    with c2: min_p = st.number_input("Min Price", 0, step=50, key="minp")
    with c3: max_p = st.number_input("Max Price", 100000, step=50, key="maxp")
    with c4: chart_type_sel = st.radio("Grafik", ["Candle", "Line"], horizontal=True, key="ctype")
    with c5: show_ma = st.checkbox("Show MA20", True, key="sma")

    ITEMS_PER_PAGE = 20
    total_pages = math.ceil(len(LIST_SAHAM_IHSG) / ITEMS_PER_PAGE)
    
    cp1, cp2, cp3 = st.columns([1, 8, 1])
    with cp1: 
        if st.button("⬅️ Prev") and st.session_state.page > 1: st.session_state.page -= 1; st.rerun()
    with cp2: st.markdown(f"<div style='text-align: center; font-weight:bold; margin-top:5px;'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)
    with cp3: 
        if st.button("Next ➡️") and st.session_state.page < total_pages: st.session_state.page += 1; st.rerun()

    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    batch = LIST_SAHAM_IHSG[start_idx:start_idx + ITEMS_PER_PAGE]

    if batch:
        with st.spinner("Loading Grid..."):
            df_batch = get_data_bulk(batch, period=tf_grid)
        
        cols = st.columns(4)
        idx = 0
        for t in batch:
            try:
                if len(batch) == 1:
                    dft = df_batch
                    if dft.empty: continue 
                else:
                    if t in df_batch.columns.levels[0]: dft = df_batch[t]
                    else: continue
                
                dft = dft.dropna()
                if dft.empty: continue
                if not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                
                with cols[idx % 4]: 
                    st.plotly_chart(create_chart(dft, t, ma20=show_ma, chart_type=chart_type_sel), use_container_width=True)
                idx += 1
            except Exception: continue

# ==========================
# TAB 2: COMPARE
# ==========================
with tabs[1]:
    sel_stocks = st.multiselect("Pilih Saham:", LIST_SAHAM_IHSG, ["BBCA.JK", "BBRI.JK"], key="ms_comp")
    if sel_stocks:
        data_c = get_data_bulk(sel_stocks, period="6mo")
        for t in sel_stocks:
            try:
                dfc = data_c[t].dropna() if len(sel_stocks) > 1 else data_c.dropna()
                if dfc.empty: continue
                pbv, per = get_fundamental_info(t)
                st.plotly_chart(create_advanced_chart(dfc, t, pbv=pbv, per=per), use_container_width=True)
            except: pass

# ==========================
# TAB 3: MARKET RECAP
# ==========================
with tabs[2]:
    st.header("📅 Market Recap")
    
    w_search = st.multiselect("Cari Saham (Kosong = Semua):", LIST_SAHAM_IHSG, key="ms_recap")
    target_weekly = w_search if w_search else LIST_SAHAM_IHSG
    
    if len(target_weekly) > 50 and not w_search:
        st.info(f"Menampilkan 50 saham pertama dari {len(target_weekly)}.")
        target_weekly = target_weekly[:50]

    if st.button("Load Data Recap"):
        with st.spinner("Calculating..."):
            w_data = get_data_bulk(target_weekly, period="2y") # Ambil 2 tahun agar 1 Year Return valid
            
            w_rows = []
            days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            today = datetime.now().date()
            start_week = today - timedelta(days=today.weekday())

            for t in target_weekly:
                try:
                    if len(target_weekly) == 1: dfw = w_data
                    else:
                        if t in w_data.columns.levels[0]: dfw = w_data[t]
                        else: continue
                    
                    dfw = dfw.dropna()
                    if dfw.empty: continue
                    
                    curr = dfw['Close'].iloc[-1]
                    vol = dfw['Volume'].iloc[-1]
                    
                    # Logic Return yang Lebih Aman
                    def get_safe_return(days_ago):
                        if len(dfw) < 5: return 0.0
                        # Cari index tanggal sekitar days_ago hari lalu
                        target_idx = -1 * min(len(dfw), days_ago) # Simple approach: Trading days approx
                        # Lebih akurat menggunakan loc index search, tapi untuk performa kita pakai iloc approx
                        # 1 Year ~ 240 trading days
                        if days_ago == 365: offset = 240
                        elif days_ago == 180: offset = 120
                        elif days_ago == 30: offset = 20
                        else: offset = 1
                        
                        if len(dfw) > offset:
                            prev = dfw['Close'].iloc[-offset]
                            return ((curr - prev) / prev) * 100
                        return 0.0

                    row = {
                        "Ticker": t, 
                        "Price": format_rupiah(curr),
                        "Volume": format_volume(vol)
                    }
                    
                    acc = 0
                    for i, d_name in enumerate(days_en):
                        t_date = start_week + timedelta(days=i)
                        val = 0.0
                        if pd.Timestamp(t_date) in dfw.index:
                            loc = dfw.index.get_loc(pd.Timestamp(t_date))
                            if loc > 0:
                                p_now = dfw['Close'].iloc[loc]
                                p_prev = dfw['Close'].iloc[loc-1]
                                val = ((p_now - p_prev) / p_prev) * 100
                        row[d_name] = val
                        acc += val
                    
                    row["Weekly (%)"] = acc
                    row["1 Month (%)"] = get_safe_return(30)
                    row["6 Month (%)"] = get_safe_return(180)
                    row["1 Year (%)"] = get_safe_return(365)
                    
                    w_rows.append(row)
                except Exception as e: continue
            
            if w_rows:
                df_res = pd.DataFrame(w_rows)
                numeric_cols = days_en + ["Weekly (%)", "1 Month (%)", "6 Month (%)", "1 Year (%)"]
                def style_color(v):
                    if isinstance(v, (int, float)):
                        return f'color: {"#00C805" if v > 0 else "#FF333A" if v < 0 else ""}'
                    return ""
                
                st.dataframe(
                    df_res.style.applymap(style_color, subset=numeric_cols).format("{:.2f}", subset=numeric_cols),
                    use_container_width=True, hide_index=True, height=500
                )
            else: st.warning("Data tidak tersedia.")

# ==========================
# TAB 4: WIN/LOSS (FIXED)
# ==========================
with tabs[3]:
    st.header("🎲 Win/Loss Heatmap (20 Hari Terakhir)")
    
    # 1. Input Search
    wl_sel = st.multiselect("Pilih Saham (Minimal 1):", LIST_SAHAM_IHSG, default=["BBCA.JK"], key="wl_input")
    
    if wl_sel:
        # 2. Ambil Data
        with st.spinner("Mengambil data..."):
            wl_data = get_data_bulk(wl_sel, period="3mo") # Ambil 3 bulan agar cukup 20 hari
        
        # 3. Loop per Saham
        for ticker in wl_sel:
            try:
                # Extract DataFrame
                if len(wl_sel) == 1: dfw = wl_data
                else:
                    if ticker in wl_data.columns.levels[0]: dfw = wl_data[ticker]
                    else: continue
                
                dfw = dfw.dropna()
                if dfw.empty: continue
                
                # Hitung Return Harian
                dfw['Pct'] = dfw['Close'].pct_change() * 100
                
                # Ambil 20 Data Terakhir & Urutkan (Lama -> Baru atau Baru -> Lama)
                # Kita ambil 20 terakhir, lalu urutkan dari kiri (terlama di jendela itu) ke kanan (terbaru)
                last_20 = dfw.tail(20)
                
                if len(last_20) > 0:
                    st.subheader(f"{ticker}")
                    
                    # Generate HTML Grid
                    html_content = '<div class="wl-wrapper">'
                    
                    for date, row in last_20.iterrows():
                        pct = row['Pct']
                        price = row['Close']
                        date_str = date.strftime('%d/%m')
                        
                        # Tentukan Warna
                        if pct > 0: bg_color = "#00C805" # Hijau
                        elif pct < 0: bg_color = "#FF333A" # Merah
                        else: bg_color = "#777777" # Abu
                        
                        html_content += f"""
                        <div class="wl-card" style="background-color: {bg_color};">
                            <div class="wl-date">{date_str}</div>
                            <div class="wl-price">{format_rupiah(price)}</div>
                            <div class="wl-pct">{pct:+.2f}%</div>
                        </div>
                        """
                    
                    html_content += '</div>'
                    st.markdown(html_content, unsafe_allow_html=True)
                    st.divider()
                    
            except Exception as e:
                st.error(f"Gagal memuat data untuk {ticker}")

# ==========================
# TAB 5: SIMULATOR
# ==========================
with tabs[4]:
    st.header("🎯 Paper Trading")
    c_s1, c_s2 = st.columns([1, 2])
    with c_s1:
        st.metric("Saldo", format_rupiah(st.session_state.sim_balance))
        with st.form("sim_form"):
            s_tick = st.selectbox("Saham", LIST_SAHAM_IHSG)
            s_act = st.radio("Aksi", ["BUY", "SELL"], horizontal=True)
            s_qty = st.number_input("Lot", 1)
            if st.form_submit_button("Submit"):
                curr_hist = yf.Ticker(s_tick).history('1d')
                if not curr_hist.empty:
                    curr = curr_hist['Close'].iloc[-1]
                    val = curr * s_qty * 100
                    if s_act == "BUY":
                        if st.session_state.sim_balance >= val:
                            st.session_state.sim_balance -= val
                            st.session_state.sim_portfolio[s_tick] = st.session_state.sim_portfolio.get(s_tick, 0) + s_qty
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": s_tick, "Action": "BUY", "Price": curr, "Qty": s_qty})
                            st.success("BUY Sukses")
                            st.rerun()
                        else: st.error("Saldo Kurang")
                    else:
                        if st.session_state.sim_portfolio.get(s_tick, 0) >= s_qty:
                            st.session_state.sim_balance += val
                            st.session_state.sim_portfolio[s_tick] -= s_qty
                            if st.session_state.sim_portfolio[s_tick] == 0: del st.session_state.sim_portfolio[s_tick]
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": s_tick, "Action": "SELL", "Price": curr, "Qty": s_qty})
                            st.success("SELL Sukses")
                            st.rerun()
                        else: st.error("Barang Kurang")
                else: st.error("Gagal ambil harga pasar")

    with c_s2:
        if st.session_state.sim_portfolio:
            p_data = []
            cur_prices = get_data_bulk(list(st.session_state.sim_portfolio.keys()), period="1d")
            total_assets = 0
            for t, q in st.session_state.sim_portfolio.items():
                try:
                    if len(st.session_state.sim_portfolio) == 1: cp = cur_prices['Close'].iloc[-1]
                    else: cp = cur_prices[t]['Close'].iloc[-1]
                    
                    v = cp * q * 100
                    total_assets += v
                    p_data.append({"Ticker": t, "Lot": q, "Val": format_rupiah(v)})
                except: pass
            st.dataframe(p_data, use_container_width=True)
            st.metric("Total Aset", format_rupiah(total_assets))
        
        if st.session_state.sim_history:
            st.write("Riwayat:")
            st.dataframe(pd.DataFrame(st.session_state.sim_history), use_container_width=True)

st.caption(f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
