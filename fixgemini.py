import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation")

# CSS Kustom untuk tampilan lebih padat (Compact)
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 1rem;}
    .stPlotlyChart {height: 300px;}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA STATIC (CONTOH 60 SAHAM IHSG UNTUK TEST PAGINATION) ---
# Saya tambahkan banyak saham agar fitur pagination (50 per hal) terlihat
LIST_SAHAM_IHSG = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# --- 3. FUNGSI BACKEND (CACHING & DATA) ---

@st.cache_data(ttl=3600) # Cache 1 jam untuk fundamental agar tidak kena rate limit
def get_fundamental_info(ticker):
    """Mengambil data PBV dan PER (Hati-hati rate limit yfinance)"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        pbv = info.get('priceToBook', 0)
        per = info.get('trailingPE', 0)
        return pbv, per
    except:
        return 0, 0

@st.cache_data(ttl=900) # Cache 15 menit untuk harga
def get_data_bulk(tickers, period="3mo", interval="1d", start=None, end=None):
    if not tickers: return pd.DataFrame()
    try:
        # Jika custom range (Cycle)
        if start and end:
            data = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, threads=True)
        else:
            data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, threads=True)
        return data
    except Exception as e:
        return pd.DataFrame()

def format_rupiah(value):
    """Format angka tanpa desimal berlebih"""
    if pd.isna(value): return "0"
    return f"{value:,.0f}"

# --- 4. VISUALISASI CHART ---

def create_compact_candle(df, ticker, ma20=True, ma200=False):
    """Grafik Candlestick Kompak untuk Tab List"""
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name="Price", showlegend=False
    ))
    
    # Moving Averages
    if ma20:
        ma_20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_20, line=dict(color='orange', width=1), name="MA20", showlegend=False))
    if ma200:
        ma_200 = df['Close'].rolling(window=200).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_200, line=dict(color='blue', width=1), name="MA200", showlegend=False))

    fig.update_layout(
        title=dict(text=ticker, font=dict(size=14), x=0.5, y=0.95),
        margin=dict(l=0, r=0, t=30, b=0),
        height=250,
        xaxis_rangeslider_visible=False,
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        xaxis=dict(showgrid=False)
    )
    return fig

def create_advanced_chart(df, ticker, show_ma20=True, style='candle', pbv=0, per=0):
    """Grafik Lengkap untuk Tab Compare (Subplots: Price + Volume)"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Plot Harga (Atas)
    if style == 'candle':
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="OHLC"
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines', line=dict(color='green', width=2), name="Close"
        ), row=1, col=1)
        # Tambah High/Low shade jika perlu, tapi line chart biasanya simple

    # MA20 Line
    if show_ma20:
        ma_20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma_20, line=dict(color='orange', width=1.5), name="MA20"), row=1, col=1)

    # Plot Volume (Bawah)
    colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

    # Title dengan Info Fundamental
    title_text = f"{ticker} | Price: {format_rupiah(df['Close'].iloc[-1])} | PBV: {pbv:.2f}x | PER: {per:.2f}x"
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=16), x=0),
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
        showlegend=False
    )
    return fig

# --- 5. UI DASHBOARD ---

st.title("📈 Observation")

# Tabs Utama (Dikurangi dan dirapikan)
tabs = st.tabs(["📋 List", "⚖️ Compare & Watchlist", "📅 Weekly Recap", "🚀 Performa", "🎲 Win/Loss", "🎯 Simulator"])

# ==========================
# TAB 1: LIST (GRID SYSTEM)
# ==========================
with tabs[0]:
    # --- Filter & Controls Bar ---
    c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
    with c1:
        timeframe_list = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y", "ytd"], index=2)
    with c2:
        min_price = st.number_input("Min Harga", value=0, step=50)
    with c3:
        max_price = st.number_input("Max Harga", value=100000, step=50)
    with c4:
        show_ma20_list = st.checkbox("Show MA20", value=True)
        show_ma200_list = st.checkbox("Show MA200", value=False)

    # --- Pagination Logic ---
    ITEMS_PER_PAGE = 50
    if 'page' not in st.session_state: st.session_state.page = 1
    
    # Filter Saham (Di dunia nyata ini dilakukan di DB, disini kita filter listnya dulu)
    # Karena kita tidak punya harga realtime semua saham sebelum fetch, kita ambil batch sesuai halaman
    # Namun untuk filter harga (Min/Max) bekerja, idealnya kita fetch harga terakhir dulu.
    # Untuk efisiensi kode ini, saya akan menerapkan filter setelah fetch data batch halaman tersebut.
    
    total_pages = math.ceil(len(LIST_SAHAM_IHSG) / ITEMS_PER_PAGE)
    
    # Tombol Pagination
    col_p1, col_p2, col_p3 = st.columns([1, 8, 1])
    with col_p1:
        if st.button("⬅️ Prev") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col_p2:
        st.markdown(f"<div style='text-align: center'>Page {st.session_state.page} of {total_pages}</div>", unsafe_allow_html=True)
    with col_p3:
        if st.button("Next ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1

    # Slicing List
    start_idx = (st.session_state.page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    batch_tickers = LIST_SAHAM_IHSG[start_idx:end_idx]

    # Get Data
    if batch_tickers:
        with st.spinner("Loading Chart Data..."):
            df_batch = get_data_bulk(batch_tickers, period=timeframe_list)
        
        # Grid Display (5 kolom)
        cols = st.columns(5)
        idx_counter = 0
        
        for t in batch_tickers:
            try:
                # Handle MultiIndex column
                df_t = df_batch[t] if len(batch_tickers) > 1 else df_batch
                df_t = df_t.dropna()
                
                if df_t.empty: continue
                
                last_price = df_t['Close'].iloc[-1]
                
                # Filter Harga
                if not (min_price <= last_price <= max_price):
                    continue

                with cols[idx_counter % 5]:
                    st.plotly_chart(
                        create_compact_candle(df_t, t, ma20=show_ma20_list, ma200=show_ma200_list),
                        use_container_width=True
                    )
                idx_counter += 1
            except Exception as e:
                continue

# ====================================
# TAB 2: COMPARE & WATCHLIST (MERGED)
# ====================================
with tabs[1]:
    st.markdown("### 🔍 Analisis & Perbandingan")
    
    # --- Input Controls ---
    col_w1, col_w2, col_w3 = st.columns([3, 1, 1])
    with col_w1:
        selected_stocks = st.multiselect(
            "Cari / Pilih Saham (Watchlist):", 
            options=LIST_SAHAM_IHSG, 
            default=["BBCA.JK", "BBRI.JK"] # Default
        )
    with col_w2:
        chart_style = st.radio("Style Grafik:", ["Candle (Kotak)", "Line (Garis)"], horizontal=True)
        style_code = 'candle' if "Candle" in chart_style else 'line'
    with col_w3:
        mode_waktu = st.radio("Mode Waktu:", ["Preset", "Cycle (Custom)"], horizontal=True)

    # --- Timeframe Logic ---
    start_date, end_date = None, None
    period_sel = "3mo" # Default
    
    if mode_waktu == "Preset":
        period_sel = st.select_slider("Rentang Waktu:", options=["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"], value="6mo")
    else:
        c_d1, c_d2 = st.columns(2)
        with c_d1: start_input = st.date_input("Mulai", value=datetime.now() - timedelta(days=60))
        with c_d2: end_input = st.date_input("Sampai", value=datetime.now())
        start_date = start_input.strftime("%Y-%m-%d")
        end_date = end_input.strftime("%Y-%m-%d")

    st.divider()

    # --- Render Charts Loop ---
    if selected_stocks:
        # Fetch Data
        data_compare = get_data_bulk(selected_stocks, period=period_sel, start=start_date, end=end_date)
        
        for ticker in selected_stocks:
            try:
                # Extract Data
                df_c = data_compare[ticker] if len(selected_stocks) > 1 else data_compare
                df_c = df_c.dropna()

                if df_c.empty:
                    st.warning(f"Data tidak tersedia untuk {ticker} pada rentang waktu ini.")
                    continue

                # Get Fundamentals (On demand agar tidak berat di awal)
                pbv, per = get_fundamental_info(ticker)
                
                # Container per saham
                with st.container():
                    st.plotly_chart(
                        create_advanced_chart(df_c, ticker, style=style_code, pbv=pbv, per=per), 
                        use_container_width=True
                    )
                    st.markdown("---") # Separator antar saham
            except Exception as e:
                st.error(f"Error loading {ticker}: {e}")
    else:
        st.info("Silakan pilih saham di menu atas untuk memulai analisis.")

# ==========================
# TAB 3: WEEKLY RECAP
# ==========================
with tabs[2]:
    st.header("📅 Weekly Performance Recap")
    
    # Tools Control
    wr_col1, wr_col2 = st.columns([3, 1])
    with wr_col1:
        weekly_search = st.multiselect("Cari Saham Spesifik:", options=LIST_SAHAM_IHSG, default=LIST_SAHAM_IHSG[:10])
    with wr_col2:
        if st.button("Reset Default"):
            weekly_search = LIST_SAHAM_IHSG[:10]
            st.rerun()

    # Logic Data Weekly
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    if weekly_search:
        # Download data start from last week to ensure we have enough data
        w_start = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
        w_data = yf.download(weekly_search, start=w_start, group_by='ticker', progress=False)
        
        weekly_rows = []
        for t in weekly_search:
            try:
                df_w = w_data[t].dropna() if len(weekly_search) > 1 else w_data.dropna()
                if df_w.empty: continue
                
                # Hitung Return Harian
                df_w["Return"] = df_w["Close"].pct_change() * 100
                df_w_idx = df_w.index.date # Convert index to date only objects
                
                # Last Price & Today %
                last_price = df_w["Close"].iloc[-1]
                last_ret = df_w["Return"].iloc[-1]
                
                row = {
                    "Ticker": t, 
                    "Price": format_rupiah(last_price), # Format integer Rupiah
                    "Today (%)": round(last_ret, 2)
                }
                
                acc_weekly = 0
                for i in range(5):
                    target_date = (start_of_week + timedelta(days=i)).date()
                    val = 0.0
                    # Cari tanggal di index
                    if target_date in df_w_idx:
                         # Mengambil nilai return pada tanggal tersebut
                         # Perlu trick karena index datetime vs date
                         loc_idx = df_w.index[df_w.index.date == target_date]
                         if len(loc_idx) > 0:
                             val = df_w.loc[loc_idx[0], "Return"]
                    
                    row[days_names[i]] = round(val, 2)
                    acc_weekly += val
                
                row["Weekly Acc (%)"] = round(acc_weekly, 2)
                weekly_rows.append(row)
            except Exception as e:
                continue
        
        if weekly_rows:
            df_res = pd.DataFrame(weekly_rows)
            
            # Styling
            def color_returns(val):
                if isinstance(val, (int, float)):
                    color = '#00C805' if val > 0 else '#FF333A' if val < 0 else ''
                    return f'color: {color}'
                return ''

            st.dataframe(
                df_res.style.applymap(color_returns, subset=['Today (%)', 'Weekly Acc (%)'] + days_names),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Tidak ada data yang ditemukan untuk rentang waktu ini.")

# ==========================
# TAB LAIN (PLACEHOLDER)
# ==========================
with tabs[3]:
    st.info("Fitur Performa sedang dikembangkan (Maintenance).")
with tabs[4]:
    st.info("Fitur Win/Loss Stats siap diintegrasikan.")
with tabs[5]:
    st.info("Trading Simulator akan segera hadir.")

st.caption(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Observation Dashboard v2.0")
