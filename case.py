import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="IHSG Pro Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .heatmap-box {
        display: inline-block;
        width: 35px; height: 35px; line-height: 35px;
        text-align: center; border-radius: 4px;
        margin: 2px; font-size: 10px; font-weight: bold; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIST TICKER ---
TICKERS = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "BBNI.JK", "UNVR.JK", "ADRO.JK", "KLBF.JK"]

# --- FUNCTIONS ---
@st.cache_data(ttl=3600)
def fetch_data(tickers):
    # Mengambil data 1 tahun untuk kalkulasi YTD dan performa
    return yf.download(tickers, period="1y", group_by='ticker')

@st.cache_data(ttl=3600)
def get_fundamental_safe(selected_tickers):
    results = []
    bar = st.progress(0)
    for i, t in enumerate(selected_tickers):
        try:
            time.sleep(0.7) # Jeda agar tidak kena rate limit
            info = yf.Ticker(t).info
            results.append({
                "Ticker": t,
                "Price": info.get("currentPrice"),
                "PER": info.get("trailingPE", "N/A"),
                "PBV": info.get("priceToBook", "N/A"),
                "MarketCap": info.get("marketCap", 0)
            })
        except:
            continue
        bar.progress((i + 1) / len(selected_tickers))
    bar.empty()
    return pd.DataFrame(results)

# --- APP LOGIC ---
if 'stock_data' not in st.session_state:
    with st.spinner("Mengambil data..."):
        st.session_state.stock_data = fetch_data(TICKERS)

st.title("🇮🇩 IHSG Dashboard Pro")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 List", "⚖️ Compare", "📊 Recap", "🔥 Win/Loss", "📅 Cek Tanggal"])

# --- TAB 1: LIST DENGAN Y-AXIS PERSENTASE ---
with tab1:
    items_per_page = 6
    total_pages = (len(TICKERS) // items_per_page) + (1 if len(TICKERS) % items_per_page > 0 else 0)
    
    col_p, _ = st.columns([1, 4])
    page = col_p.number_input("Halaman", min_value=1, max_value=total_pages)
    
    start = (page - 1) * items_per_page
    current_batch = TICKERS[start : start + items_per_page]
    
    cols = st.columns(3)
    for i, t in enumerate(current_batch):
        with cols[i % 3]:
            df = st.session_state.stock_data[t]['Close'].dropna().tail(30)
            if not df.empty:
                first_p = df.iloc[0]
                last_p = df.iloc[-1]
                total_ret = ((last_p - first_p) / first_p) * 100
                
                # Membuat Subplot dengan Secondary Y-Axis
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Sumbu Kiri: Harga (Line Chart)
                fig.add_trace(
                    go.Scatter(x=df.index, y=df, name="Price", line_color="#1f77b4", fill='tozeroy'),
                    secondary_y=False
                )
                
                # Sumbu Kanan: Persentase (Kita sesuaikan range-nya agar sinkron)
                # Formula: ((Harga / Harga Awal) - 1) * 100
                fig.add_trace(
                    go.Scatter(x=df.index, y=((df / first_p) - 1) * 100, name="Return %", opacity=0),
                    secondary_y=True
                )
                
                fig.update_layout(
                    title=f"<b>{t}</b> (30D: {total_ret:+.2f}%)",
                    height=280, margin=dict(l=0, r=0, t=40, b=0),
                    showlegend=False, xaxis_visible=False
                )
                
                fig.update_yaxes(title_text="Price", secondary_y=False, tickfont_size=9)
                fig.update_yaxes(title_text="Return %", secondary_y=True, tickfont_size=9, side="right")
                
                st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: COMPARE ---
with tab2:
    selected = st.multiselect("Pilih Saham", TICKERS, default=TICKERS[:2])
    if st.button("Bandingkan Fundamental"):
        res = get_fundamental_safe(selected)
        st.table(res)

# --- TAB 3: RECAP ---
with tab3:
    recap_list = []
    for t in TICKERS:
        d = st.session_state.stock_data[t]['Close'].dropna()
        recap_list.append({
            "Ticker": t,
            "1D %": ((d.iloc[-1]/d.iloc[-2])-1)*100,
            "1W %": ((d.iloc[-1]/d.iloc[-5])-1)*100,
            "YTD %": ((d.iloc[-1]/d.iloc[0])-1)*100
        })
    st.dataframe(pd.DataFrame(recap_list).style.format(precision=2))

# --- TAB 4: WIN/LOSS ---
with tab4:
    for t in TICKERS[:5]:
        st.write(f"**{t}** (20 Hari Terakhir)")
        d = st.session_state.stock_data[t]['Close'].dropna().tail(21).pct_change().dropna()
        h_line = ""
        for v in d:
            c = "#2ecc71" if v > 0 else "#e74c3c" if v < 0 else "#bdc3c7"
            h_line += f'<div class="heatmap-box" style="background-color:{c}">{v*100:.1f}</div>'
        st.markdown(h_line, unsafe_allow_html=True)

# --- TAB 5: CEK TANGGAL ---
with tab5:
    c1, c2 = st.columns(2)
    sd = c1.date_input("Mulai", datetime.now() - timedelta(days=30))
    ed = c2.date_input("Akhir", datetime.now())
    tk = st.selectbox("Pilih Ticker", TICKERS, key="cek")
    
    try:
        p_data = st.session_state.stock_data[tk]['Close'].dropna()
        v1, v2 = p_data.asof(pd.Timestamp(sd)), p_data.asof(pd.Timestamp(ed))
        st.metric(f"Performa {tk}", f"{v2:,.0f}", f"{((v2-v1)/v1)*100:.2f}%")
    except:
        st.error("Data tidak tersedia")
