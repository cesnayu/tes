import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import gc

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(layout="wide", page_title="Observation Pro")

# --- 2. CSS ---
st.markdown("""
<style>
    .wl-box {
        border-radius: 5px; padding: 10px; text-align: center; color: white;
        margin-bottom: 10px; font-family: sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .wl-date { font-size: 11px; opacity: 0.9; margin-bottom: 4px; }
    .wl-price { font-size: 14px; font-weight: bold; margin-bottom: 2px; }
    .wl-pct { font-size: 12px; font-weight: bold; }
    /* Sembunyikan indeks tabel agar rapi */
    thead tr th:first-child {display:none}
    tbody th {display:none}
    /* Mempercantik tombol */
    div.stButton > button {width: 100%;}
    /* Badge gain/loss */
    .gain-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LIST SAHAM ---
RAW_TICKERS = [
    "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]
LIST_SAHAM_IHSG = [f"{t}.JK" for t in RAW_TICKERS]

# --- 4. STATE MANAGEMENT (PERSISTENCE) ---
if 'page' not in st.session_state: st.session_state.page = 1
if 'recap_data' not in st.session_state: st.session_state.recap_data = None
if 'date_check_data' not in st.session_state: st.session_state.date_check_data = None

# --- 5. FUNGSI DATA ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_fundamental(ticker):
    try:
        i = yf.Ticker(ticker).info
        return i.get('priceToBook', 0), i.get('trailingPE', 0)
    except: return 0, 0

@st.cache_data(ttl=600, show_spinner=False)
def get_data(tickers, period="3mo", interval="1d", start=None, end=None):
    if not tickers: return pd.DataFrame()
    try:
        if start and end:
            d = yf.download(tickers, start=start, end=end, interval=interval, group_by='ticker', progress=False, auto_adjust=True, threads=True)
        else:
            d = yf.download(tickers, period=period, interval=interval, group_by='ticker', progress=False, auto_adjust=True, threads=True)
        return d
    except: return pd.DataFrame()
    finally:
        gc.collect()

def fetch_data_chunked(ticker_list, period="2y", chunk_size=50):
    full_data = pd.DataFrame()
    prog_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(0, len(ticker_list), chunk_size):
        chunk = ticker_list[i:i+chunk_size]
        status_text.text(f"Mengunduh batch {i} - {i+chunk_size}...")
        try:
            temp_data = get_data(chunk, period=period)
            if not temp_data.empty:
                if full_data.empty: full_data = temp_data
                else: full_data = pd.concat([full_data, temp_data], axis=1)
        except: pass
        prog_bar.progress(min((i + chunk_size) / len(ticker_list), 1.0))
        gc.collect()
        
    status_text.empty()
    prog_bar.empty()
    return full_data

def fmt_idr(val):
    return f"{val:,.0f}" if not pd.isna(val) else "0"

# --- 6. VISUALISASI ---

def chart_grid(df, ticker, ma20=True, chart_type="Candle"):
    """
    Grafik grid dengan:
    - Sumbu Y kiri  : harga asli (log scale)
    - Sumbu Y kanan : label persentase ±5% step dari harga pertama
    - Badge gain/loss total periode di pojok kanan atas
    """
    import numpy as np

    fig = go.Figure()

    price_first = df['Close'].iloc[0]
    price_last  = df['Close'].iloc[-1]
    pct_gain    = ((price_last - price_first) / price_first) * 100
    gain_color  = "#00C805" if pct_gain >= 0 else "#FF333A"
    gain_sign   = "+" if pct_gain >= 0 else ""

    if chart_type == "Line":
        clr = '#00C805' if price_last >= price_first else '#FF333A'
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], mode='lines',
            line=dict(color=clr, width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            fill='tozeroy',
            fillcolor=f"rgba{tuple(int(clr.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.08,)}",
            mode='none'
        ))
        xaxis_cfg = dict(showgrid=False, showticklabels=False)
    else:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close']
        ))
        xaxis_cfg = dict(showgrid=False, showticklabels=False, rangeslider=dict(visible=False))

    if ma20 and len(df) > 20:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'].rolling(20).mean(),
            line=dict(color='orange', width=1), name='MA20'
        ))

    # ── Hitung tick % kanan: setiap 5% dari harga pertama ──
    data_low  = df['Low'].min()
    data_high = df['High'].max()
    margin    = (data_high - data_low) * 0.08 if data_high != data_low else data_high * 0.05
    y_low     = max(data_low - margin, price_first * 0.01)   # hindari ≤ 0 untuk log
    y_high    = data_high + margin

    # Rentang % yang tercakup
    pct_low  = ((y_low  - price_first) / price_first) * 100
    pct_high = ((y_high - price_first) / price_first) * 100

    # Buat tick setiap 5%
    step = 5
    tick_pcts   = list(range(
        int(math.floor(pct_low  / step) * step),
        int(math.ceil (pct_high / step) * step) + step,
        step
    ))
    tick_prices = [price_first * (1 + p / 100) for p in tick_pcts]
    tick_labels = [f"{p:+d}%" for p in tick_pcts]

    # Filter tick di dalam range
    filtered = [(p, l) for p, l in zip(tick_prices, tick_labels) if y_low <= p <= y_high]
    tick_prices_f = [x[0] for x in filtered]
    tick_labels_f = [x[1] for x in filtered]

    clr_title = "green" if price_last >= df['Open'].iloc[-1] else "red"

    fig.update_layout(
        title=dict(
            text=f"{ticker} ({fmt_idr(price_last)})",
            font=dict(size=13, color=clr_title),
            x=0.5, y=0.93
        ),
        margin=dict(l=5, r=55, t=32, b=5),   # margin kanan lebih lebar untuk label %
        height=250,
        showlegend=False,
        # Sumbu Y kiri — log scale, harga asli, disembunyikan label-nya
        yaxis=dict(
            type="log",
            range=[math.log10(max(y_low, 1e-9)), math.log10(y_high)],
            showgrid=True,
            gridcolor='rgba(128,128,128,0.15)',
            tickfont=dict(size=7),
            showticklabels=False,   # sembunyikan label harga kiri agar tidak crowded
        ),
        # Sumbu Y kanan — overlay, tick % setiap 5%
        yaxis2=dict(
            overlaying="y",
            side="right",
            type="log",
            range=[math.log10(max(y_low, 1e-9)), math.log10(y_high)],
            tickvals=tick_prices_f,
            ticktext=tick_labels_f,
            tickfont=dict(size=8, color="rgba(200,200,200,0.85)"),
            showgrid=False,
            zeroline=False,
        ),
        xaxis=xaxis_cfg,
    )

    # ── Garis baseline (0%) ──
    fig.add_hline(
        y=price_first,
        line=dict(color="rgba(180,180,180,0.4)", width=1, dash="dot"),
    )

    # ── Badge gain total ──
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.99,
        text=f"<b>{gain_sign}{pct_gain:.1f}%</b>",
        showarrow=False,
        font=dict(size=11, color=gain_color),
        align="left",
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor=gain_color,
        borderwidth=1,
        borderpad=3,
        xanchor="left",
        yanchor="top"
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
tabs = st.tabs(["📋 List", "⚖️ Compare", "📅 Recap", "🎲 Win/Loss", "🗓️ Cek Tanggal"])

# === TAB 1: LIST ===
with tabs[0]:
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    with c1: tf = st.selectbox("Waktu", ["5d", "1mo", "3mo", "6mo", "1y"], 2)
    with c2: min_p = st.number_input("Min Rp", 0, step=50)
    with c3: max_p = st.number_input("Max Rp", 100, value=100000, step=50)
    with c4: c_type = st.radio("Grafik", ["Candle", "Line"], horizontal=True)
    with c5: show_ma = st.checkbox("MA20", True)

    per_page = 20
    total_pages = math.ceil(len(LIST_SAHAM_IHSG)/per_page)
    
    b1, b2, b3 = st.columns([1, 8, 1])
    if b1.button("⬅️") and st.session_state.page > 1: st.session_state.page -= 1; st.rerun()
    b2.markdown(f"<div style='text-align:center; margin-top:5px'><b>Page {st.session_state.page}/{total_pages}</b></div>", unsafe_allow_html=True)
    if b3.button("➡️") and st.session_state.page < total_pages: st.session_state.page += 1; st.rerun()

    start_idx = (st.session_state.page-1)*per_page
    batch = LIST_SAHAM_IHSG[start_idx:start_idx+per_page]
    
    if batch:
        with st.spinner("Loading Grid..."):
            df_b = get_data(batch, period=tf)
        
        # ── Kumpulkan semua data ticker yang lolos filter ──
        valid_data = {}
        for t in batch:
            try:
                if len(batch) > 1:
                    if t not in df_b.columns.levels[0]: continue
                    dft = df_b[t].dropna()
                else:
                    dft = df_b.dropna()
                if dft.empty: continue
                if not (min_p <= dft['Close'].iloc[-1] <= max_p): continue
                valid_data[t] = dft
            except:
                continue

        # ── Render grafik ──
        cols = st.columns(4)
        idx = 0
        for t, dft in valid_data.items():
            with cols[idx % 4]:
                st.plotly_chart(chart_grid(dft, t, show_ma, c_type), use_container_width=True)
            idx += 1

        gc.collect()

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
        gc.collect()

# === TAB 3: RECAP (PERSISTENT) ===
with tabs[2]:
    st.markdown("### 📊 Rekapitulasi Pasar")
    
    search_query = st.text_input("🔍 Filter Tabel (Contoh: BBCA):", value="")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("Muat Data Baru (Update)"):
            target_tickers = LIST_SAHAM_IHSG
            with st.spinner("Mengunduh Data..."):
                d_r = fetch_data_chunked(target_tickers, period="2y", chunk_size=50)
                
                rows = []
                now = datetime.now().date()
                start_w = now - timedelta(days=now.weekday())
                
                for t in target_tickers:
                    try:
                        if t not in d_r.columns.levels[0]: continue
                        dt = d_r[t].dropna()
                        if dt.empty: continue
                        
                        curr = dt['Close'].iloc[-1]
                        
                        def get_ret(days):
                            if len(dt) < 5: return 0.0
                            if days == 365: offset = 250
                            elif days == 180: offset = 125
                            elif days == 30: offset = 20
                            else: offset = 1
                            if len(dt) > offset:
                                return ((curr - dt['Close'].iloc[-offset])/dt['Close'].iloc[-offset])*100
                            return 0.0
                        
                        row = {"Ticker": t, "Harga": fmt_idr(curr), "Vol": fmt_idr(dt['Volume'].iloc[-1])}
                        
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
                    st.session_state.recap_data = pd.DataFrame(rows)
                gc.collect()

    with col_r2:
        if st.button("Hapus Data (Reset)"):
            st.session_state.recap_data = None
            st.rerun()

    if st.session_state.recap_data is not None:
        df_show = st.session_state.recap_data
        
        if search_query:
            df_show = df_show[df_show['Ticker'].str.contains(search_query.upper())]
            
        def color_val(v): 
            if isinstance(v, (int, float)): return f'color: {"green" if v>0 else "red" if v<0 else ""}'
            return ""
        
        st.dataframe(
            df_show.style.applymap(color_val).format("{:.2f}", subset=["Weekly%", "1M%", "6M%", "1Y%", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"]), 
            height=600, 
            use_container_width=True
        )
    else:
        st.info("Data belum dimuat. Klik 'Muat Data Baru' untuk memulai.")

# === TAB 4: WIN/LOSS ===
with tabs[3]:
    st.subheader("🎲 Win/Loss Heatmap")
    txt = st.text_input("Ketik Kode Saham:", value="BBCA, GOTO")
    
    if txt:
        ticks = [x.strip().upper() for x in txt.split(",") if x.strip()]
        clean_ticks = []
        for t in ticks:
            if not t.endswith(".JK"): clean_ticks.append(f"{t}.JK")
            else: clean_ticks.append(t)
            
        if clean_ticks:
            with st.spinner("Fetching..."):
                d_wl = get_data(clean_ticks, period="3mo")
            
            for t in clean_ticks:
                try:
                    dt = d_wl[t] if len(clean_ticks)>1 else d_wl
                    dt = dt.dropna()
                    if dt.empty: continue
                    
                    dt['Pct'] = dt['Close'].pct_change() * 100
                    last20 = dt.tail(20).sort_index()
                    
                    st.markdown(f"**{t}**")
                    chunks = [last20.iloc[i:i+5] for i in range(0, len(last20), 5)]
                    
                    for chunk in chunks:
                        cols = st.columns(5)
                        for i, (date, row) in enumerate(chunk.iterrows()):
                            pct = row['Pct']
                            bg = "#00C805" if pct > 0 else "#FF333A" if pct < 0 else "#555"
                            with cols[i]:
                                st.markdown(f"""
                                <div class="wl-box" style="background-color: {bg};">
                                    <div class="wl-date">{date.strftime('%d/%m')}</div>
                                    <div class="wl-price">{fmt_idr(row['Close'])}</div>
                                    <div class="wl-pct">{pct:+.2f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                    st.divider()
                except: st.error(f"Gagal memuat {t}")
            gc.collect()

# === TAB 5: CEK TANGGAL (PERSISTENT) ===
with tabs[4]:
    st.subheader("🗓️ Perbandingan Harga Berdasarkan Tanggal")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_start = st.date_input("Tanggal Awal", value=datetime.now() - timedelta(days=30))
    with col_d2:
        date_end = st.date_input("Tanggal Akhir", value=datetime.now())

    filter_text = st.text_input("🔍 Filter Hasil:", placeholder="Contoh: BANK, BBCA")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Hitung Perubahan"):
            if date_start >= date_end:
                st.error("Tanggal error")
            else:
                with st.spinner("Mengambil data..."):
                    s_str = date_start.strftime("%Y-%m-%d")
                    e_str = (date_end + timedelta(days=1)).strftime("%Y-%m-%d")
                    
                    chunk_size = 50
                    prog = st.progress(0)
                    res_data = []
                    
                    for i in range(0, len(LIST_SAHAM_IHSG), chunk_size):
                        chunk = LIST_SAHAM_IHSG[i:i+chunk_size]
                        try:
                            d_batch = yf.download(chunk, start=s_str, end=e_str, group_by='ticker', progress=False, auto_adjust=True, threads=True)
                            for t in chunk:
                                if t not in d_batch.columns.levels[0]: continue
                                df_t = d_batch[t].dropna()
                                if df_t.empty: continue
                                
                                p_start = df_t['Close'].iloc[0]
                                p_end = df_t['Close'].iloc[-1]
                                change = ((p_end - p_start) / p_start) * 100
                                
                                res_data.append({
                                    "Ticker": t,
                                    "Harga Awal": fmt_idr(p_start),
                                    "Harga Akhir": fmt_idr(p_end),
                                    "Perubahan (%)": change
                                })
                        except: pass
                        prog.progress(min((i + chunk_size) / len(LIST_SAHAM_IHSG), 1.0))
                    
                    prog.empty()
                    if res_data:
                        st.session_state.date_check_data = pd.DataFrame(res_data)
                    gc.collect()

    with col_btn2:
        if st.button("Reset Tabel"):
            st.session_state.date_check_data = None
            st.rerun()

    if st.session_state.date_check_data is not None:
        df_res = st.session_state.date_check_data
        
        if filter_text:
            df_res = df_res[df_res['Ticker'].str.contains(filter_text.upper())]
        
        def color_change(v):
            return f'color: {"green" if v > 0 else "red" if v < 0 else "black"}'
        
        st.dataframe(
            df_res.style.applymap(color_change, subset=["Perubahan (%)"]).format("{:.2f}", subset=["Perubahan (%)"]),
            use_container_width=True,
            height=600
        )
    else:
        st.info("Silakan pilih tanggal dan klik 'Hitung Perubahan'")
