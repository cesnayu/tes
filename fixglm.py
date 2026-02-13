import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import pytz 

# --- 1. KONFIGURASI HALAMAN & WAKTU ---
st.set_page_config(layout="wide", page_title="Observation")

# Definisi Waktu Global
today = datetime.now()
end_date_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")
start_of_week = today - timedelta(days=today.weekday())
days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

DB_FILE = "stock_database.json"

# --- 2. DATA STATIC (LIST SAHAM IHSG) ---
# Silakan isi daftar saham lengkap di sini. Saya sertakan contoh singkat agar code bisa run.
LIST_SAHAM_IHSG = [
    ""BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# --- 3. FUNGSI DATABASE & UTILS ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", [])
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

@st.cache_data(ttl=600)
def get_stock_data(ticker, period="1mo", interval="1d", start=None, end=None):
    """Mengambil data saham dengan caching untuk mencegah rate limit."""
    try:
        if start and end:
            data = yf.download(ticker, start=start, end=end, progress=False, group_by='ticker')
        else:
            data = yf.download(ticker, period=period, interval=interval, progress=False, group_by='ticker')
        
        # Flatten kolom jika multi-index
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600) # Cache info lebih lama karena berat
def get_stock_info(ticker):
    """Mengambil info fundamental (PBV, PER) dengan hati-hati."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "pbv": info.get('priceToBook', None),
            "per": info.get('forwardPE', None),
            "name": info.get('longName', ticker)
        }
    except:
        return {"pbv": None, "per": None, "name": ticker}

def format_number(num):
    """Format angka agar 28.0000 menjadi 28, tapi 28.5 tetap 28.5"""
    if isinstance(num, (int, float)):
        if num == int(num):
            return int(num)
        return round(num, 2)
    return num

# --- 4. INISIALISASI SESSION STATE ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data["watchlist"] if (saved_data and "watchlist" in saved_data) else []
if 'list_page' not in st.session_state:
    st.session_state.list_page = 1
if 'compare_search' not in st.session_state:
    st.session_state.compare_search = ""
if 'weekly_filter' not in st.session_state:
    st.session_state.weekly_filter = ""

# --- 5. MAIN UI DASHBOARD ---
st.title("🔭 Observation")

# --- TABS ---
tab_list, tab_compare, tab_recap = st.tabs(["📋 List", "⚖️ Compare & Watchlist", "📅 Weekly Recap"])

# ==========================================
# TAB 1: LIST (GRID DENGAN FITUR LENGKAP)
# ==========================================
with tab_list:
    st.subheader("Market Grid & Screener")
    
    # --- FILTERS & CONTROLS ---
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
    
    with col_ctrl1:
        timeframe = st.selectbox("Timeframe", ["5d", "1mo", "3mo", "6mo", "1y"], index=1)
        show_ma20 = st.checkbox("Tampilkan MA20", value=True)
        show_ma200 = st.checkbox("Tampilkan MA200", value=False)
    
    with col_ctrl2:
        min_price = st.number_input("Min Harga", value=0, min_value=0, step=100)
        max_price = st.number_input("Max Harga", value=100000, min_value=0, step=1000)
    
    with col_ctrl3:
        min_vol = st.number_input("Min Transaksi (Vol)", value=0, min_value=0, step=100000)
        max_vol = st.number_input("Max Transaksi (Vol)", value=1000000000, min_value=0, step=1000000)

    # --- LOGIKA FILTERING & PAGINATION ---
    # Kita ambil data bulk (agar efisien), tapi yfinance download cukup berat jika semua saham.
    # Untuk demo, kita filter list statis dulu baru ambil datanya per batch atau per saham.
    # Di sini kita simulasi ambil data untuk filtering harga terakhir.
    
    st.divider()
    
    # Tampilkan Pagination
    items_per_page = 50
    total_items = len(LIST_SAHAM_IHSG)
    total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)
    
    col_page_nav = st.columns([1, 2, 1])
    with col_page_nav[0]:
        if st.button("⬅️ Prev", disabled=(st.session_state.list_page == 1)):
            st.session_state.list_page -= 1
            st.rerun()
    
    with col_page_nav[1]:
        st.write(f"Halaman {st.session_state.list_page} dari {total_pages}")
    
    with col_page_nav[2]:
        if st.button("Next ➡️", disabled=(st.session_state.list_page >= total_pages)):
            st.session_state.list_page += 1
            st.rerun()

    # Slice list saham berdasarkan halaman
    start_idx = (st.session_state.list_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_tickers = LIST_SAHAM_IHSG[start_idx:end_idx]
    
    # Grid Container
    grid_container = st.container()
    
    # Ambil data untuk halaman ini (Batch download)
    # Gunakan progress bar agar UX lebih baik
    with st.spinner(f"Memuat data untuk {len(current_tickers)} saham..."):
        bulk_data = get_stock_data(current_tickers, period=timeframe, interval="1d")
    
    # Loop dan Filter Real-time
    cols = st.columns(5) # 5 kolom grid agar kompak (kotak-kotak)
    col_idx = 0

    for ticker in current_tickers:
        try:
            # Cek apakah data ticker ada (handle single ticker vs multi ticker return structure)
            df = bulk_data.copy()
            if len(current_tickers) > 1:
                if ticker not in df.columns.levels[0]:
                    continue
                df_t = df[ticker].dropna()
            else:
                df_t = df.dropna()

            if df_t.empty:
                continue

            # --- FILTER LOGIC ---
            last_price = df_t['Close'].iloc[-1]
            last_vol = df_t['Volume'].iloc[-1] if 'Volume' in df_t.columns else 0
            
            # Cek Filter Harga
            if not (min_price <= last_price <= max_price):
                continue
            # Cek Filter Volume
            if not (min_vol <= last_vol <= max_vol):
                continue
            
            # --- CHARTING (KOTAK KECIL) ---
            with cols[col_idx % 5]:
                # Container Style "Kotak"
                st.markdown(f"""
                <div style='border: 1px solid #ddd; padding: 10px; border-radius: 8px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <strong>{ticker}</strong><br/>
                    <span style='color: {'green' if last_price >= df_t['Close'].iloc[0] else 'red'}; font-size: 14px;'>{format_number(last_price)}</span>
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure()
                color = '#00C805' if last_price >= df_t['Close'].iloc[0] else '#FF333A'
                
                fig.add_trace(go.Scatter(x=df_t.index, y=df_t['Close'], mode='lines', line=dict(color=color, width=1), showlegend=False))
                
                if show_ma20 and len(df_t) >= 20:
                    df_t['MA20'] = df_t['Close'].rolling(window=20).mean()
                    fig.add_trace(go.Scatter(x=df_t.index, y=df_t['MA20'], mode='lines', line=dict(color='orange', width=1), showlegend=False))
                
                if show_ma200 and len(df_t) >= 200:
                    df_t['MA200'] = df_t['Close'].rolling(window=200).mean()
                    fig.add_trace(go.Scatter(x=df_t.index, y=df_t['MA200'], mode='lines', line=dict(color='blue', width=1), showlegend=False))

                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=150, xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}, yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False})
                st.plotly_chart(fig, use_container_width=True)
                
                # Tombol tambah ke watchlist kecil
                if st.button("⭐", key=f"add_{ticker}", help="Tambah ke Watchlist"):
                    if ticker not in st.session_state.watchlist:
                        st.session_state.watchlist.append(ticker)
                        save_data()
                
                col_idx += 1
        except Exception as e:
            continue

# ==========================================
# TAB 2: COMPARE & WATCHLIST (GABUNGAN)
# ==========================================
with tab_compare:
    st.subheader("⚖️ Bandingkan & Watchlist")
    
    # Layout: Search di atas, Chart di bawah
    with st.expander("🔍 Pilih Saham (Kode, dipisah koma)", expanded=True):
        col_search, col_btn = st.columns([4, 1])
        with col_search:
            default_search = ", ".join(st.session_state.watchlist) if st.session_state.watchlist else ""
            user_input = st.text_input("Input Saham (Misal: BBCA.JK, BBRI.JK)", value=default_search, key="comp_input")
        with col_btn:
            st.write("&nbsp;")
            st.write("&nbsp;")
            if st.button("Analisa"):
                st.session_state.compare_search = user_input
                st.rerun()

    # --- SETTINGS CHART ---
    col_set1, col_set2, col_set3 = st.columns(3)
    with col_set1:
        comp_tf = st.selectbox("Rentang Waktu", ["5d", "1mo", "3mo", "6mo", "1y"], key="comp_tf")
    with col_set2:
        chart_type = st.selectbox("Tipe Grafik", ["Line (Close)", "Candle (High-Low)"], key="comp_type")
    with col_set3:
        use_custom_range = st.checkbox("Gunakan Rentang Kustom (Cycle)", key="comp_cycle")
    
    start_date = None
    end_date = None
    if use_custom_range:
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("Dari", value=today - timedelta(days=30))
        with col_date2:
            end_date = st.date_input("Sampai", value=today)

    # --- RENDER CHARTS ---
    # Parse tickers dari session state atau input
    tickers_to_analyze = [x.strip().upper() for x in st.session_state.compare_search.split(",") if x.strip()]
    
    if not tickers_to_analyze:
        st.info("Silakan masukkan kode saham untuk memulai perbandingan.")
    else:
        for ticker in tickers_to_analyze:
            try:
                with st.spinner(f"Memuat {ticker}..."):
                    df_comp = get_stock_data(ticker, period=comp_tf, start=start_date, end=end_date)
                    info_comp = get_stock_info(ticker)
                    
                    # Handle single ticker dataframe structure
                    if 'Close' not in df_comp.columns and len(df_comp.columns) > 0:
                        # Kadang yfinance return multiindex meski single ticker
                         df_comp.columns = df_comp.columns.get_level_values(0)
                    
                    if df_comp.empty:
                        st.warning(f"Data tidak ditemukan untuk {ticker}")
                        continue

                    # Hitung MA20
                    df_comp['MA20'] = df_comp['Close'].rolling(window=20).mean()

                    # --- HEADER INFO ---
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### {ticker} ({info_comp['name']})")
                    c2.metric("PER", f"{info_comp['per']:.2f}" if info_comp['per'] else "N/A")
                    c3.metric("PBV", f"{info_comp['pbv']:.2f}" if info_comp['pbv'] else "N/A")

                    # --- CHART ---
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                    
                    if chart_type == "Candle (High-Low)":
                        fig.add_trace(go.Candlestick(x=df_comp.index, open=df_comp['Open'], high=df_comp['High'], low=df_comp['Low'], close=df_comp['Close'], name="Price"), row=1, col=1)
                    else:
                        fig.add_trace(go.Scatter(x=df_comp.index, y=df_comp['Close'], mode='lines', name="Price", line=dict(color='#3366CC')), row=1, col=1)
                    
                    # MA20 Line
                    fig.add_trace(go.Scatter(x=df_comp.index, y=df_comp['MA20'], mode='lines', name='MA20', line=dict(color='orange', width=1)), row=1, col=1)

                    # Volume Bar
                    fig.add_trace(go.Bar(x=df_comp.index, y=df_comp['Volume'], name="Volume", marker_color='rgba(0,0,0,0.3)'), row=2, col=1)

                    fig.update_layout(height=500, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
                    fig.update_xaxes(title_text="Date", row=2, col=1)
                    st.plotly_chart(fig, use_container_width=True)
                    st.divider()
                    
            except Exception as e:
                st.error(f"Gagal memproses {ticker}: {e}")

# ==========================================
# TAB 3: WEEKLY RECAP (FORMAT & FILTER)
# ==========================================
with tab_recap:
    st.subheader("📅 Weekly Performance Recap")
    
    # Search & Reset
    col_s1, col_s2 = st.columns([4, 1])
    with col_s1:
        search_recap = st.text_input("Cari Saham...", value=st.session_state.weekly_filter, key="recap_search_inp").upper()
    with col_s2:
        if st.button("Reset"):
            st.session_state.weekly_filter = ""
            st.rerun()
    
    # Update state filter jika input berubah (biar tidak re-run terus menerus saat ngetik, kita butuh enter atau tombol, tapi streamlit auto rerun)
    # Kita gunakan logika langsung di bawah
    
    # Fetch Data (Logic sama seperti asli tapi dibatasi list saham yg ada di LIST_SAHAM_IHSG)
    # Filter list berdasarkan search
    filtered_list = LIST_SAHAM_IHSG
    if search_recap:
        filtered_list = [t for t in LIST_SAHAM_IHSG if search_recap in t]
    
    if not filtered_list:
        st.warning("Tidak ada saham yang cocok.")
    else:
        with st.spinner("Menghitung performa mingguan..."):
            # Kita gunakan fungsi download bulk lagi untuk efficiency
            # Kita butuh data 2 minggu ke belakang untuk recap minggu ini
            start_recap = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
            raw_data = get_stock_data(filtered_list, start=start_recap, end=end_date_str)
            
            recap_rows = []
            
            for t in filtered_list:
                try:
                    # Ambil data per ticker
                    df_t = raw_data[t].dropna() if len(filtered_list) > 1 else raw_data.dropna()
                    if df_t.empty: continue
                    
                    df_t.index = df_t.index.date # Normalize index to date
                    
                    # Kalkulasi Return
                    df_t['Return'] = df_t['Close'].pct_change() * 100
                    
                    # Ambil harga terakhir dan return hari ini (baris terakhir)
                    current_price = df_t['Close'].iloc[-1]
                    today_ret = df_t['Return'].iloc[-1]
                    
                    row = {
                        "Ticker": t,
                        "Price": format_number(current_price), # Format agar 28.00 jadi 28
                        "Today (%)": format_number(today_ret)
                    }
                    
                    # Weekly Cols (Senin - Jumat minggu ini)
                    weekly_vals = []
                    for i in range(5):
                        target_day = (start_of_week + timedelta(days=i)).date()
                        if target_day in df_t.index:
                            val = df_t.loc[target_day, 'Return']
                            # Kadang return val is series if index unique issue, simple check:
                            if isinstance(val, pd.Series): val = val.iloc[0]
                            row[days_names[i]] = format_number(val)
                            weekly_vals.append(val)
                        else:
                            row[days_names[i]] = "-"
                    
                    # Weekly Accumulation
                    valid_vals = [v for v in weekly_vals if isinstance(v, (int, float))]
                    row["Weekly Acc (%)"] = format_number(sum(valid_vals))
                    recap_rows.append(row)
                except:
                    continue
            
            if recap_rows:
                df_recap = pd.DataFrame(recap_rows)
                
                # Styling
                def color_returns(val):
                    if isinstance(val, (int, float)):
                        if val > 0: return 'color: #00C805; font-weight: bold;'
                        elif val < 0: return 'color: #FF333A; font-weight: bold;'
                    return ''
                
                # Apply style
                styled_df = df_recap.style.applymap(color_returns, subset=['Today (%)', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Weekly Acc (%)'])
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("Data weekly recap tidak tersedia untuk periode ini.")

st.caption(f"Data processed at: {today.strftime('%Y-%m-%d %H:%M:%S')} | Source: Yahoo Finance")
