import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN (WAJIB PALING ATAS) ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# --- 2. CSS SEDERHANA (SAFE MODE) ---
st.markdown("""
<style>
    /* Styling Dasar untuk Kotak Win/Loss */
    .wl-box {
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        font-family: sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .wl-date { font-size: 11px; opacity: 0.9; margin-bottom: 4px; }
    .wl-price { font-size: 14px; font-weight: bold; margin-bottom: 2px; }
    .wl-pct { font-size: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LIST SAHAM ---
LIST_SAHAM_IHSG = [
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "GOTO.JK", "KLBF.JK",
    "AMRT.JK", "MDKA.JK", "ADRO.JK", "UNTR.JK", "CPIN.JK", "INCO.JK", "PGAS.JK", "ITMG.JK", "PTBA.JK", "ANTM.JK",
    "BRPT.JK", "INDF.JK", "INKP.JK", "TPIA.JK", "EXCL.JK", "ISAT.JK", "TOWR.JK", "TBIG.JK", "MTEL.JK", "BUKA.JK",
    "ARTO.JK", "EMTK.JK", "SCMA.JK", "MNCN.JK", "MEDIA.JK", "JPFA.JK", "SMGR.JK", "INTP.JK", "JSMR.JK", "WIKA.JK",
    "PTPP.JK", "ADHI.JK", "WSKT.JK", "CTRA.JK", "BSDE.JK", "PWON.JK", "SMRA.JK", "ASRI.JK", "LPPF.JK", "RALS.JK",
    "ACES.JK", "MAPI.JK", "MAPA.JK", "ERAA.JK", "SIDO.JK", "KAEF.JK", "HEAL.JK", "MIKA.JK", "SILO.JK", "SAME.JK"
]

# --- 4. STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'sim_balance' not in st.session_state: st.session_state.sim_balance = 100000000
if 'sim_portfolio' not in st.session_state: st.session_state.sim_portfolio = {}
if 'sim_history' not in st.session_state: st.session_state.sim_history = []

# --- 5. FUNGSI CACHE & DATA ---
@st.cache_data(ttl=3600)
def get_fundamental(ticker):
    try:
        i = yf.Ticker(ticker).info
        return i.get('priceToBook', 0), i.get('trailingPE', 0)
    except: return 0, 0

@st.cache_data(ttl=600)
def get_data(tickers, period="3mo", interval="1d"):
    if not tickers: return pd.DataFrame()
    try:
        # auto_adjust=True memperbaiki masalah data OHLC
        d = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=True)
        return d
    except: return pd.DataFrame()

def fmt_idr(val):
    return f"{val:,.0f}" if not pd.isna(val) else "0"

# --- 6. VISUALISASI ---
def chart_grid(df, ticker, ma20=True, chart_type="Candle"):
    fig = go.Figure()
    # Line
    if chart_type == "Line":
        clr = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=clr, width=2)))
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill='tozeroy', fillcolor=f"rgba{tuple(int(clr.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.1,)}", mode='none'))
        xaxis_cfg = dict(showgrid=False, showticklabels=False)
    # Candle
    else:
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
        xaxis_cfg = dict(showgrid=False, showticklabels=False, rangeslider=dict(visible=False))

    if ma20 and len(df)>20:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1)))

    clr_title = "green" if df['Close'].iloc[-1] >= df['Open'].iloc[-1] else "red"
    fig.update_layout(
        title=dict(text=f"{ticker} ({fmt_idr(df['Close'].iloc[-1])})", font=dict(size=14, color=clr_title), x=0.5, y=0.9),
        margin=dict(l=5, r=5, t=30, b=5), height=250, showlegend=False, 
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', tickfont=dict(size=8)),
        xaxis=xaxis_cfg
    )
    return fig

def chart_detail(df, ticker, pbv=0, per=0):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']), row=1, col=1)
    if len(df)>20: fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='orange', width=1)), row=1, col=1)
    
    clrs = ['red' if r['Open'] > r['Close'] else 'green' for i, r in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=clrs), row=2, col=1)
    
    fig.update_layout(title=f"{ticker} | PBV: {pbv:.2f} | PER: {per:.2f}", height=500, xaxis_rangeslider_visible=False, showlegend=False)
    return fig

# --- 7. MAIN UI ---
st.title("Observation Pro")

# Definisikan Tab
tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Recap", "🎲 Win/Loss", "🎯 Simulator"])

# === TAB 1: LIST ===
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    with c1: tf = st.selectbox("Waktu", ["5d", "1mo", "3mo", "6mo", "1y"], 2)
    with c2: min_p = st.number_input("Min Rp", 0, step=50)
    with c3: max_p = st.number_input("Max Rp", 100000, value=100000, step=50)
    with c4: c_type = st.radio("Grafik", ["Candle", "Line"], horizontal=True)
    with c5: show_ma = st.checkbox("MA20", True)

    per_page = 20
    total_pages = math.ceil(len(LIST_SAHAM_IHSG)/per_page)
    
    # Pagination
    b1, b2, b3 = st.columns([1, 8, 1])
    if b1.button("⬅️") and st.session_state.page > 1: st.session_state.page -= 1; st.rerun()
    b2.markdown(f"<div style='text-align:center; margin-top:5px'><b>Page {st.session_state.page}/{total_pages}</b></div>", unsafe_allow_html=True)
    if b3.button("➡️") and st.session_state.page < total_pages: st.session_state.page += 1; st.rerun()

    # Data
    start = (st.session_state.page-1)*per_page
    batch = LIST_SAHAM_IHSG[start:start+per_page]
    
    if batch:
        with st.spinner("Loading..."):
            df_b = get_data(batch, period=tf)
        
        cols = st.columns(4) # Grid 4 Kolom
        idx = 0
        for t in batch:
            try:
                # Handle Data Structure
                dft = df_b[t] if len(batch) > 1 else df_b
                if t not in df_b.columns.levels[0] and len(batch) > 1: continue # Skip if no data
                
                dft = dft.dropna()
                if dft.empty: continue
                if not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                
                with cols[idx % 4]:
                    st.plotly_chart(chart_grid(dft, t, show_ma, c_type), use_container_width=True)
                idx += 1
            except: continue

# === TAB 2: COMPARE ===
with tabs[1]:
    sel = st.multiselect("Pilih Saham", LIST_SAHAM_IHSG, ["BBCA.JK", "BBRI.JK"])
    if sel:
        d_c = get_data(sel, period="6mo")
        for t in sel:
            try:
                dt = d_c[t] if len(sel)>1 else d_c
                dt = dt.dropna()
                if dt.empty: continue
                pbv, per = get_fundamental(t)
                st.plotly_chart(chart_detail(dt, t, pbv, per), use_container_width=True)
            except: pass

# === TAB 3: RECAP ===
with tabs[2]:
    search = st.multiselect("Cari Saham (Kosong = Semua)", LIST_SAHAM_IHSG)
    target = search if search else LIST_SAHAM_IHSG[:50] # Limit 50 default biar ringan
    
    if st.button("Load Data"):
        d_r = get_data(target, period="2y")
        rows = []
        now = datetime.now().date()
        start_w = now - timedelta(days=now.weekday())
        
        for t in target:
            try:
                dt = d_r[t] if len(target)>1 else d_r
                dt = dt.dropna()
                if dt.empty: continue
                
                curr = dt['Close'].iloc[-1]
                
                # Safe Return Calc
                def get_ret(days):
                    if len(dt) < 5: return 0.0
                    idx = -1 * min(len(dt), int(days*0.7)) # Approx trading days
                    return ((curr - dt['Close'].iloc[idx])/dt['Close'].iloc[idx])*100
                
                row = {"Ticker": t, "Harga": fmt_idr(curr), "Vol": fmt_idr(dt['Volume'].iloc[-1])}
                
                # Weekly Days
                acc = 0
                for i, d in enumerate(["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]):
                    t_date = pd.Timestamp(start_w + timedelta(days=i))
                    val = 0.0
                    if t_date in dt.index:
                        loc = dt.index.get_loc(t_date)
                        if loc > 0: val = ((dt['Close'].iloc[loc] - dt['Close'].iloc[loc-1])/dt['Close'].iloc[loc-1])*100
                    row[d] = val
                    acc += val
                
                row["Weekly%"] = acc
                row["1M%"] = get_ret(30)
                row["6M%"] = get_ret(180)
                row["1Y%"] = get_ret(365)
                rows.append(row)
            except: continue
            
        if rows:
            sdf = pd.DataFrame(rows)
            def color_val(v): 
                if isinstance(v, (int, float)): return f'color: {"green" if v>0 else "red" if v<0 else ""}'
                return ""
            st.dataframe(sdf.style.applymap(color_val).format("{:.2f}", subset=["Weekly%", "1M%", "6M%", "1Y%", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"]), height=500, use_container_width=True)

# === TAB 4: WIN/LOSS (FIXED) ===
with tabs[3]:
    st.subheader("🎲 Win/Loss Heatmap (20 Hari)")
    
    # INPUT MANUAL TEXT
    txt = st.text_input("Ketik Kode Saham (pisahkan koma):", value="BBCA.JK, GOTO.JK, BMRI.JK")
    
    if txt:
        ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
        if ticks:
            with st.spinner("Fetching..."):
                d_wl = get_data(ticks, period="3mo")
            
            for t in ticks:
                try:
                    dt = d_wl[t] if len(ticks)>1 else d_wl
                    dt = dt.dropna()
                    if dt.empty: continue
                    
                    dt['Pct'] = dt['Close'].pct_change() * 100
                    last20 = dt.tail(20).sort_index() # Urutkan dari terlama ke terbaru
                    
                    st.markdown(f"**{t}**")
                    
                    # LOGIKA GRID MANUAL (Anti Error Div Class)
                    # Kita bagi data menjadi potongan 5 (chunk)
                    chunks = [last20.iloc[i:i+5] for i in range(0, len(last20), 5)]
                    
                    for chunk in chunks:
                        cols = st.columns(5) # Buat 5 kolom
                        for i, (date, row) in enumerate(chunk.iterrows()):
                            pct = row['Pct']
                            bg = "#00C805" if pct > 0 else "#FF333A" if pct < 0 else "#555"
                            
                            with cols[i]:
                                # HTML Sederhana
                                st.markdown(f"""
                                <div class="wl-box" style="background-color: {bg};">
                                    <div class="wl-date">{date.strftime('%d/%m')}</div>
                                    <div class="wl-price">{fmt_idr(row['Close'])}</div>
                                    <div class="wl-pct">{pct:+.2f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                    st.divider()
                except: st.error(f"Gagal memuat {t}")

# === TAB 5: SIMULATOR ===
with tabs[4]:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Saldo", fmt_idr(st.session_state.sim_balance))
        with st.form("sim"):
            t_s = st.selectbox("Saham", LIST_SAHAM_IHSG)
            act = st.radio("Aksi", ["BUY", "SELL"], horizontal=True)
            qty = st.number_input("Lot", 1)
            if st.form_submit_button("Submit"):
                h = yf.Ticker(t_s).history('1d')
                if not h.empty:
                    p = h['Close'].iloc[-1]
                    val = p * qty * 100
                    if act == "BUY":
                        if st.session_state.sim_balance >= val:
                            st.session_state.sim_balance -= val
                            st.session_state.sim_portfolio[t_s] = st.session_state.sim_portfolio.get(t_s, 0) + qty
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": t_s, "Action": "BUY", "Price": p, "Qty": qty})
                            st.success("Beli Sukses")
                            st.rerun()
                        else: st.error("Dana Kurang")
                    else:
                        if st.session_state.sim_portfolio.get(t_s, 0) >= qty:
                            st.session_state.sim_balance += val
                            st.session_state.sim_portfolio[t_s] -= qty
                            if st.session_state.sim_portfolio[t_s] == 0: del st.session_state.sim_portfolio[t_s]
                            st.session_state.sim_history.append({"Date": datetime.now(), "Ticker": t_s, "Action": "SELL", "Price": p, "Qty": qty})
                            st.success("Jual Sukses")
                            st.rerun()
                        else: st.error("Stok Kurang")

    with c2:
        if st.session_state.sim_portfolio:
            pd_p = []
            cur_p = get_data(list(st.session_state.sim_portfolio.keys()), period="1d")
            tot = 0
            for t, q in st.session_state.sim_portfolio.items():
                try:
                    cp = cur_p[t]['Close'].iloc[-1] if len(st.session_state.sim_portfolio) > 1 else cur_p['Close'].iloc[-1]
                    v = cp * q * 100
                    tot += v
                    pd_p.append({"Ticker": t, "Lot": q, "Val": fmt_idr(v)})
                except: pass
            st.dataframe(pd_p)
            st.metric("Total Aset", fmt_idr(tot))
        
        if st.session_state.sim_history:
            st.dataframe(st.session_state.sim_history)
