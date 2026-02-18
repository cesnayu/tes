import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import math
import gc

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# --- 2. CSS CUSTOM ---
st.markdown("""
<style>
    thead tr th:first-child {display:none}
    tbody th {display:none}
    div.stButton > button {width: 100%;}
    /* Mempercantik tampilan tab */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #1e1e1e;
        border-radius: 5px 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LIST SAHAM (Sesuai List Kamu) ---
RAW_TICKERS = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "GOTO", "ADRO", "PTBA", "ANTM", "KLBF"
]
LIST_SAHAM_IHSG = [f"{t}.JK" for t in RAW_TICKERS]

# --- 4. STATE MANAGEMENT ---
if 'page' not in st.session_state: st.session_state.page = 1

# --- 5. FUNGSI AMBIL DATA ---
@st.cache_data(ttl=60, show_spinner=False)
def get_intraday_data(tickers):
    if not tickers: return pd.DataFrame()
    try:
        # 1 menit interval untuk grafik yang mulus (smooth)
        d = yf.download(tickers, period="1d", interval="1m", group_by='ticker', progress=False, auto_adjust=True)
        return d
    except: return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_historical_data(tickers, period="3mo"):
    if not tickers: return pd.DataFrame()
    try:
        d = yf.download(tickers, period=period, interval="1d", group_by='ticker', progress=False, auto_adjust=True)
        return d
    except: return pd.DataFrame()

def fmt_idr(val):
    return f"{val:,.0f}" if not pd.isna(val) else "0"

# --- 6. VISUALISASI INTRADAY (ZOOM MODE) ---
def chart_intraday_zoom(df, ticker):
    fig = go.Figure()
    
    first_p = df['Open'].iloc[0]
    last_p = df['Close'].iloc[-1]
    
    # Skala grid tiap 5% dari harga sekarang
    tick_interval = last_p * 0.05
    
    # Warna: Hijau jika naik dari harga buka, Merah jika turun
    is_up = last_p >= first_p
    line_clr = '#00C805' if is_up else '#FF333A'
    fill_clr = 'rgba(0, 200, 5, 0.15)' if is_up else 'rgba(255, 51, 58, 0.15)'

    # Grafik Area
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'], 
        mode='lines', 
        line=dict(color=line_clr, width=2.5),
        fill='tozeroy',
        fillcolor=fill_clr,
        name=ticker
    ))
    
    # Tambahkan garis horizontal harga OPEN sebagai acuan
    fig.add_hline(y=first_p, line_dash="dash", line_color="rgba(255,255,255,0.3)", 
                  annotation_text="Open", annotation_position="bottom left")

    # Hitung pergerakan Y agar tidak dari nol (ZOOMED)
    y_min = df['Close'].min() * 0.995 # Beri sedikit padding 0.5% di bawah
    y_max = df['Close'].max() * 1.005 # Beri sedikit padding 0.5% di atas

    fig.update_layout(
        title=f"<b>{ticker}</b> | <span style='color:{line_clr}'>{fmt_idr(last_p)} ({((last_p-first_p)/first_p*100):+.2f}%)</span>",
        margin=dict(l=10, r=60, t=50, b=10),
        height=380,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, title="Time (1m Interval)"),
        yaxis=dict(
            side="right", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)',
            autorange=False, 
            range=[y_min, y_max], # Mengunci range ke area harga saja (TIDAK DARI 0)
            tickmode='linear',
            dtick=tick_interval, 
            tickformat=',.0f'
        )
    )
    return fig

# --- 7. MAIN UI ---
tabs = st.tabs(["🔍 Multi-Search", "📋 Grid List", "⚖️ Comparison"])

# === TAB 1: MULTI-SEARCH (INTRADAY 1D) ===
with tabs[0]:
    st.subheader("Live Intraday Viewer (Skala 5%)")
    search_input = st.text_input("Masukkan kode saham (pisahkan spasi):", 
                                placeholder="Contoh: BBCA BBRI GOTO BREN",
                                key="multi_search_key").upper()
    
    if search_input:
        tickers = [s.strip() for s in search_input.replace(',', ' ').split() if s.strip()]
        tickers_jk = [s if s.endswith(".JK") else f"{s}.JK" for s in tickers]
        
        with st.spinner("Menarik data menit ke menit..."):
            data_batch = get_intraday_data(tickers_jk)
            
        if not data_batch.empty:
            cols = st.columns(2) # Tampilan 2 kolom agar grafik lebar
            for i, t in enumerate(tickers_jk):
                try:
                    # Ambil data spesifik saham
                    if len(tickers_jk) > 1:
                        if t not in data_batch.columns.levels[0]: continue
                        df_stock = data_batch[t].dropna()
                    else:
                        df_stock = data_batch.dropna()
                    
                    if df_stock.empty: continue
                    
                    with cols[i % 2]:
                        st.plotly_chart(chart_intraday_zoom(df_stock, t), use_container_width=True)
                except: continue
            gc.collect()
        else:
            st.error("Data tidak ditemukan. Pastikan kode saham benar (Contoh: BBCA).")

# === TAB 2: GRID LIST (HISTORICAL) ===
with tabs[1]:
    c1, c2 = st.columns([1, 2])
    with c1: tf = st.selectbox("Rentang Waktu", ["5d", "1mo", "3mo", "1y"], index=2)
    
    per_page = 12
    total_pg = math.ceil(len(LIST_SAHAM_IHSG)/per_page)
    
    # Navigasi Halaman
    nav1, nav2, nav3 = st.columns([1, 2, 1])
    if nav1.button("⬅️ Prev") and st.session_state.page > 1:
        st.session_state.page -= 1
        st.rerun()
    nav2.write(f"Halaman {st.session_state.page} dari {total_pg}")
    if nav3.button("Next ➡️") and st.session_state.page < total_pg:
        st.session_state.page += 1
        st.rerun()

    start_idx = (st.session_state.page - 1) * per_page
    current_batch = LIST_SAHAM_IHSG[start_idx : start_idx + per_page]
    
    if current_batch:
        df_hist = get_historical_data(current_batch, period=tf)
        cols_grid = st.columns(3)
        for idx, t in enumerate(current_batch):
            try:
                if t not in df_hist.columns.levels[0]: continue
                with cols_grid[idx % 3]:
                    # Grafik mini sederhana untuk grid
                    dft = df_hist[t].dropna()
                    fig_mini = go.Figure()
                    fig_mini.add_trace(go.Scatter(x=dft.index, y=dft['Close'], line=dict(color='#00C805', width=1.5)))
                    fig_mini.update_layout(title=f"{t}", height=200, margin=dict(l=0,r=0,t=30,b=0), xaxis_visible=False)
                    st.plotly_chart(fig_mini, use_container_width=True)
            except: continue

# === TAB 3: COMPARISON ===
with tabs[2]:
    st.write("Gunakan Tab Multi-Search untuk analisis mendalam.")
