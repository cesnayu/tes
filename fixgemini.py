import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# CSS Kustom: Tampilan Padat & Kotak Win/Loss
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    div[data-testid="stMetricValue"] {font-size: 1rem;}
    .stPlotlyChart {height: 250px;}
    
    /* CSS untuk Win/Loss Box */
    .wl-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 4px;
        width: 100%;
        max-width: 150px;
    }
    .wl-box {
        width: 100%;
        padding-top: 100%; /* Aspect Ratio 1:1 */
        position: relative;
        border-radius: 2px;
    }
    .wl-content {
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
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

# --- 5. FUNGSI VISUALISASI ---

def create_compact_candle(df, ticker, ma20=True, ma200=False):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price", showlegend=False))
    if ma20 and len(df) > 20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1), showlegend=False))
    if ma200 and len(df) > 200:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(200).mean(), line=dict(color='blue', width=1), showlegend=False))
    
    color_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    fig.update_layout(
        title=dict(text=f"{ticker} ({format_rupiah(df['Close'].iloc[-1])})", font=dict(size=12, color=color_title), x=0.5, y=0.95),
        margin=dict(l=5, r=5, t=30, b=5), height=200, xaxis_rangeslider_visible=False,
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

tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Weekly", "🚀 Performa", "🎲 Win/Loss", "🎯 Simulator"])

# ==========================
# TAB 1: LIST (GRID)
# ==========================
with tabs[0]:
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1: tf_grid = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=2)
    with c2: min_p = st.number_input("Min Price", 0, step=50)
    with c3: max_p = st.number_input("Max Price", 100000, step=50)
    with c4: show_ma = st.checkbox("Show MA20", True)

    ITEMS_PER_PAGE = 50
    total_pages = math.ceil(len(LIST_SAHAM_IHSG) / ITEMS_PER_PAGE)
    
    cp1, cp2, cp3 = st.columns([1, 8, 1])
    with cp1: 
        if st.button("⬅️ Prev") and st.session_state.page > 1: st.session_state.page -= 1; st.rerun()
    with cp2: st.markdown(f"<div style='text-align: center'>Page {st.session_state.page}/{total_pages}</div>", unsafe_allow_html=True)
    with cp3: 
        if st.button("Next ➡️") and st.session_state.page < total_pages: st.session_state.page += 1; st.rerun()

    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    batch = LIST_SAHAM_IHSG[start_idx:start_idx + ITEMS_PER_PAGE]

    if batch:
        with st.spinner("Loading Grid..."):
            df_batch = get_data_bulk(batch, period=tf_grid)
        cols = st.columns(5)
        idx = 0
        for t in batch:
            try:
                dft = df_batch[t].dropna() if len(batch) > 1 else df_batch.dropna()
                if dft.empty or not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                with cols[idx % 5]: st.plotly_chart(create_compact_candle(dft, t, ma20=show_ma), use_container_width=True)
                idx += 1
            except: continue

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
# TAB 3: WEEKLY RECAP
# ==========================
with tabs[2]:
    st.header("📅 Weekly Recap")
    
    # Logic: Jika search kosong -> Pakai SEMUA list. Jika ada isi -> Pakai yang di-search.
    w_search = st.multiselect("Filter Saham (Kosongkan untuk melihat semua):", LIST_SAHAM_IHSG)
    target_weekly = w_search if w_search else LIST_SAHAM_IHSG
    
    # Batasi load jika terlalu banyak (opsional, tapi disarankan)
    if len(target_weekly) > 100:
        st.warning("Menampilkan 100 saham pertama untuk kinerja optimal.")
        target_weekly = target_weekly[:100]

    if target_weekly:
        with st.spinner("Calculating Weekly Data..."):
            # Fetch data 10 hari ke belakang untuk aman
            today = datetime.now()
            start_week = today - timedelta(days=today.weekday())
            fetch_start = (start_week - timedelta(days=7)).strftime("%Y-%m-%d")
            
            w_data = get_data_bulk(target_weekly, start=fetch_start, end=(today + timedelta(days=1)).strftime("%Y-%m-%d"))
            
            w_rows = []
            days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            
            for t in target_weekly:
                try:
                    dfw = w_data[t].dropna() if len(target_weekly) > 1 else w_data.dropna()
                    if dfw.empty: continue
                    
                    dfw['Ret'] = dfw['Close'].pct_change() * 100
                    last_p = dfw['Close'].iloc[-1]
                    
                    row = {"Ticker": t, "Price": format_rupiah(last_p)}
                    
                    acc = 0
                    for i, d_name in enumerate(days_en):
                        t_date = (start_week + timedelta(days=i)).date()
                        # Match date
                        val = 0.0
                        matches = dfw[dfw.index.date == t_date]
                        if not matches.empty:
                            val = matches['Ret'].iloc[0]
                        row[d_name] = val
                        acc += val
                    
                    row["Total (%)"] = acc
                    w_rows.append(row)
                except: continue
            
            if w_rows:
                df_res = pd.DataFrame(w_rows)
                # Styling
                def style_color(v):
                    if isinstance(v, (int, float)):
                        return f'color: {"#00C805" if v > 0 else "#FF333A" if v < 0 else ""}'
                    return ""
                
                st.dataframe(
                    df_res.style.applymap(style_color, subset=days_en + ["Total (%)"]).format("{:.2f}", subset=days_en + ["Total (%)"]),
                    use_container_width=True, hide_index=True
                )

# ==========================
# TAB 4: PERFORMA
# ==========================
with tabs[3]:
    st.header("🚀 Performance Metrics")
    p_sel = st.multiselect("Pilih Saham:", LIST_SAHAM_IHSG, default=LIST_SAHAM_IHSG[:5])
    
    if p_sel:
        with st.spinner("Analyzing Performance..."):
            # Ambil data 1 tahun + buffer
            p_data = get_data_bulk(p_sel, period="1y")
            p_rows = []
            
            for t in p_sel:
                try:
                    dfp = p_data[t].dropna() if len(p_sel) > 1 else p_data.dropna()
                    if dfp.empty: continue
                    
                    curr = dfp['Close'].iloc[-1]
                    
                    def get_change(days):
                        if len(dfp) < days: return 0.0
                        prev = dfp['Close'].iloc[-days]
                        return ((curr - prev) / prev) * 100

                    # YTD Calculation
                    curr_year = datetime.now().year
                    df_ytd = dfp[dfp.index.year == curr_year]
                    ytd_val = ((curr - df_ytd['Open'].iloc[0]) / df_ytd['Open'].iloc[0] * 100) if not df_ytd.empty else 0.0

                    p_rows.append({
                        "Ticker": t,
                        "Price": format_rupiah(curr),
                        "1 Week (%)": get_change(5),
                        "1 Month (%)": get_change(20),
                        "3 Month (%)": get_change(60),
                        "6 Month (%)": get_change(120),
                        "YTD (%)": ytd_val
                    })
                except: continue
            
            if p_rows:
                df_perf = pd.DataFrame(p_rows)
                def color_perf(v):
                    if isinstance(v, (int, float)):
                        return f'color: {"#00C805" if v > 0 else "#FF333A" if v < 0 else ""}'
                    return ""
                
                st.dataframe(
                    df_perf.style.applymap(color_perf, subset=["1 Week (%)", "1 Month (%)", "3 Month (%)", "6 Month (%)", "YTD (%)"])
                                 .format("{:.2f}", subset=["1 Week (%)", "1 Month (%)", "3 Month (%)", "6 Month (%)", "YTD (%)"]),
                    use_container_width=True, hide_index=True
                )

# ==========================
# TAB 5: WIN/LOSS (20 DAYS)
# ==========================
with tabs[4]:
    st.header("🎲 Win/Loss Heatmap (Last 20 Days)")
    wl_sel = st.multiselect("Cari Saham:", LIST_SAHAM_IHSG, default=["BBCA.JK", "GOTO.JK"])
    
    if wl_sel:
        # Ambil data 2 bulan untuk memastikan dapat 20 hari trading
        wl_data = get_data_bulk(wl_sel, period="3mo")
        
        for t in wl_sel:
            try:
                dfw = wl_data[t].dropna() if len(wl_sel) > 1 else wl_data.dropna()
                if dfw.empty: continue
                
                # Hitung perubahan dan ambil 20 terakhir
                dfw['Change'] = dfw['Close'].pct_change()
                last_20 = dfw['Change'].tail(20).tolist()
                
                # Jika data kurang dari 20, pad dengan 0
                if len(last_20) < 20:
                    last_20 = [0] * (20 - len(last_20)) + last_20
                
                # Render HTML Grid
                st.subheader(f"{t}")
                
                html_grid = '<div class="wl-grid">'
                for val in last_20:
                    color = "#00C805" if val > 0 else "#FF333A" if val < 0 else "#DDDDDD"
                    # Tooltip sederhana dengan title
                    html_grid += f'<div class="wl-box"><div class="wl-content" style="background-color: {color};" title="{val*100:.2f}%"></div></div>'
                html_grid += '</div>'
                
                st.markdown(html_grid, unsafe_allow_html=True)
                st.caption("Kotak berurutan dari kiri ke kanan, baris atas ke bawah (20 Hari Terakhir). Hijau = Naik, Merah = Turun.")
                st.divider()

            except Exception as e: st.error(f"Error {t}")

# ==========================
# TAB 6: SIMULATOR
# ==========================
with tabs[5]:
    st.header("🎯 Simple Paper Trading")
    
    # --- Sidebar Info ---
    col_sim1, col_sim2 = st.columns([1, 2])
    
    with col_sim1:
        st.metric("Sisa Saldo (IDR)", format_rupiah(st.session_state.sim_balance))
        
        with st.form("order_form"):
            st.subheader("Buat Transaksi")
            sim_ticker = st.selectbox("Saham", LIST_SAHAM_IHSG)
            sim_action = st.radio("Aksi", ["BUY", "SELL"], horizontal=True)
            sim_qty = st.number_input("Jumlah Lot (1 Lot = 100 Lembar)", min_value=1, value=1)
            
            # Get real price for validation
            sim_price = 0
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
                        else:
                            st.error("Saldo tidak cukup!")
                    elif sim_action == "SELL":
                        curr_qty = st.session_state.sim_portfolio.get(sim_ticker, 0)
                        if curr_qty >= sim_qty:
                            st.session_state.sim_balance += total_val
                            st.session_state.sim_portfolio[sim_ticker] -= sim_qty
                            if st.session_state.sim_portfolio[sim_ticker] == 0:
                                del st.session_state.sim_portfolio[sim_ticker]
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": sim_ticker, "Action": "SELL", "Price": sim_price, "Qty": sim_qty})
                            st.success(f"SELL {sim_ticker} Sukses!")
                            st.rerun()
                        else:
                            st.error("Barang tidak cukup!")
                else:
                    st.error("Gagal mengambil harga pasar.")

    with col_sim2:
        st.subheader("Portofolio Saat Ini")
        if st.session_state.sim_portfolio:
            port_rows = []
            # Fetch current prices for portfolio
            port_tickers = list(st.session_state.sim_portfolio.keys())
            curr_data = get_data_bulk(port_tickers, period="1d")
            
            total_asset = 0
            for t, qty in st.session_state.sim_portfolio.items():
                try:
                    # Handle price
                    dft = curr_data[t] if len(port_tickers) > 1 else curr_data
                    curr_p = dft['Close'].iloc[-1]
                    val = curr_p * qty * 100
                    total_asset += val
                    port_rows.append({"Ticker": t, "Lot": qty, "Last Price": format_rupiah(curr_p), "Value (IDR)": format_rupiah(val)})
                except: pass
            
            st.dataframe(pd.DataFrame(port_rows), use_container_width=True)
            st.metric("Total Aset Saham", format_rupiah(total_asset))
            st.metric("Total Equity (Cash + Saham)", format_rupiah(st.session_state.sim_balance + total_asset))
        else:
            st.info("Portofolio Kosong.")
        
        st.divider()
        st.subheader("Riwayat Transaksi")
        if st.session_state.sim_history:
            st.dataframe(pd.DataFrame(st.session_state.sim_history), use_container_width=True)

st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
