import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
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
LIST_SAHAM_IHSG = [
   "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# --- 3. FUNGSI DATABASE (JSON) ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: 
            return None
    return None

def save_data():
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "picked_stocks": st.session_state.get("picked_stocks", []),
        "weekly_filter": st.session_state.get("weekly_filter", "")
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# --- 4. INISIALISASI SESSION STATE ---
saved_data = load_data()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = saved_data.get("watchlist", []) if saved_data else []
if 'picked_stocks' not in st.session_state:
    st.session_state.picked_stocks = saved_data.get("picked_stocks", []) if saved_data else []
if 'grid_page' not in st.session_state:
    st.session_state.grid_page = 1
if 'weekly_filter' not in st.session_state:
    st.session_state.weekly_filter = saved_data.get("weekly_filter", "") if saved_data else ""
if 'compare_list' not in st.session_state:
    st.session_state.compare_list = []
if 'compare_timeframe' not in st.session_state:
    st.session_state.compare_timeframe = "1mo"

# --- 5. FUNGSI BACKEND (CACHING) ---
@st.cache_data(ttl=3600)  # Cache 1 jam untuk menghindari rate limit
def get_stock_history_bulk(tickers, period="3mo", interval="1d"):
    if not tickers: 
        return pd.DataFrame()
    try:
        data = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'pbv': info.get('priceToBook', 'N/A'),
            'per': info.get('trailingPE', 'N/A'),
            'name': info.get('longName', ticker)
        }
    except:
        return {'pbv': 'N/A', 'per': 'N/A', 'name': ticker}

@st.cache_data(ttl=3600)
def get_weekly_recap_data(tickers):
    start_date = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
    data = yf.download(tickers, start=start_date, group_by="ticker", progress=False, auto_adjust=True)
    all_rows = []
    for t in tickers:
        try:
            if len(tickers) > 1:
                df = data[t].dropna().copy()
            else:
                df = data.dropna().copy()
            if df.empty: 
                continue
            df["Return"] = df["Close"].pct_change() * 100
            df.index = df.index.date
            row = {
                "Ticker": t, 
                "Price": round(df["Close"].iloc[-1], 2), 
                "Today (%)": round(df["Return"].iloc[-1], 2)
            }
            weekly_vals = []
            gain_count = 0
            for i in range(5):
                target = (start_of_week + timedelta(days=i)).date()
                if target in df.index:
                    val = df.loc[target, "Return"]
                    if isinstance(val, pd.Series): 
                        val = val.iloc[0]
                    row[days_names[i]] = round(val, 2)
                    weekly_vals.append(val)
                    if val > 0: 
                        gain_count += 1
                else: 
                    row[days_names[i]] = 0.0
            row["Weekly Acc (%)"] = round(sum(weekly_vals), 2)
            row["Win Rate"] = f"{gain_count}/5"
            all_rows.append(row)
        except: 
            continue
    return pd.DataFrame(all_rows)

# --- 6. FUNGSI VISUALISASI ---
def create_box_chart(df, ticker, show_ma20=False, show_ma200=False, chart_type='line'):
    fig = go.Figure()
    
    # Calculate MAs
    if show_ma20 and len(df) >= 20:
        df['MA20'] = df['Close'].rolling(window=20).mean()
    if show_ma200 and len(df) >= 200:
        df['MA200'] = df['Close'].rolling(window=200).mean()
    
    color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
    
    if chart_type == 'ohlc':
        # OHLC bars
        fig.add_trace(go.Ohlc(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="OHLC",
            increasing_line_color='#00C805',
            decreasing_line_color='#FF333A'
        ))
    else:
        # Line chart
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'], 
            mode='lines', 
            line=dict(color=color_line, width=2), 
            name="Close"
        ))
    
    # Add MAs
    if show_ma20 and 'MA20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['MA20'], 
            mode='lines', 
            line=dict(color='orange', width=1), 
            name="MA20"
        ))
    if show_ma200 and 'MA200' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['MA200'], 
            mode='lines', 
            line=dict(color='blue', width=1), 
            name="MA200"
        ))
    
    fig.update_layout(
        title=dict(text=ticker, font=dict(size=14), x=0.5),
        margin=dict(l=10, r=10, t=40, b=10),
        height=200,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', showticklabels=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', tickfont=dict(size=9))
    
    return fig

def create_compare_chart(df, ticker, timeframe, show_volume=True, chart_type='line', 
                        ma_periods=[20], date_range=None):
    fig = make_subplots(
        rows=2 if show_volume else 1, 
        cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3] if show_volume else [1],
        subplot_titles=(ticker, 'Volume') if show_volume else (ticker,)
    )
    
    # Filter by date range if specified
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]
    
    # Calculate MAs
    for ma in ma_periods:
        if len(df) >= ma:
            df[f'MA{ma}'] = df['Close'].rolling(window=ma).mean()
    
    color_line = '#00C805' if df['Close'].iloc[-1] >= df['Close'].iloc[0] else '#FF333A'
    
    if chart_type == 'ohlc':
        fig.add_trace(go.Ohlc(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="OHLC", increasing_line_color='#00C805',
            decreasing_line_color='#FF333A'
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines',
            line=dict(color=color_line, width=2), name="Close"
        ), row=1, col=1)
    
    # Add MAs
    colors = ['orange', 'blue', 'purple']
    for i, ma in enumerate(ma_periods):
        if f'MA{ma}' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[f'MA{ma}'], mode='lines',
                line=dict(color=colors[i % len(colors)], width=1, dash='dash'),
                name=f'MA{ma}'
            ), row=1, col=1)
    
    # Volume
    if show_volume:
        colors_vol = ['#00C805' if df['Close'].iloc[i] >= df['Open'].iloc[i] 
                      else '#FF333A' for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=colors_vol, name="Volume"
        ), row=2, col=1)
    
    fig.update_layout(
        height=400 if show_volume else 300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig

# --- 7. MAIN UI DASHBOARD ---
st.title("📈 Observation")

# DEFINISI 5 TAB (SESUAI PERMINTAAN)
tabs = st.tabs([
    "📊 List", "⚖️ Bandingkan & Watchlist", "📅 Weekly Recap", 
    "🚀 Performa", "🎲 Win/Loss"
])

# === TAB 1: LIST (GRID YANG DIMODIFIKASI) ===
with tabs[0]:
    st.header("📊 List Saham")
    
    # Filter section
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        timeframe = st.selectbox(
            "Timeframe:", 
            ["5d", "1mo", "3mo", "6mo", "1y"], 
            index=1, 
            key="list_tf"
        )
    
    with col2:
        min_price = st.number_input("Min Price:", value=0, min_value=0, step=100)
    
    with col3:
        max_price = st.number_input("Max Price:", value=100000, min_value=0, step=100)
    
    with col4:
        min_volume = st.number_input("Min Volume (M):", value=0, min_value=0, step=1)
    
    # MA filters
    col5, col6, col7 = st.columns([1, 1, 1])
    with col5:
        show_ma20 = st.checkbox("MA20", value=False, key="list_ma20")
    with col6:
        show_ma200 = st.checkbox("MA200", value=False, key="list_ma200")
    with col7:
        chart_type = st.selectbox("Chart Type:", ["line", "ohlc"], key="list_chart_type")
    
    # Pagination
    items_per_page = 50
    total_pages = math.ceil(len(LIST_SAHAM_IHSG) / items_per_page)
    
    col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
    with col_page2:
        page = st.number_input(
            f"Page (1-{total_pages}):", 
            min_value=1, 
            max_value=total_pages, 
            value=st.session_state.grid_page,
            key="list_page"
        )
        st.session_state.grid_page = page
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_tickers = LIST_SAHAM_IHSG[start_idx:end_idx]
    
    # Fetch data
    data_grid = get_stock_history_bulk(current_tickers, period=timeframe)
    
    # Filter stocks
    filtered_stocks = []
    for t in current_tickers:
        try:
            if len(current_tickers) > 1:
                df = data_grid[t].dropna()
            else:
                df = data_grid.dropna()
            
            if df.empty:
                continue
                
            last_price = df['Close'].iloc[-1]
            avg_volume = df['Volume'].mean() / 1_000_000  # Convert to millions
            
            if min_price <= last_price <= max_price and avg_volume >= min_volume:
                filtered_stocks.append((t, df))
        except:
            continue
    
    # Display grid - compact box layout
    if filtered_stocks:
        cols_per_row = 4
        for i in range(0, len(filtered_stocks), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, (ticker, df) in enumerate(filtered_stocks[i:i+cols_per_row]):
                with row_cols[j]:
                    with st.container():
                        st.plotly_chart(
                            create_box_chart(df, ticker, show_ma20, show_ma200, chart_type),
                            use_container_width=True,
                            key=f"chart_{ticker}_{page}"
                        )
                        
                        # Compact info
                        last_price = df['Close'].iloc[-1]
                        change = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
                        vol = df['Volume'].iloc[-1] / 1_000_000
                        
                        st.markdown(f"""
                        <div style='font-size: 11px; line-height: 1.2;'>
                        <b>{ticker}</b><br>
                        Rp {last_price:,.0f} | {change:+.2f}%<br>
                        Vol: {vol:.1f}M
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"➕", key=f"add_{ticker}_{page}", help="Add to Compare"):
                            if ticker not in st.session_state.compare_list:
                                st.session_state.compare_list.append(ticker)
                                st.success(f"Added {ticker}")
    else:
        st.warning("No stocks match the filters.")

# === TAB 2: BANDINGKAN & WATCHLIST (DIGABUNG) ===
with tabs[1]:
    st.header("⚖️ Bandingkan & Watchlist")
    
    # Search section
    st.subheader("🔍 Search Stocks")
    search_input = st.text_input(
        "Enter stock codes (comma separated):", 
        value="BBCA.JK, BBRI.JK",
        key="compare_search"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ Add to Compare", key="btn_add_compare"):
            new_stocks = [s.strip().upper() for s in search_input.split(",") if s.strip()]
            for s in new_stocks:
                if s not in st.session_state.compare_list:
                    st.session_state.compare_list.append(s)
            save_data()
    
    with col2:
        if st.button("🗑️ Clear All", key="btn_clear_compare"):
            st.session_state.compare_list = []
            save_data()
    
    # Timeframe selection
    col_tf, col_chart, col_date = st.columns(3)
    with col_tf:
        compare_tf = st.selectbox(
            "Timeframe:",
            ["5d", "1mo", "3mo", "6mo", "1y"],
            index=1,
            key="compare_tf_select"
        )
    with col_chart:
        compare_chart_type = st.selectbox(
            "Chart Type:",
            ["line", "ohlc"],
            index=0,
            key="compare_chart_type"
        )
    with col_date:
        enable_date_range = st.checkbox("Custom Date Range", key="enable_date_range")
    
    # Date range picker
    date_range = None
    if enable_date_range:
        col_start, col_end = st.columns(2)
        with col_start:
            start_date = st.date_input("Start:", today - timedelta(days=30), key="compare_start")
        with col_end:
            end_date = st.date_input("End:", today, key="compare_end")
        date_range = (start_date, end_date)
    
    # MA selection
    col_ma1, col_ma2, col_ma3 = st.columns(3)
    with col_ma1:
        ma_20 = st.checkbox("MA 20", value=True, key="compare_ma20")
    with col_ma2:
        ma_200 = st.checkbox("MA 200", value=False, key="compare_ma200")
    with col_ma3:
        show_vol = st.checkbox("Show Volume", value=True, key="compare_volume")
    
    ma_periods = []
    if ma_20: ma_periods.append(20)
    if ma_200: ma_periods.append(200)
    
    # Display comparison
    if st.session_state.compare_list:
        st.markdown("---")
        
        # Fetch data for all stocks
        compare_data = get_stock_history_bulk(
            st.session_state.compare_list, 
            period=compare_tf if not date_range else "1y"
        )
        
        for ticker in st.session_state.compare_list:
            try:
                if len(st.session_state.compare_list) > 1:
                    df = compare_data[ticker].dropna()
                else:
                    df = compare_data.dropna()
                
                if df.empty:
                    continue
                
                # Get info
                info = get_stock_info(ticker)
                
                # Display stock info
                col_info1, col_info2, col_info3, col_info4 = st.columns([2, 1, 1, 1])
                with col_info1:
                    st.markdown(f"### {ticker} - {info['name']}")
                with col_info2:
                    st.metric("PBV", f"{info['pbv']:.2f}" if isinstance(info['pbv'], (int, float)) else "N/A")
                with col_info3:
                    st.metric("PER", f"{info['per']:.2f}" if isinstance(info['per'], (int, float)) else "N/A")
                with col_info4:
                    if st.button(f"❌ Remove {ticker}", key=f"rem_{ticker}"):
                        st.session_state.compare_list.remove(ticker)
                        save_data()
                        st.rerun()
                
                # Chart
                st.plotly_chart(
                    create_compare_chart(
                        df, ticker, compare_tf, show_vol, 
                        compare_chart_type, ma_periods, date_range
                    ),
                    use_container_width=True,
                    key=f"compare_chart_{ticker}"
                )
                
                st.markdown("---")
            except Exception as e:
                st.error(f"Error loading {ticker}: {str(e)}")
    else:
        st.info("Search and add stocks to compare. Example: BBCA.JK, BBRI.JK, GOTO.JK")

# === TAB 3: WEEKLY RECAP ===
with tabs[2]:
    st.header("📅 Weekly Recap")
    
    # Search and filter
    col_search, col_reset = st.columns([3, 1])
    with col_search:
        weekly_search = st.text_input(
            "Cari Saham:", 
            value=st.session_state.weekly_filter,
            key="weekly_search_input"
        )
        st.session_state.weekly_filter = weekly_search
    with col_reset:
        if st.button("🔄 Reset Filter", key="reset_weekly"):
            st.session_state.weekly_filter = ""
            save_data()
            st.rerun()
    
    with st.spinner("Calculating weekly returns..."):
        # Filter list based on search
        filtered_list = LIST_SAHAM_IHSG
        if weekly_search:
            filtered_list = [s for s in LIST_SAHAM_IHSG if weekly_search.upper() in s]
        
        if not filtered_list:
            st.warning("No stocks found matching your search.")
        else:
            df_weekly = get_weekly_recap_data(filtered_list[:50])  # Limit to 50 for performance
            
            if not df_weekly.empty:
                # Format price without unnecessary decimals
                df_weekly['Price'] = df_weekly['Price'].apply(lambda x: f"{x:,.0f}" if x == int(x) else f"{x:,.2f}")
                
                def style_returns(val):
                    if isinstance(val, (int, float)):
                        color = '#00ff00' if val > 0 else '#ff4b4b' if val < 0 else 'white'
                        return f'color: {color}'
                    return ''
                
                styled_df = df_weekly.style.applymap(
                    style_returns, 
                    subset=['Today (%)', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Weekly Acc (%)']
                )
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                # Delete/Reset individual stocks
                st.subheader("🗑️ Hapus Saham dari Tampilan")
                cols = st.columns(4)
                for idx, ticker in enumerate(df_weekly['Ticker'].tolist()):
                    with cols[idx % 4]:
                        if st.button(f"❌ {ticker}", key=f"del_weekly_{ticker}"):
                            # Note: This only removes from display, not from database
                            st.session_state.weekly_filter = ""
                            st.rerun()
            else:
                st.warning("No data available for the selected stocks.")

# === TAB 4: PERFORMA ===
with tabs[3]:
    st.header("🚀 Performa Saham")
    st.info("Fitur performa akan ditampilkan di sini.")

# === TAB 5: WIN/LOSS ===
with tabs[4]:
    st.header("🎲 Win/Loss Stats")
    st.info("Fitur Win/Loss akan ditampilkan di sini.")

st.caption(f"Last Update: {today.strftime('%Y-%m-%d %H:%M:%S')} | Data by Yahoo Finance")
