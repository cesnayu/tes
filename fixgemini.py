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
    .stPlotlyChart {height: 280px;} /* Tinggi chart grid diperbesar sedikit */
    
    /* CSS untuk Win/Loss Box */
    .wl-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr); /* 5 kolom per baris grid kecil */
        gap: 2px;
        width: 100%;
    }
    .wl-box {
        width: 100%;
        padding-top: 80%; /* Aspect ratio kotak */
        position: relative;
        border-radius: 2px;
        cursor: help;
    }
    .wl-content {
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px; /* Ukuran font angka di dalam kotak */
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
    }
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
# Simulator State
if 'sim_balance' not in st.session_state: st.session_state.sim_balance = 100000000 # 100 Juta
if 'sim_portfolio' not in st.session_state: st.session_state.sim_portfolio = {} # Dictionary {Ticker: Qty}
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
            data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, threads=True)
        else:
            data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, threads=True)
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

# --- 5. FUNGSI VISUALISASI ---

def create_compact_chart(df, ticker, ma20=True, chart_type="Candle"):
    fig = go.Figure()
    
    # Switch antara Candle dan Line
    if chart_type == "Line":
        color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', 
            line=dict(color=color_line, width=2), name="Price"
        ))
        # Area fill untuk Line chart agar lebih cantik
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], fill='tozeroy', mode='none',
            fillcolor=f"rgba{tuple(int(color_line.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}",
            showlegend=False
        ))
    else:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
            name="Price", showlegend=False
        ))

    if ma20 and len(df) > 20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), showlegend=False, name="MA20"))
    
    last_price = df['Close'].iloc[-1]
    color_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    
    fig.update_layout(
        title=dict(text=f"{ticker} ({format_rupiah(last_price)})", font=dict(size=14, color=color_title), x=0.5, y=0.95),
        margin=dict(l=5, r=5, t=30, b=5), height=250, xaxis_rangeslider_visible=False,
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=dict(showgrid=False, showticklabels=False)
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

# --- 6. UI DASHBOARD UTAMA ---
st.title("📈 Observation Pro")

tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Market Recap", "🎲 Win/Loss", "🎯 Simulator"])

# ==========================
# TAB 1: LIST (GRID 4 KOLOM)
# ==========================
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5])
    with c1: tf_grid = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=2)
    with c2: min_p = st.number_input("Min Price", 0, step=50)
    with c3: max_p = st.number_input("Max Price", 100000, step=50)
    with c4: chart_type_sel = st.radio("Grafik", ["Candle", "Line"], horizontal=True)
    with c5: show_ma = st.checkbox("Show MA20", True)

    ITEMS_PER_PAGE = 40 # Disesuaikan agar pas 4 kolom x 10 baris
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
        
        # Grid 4 Kolom
        cols = st.columns(4)
        idx = 0
        for t in batch:
            try:
                # MultiIndex handling
                if len(batch) > 1:
                    if t in df_batch.columns.levels[0]:
                        dft = df_batch[t].dropna()
                    else: continue
                else: dft = df_batch.dropna()

                if dft.empty or not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                
                with cols[idx % 4]: 
                    st.plotly_chart(
                        create_compact_chart(dft, t, ma20=show_ma, chart_type=chart_type_sel), 
                        use_container_width=True
                    )
                idx += 1
            except Exception as e: continue

# ==========================
# TAB 2: COMPARE
# ==========================
with tabs[1]:
    sel_stocks = st.multiselect("Pilih Saham:", LIST_SAHAM_IHSG, ["BBCA.JK", "BBRI.JK"])
    c_style = st.radio("Style:", ["Candle", "Line"], horizontal=True)
    period_c = st.select_slider("Range:", ["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    
    if sel_stocks:
        data_c = get_data_bulk(sel_stocks, period=period_c)
        for t in sel_stocks:
            try:
                dfc = data_c[t].dropna() if len(sel_stocks) > 1 else data_c.dropna()
                if dfc.empty: continue
                pbv, per = get_fundamental_info(t)
                st.plotly_chart(create_advanced_chart(dfc, t, style=c_style.lower(), pbv=pbv, per=per), use_container_width=True)
                st.divider()
            except: pass

# ==========================
# TAB 3: MARKET RECAP (Ex Weekly)
# ==========================
with tabs[2]:
    st.header("📅 Market Recap & Performance")
    
    # Fitur Search: Default Kosong = Semua
    w_search = st.multiselect("Cari Saham (Bisa pilih banyak, kosongkan untuk semua):", LIST_SAHAM_IHSG)
    
    # Logic: Jika search ada isi, gunakan search. Jika kosong, gunakan semua.
    target_weekly = w_search if w_search else LIST_SAHAM_IHSG
    
    # Optimasi: Jika load semua, batasi 100 biar gak crash memory
    is_truncated = False
    if len(target_weekly) > 100:
        target_weekly = target_weekly[:100]
        is_truncated = True

    if st.button("Refresh Data") or target_weekly:
        if is_truncated: st.warning("⚠️ Menampilkan 100 saham pertama untuk kinerja optimal.")
        
        with st.spinner("Calculating Data (1 Year History)..."):
            # Fetch 1 Year data untuk hitung 1M, 6M, 1Y
            w_data = get_data_bulk(target_weekly, period="1y")
            
            w_rows = []
            days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            
            today = datetime.now()
            start_week = today - timedelta(days=today.weekday())
            
            for t in target_weekly:
                try:
                    dfw = w_data[t].dropna() if len(target_weekly) > 1 else w_data.dropna()
                    if dfw.empty: continue
                    
                    # Data Points
                    curr = dfw['Close'].iloc[-1]
                    vol = dfw['Volume'].iloc[-1]
                    
                    # Helper Percent Change
                    def get_pct(days_back):
                        if len(dfw) < days_back: return 0.0
                        prev = dfw['Close'].iloc[-days_back]
                        return ((curr - prev) / prev) * 100

                    row = {
                        "Ticker": t, 
                        "Price": format_rupiah(curr),
                        "Volume": format_volume(vol)
                    }
                    
                    # Weekly Breakdown
                    acc = 0
                    for i, d_name in enumerate(days_en):
                        t_date = (start_week + timedelta(days=i)).date()
                        val = 0.0
                        # Check date exists in index
                        matches = dfw[dfw.index.date == t_date]
                        if not matches.empty:
                            val = matches['Close'].pct_change().iloc[0] * 100 # Approx return that day
                            # Correct logic: Need daily return relative to prev day close
                            # Simplified: matches['pct_change'] if calculated before
                        
                        # Re-calculate exact return for that specific date row
                        if t_date in dfw.index.date:
                            loc = dfw.index.get_loc(pd.Timestamp(t_date))
                            if loc > 0:
                                p_today = dfw['Close'].iloc[loc]
                                p_prev = dfw['Close'].iloc[loc-1]
                                val = ((p_today - p_prev)/p_prev) * 100

                        row[d_name] = val
                        acc += val
                    
                    row["Weekly (%)"] = acc
                    row["1 Month (%)"] = get_pct(20)
                    row["6 Month (%)"] = get_pct(120)
                    row["1 Year (%)"] = get_pct(240)
                    
                    w_rows.append(row)
                except Exception as e: continue
            
            if w_rows:
                df_res = pd.DataFrame(w_rows)
                
                # Format Kolom Warna
                numeric_cols = days_en + ["Weekly (%)", "1 Month (%)", "6 Month (%)", "1 Year (%)"]
                
                def style_color(v):
                    if isinstance(v, (int, float)):
                        return f'color: {"#00C805" if v > 0 else "#FF333A" if v < 0 else ""}'
                    return ""
                
                st.dataframe(
                    df_res.style.applymap(style_color, subset=numeric_cols).format("{:.2f}", subset=numeric_cols),
                    use_container_width=True, hide_index=True
                )
            else:
                st.info("Data tidak tersedia.")

# ==========================
# TAB 4: WIN/LOSS (CENTERED)
# ==========================
with tabs[3]:
    st.header("🎲 Win/Loss Heatmap (Last 20 Days)")
    
    # 1. Pilih Saham
    wl_sel = st.multiselect("Pilih Saham (Max 4 per baris akan disusun tengah):", LIST_SAHAM_IHSG, default=["BBCA.JK", "GOTO.JK"])
    
    if wl_sel:
        # Ambil Data
        wl_data = get_data_bulk(wl_sel, period="3mo")
        
        # Pecah list saham menjadi chunks of 4 (Baris)
        chunk_size = 4
        chunks = [wl_sel[i:i + chunk_size] for i in range(0, len(wl_sel), chunk_size)]
        
        for chunk in chunks:
            # Logic Centering:
            # Gunakan st.columns dengan padding kiri kanan dinamis
            # Jika 1 saham: padding besar, konten, padding besar
            # Jika 4 saham: full width
            
            count = len(chunk)
            
            # Setup Kolom Layout (Tengah)
            if count == 1:
                cols = st.columns([1.5, 1, 1.5])
                active_col_indices = [1]
            elif count == 2:
                cols = st.columns([1, 1, 1, 1]) # Padding | Item | Item | Padding -> Salah
                # Lebih baik: Padding | Item | Item | Padding
                cols = st.columns([1, 1.5, 1.5, 1])
                active_col_indices = [1, 2]
            elif count == 3:
                cols = st.columns([0.5, 1, 1, 1, 0.5])
                active_col_indices = [1, 2, 3]
            else: # 4 items
                cols = st.columns(4)
                active_col_indices = [0, 1, 2, 3]

            # Loop Render per Saham di Row ini
            for i, ticker in enumerate(chunk):
                with cols[active_col_indices[i]]:
                    try:
                        # Extract Data
                        dfw = wl_data[ticker].dropna() if len(wl_sel) > 1 else wl_data.dropna()
                        if dfw.empty: continue
                        
                        dfw['Pct'] = dfw['Close'].pct_change() * 100
                        # Ambil 20 hari terakhir
                        last_df = dfw.tail(20)
                        
                        # Siapkan List Data
                        vals = last_df['Pct'].tolist()
                        dates = last_df.index.strftime('%d %b').tolist()
                        
                        # Padding jika data < 20
                        if len(vals) < 20:
                            vals = [0] * (20 - len(vals)) + vals
                            dates = ["-"] * (20 - len(dates)) + dates
                        
                        st.markdown(f"<div style='text-align:center; font-weight:bold; margin-bottom:5px;'>{ticker}</div>", unsafe_allow_html=True)
                        
                        # Generate HTML Grid
                        html = '<div class="wl-grid">'
                        for val, date_str in zip(vals, dates):
                            color = "#00C805" if val > 0 else "#FF333A" if val < 0 else "#DDDDDD"
                            # Tooltip: Date + Value
                            tooltip = f"{date_str}: {val:.2f}%"
                            # Text inside box: Round number
                            text_val = f"{val:.1f}" if abs(val) >= 1 else "" 
                            
                            html += f'''
                            <div class="wl-box" title="{tooltip}">
                                <div class="wl-content" style="background-color: {color};">
                                    {text_val}
                                </div>
                            </div>
                            '''
                        html += '</div>'
                        st.markdown(html, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Err {ticker}")
            
            st.write("") # Spacer antar row
            st.write("") 

# ==========================
# TAB 5: SIMULATOR
# ==========================
with tabs[4]:
    st.header("🎯 Simple Paper Trading")
    
    col_sim1, col_sim2 = st.columns([1, 2])
    
    with col_sim1:
        st.metric("Sisa Saldo (IDR)", format_rupiah(st.session_state.sim_balance))
        
        with st.form("order_form"):
            st.subheader("Buat Transaksi")
            sim_ticker = st.selectbox("Saham", LIST_SAHAM_IHSG)
            sim_action = st.radio("Aksi", ["BUY", "SELL"], horizontal=True)
            sim_qty = st.number_input("Jumlah Lot (1 Lot = 100 Lembar)", min_value=1, value=1)
            
            if st.form_submit_button("Submit Order"):
                stock_info = yf.Ticker(sim_ticker).history(period="1d")
                if not stock_info.empty:
                    sim_price = stock_info['Close'].iloc[-1]
                    total_val = sim_price * sim_qty * 100
                    
                    if sim_action == "BUY":
                        if st.session_state.sim_balance >= total_val:
                            st.session_state.sim_balance -= total_val
                            st.session_state.sim_portfolio[sim_ticker] = st.session_state.sim_portfolio.get(sim_ticker, 0) + sim_qty
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": sim_ticker, "Action": "BUY", "Price": sim_price, "Qty": sim_qty})
                            st.success(f"BUY {sim_ticker} Sukses!")
                            st.rerun()
                        else: st.error("Saldo tidak cukup!")
                    elif sim_action == "SELL":
                        curr_qty = st.session_state.sim_portfolio.get(sim_ticker, 0)
                        if curr_qty >= sim_qty:
                            st.session_state.sim_balance += total_val
                            st.session_state.sim_portfolio[sim_ticker] -= sim_qty
                            if st.session_state.sim_portfolio[sim_ticker] == 0: del st.session_state.sim_portfolio[sim_ticker]
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": sim_ticker, "Action": "SELL", "Price": sim_price, "Qty": sim_qty})
                            st.success(f"SELL {sim_ticker} Sukses!")
                            st.rerun()
                        else: st.error("Barang tidak cukup!")
                else: st.error("Gagal mengambil harga.")

    with col_sim2:
        st.subheader("Portofolio Saat Ini")
        if st.session_state.sim_portfolio:
            port_rows = []
            port_tickers = list(st.session_state.sim_portfolio.keys())
            curr_data = get_data_bulk(port_tickers, period="1d")
            
            total_asset = 0
            for t, qty in st.session_state.sim_portfolio.items():
                try:
                    dft = curr_data[t] if len(port_tickers) > 1 else curr_data
                    curr_p = dft['Close'].iloc[-1]
                    val = curr_p * qty * 100
                    total_asset += val
                    port_rows.append({"Ticker": t, "Lot": qty, "Last Price": format_rupiah(curr_p), "Value (IDR)": format_rupiah(val)})
                except: pass
            
            st.dataframe(pd.DataFrame(port_rows), use_container_width=True)
            st.metric("Total Aset Saham", format_rupiah(total_asset))
            st.metric("Total Equity", format_rupiah(st.session_state.sim_balance + total_asset))
        else: st.info("Portofolio Kosong.")
        
        if st.session_state.sim_history:
            st.divider()
            st.subheader("Riwayat Transaksi")
            st.dataframe(pd.DataFrame(st.session_state.sim_history), use_container_width=True)

st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
