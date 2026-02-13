import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import math
import json
import os

# ─────────────────────────────────────────────
#  1. KONFIGURASI HALAMAN & WAKTU
# ─────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Observation")

today      = datetime.now()
end_date_str  = (today + timedelta(days=1)).strftime("%Y-%m-%d")
start_of_week = today - timedelta(days=today.weekday())
days_names    = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

DB_FILE = "stock_database.json"

# ─────────────────────────────────────────────
#  2. DAFTAR SAHAM IHSG
# ─────────────────────────────────────────────
LIST_SAHAM_IHSG = [
   "BREN", "BBCA", "DSSA", "BBRI", "TPIA", "DCII", "BYAN", "AMMN", "BMRI", "TLKM", "ASII", "MORA", "SRAJ", "CUAN", "BRPT", "BBNI", "PANI", "BNLI", "BRMS", "CDIA", "DNET", "IMPC", "FILM", "MPRO", "BRIS", "ICBP", "HMSP", "BUMI", "EMAS", "UNTR", "ANTM", "NCKL", "SMMA", "ADMR", "CASA", "UNVR", "RISE", "CPIN", "MLPT", "AMRT", "MDKA", "ISAT", "MBMA", "GOTO", "INCO", "AADI", "INDF", "PTRO", "BELI", "ADRO", "EXCL", "TCPI", "KLBF", "EMTK", "MYOR", "PGAS", "INKP", "PGUN", "PGEO", "GEMS", "MTEL", "BNGA", "CMRY", "ARCI", "TBIG", "MEGA", "SILO", "MEDC", "GIAA", "SOHO", "VKTR", "CBDK", "MIKA", "NISP", "JPFA", "GGRM", "TOWR", "BBHI", "ENRG", "TAPG", "SUPA", "BUVA", "PTBA", "BINA", "COIN", "AVIA", "JSMR", "AKRA", "NSSS", "PNBN", "ITMG", "BDMN", "ARKO", "MDIY", "TINS", "BSIM", "INTP", "JARR", "BKSL", "BTPN", "ARTO", "FAPA", "MKPI", "RMKE", "SRTG", "TKIM", "MAPA", "MSIN", "MAPI", "RLCO", "HEAL", "BSDE", "KPIG", "CITA", "PWON", "BNBR", "APIC", "BBTN", "SMGR", "RAJA", "POLU", "LIFE", "BNII", "INDY", "CTRA", "SMAR", "SCMA", "SSMS", "CARE", "ULTJ", "SIDO", "DSNG", "BBSI", "BUKA", "AALI", "RATU", "BBKP", "HRUM", "CMNT", "SGRO", "PSAB", "JRPT", "YUPI", "STAA", "STTP", "GOOD", "MCOL", "WIFI", "AUTO", "TSPC", "NICL", "ALII", "SHIP", "MLBI", "PACK", "DEWA", "CYBR", "PRAY", "POWR", "ESSA", "BMAS", "MIDI", "EDGE", "BIPI", "BSSR", "SMSM", "ADMF", "ELPI", "BFIN", "HRTA", "CLEO", "BTPS", "CMNP", "CNMA", "BANK", "ADES", "INPP", "BJBR", "SIMP", "BJTM", "PNLF", "INET", "SINI", "TLDN", "GMFI", "NATO", "BBMD", "LSIP", "TMAS", "ABMM", "DUTI", "BHAT", "DAAZ", "SGER", "DMND", "CLAY", "IBST", "MTDL", "BULL", "ACES", "LPKR", "DMAS", "SMRA", "SSIA", "ERAA", "EPMT", "SMDR", "KRAS", "JSPT", "BOGA", "MAYA", "AGII", "OMED", "PALM", "ANJT", "TOBA", "DATA", "BESS", "INDS", "CASS", "ELSA", "AGRO", "SAME", "UANG", "MNCN", "LINK", "BPII", "YULE", "TRIN", "BALI", "UDNG", "PBSA", "CTBN", "DRMA", "NIRO", "DKFT", "GTSI", "MTLA", "BBYB", "TFCO", "ROTI", "FISH", "TRIM", "PYFA", "TGKA", "GOLF", "KIJA", "JTPE", "MASB", "HUMI", "FORE", "MPMX", "RDTX", "MSTI", "BSWD", "IMAS", "BIRD", "LPCK", "ASSA", "TUGU", "BWPT", "WIIM", "RONY", "LPPF", "CENT", "SDRA", "SURE", "VICI", "MGLV", "NOBU", "KEEN", "PSGO", "AMAR", "CPRO", "CBRE", "SOCI", "ARNA", "TBLA", "STAR", "GJTL", "VICO", "PBID", "INPC", "GGRP", "IRSX", "AGRS", "HEXA", "TOTL", "UNIC", "SMMT", "BUKK", "ROCK", "SKRN", "MDLA", "MMLP", "MINA", "BACA", "MAPB", "KEJU", "BGTG", "SOTS", "MBSS", "SAMF", "BHIT", "ARGO", "CBUT", "PNIN", "MARK", "SMDM", "ISSP", "FPNI", "APLN", "MYOH", "ASRI", "SMIL", "DAYA", "KAEF", "IFSH", "BNBA", "RALS", "JAWA", "MCOR", "PKPK", "HATM", "TOTO", "BCIC", "IATA", "MAHA", "FOLK", "SMBR", "SFAN", "BISI", "BABP", "FUTR", "PSKT", "OASA", "ASLI", "SSTM", "SIPD", "MGRO", "PORT", "DNAR", "MKAP", "BVIC", "BOLT", "PNGO", "IPCC", "BLTZ", "ASGR", "POLI", "DWGL", "BMTR", "GMTD", "WINS", "IFII", "MSJA", "BCAP", "OMRE", "BEEF", "KMTR", "NICE", "BKSW", "PRDA", "DOID", "TRUE", "BLUE", "MDIA", "WOOD", "ACST", "IMJS", "AMAG", "PTPP", "MTMH", "CSRA", "MLIA", "ITMA", "DGWG", "KETR", "NRCA", "DMMX", "SCCO", "INDR", "PNBS", "BRAM", "LUCY", "MBAP", "TPMA", "ELTY", "IPTV", "STRK", "TEBE", "ADHI", "LPGI", "SUNI", "HILL", "PSSI", "MINE", "FAST", "DVLA", "ERAL", "HERO", "KINO", "CSAP", "UCID", "IPCM", "MLPL", "VISI", "PTSN", "BBRM", "SPTO", "FMII", "PPRE", "MAIN", "AYAM", "EURO", "SKLT", "DEPO", "BSBK", "MKTR", "BMHS", "NEST", "PMJS", "BEKS", "KKGI", "DLTA", "AMFG", "RAAM", "TRGU", "ALDO", "GWSA", "PSAT", "GSMF", "CARS", "PADI", "BBLD", "DOOH", "ABDA", "BELL", "NETV", "MERK", "BLOG", "DILD", "TAMU", "CEKA", "ATIC", "TRST", "SONA", "BBSS", "KBLI", "BLES", "CFIN", "JKON", "TIFA", "CAMP", "RANC", "MITI", "TCID", "WSBP", "GZCO", "AISA", "CITY", "JIHD", "LTLS", "IBOS", "ADCP", "ARTA", "BUAH", "INDO", "WOMF", "BEST", "PANS", "TBMS", "ENAK", "RSCH", "BLTA", "JGLE", "MTWI", "ARII", "BTEK", "AREA", "BOLA", "SHID", "ZINC", "ASLC", "PEVE", "LIVE", "MMIX", "GHON", "CHIP", "WIRG", "GDST", "PBRX", "GRIA", "ATAP", "CMPP", "NELY", "RMKO", "NICK", "SMGA", "SPMA", "RELI", "HGII", "BUDI", "SKBM", "COCO", "LEAD", "VOKS", "PDPP", "MHKI", "NFCX", "PTPW", "PJAA", "ZATA", "NIKL", "FUJI", "AMOR", "PANR", "ADMG", "MGNA", "TALF", "AMAN", "BABY", "MTFN", "WTON", "IPOL", "SULI", "PMUI", "KSIX", "PADA", "LFLO", "BPFI", "JECC", "FORU", "HDFA", "KOKA", "BDKR", "DGIK", "WMUU", "PGJO", "RODA", "KDSI", "AXIO", "TIRA", "MDLN", "MOLI", "BEER", "HOKI", "BRNA", "GTBO", "BIKE", "UNIQ", "MPPA", "APEX", "AHAP", "GTRA", "SWID", "IKBI", "HOMI", "HOPE", "EKAD", "VIVA", "UNSP", "PEGE", "PZZA", "SOFA", "IRRA", "ELIT", "WEGE", "SOSS", "AWAN", "SMKL", "GLVA", "TRIS", "KOTA", "GUNA", "HAIS", "UNTD", "CHEK", "LABS", "BOAT", "PNSE", "MREI", "FITT", "KONI", "VTNY", "URBN", "TRON", "IDPR", "WINE", "DART", "PJHB", "GPRA", "MDKI", "KING", "CNKO", "UFOE", "BSML", "VERN", "HALO", "COAL", "APLI", "CRAB", "ESTA", "SURI", "MDRN", "MAXI", "KMDS", "CLPI", "BAYU", "VRNA", "TIRT", "IGAR", "LAPD", "IKPM", "SCNP", "MCAS", "REAL", "RIGS", "CCSI", "GDYR", "GULA", "NASA", "PDES", "CSIS", "GOLD", "PTPS", "CBPE", "SOLA", "TYRE", "ZONE", "BIPP", "BKDP", "ESTI", "IOTF", "LPLI", "VAST", "HYGN", "ASRM", "KREN", "SMLE", "DYAN", "DGNS", "EAST", "HAJJ", "TFAS", "SRSN", "JATI", "KBLM", "DADA", "BMSR", "KOBX", "NAIK", "KBAG", "TARA", "SATU", "ASPR", "ASHA", "YOII", "UVCR", "CRSN", "YPAS", "TRUS", "ATLA", "INTA", "ERTX", "GPSO", "PART", "MUTU", "SAFE", "KLAS", "AKPI", "ITIC", "CGAS", "EMDE", "MICE", "VINS", "ASMI", "HRME", "BPTR", "AMIN", "ASPI", "IKAI", "BINO", "SAGE", "TOSK", "BTON", "OKAS", "MPXL", "WGSH", "ACRO", "AGAR", "INOV", "POLA", "LMPI", "FIRE", "ANDI", "PUDP", "DOSS", "FWCT", "AKSI", "CASH", "KBLV", "PRIM", "NTBK", "DEWI", "OBAT", "ASJT", "ALKA", "ECII", "RELF", "LCKM", "PEHA", "AKKU", "ENZO", "AYLS", "INPS", "BAJA", "WINR", "ASDM", "SDPC", "TRJA", "SAPX", "WAPO", "PTMP", "BAUT", "MEJA", "JMAS", "LPPS", "OBMD", "NPGF", "NZIA", "MANG", "LION", "TAXI", "PTSP", "APII", "CAKK", "NANO", "SLIS", "DFAM", "WOWS", "SDMU", "CINT", "ZYRX", "DKHH", "MRAT", "ABBA", "BOBA", "DIVA", "PURA", "MARI", "PAMG", "BAPI", "CANI", "KOPI", "DSFI", "SMKM", "WEHA", "PURI", "LPIN", "IBFN", "RUIS", "NAYZ", "LAJU", "TRUK", "LAND", "KARW", "HELI", "CHEM", "SEMA", "PSDN", "IPAC", "SNLK", "INTD", "MSKY", "MBTO", "KRYA", "ASBI", "INCI", "TMPO", "GEMA", "ISAP", "YELO", "MERI", "PTIS", "ISEA", "FOOD", "LABA", "MPIX", "RGAS", "DEFI", "KUAS", "SBMA", "EPAC", "RCCC", "KIOS", "INAI", "RBMS", "MIRA", "NASI", "MEDS", "CSMI", "CTTH", "OLIV", "JAST", "IDEA", "OPMS", "PTDU", "PGLI", "FLMC", "BCIP", "INCF", "HDIT", "JAYA", "AIMS", "RUNS", "POLY", "OILS", "BATA", "KOIN", "ICON", "LRNA", "MPOW", "PICO", "IKAN", "TAYS", "ESIP", "KJEN", "LUCK", "TNCA", "KICI", "SOUL", "ARKA", "PLAN", "BMBL", "BAPA", "RICY", "WIDI", "DIGI", "INDX", "HADE", "TAMA", "PCAR", "LOPI", "GRPH", "HBAT", "PIPA", "KLIN", "PPRI", "AEGS", "SPRE", "KAQI", "NINE", "KOCI", "LMAX", "BRRC", "RAFI", "TOOL", "BATR", "AMMS", "KKES", "SICO", "BAIK", "GRPM", "KDTN", "MSIE"
]

# ─────────────────────────────────────────────
#  3. DATABASE JSON
# ─────────────────────────────────────────────
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
        "compare_stocks": st.session_state.get("compare_stocks", []),
        "weekly_stocks": st.session_state.get("weekly_stocks", []),
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# ─────────────────────────────────────────────
#  4. SESSION STATE
# ─────────────────────────────────────────────
saved_data = load_data()

if "watchlist" not in st.session_state:
    st.session_state.watchlist = (
        saved_data["watchlist"]
        if saved_data and "watchlist" in saved_data
        else []
    )
if "compare_stocks" not in st.session_state:
    st.session_state.compare_stocks = (
        saved_data.get("compare_stocks", [])
        if saved_data
        else []
    )
if "weekly_stocks" not in st.session_state:
    st.session_state.weekly_stocks = (
        saved_data.get("weekly_stocks", [])
        if saved_data
        else list(dict.fromkeys(LIST_SAHAM_IHSG[:20]))
    )
if "grid_page" not in st.session_state:
    st.session_state.grid_page = 1
if "grid_tf" not in st.session_state:
    st.session_state.grid_tf = "1mo"

# ─────────────────────────────────────────────
#  5. BACKEND / CACHING  (TTL-only, no duplicates)
# ─────────────────────────────────────────────

PERIOD_MAP = {
    "5d": ("5d",  "1d"),
    "1mo": ("1mo", "1d"),
    "3mo": ("3mo", "1d"),
    "6mo": ("6mo", "1wk"),
    "1y":  ("1y",  "1wk"),
}

@st.cache_data(ttl=600, show_spinner=False)
def get_stock_history_bulk(tickers: tuple, period: str = "1mo"):
    """Bulk-download — returns raw yfinance DataFrame (multi-level cols when >1 ticker)."""
    if not tickers:
        return pd.DataFrame()
    p, iv = PERIOD_MAP.get(period, ("1mo", "1d"))
    try:
        data = yf.download(list(tickers), period=p, interval=iv,
                           group_by="ticker", auto_adjust=True, progress=False)
        return data
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_single_stock(ticker: str, period: str = "1mo"):
    p, iv = PERIOD_MAP.get(period, ("1mo", "1d"))
    try:
        df = yf.download(ticker, period=p, interval=iv,
                         auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False)
def get_stock_info(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        return {
            "pbv": info.get("priceToBook", None),
            "per": info.get("trailingPE", None),
        }
    except Exception:
        return {"pbv": None, "per": None}

@st.cache_data(ttl=600, show_spinner=False)
def get_weekly_recap_data(tickers: tuple):
    start_date = (start_of_week - timedelta(days=7)).strftime("%Y-%m-%d")
    if not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(list(tickers), start=start_date,
                           group_by="ticker", auto_adjust=True, progress=False)
    except Exception:
        return pd.DataFrame()

    all_rows = []
    for t in tickers:
        try:
            if len(tickers) == 1:
                df = data.copy()
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
            else:
                df = data[t].copy()
            df = df.dropna(how="all")
            if df.empty:
                continue
            df["Return"] = df["Close"].pct_change() * 100
            df.index = pd.to_datetime(df.index).date

            last_close = df["Close"].iloc[-1]
            # Format harga: hapus desimal jika bulat
            if isinstance(last_close, (int, float)):
                price_val = int(last_close) if last_close == int(last_close) else round(last_close, 2)
            else:
                price_val = last_close

            row = {
                "Ticker": t,
                "Price": price_val,
                "Today (%)": round(float(df["Return"].iloc[-1]), 2),
            }
            weekly_vals = []
            gain_count = 0
            for i in range(5):
                target = (start_of_week + timedelta(days=i)).date()
                if target in df.index:
                    val = df.loc[target, "Return"]
                    if isinstance(val, pd.Series):
                        val = val.iloc[0]
                    val = float(val)
                    row[days_names[i]] = round(val, 2)
                    weekly_vals.append(val)
                    if val > 0:
                        gain_count += 1
                else:
                    row[days_names[i]] = 0.0
            row["Weekly Acc (%)"] = round(sum(weekly_vals), 2)
            row["Win Rate"] = f"{gain_count}/5"
            all_rows.append(row)
        except Exception:
            continue
    return pd.DataFrame(all_rows)

# ─────────────────────────────────────────────
#  6. HELPER: extract single ticker from bulk
# ─────────────────────────────────────────────
def extract_ticker(data: pd.DataFrame, ticker: str, n_tickers: int) -> pd.DataFrame:
    try:
        if n_tickers == 1:
            df = data.copy()
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
        else:
            df = data[ticker].copy()
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame()

# ─────────────────────────────────────────────
#  7. VISUALISASI
# ─────────────────────────────────────────────
def create_mini_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Kotak kecil, garis harga, MA20 kalau cukup data."""
    color = "#00C805" if df["Close"].iloc[-1] >= df["Close"].iloc[0] else "#FF333A"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        mode="lines", line=dict(color=color, width=1.5), name="Price",
        hovertemplate="%{x|%d %b}<br>%{y:,.0f}<extra></extra>"
    ))
    if len(df) >= 20:
        ma20 = df["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma20,
            mode="lines", line=dict(color="#FFD700", width=1, dash="dot"),
            name="MA20", hoverinfo="skip"
        ))
    fig.update_layout(
        height=160, margin=dict(l=4, r=4, t=28, b=4),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#ccc", size=9),
        title=dict(text=f"<b>{ticker}</b>", font=dict(size=11), x=0.5),
        showlegend=False,
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=8), zeroline=False),
    )
    return fig


def create_compare_chart(df: pd.DataFrame, ticker: str,
                         chart_type: str = "Line",
                         show_ma20: bool = True,
                         show_volume: bool = True,
                         cycle_range: tuple = None) -> go.Figure:
    """Grafik per saham di tab Watch/Compare."""
    rows = 2 if show_volume else 1
    row_h = [0.72, 0.28] if show_volume else [1.0]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, row_heights=row_h)

    # Tentukan data yang ditampilkan (cycle range)
    df_plot = df.copy()
    if cycle_range and len(cycle_range) == 2 and cycle_range[0] and cycle_range[1]:
        mask = (df_plot.index >= pd.to_datetime(cycle_range[0])) & \
               (df_plot.index <= pd.to_datetime(cycle_range[1]))
        df_plot = df_plot[mask]
    if df_plot.empty:
        df_plot = df.copy()

    color_up = "#00C805"
    color_dn = "#FF333A"
    rising = df_plot["Close"].iloc[-1] >= df_plot["Close"].iloc[0] if len(df_plot) > 1 else True
    line_color = color_up if rising else color_dn

    if chart_type == "Candlestick (HL)":
        fig.add_trace(go.Candlestick(
            x=df_plot.index,
            open=df_plot["Open"], high=df_plot["High"],
            low=df_plot["Low"], close=df_plot["Close"],
            increasing_line_color=color_up, decreasing_line_color=color_dn,
            name="Price"
        ), row=1, col=1)
    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(
            x=df_plot.index,
            open=df_plot["Open"], high=df_plot["High"],
            low=df_plot["Low"], close=df_plot["Close"],
            increasing_line_color=color_up, decreasing_line_color=color_dn,
            name="Price"
        ), row=1, col=1)
    else:  # Line
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=df_plot["Close"],
            mode="lines", line=dict(color=line_color, width=2), name="Price",
            hovertemplate="%{x|%d %b %Y}<br>Close: %{y:,.0f}<extra></extra>"
        ), row=1, col=1)

    if show_ma20 and len(df_plot) >= 20:
        ma20 = df_plot["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=df_plot.index, y=ma20,
            mode="lines", line=dict(color="#FFD700", width=1.2, dash="dot"),
            name="MA20"
        ), row=1, col=1)

    if show_volume and "Volume" in df_plot.columns:
        colors = [color_up if c >= o else color_dn
                  for c, o in zip(df_plot["Close"], df_plot["Open"])]
        fig.add_trace(go.Bar(
            x=df_plot.index, y=df_plot["Volume"],
            marker_color=colors, name="Volume", opacity=0.6,
            hovertemplate="%{x|%d %b}<br>Vol: %{y:,.0f}<extra></extra>"
        ), row=2, col=1)

    fig.update_layout(
        height=420, margin=dict(l=8, r=8, t=40, b=8),
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font=dict(color="#ccc"),
        title=dict(text=f"<b>{ticker}</b>", font=dict(size=14), x=0.5),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0.5, xanchor="center"),
        xaxis_rangeslider_visible=False,
        xaxis=dict(showgrid=False),
        xaxis2=dict(showgrid=False) if show_volume else {},
        yaxis=dict(showgrid=True, gridcolor="#1e2530"),
        yaxis2=dict(showgrid=False) if show_volume else {},
    )
    return fig

# ─────────────────────────────────────────────
#  8. JUDUL APLIKASI
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Global dark theme tweak */
    .stApp { background: #0e1117; }
    /* Title */
    .obs-title {
        font-family: 'Georgia', serif;
        font-size: 2rem; font-weight: 700;
        color: #e8e0d0;
        letter-spacing: .15em; margin-bottom: .15rem;
    }
    .obs-sub {
        font-size: .75rem; color: #666; letter-spacing: .2em;
        text-transform: uppercase; margin-bottom: 1rem;
    }
    /* Compact metric cards */
    .metric-card {
        background: #161b22; border: 1px solid #21262d;
        border-radius: 6px; padding: 6px 10px;
        display: inline-block; margin: 2px 4px;
    }
    .metric-label { font-size: .65rem; color: #666; text-transform: uppercase; }
    .metric-value { font-size: 1rem; font-weight: 600; color: #e8e0d0; }
    /* Pagination button */
    div[data-testid="stHorizontalBlock"] button { min-width: 36px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="obs-title">Observation</div>', unsafe_allow_html=True)
st.markdown(f'<div class="obs-sub">Indonesia Stock Market · {today.strftime("%A, %d %B %Y")}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  9. TAB UTAMA  (4 tab saja)
# ─────────────────────────────────────────────
tabs = st.tabs(["📋 List", "🔭 Watch / Compare", "📅 Weekly Recap", "🏆 Win/Loss"])

# ═══════════════════════════════════════════════════════
# TAB 1: LIST
# ═══════════════════════════════════════════════════════
with tabs[0]:

    # ─── Kontrol atas ───────────────────────────────────
    ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([1.6, 1.2, 1.2, 1.2, 1.2])
    with ctrl1:
        tf_options = ["5d", "1mo", "3mo", "6mo", "1y"]
        tf_label   = ["5 Hari", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun"]
        tf_sel = st.selectbox("Timeframe", tf_options,
                              format_func=lambda x: tf_label[tf_options.index(x)],
                              key="grid_tf_sel")
    with ctrl2:
        min_price = st.number_input("Min Harga", value=0, step=100, key="min_price")
    with ctrl3:
        max_price = st.number_input("Max Harga (0=all)", value=0, step=100, key="max_price")
    with ctrl4:
        min_vol = st.number_input("Min Volume (juta)", value=0.0, step=0.1, key="min_vol",
                                  format="%.1f")
    with ctrl5:
        show_ma_grid = st.selectbox("Tampilkan MA", ["Tidak", "MA20", "MA200", "MA20 & MA200"],
                                    key="ma_grid")

    # ─── Pagination ─────────────────────────────────────
    PAGE_SIZE = 50
    total_stocks = len(LIST_SAHAM_IHSG)
    total_pages  = math.ceil(total_stocks / PAGE_SIZE)

    pg_cols = st.columns([1, 4, 1])
    with pg_cols[0]:
        if st.button("◀", key="prev_page", use_container_width=True):
            if st.session_state.grid_page > 1:
                st.session_state.grid_page -= 1
    with pg_cols[1]:
        st.markdown(
            f"<div style='text-align:center;padding:6px 0;color:#888;font-size:.85rem;'>"
            f"Halaman {st.session_state.grid_page} / {total_pages} "
            f"({total_stocks} saham)</div>",
            unsafe_allow_html=True
        )
    with pg_cols[2]:
        if st.button("▶", key="next_page", use_container_width=True):
            if st.session_state.grid_page < total_pages:
                st.session_state.grid_page += 1

    start_idx = (st.session_state.grid_page - 1) * PAGE_SIZE
    end_idx   = start_idx + PAGE_SIZE
    page_tickers = LIST_SAHAM_IHSG[start_idx:end_idx]

    # ─── Download data halaman ini ───────────────────────
    with st.spinner("Memuat data saham..."):
        bulk_data = get_stock_history_bulk(tuple(page_tickers), period=tf_sel)

    # ─── Render grid ────────────────────────────────────
    COLS = 4
    rows_iter = [page_tickers[i:i+COLS] for i in range(0, len(page_tickers), COLS)]

    for row_t in rows_iter:
        grid_cols = st.columns(COLS)
        for col_i, t in enumerate(row_t):
            with grid_cols[col_i]:
                df_g = extract_ticker(bulk_data, t, len(page_tickers))
                if df_g.empty:
                    st.caption(f"⚠ {t}")
                    continue

                # Filter harga
                last_close = float(df_g["Close"].iloc[-1]) if not df_g.empty else 0
                if min_price > 0 and last_close < min_price:
                    continue
                if max_price > 0 and last_close > max_price:
                    continue

                # Filter volume
                last_vol = float(df_g["Volume"].iloc[-1]) if "Volume" in df_g.columns else 0
                if min_vol > 0 and (last_vol / 1_000_000) < min_vol:
                    continue

                # Build chart dengan MA pilihan
                color = "#00C805" if df_g["Close"].iloc[-1] >= df_g["Close"].iloc[0] else "#FF333A"
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_g.index, y=df_g["Close"],
                    mode="lines", line=dict(color=color, width=1.5), name="Price",
                    hovertemplate="%{x|%d %b}<br>%{y:,.0f}<extra></extra>"
                ))

                if "MA20" in show_ma_grid and len(df_g) >= 20:
                    fig.add_trace(go.Scatter(
                        x=df_g.index, y=df_g["Close"].rolling(20).mean(),
                        mode="lines", line=dict(color="#FFD700", width=1, dash="dot"),
                        name="MA20", hoverinfo="skip"
                    ))
                if "MA200" in show_ma_grid and len(df_g) >= 200:
                    fig.add_trace(go.Scatter(
                        x=df_g.index, y=df_g["Close"].rolling(200).mean(),
                        mode="lines", line=dict(color="#00BFFF", width=1, dash="dot"),
                        name="MA200", hoverinfo="skip"
                    ))

                chg = ((df_g["Close"].iloc[-1] / df_g["Close"].iloc[0]) - 1) * 100
                fig.update_layout(
                    height=160, margin=dict(l=4, r=4, t=28, b=4),
                    paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                    font=dict(color="#ccc", size=9),
                    title=dict(
                        text=f"<b>{t.replace('.JK','')}</b> "
                             f"<span style='color:{'#00C805' if chg>=0 else '#FF333A'};"
                             f"font-size:9px'>{chg:+.1f}%</span>",
                        font=dict(size=11), x=0.5
                    ),
                    showlegend=False,
                    xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, tickfont=dict(size=8), zeroline=False),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"gc_{t}_{tf_sel}")

    # Pagination bottom
    pg_cols2 = st.columns([1, 4, 1])
    with pg_cols2[0]:
        if st.button("◀", key="prev_page2", use_container_width=True):
            if st.session_state.grid_page > 1:
                st.session_state.grid_page -= 1
    with pg_cols2[1]:
        st.markdown(
            f"<div style='text-align:center;padding:6px 0;color:#888;font-size:.85rem;'>"
            f"Halaman {st.session_state.grid_page} / {total_pages}</div>",
            unsafe_allow_html=True
        )
    with pg_cols2[2]:
        if st.button("▶", key="next_page2", use_container_width=True):
            if st.session_state.grid_page < total_pages:
                st.session_state.grid_page += 1

# ═══════════════════════════════════════════════════════
# TAB 2: WATCH / COMPARE
# ═══════════════════════════════════════════════════════
with tabs[1]:

    # ─── Search & Manage ────────────────────────────────
    st.markdown("#### Tambah Saham")
    add_col, btn_col = st.columns([4, 1])
    with add_col:
        new_raw = st.text_input(
            "Kode saham (pisahkan koma, misal: BBCA, BBRI, GOTO)",
            key="wc_add_input", placeholder="BBCA, BBRI, GOTO"
        )
    with btn_col:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("➕ Tambah", use_container_width=True, key="wc_add_btn"):
            if new_raw.strip():
                for code in new_raw.split(","):
                    code = code.strip().upper()
                    if code and not code.endswith(".JK"):
                        code += ".JK"
                    if code and code not in st.session_state.compare_stocks:
                        st.session_state.compare_stocks.append(code)
                save_data()
                st.rerun()

    # ─── Chip hapus ─────────────────────────────────────
    if st.session_state.compare_stocks:
        chip_cols = st.columns(min(len(st.session_state.compare_stocks), 8))
        for idx, t in enumerate(list(st.session_state.compare_stocks)):
            with chip_cols[idx % 8]:
                if st.button(f"✕ {t.replace('.JK','')}", key=f"rm_{t}", use_container_width=True):
                    st.session_state.compare_stocks.remove(t)
                    save_data()
                    st.rerun()

        # ─── Kontrol global ──────────────────────────────
        st.divider()
        opt1, opt2, opt3, opt4, opt5 = st.columns([1.5, 1.5, 1, 1, 1])
        with opt1:
            wc_tf_opts = ["5d", "1mo", "3mo", "6mo", "1y"]
            wc_tf_lbl  = ["5 Hari", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun"]
            wc_tf = st.selectbox("Rentang Waktu", wc_tf_opts,
                                 format_func=lambda x: wc_tf_lbl[wc_tf_opts.index(x)],
                                 index=1, key="wc_tf")
        with opt2:
            chart_type = st.selectbox("Jenis Grafik", ["Line", "Candlestick (HL)", "OHLC"],
                                      key="wc_chart_type")
        with opt3:
            show_ma20 = st.checkbox("MA20", value=True, key="wc_ma20")
        with opt4:
            show_vol_wc = st.checkbox("Volume", value=True, key="wc_vol")
        with opt5:
            use_cycle  = st.checkbox("Cycle Range", value=False, key="wc_cycle_on")

        cycle_range = (None, None)
        if use_cycle:
            cyc_c1, cyc_c2 = st.columns(2)
            with cyc_c1:
                cyc_from = st.date_input("Cycle Dari", key="wc_cyc_from",
                                         value=today - timedelta(days=90))
            with cyc_c2:
                cyc_to   = st.date_input("Cycle Sampai", key="wc_cyc_to",
                                         value=today)
            cycle_range = (cyc_from, cyc_to)

        st.divider()

        # ─── Render tiap saham ────────────────────────────
        for t in st.session_state.compare_stocks:
            df_c = get_single_stock(t, period=wc_tf)
            if df_c.empty:
                st.warning(f"Data tidak tersedia: {t}")
                continue

            # PBV & PER
            info = get_stock_info(t)
            lc = float(df_c["Close"].iloc[-1])
            pbv_txt = f"{info['pbv']:.2f}x" if info["pbv"] else "N/A"
            per_txt = f"{info['per']:.1f}x" if info["per"] else "N/A"

            m1, m2, m3 = st.columns([2, 1, 1])
            with m1:
                chg_c = ((df_c["Close"].iloc[-1] / df_c["Close"].iloc[0]) - 1) * 100
                chg_color = "#00C805" if chg_c >= 0 else "#FF333A"
                price_fmt = int(lc) if lc == int(lc) else round(lc, 2)
                st.markdown(
                    f"**{t}** &nbsp;&nbsp;"
                    f"<span style='font-size:1.1rem;color:#e8e0d0'>{price_fmt:,}</span> &nbsp;"
                    f"<span style='color:{chg_color}'>{chg_c:+.1f}%</span>",
                    unsafe_allow_html=True
                )
            with m2:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<div class='metric-label'>PBV</div>"
                    f"<div class='metric-value'>{pbv_txt}</div></div>",
                    unsafe_allow_html=True
                )
            with m3:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<div class='metric-label'>PER</div>"
                    f"<div class='metric-value'>{per_txt}</div></div>",
                    unsafe_allow_html=True
                )

            fig_c = create_compare_chart(df_c, t,
                                         chart_type=chart_type,
                                         show_ma20=show_ma20,
                                         show_volume=show_vol_wc,
                                         cycle_range=cycle_range if use_cycle else None)
            st.plotly_chart(fig_c, use_container_width=True, key=f"wc_{t}_{wc_tf}")
            st.divider()

    else:
        st.info("Belum ada saham. Tambahkan kode saham di atas (contoh: BBCA, BBRI).")

# ═══════════════════════════════════════════════════════
# TAB 3: WEEKLY RECAP
# ═══════════════════════════════════════════════════════
with tabs[2]:

    # ─── Cari & Kelola saham ────────────────────────────
    wkc1, wkc2 = st.columns([4, 1])
    with wkc1:
        wk_add = st.text_input("Tambah saham ke recap (koma-separated)",
                               key="wk_add_input", placeholder="BBCA, TLKM")
    with wkc2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("➕ Tambah", key="wk_add_btn", use_container_width=True):
            if wk_add.strip():
                for code in wk_add.split(","):
                    code = code.strip().upper()
                    if code and not code.endswith(".JK"):
                        code += ".JK"
                    if code and code not in st.session_state.weekly_stocks:
                        st.session_state.weekly_stocks.append(code)
                save_data()
                st.rerun()

    col_reset, col_del = st.columns([1, 3])
    with col_reset:
        if st.button("🔄 Reset ke Default", key="wk_reset"):
            st.session_state.weekly_stocks = list(dict.fromkeys(LIST_SAHAM_IHSG[:20]))
            save_data()
            st.rerun()

    # Chip hapus saham
    if st.session_state.weekly_stocks:
        chip_cols_wk = st.columns(min(len(st.session_state.weekly_stocks), 10))
        for idx, t in enumerate(list(st.session_state.weekly_stocks)):
            with chip_cols_wk[idx % 10]:
                if st.button(f"✕ {t.replace('.JK','')}", key=f"wkrm_{t}", use_container_width=True):
                    st.session_state.weekly_stocks.remove(t)
                    save_data()
                    st.rerun()

    st.divider()

    if st.session_state.weekly_stocks:
        with st.spinner("Menghitung weekly return..."):
            df_weekly = get_weekly_recap_data(tuple(st.session_state.weekly_stocks))

        if not df_weekly.empty:
            # Format kolom Price — tidak tampilkan .0000
            def fmt_price(v):
                if isinstance(v, (int, float)):
                    return f"{int(v):,}" if v == int(v) else f"{v:,.2f}"
                return str(v)

            def style_returns(val):
                if isinstance(val, (int, float)):
                    if val > 0:
                        return "color: #00C805; font-weight:600"
                    elif val < 0:
                        return "color: #FF333A; font-weight:600"
                return ""

            return_cols = ["Today (%)", "Monday", "Tuesday", "Wednesday",
                           "Thursday", "Friday", "Weekly Acc (%)"]

            styled = (df_weekly.style
                      .format({"Price": fmt_price})
                      .applymap(style_returns, subset=return_cols)
                      .format("{:+.2f}%", subset=return_cols)
                      )
            st.dataframe(styled, use_container_width=True, hide_index=True)
        else:
            st.warning("Data belum tersedia (pasar mungkin belum buka hari ini).")
    else:
        st.info("Tambahkan saham untuk melihat weekly recap.")

# ═══════════════════════════════════════════════════════
# TAB 4: WIN/LOSS
# ═══════════════════════════════════════════════════════
with tabs[3]:

    wl_in = st.text_area("Masukkan kode saham (koma-separated):",
                         value="BBCA.JK, GOTO.JK, BBRI.JK", key="wl_input")
    if st.button("Hitung Statistik", key="wl_calc"):
        wl_list = []
        for x in wl_in.split(","):
            code = x.strip().upper()
            if code and not code.endswith(".JK"):
                code += ".JK"
            if code:
                wl_list.append(code)

        with st.spinner("Mengambil data..."):
            data_wl = get_stock_history_bulk(tuple(wl_list), period="3mo")

        for t in wl_list:
            df_wl = extract_ticker(data_wl, t, len(wl_list))
            if df_wl.empty:
                st.warning(f"Data tidak tersedia: {t}")
                continue

            df_wl = df_wl.copy()
            df_wl["Change"] = df_wl["Close"].pct_change() * 100
            df_30 = df_wl.tail(30).sort_index(ascending=False)

            win_count = len(df_30[df_30["Change"] > 0])
            loss_count = len(df_30[df_30["Change"] < 0])
            win_rate = (win_count / len(df_30)) * 100

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t, "Win/Loss")
            c2.metric("Win Rate", f"{win_rate:.1f}%")
            c3.metric("Win", str(win_count))
            c4.metric("Loss", str(loss_count))

            with st.expander(f"📋 30 Hari Terakhir — {t}"):
                def bg_color(val):
                    if isinstance(val, (int, float)):
                        if val > 0: return "background-color:#0d2b0d;color:#00C805"
                        elif val < 0: return "background-color:#2b0d0d;color:#FF333A"
                    return ""

                def fmt_close(v):
                    if isinstance(v, (int, float)):
                        return f"{int(v):,}" if v == int(v) else f"{v:,.2f}"
                    return str(v)

                styled_wl = (df_30[["Close", "Change"]]
                             .style
                             .applymap(bg_color, subset=["Change"])
                             .format({"Close": fmt_close, "Change": "{:+.2f}%"})
                             )
                st.dataframe(styled_wl, use_container_width=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown(
    f"<div style='text-align:center;color:#444;font-size:.72rem;margin-top:2rem;'>"
    f"Observation · Data by Yahoo Finance · "
    f"{today.strftime('%Y-%m-%d %H:%M')}</div>",
    unsafe_allow_html=True
)
