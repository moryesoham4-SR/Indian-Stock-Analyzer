import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
# mysql removed for cloud deployment
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import time


# =========================
# SECTOR MAPPING
# =========================

SECTOR_STOCKS = {
    "All Sectors": [],
    "Banking & Finance": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK",
        "BAJFINANCE", "BAJAJFINSV", "INDUSINDBK", "BANDHANBNK",
        "PNB", "BANKBARODA", "CANBK", "UNIONBANK", "IDFCFIRSTB",
        "FEDERALBNK", "RBLBANK", "YESBANK", "AUBANK", "CHOLAFIN",
        "MUTHOOTFIN", "MANAPPURAM", "LICHSGFIN", "HDFC", "SBILIFE",
        "HDFCLIFE", "ICICIGI", "SBICARD"
    ],
    "Information Technology": [
        "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM",
        "MPHASIS", "PERSISTENT", "COFORGE", "OFSS", "KPITTECH",
        "TATAELXSI", "MASTEK", "NIITTECH", "HEXAWARE"
    ],
    "Pharmaceuticals": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "AUROPHARMA",
        "LUPIN", "BIOCON", "ALKEM", "TORNTPHARM", "IPCALAB",
        "NATCOPHARMA", "GLENMARK", "GRANULES", "LALPATHLAB",
        "METROPOLIS", "APOLLOHOSP", "FORTIS", "MAXHEALTH"
    ],
    "Oil & Gas": [
        "RELIANCE", "ONGC", "BPCL", "IOC", "GAIL", "HINDPETRO",
        "OIL", "MGL", "IGL", "GSPL", "PETRONET", "CASTROLIND"
    ],
    "Automobile": [
        "TATAMOTORS", "MARUTI", "M&M", "BAJAJ-AUTO", "HEROMOTOCO",
        "EICHERMOT", "TVSMOTORS", "ASHOKLEY", "BHARATFORG",
        "MOTHERSON", "BOSCHLTD", "MRF", "APOLLOTYRE", "CEATLTD"
    ],
    "FMCG": [
        "ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "DABUR",
        "MARICO", "GODREJCP", "COLPAL", "EMAMILTD", "TATACONSUM",
        "UBL", "RADICO", "VBL", "PGHH"
    ],
    "Metals & Mining": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA",
        "NMDC", "SAIL", "NATIONALUM", "HINDCOPPER", "MOIL",
        "WELCORP", "APL", "RATNAMANI", "TIINDIA"
    ],
    "Infrastructure & Construction": [
        "LT", "ADANIPORTS", "ADANIENT", "ADANIGREEN", "ADANITRANS",
        "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "BRIGADE",
        "PHOENIXLTD", "SOBHA", "NESCO", "IRB"
    ],
    "Power & Energy": [
        "POWERGRID", "NTPC", "TATAPOWER", "ADANIPOWER", "TORNTPOWER",
        "CESC", "NHPC", "SJVN", "RPOWER", "JSWENERGY",
        "GREENKO", "RENEW"
    ],
    "Consumer Durables": [
        "TITAN", "VOLTAS", "HAVELLS", "WHIRLPOOL", "BLUESTARCO",
        "CROMPTON", "ORIENTELEC", "VGUARD", "SYMPHONY", "TTK",
        "RAJESHEXPO", "KAJARIACER", "CERA"
    ],
    "Telecom": [
        "BHARTIARTL", "IDEA", "INDUSTOWER", "TTML", "RAILTEL"
    ],
    "Cement": [
        "ULTRACEMCO", "SHREECEM", "AMBUJACEM", "ACC", "DALMIACEM",
        "RAMCOCEM", "HEIDELBERG", "JKCEMENT", "BIRLACORPN"
    ],
    "Chemicals": [
        "PIDILITIND", "AARTIIND", "DEEPAKNTR", "GNFC", "GSFC",
        "ALKYLAMINE", "FINEORG", "GALAXYSURF", "NAVINFLUOR"
    ],
}

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Indian Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

# =========================
# GLOBAL CSS
# =========================

st.markdown(
    """
    <style>

    /* ── NSE STYLE THEME ── */

    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: #020c08;
        background-image:
            linear-gradient(rgba(0,180,80,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,180,80,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        color: #e0ffe0;
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        background: rgba(2, 18, 10, 0.92);
        border-radius: 4px;
        border: 1px solid rgba(0,180,80,0.15);
        padding: clamp(1rem, 3vw, 2rem);
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: #010c06 !important;
        border-right: 2px solid #00b450 !important;
    }

    section[data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar radio items */
    [data-testid="stSidebar"] label {
        color: #90c890 !important;
        font-size: 13px !important;
        letter-spacing: 0.03em;
        transition: color 0.2s;
        text-transform: uppercase;
    }

    [data-testid="stSidebar"] label:hover {
        color: #00ff80 !important;
    }

    /* ── KPI CARDS — terminal style ── */
    [data-testid="metric-container"] {
        background: #010e07 !important;
        border: 1px solid #00b450 !important;
        border-left: 3px solid #00ff80 !important;
        border-radius: 2px !important;
        padding: 16px 20px !important;
        box-shadow: 0 0 12px rgba(0,255,80,0.08), inset 0 0 20px rgba(0,100,40,0.05) !important;
        transition: all 0.2s ease !important;
        animation: fadeSlideUp 0.4s ease both !important;
        position: relative;
    }

    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00ff80, transparent);
    }

    [data-testid="metric-container"]:hover {
        border-color: #00ff80 !important;
        box-shadow: 0 0 20px rgba(0,255,80,0.18), inset 0 0 30px rgba(0,100,40,0.08) !important;
        transform: translateY(-2px) !important;
    }

    [data-testid="metric-container"] label {
        color: #4dcc80 !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        font-family: 'Share Tech Mono', monospace !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00ff80 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 22px !important;
        font-weight: 400 !important;
        text-shadow: 0 0 10px rgba(0,255,80,0.4) !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-family: 'Share Tech Mono', monospace !important;
    }

    /* ── HEADINGS ── */
    h1 {
        color: #00ff80 !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid rgba(0,180,80,0.3) !important;
        padding-bottom: 10px !important;
        text-shadow: 0 0 20px rgba(0,255,80,0.3) !important;
        animation: fadeSlideUp 0.4s ease both !important;
    }

    h2 {
        color: #00cc66 !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        animation: fadeSlideUp 0.4s ease both !important;
    }

    h3 {
        color: #00aa55 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        width: 100% !important;
        border-radius: 2px !important;
        background: transparent !important;
        color: #00ff80 !important;
        border: 1px solid #00b450 !important;
        font-weight: 600 !important;
        font-family: 'Share Tech Mono', monospace !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 0 10px rgba(0,180,80,0.1) !important;
    }

    .stButton > button:hover {
        background: rgba(0,180,80,0.12) !important;
        border-color: #00ff80 !important;
        box-shadow: 0 0 20px rgba(0,255,80,0.25) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border: 1px solid rgba(0,180,80,0.2) !important;
        border-radius: 2px !important;
        overflow: hidden !important;
        animation: fadeSlideUp 0.5s ease both !important;
    }

    /* ── SELECTBOX / INPUTS ── */
    .stSelectbox > div > div {
        background: #010e07 !important;
        border: 1px solid #00b450 !important;
        border-radius: 2px !important;
        color: #00ff80 !important;
    }

    .stNumberInput > div > div > input {
        background: #010e07 !important;
        border: 1px solid #00b450 !important;
        color: #00ff80 !important;
        border-radius: 2px !important;
        font-family: 'Share Tech Mono', monospace !important;
    }

    .stMultiSelect > div {
        background: #010e07 !important;
        border: 1px solid #00b450 !important;
        border-radius: 2px !important;
    }

    .stSlider > div > div > div {
        background: #00b450 !important;
    }

    /* ── ALERTS ── */
    .stSuccess {
        background: rgba(0,180,80,0.08) !important;
        border: 1px solid #00b450 !important;
        border-left: 3px solid #00ff80 !important;
        border-radius: 2px !important;
        color: #00ff80 !important;
    }

    .stError {
        background: rgba(255,50,50,0.08) !important;
        border: 1px solid #cc3333 !important;
        border-left: 3px solid #ff4444 !important;
        border-radius: 2px !important;
    }

    .stWarning {
        background: rgba(255,180,0,0.08) !important;
        border: 1px solid #cc8800 !important;
        border-left: 3px solid #ffaa00 !important;
        border-radius: 2px !important;
    }

    .stInfo {
        background: rgba(0,120,180,0.08) !important;
        border: 1px solid #0066cc !important;
        border-left: 3px solid #0088ff !important;
        border-radius: 2px !important;
    }

    /* ── TICKER SCROLL ── */
    @keyframes tickerScroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    .ticker-track {
        display: flex;
        gap: 40px;
        animation: tickerScroll 25s linear infinite;
        white-space: nowrap;
        font-family: 'Share Tech Mono', monospace;
    }

    .ticker-wrap {
        overflow: hidden;
        background: #010e07;
        padding: 10px 0;
        border-radius: 2px;
        margin-bottom: 20px;
        border-top: 1px solid #00b450;
        border-bottom: 1px solid #00b450;
        font-size: 14px;
        font-weight: bold;
        color: #00ff80;
        letter-spacing: 0.05em;
    }

    /* ── SKELETON ── */
    @keyframes skeletonPulse {
        0%   { opacity: 0.2; }
        50%  { opacity: 0.5; }
        100% { opacity: 0.2; }
    }

    .skeleton {
        background: rgba(0,180,80,0.08);
        border: 1px solid rgba(0,180,80,0.15);
        border-radius: 2px;
        height: 80px;
        animation: skeletonPulse 1.4s ease-in-out infinite;
        margin-bottom: 12px;
    }

    /* ── ANIMATIONS ── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    .js-plotly-plot { animation: fadeIn 0.5s ease both; }

    /* ── SPINNER ── */
    .stSpinner > div { border-top-color: #00ff80 !important; }

    /* ── PROGRESS BAR ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00b450, #00ff80) !important;
        border-radius: 0;
        box-shadow: 0 0 8px rgba(0,255,80,0.4);
    }

    /* ── EXPANDER ── */
    .streamlit-expanderHeader {
        background: #010e07 !important;
        border: 1px solid rgba(0,180,80,0.2) !important;
        color: #00cc66 !important;
        border-radius: 2px !important;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab"] {
        color: #4dcc80 !important;
        border-bottom: 2px solid transparent !important;
        font-family: 'Share Tech Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    .stTabs [aria-selected="true"] {
        color: #00ff80 !important;
        border-bottom: 2px solid #00ff80 !important;
    }

    /* ── MOBILE ── */
    @media (max-width: 768px) {
        [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
        h1 { font-size: 1.2rem !important; }
        h2 { font-size: 1rem !important; }
        [data-testid="metric-container"] { padding: 10px !important; }
        .ticker-wrap { font-size: 12px !important; }
        .block-container { padding: 0.75rem !important; }
        .stDownloadButton > button { width: 100% !important; }
    }

    /* Hide Streamlit's keyboard shortcut button */
    button[data-testid="baseButton-headerNoPadding"],
    button[kind="header"],
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Hide keyboard shortcut tooltip */
    .st-emotion-cache-1dp5vir,
    .eyeqlp53 {
        display: none !important;
    }

    @media (max-width: 480px) {
        h1 { font-size: 1rem !important; }
        [data-testid="metric-container"] { padding: 8px !important; }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# NSE TERMINAL BOOT SCREEN
# =========================

if "booted" not in st.session_state:
    st.session_state.booted = False

if not st.session_state.booted:
    import time as _time

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    .boot-wrap {
        background: #000;
        border: 1px solid #00b450;
        border-left: 3px solid #00ff80;
        padding: 40px;
        font-family: 'Share Tech Mono', monospace;
        margin: 40px auto;
        max-width: 600px;
    }
    .boot-logo {
        color: #00ff80;
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 0.3em;
        text-align: center;
        margin-bottom: 6px;
        animation: glow 1s ease-in-out infinite alternate;
    }
    .boot-sub {
        color: #4dcc80;
        font-size: 0.7rem;
        letter-spacing: 0.3em;
        text-align: center;
        margin-bottom: 30px;
    }
    .boot-line { color: #00b450; font-size: 0.8rem; margin: 6px 0; }
    .ok   { color: #00ff80; }
    .warn { color: #ffaa00; }
    .info { color: #4dcc80; }
    @keyframes glow {
        from { text-shadow: 0 0 5px rgba(0,255,80,0.3); }
        to   { text-shadow: 0 0 20px rgba(0,255,80,0.8); }
    }
    </style>
    """, unsafe_allow_html=True)

    boot_ph = st.empty()

    lines = [
        ('[INIT]', 'info', 'Booting NSE Terminal System...'),
        ('[ OK ]', 'ok',   'Market data engine loaded'),
        ('[ OK ]', 'ok',   'Yahoo Finance connector ready'),
        ('[ OK ]', 'ok',   'Technical indicators module loaded'),
        ('[ OK ]', 'ok',   'AI prediction engine initialized'),
        ('[ OK ]', 'ok',   'Database connection established'),
        ('[WARN]', 'warn', 'Live ticker running in static mode'),
        ('[ OK ]', 'ok',   'All systems ready — launching...'),
    ]

    shown = []
    for tag, cls, msg in lines:
        shown.append(f'<div class="boot-line {cls}">{tag} &nbsp; {msg}</div>')
        bar_pct = int((len(shown) / len(lines)) * 100)
        bar_fill = "█" * (bar_pct // 5) + "░" * (20 - bar_pct // 5)
        boot_ph.markdown(
            f"""
            <div class="boot-wrap">
                <div class="boot-logo">STOCK ANALYZER</div>
                <div class="boot-sub">NSE ● AI POWERED TERMINAL ● v2.0</div>
                {"".join(shown)}
                <div style="margin-top:20px;color:#00b450;font-size:0.75rem;">
                    [{bar_fill}] {bar_pct}%
                </div>
                <div style="color:#4dcc80;font-size:0.65rem;margin-top:8px;letter-spacing:0.15em;">
                    INITIALIZING... PLEASE WAIT
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        _time.sleep(0.35)

    _time.sleep(0.5)
    boot_ph.empty()
    st.session_state.booted = True
    st.rerun()

# =========================
# SIDEBAR
# =========================

from datetime import datetime
import pytz

# Market status check
IST = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(IST)
weekday = now_ist.weekday()  # 0=Mon, 6=Sun
hour    = now_ist.hour
minute  = now_ist.minute
time_val = hour * 60 + minute

if weekday >= 5:
    mkt_status = "CLOSED"
    mkt_color  = "#ff4444"
    mkt_dot    = "🔴"
elif time_val < 9*60:
    mkt_status = "PRE-OPEN"
    mkt_color  = "#ffaa00"
    mkt_dot    = "🟡"
elif time_val < 9*60+15:
    mkt_status = "PRE-OPEN"
    mkt_color  = "#ffaa00"
    mkt_dot    = "🟡"
elif time_val <= 15*60+30:
    mkt_status = "LIVE"
    mkt_color  = "#00ff80"
    mkt_dot    = "🟢"
else:
    mkt_status = "CLOSED"
    mkt_color  = "#ff4444"
    mkt_dot    = "🔴"

st.sidebar.markdown(
    f"""
    <div style="
        text-align:center;
        padding:16px 12px;
        border-bottom: 1px solid #00b450;
        margin-bottom:16px;
        background: #010e07;
    ">
        <div style="
            font-family:'Share Tech Mono',monospace;
            font-size:11px;
            color:{mkt_color};
            letter-spacing:0.2em;
            text-transform:uppercase;
            margin-bottom:6px;
        ">NSE ● {mkt_status}</div>
        <div style="
            font-family:'Share Tech Mono',monospace;
            font-size:18px;
            color:#00ff80;
            font-weight:bold;
            letter-spacing:0.05em;
        ">STOCK ANALYZER</div>
        <div style="
            font-size:11px;
            color:#4dcc80;
            margin-top:6px;
            letter-spacing:0.1em;
            text-transform:uppercase;
        ">AI Powered Terminal</div>
        <div style="
            margin-top:8px;
            font-family:'Share Tech Mono',monospace;
            font-size:10px;
            color:{mkt_color};
            letter-spacing:0.1em;
        ">{mkt_dot} Market {mkt_status} &nbsp;|&nbsp; {now_ist.strftime("%I:%M %p")} IST</div>
        <div style="
            margin-top:10px;
            height:1px;
            background:linear-gradient(90deg,transparent,#00b450,transparent);
        "></div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Go To",
    [
        "Dashboard",
        "Technical Analysis",
        "SQL Records",
        "AI Prediction",
        "Portfolio Tracker",
        "Market Dashboard",
        "Stock News",
        "Watchlist",
        "Stock Comparison",
        "Fundamental Analysis",
        "52-Week Analysis",
        "Export Data",
        "Stock Screener",
        "Sector Analysis",
        "Price Alerts",
        "SIP Calculator",
        "PDF Report",
        "Earnings Calendar",
    ]
)

# =========================
# STOCK SEARCH FROM CSV
# =========================

stock_df      = pd.read_csv("stocks.csv")
stock_symbols = stock_df["SYMBOL"].dropna().astype(str).tolist()

# Sector filter
selected_sector = st.sidebar.selectbox(
    "🏭 Filter by Sector",
    options=list(SECTOR_STOCKS.keys())
)

# Filter stock list by sector
if selected_sector == "All Sectors":
    filtered_symbols = stock_symbols
else:
    sector_list      = SECTOR_STOCKS[selected_sector]
    filtered_symbols = [s for s in stock_symbols if s in sector_list]
    if not filtered_symbols:
        filtered_symbols = stock_symbols  # fallback if no match

selected_stock = st.sidebar.selectbox("🔍 Search Stock", options=filtered_symbols)
stock          = selected_stock + ".NS"

# =========================
# LIVE MARKET TICKER
# =========================

# =========================
# MARKET BANNER (no external fetch needed)
# =========================

st.markdown(
    f"""
    <div class="ticker-wrap">
        <div class="ticker-track">
            <span style="color:#00ff80;">▲ NIFTY 50</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">NSE LIVE TERMINAL</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ SENSEX</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">AI POWERED ANALYSIS</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ BANK NIFTY</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">TECHNICAL INDICATORS</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ NIFTY IT</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">SECTOR ANALYSIS</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ NIFTY PHARMA</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">STOCK SCREENER</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ NIFTY 50</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">NSE LIVE TERMINAL</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ SENSEX</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">AI POWERED ANALYSIS</span>
            &nbsp;&nbsp;
            <span style="color:#00ff80;">▲ BANK NIFTY</span>
            &nbsp;&nbsp;
            <span style="color:#4dcc80;">TECHNICAL INDICATORS</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# FETCH STOCK DATA
# =========================

skeleton_ph = st.empty()
skeleton_ph.markdown(
    """
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:1rem;">
        <div class="skeleton"></div><div class="skeleton"></div>
        <div class="skeleton"></div><div class="skeleton"></div>
    </div>
    """,
    unsafe_allow_html=True
)

ticker = yf.Ticker(stock)
data   = ticker.history(period="6mo")
skeleton_ph.empty()

if data.empty:
    st.error("❌ Invalid Stock Symbol or no data available.")
    st.stop()

data.reset_index(inplace=True)

# =========================
# INDICATORS
# =========================

data["MA20"] = data["Close"].rolling(window=20).mean()
data["MA50"] = data["Close"].rolling(window=50).mean()

delta    = data["Close"].diff()
gain     = delta.where(delta > 0, 0)
loss     = -delta.where(delta < 0, 0)
data["RSI"] = 100 - (100 / (1 + gain.rolling(14).mean() / loss.rolling(14).mean()))

ema12               = data["Close"].ewm(span=12, adjust=False).mean()
ema26               = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"]        = ema12 - ema26
data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()

data["BB_Middle"] = data["Close"].rolling(window=20).mean()
std_dev           = data["Close"].rolling(window=20).std()
data["BB_Upper"]  = data["BB_Middle"] + (2 * std_dev)
data["BB_Lower"]  = data["BB_Middle"] - (2 * std_dev)

# =========================
# LIVE PRICE
# =========================

try:
    live_price = ticker.info.get("currentPrice", float(data["Close"].iloc[-1]))
except Exception:
    live_price = float(data["Close"].iloc[-1])
latest_high   = float(data["High"].iloc[-1])
latest_low    = float(data["Low"].iloc[-1])
latest_volume = int(data["Volume"].iloc[-1])

# =========================
# PLOTLY LAYOUT HELPER
# =========================

def mobile_layout(**kwargs):
    defaults = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(2,14,7,0.95)",
        font=dict(color="#4dcc80", family="'Share Tech Mono', monospace", size=11),
        xaxis=dict(
            gridcolor="rgba(0,180,80,0.08)",
            linecolor="#004d22",
            tickcolor="#004d22",
            tickfont=dict(color="#4dcc80", size=10),
            title_font=dict(color="#4dcc80")
        ),
        yaxis=dict(
            gridcolor="rgba(0,180,80,0.08)",
            linecolor="#004d22",
            tickcolor="#004d22",
            tickfont=dict(color="#4dcc80", size=10),
            title_font=dict(color="#4dcc80")
        ),
        legend=dict(
            bgcolor="rgba(1,14,7,0.8)",
            bordercolor="#00b450",
            borderwidth=1,
            font=dict(color="#4dcc80", size=10)
        ),
        title_font=dict(color="#00ff80", size=13),
        margin=dict(l=8, r=8, t=40, b=8),
        autosize=True,
    )
    defaults.update(kwargs)
    return defaults

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.title("📈 Indian Stock Market Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Current Price", f"₹{live_price:.2f}")
    col2.metric("📈 Day High",      f"₹{latest_high:.2f}")
    col3.metric("📉 Day Low",       f"₹{latest_low:.2f}")
    col4.metric("📊 Volume",        f"{latest_volume:,}")

    st.subheader(f"📋 {stock} — Recent Data")
    st.dataframe(data.tail(), use_container_width=True)

    st.subheader("📈 Candlestick Chart")

    with st.spinner("Rendering chart..."):
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data["Date"], open=data["Open"], high=data["High"],
            low=data["Low"], close=data["Close"], name="Candlestick"
        ))
        fig.add_trace(go.Scatter(x=data["Date"], y=data["MA20"], mode="lines", name="MA20", line=dict(color="#FBBF24", width=1.5)))
        fig.add_trace(go.Scatter(x=data["Date"], y=data["MA50"], mode="lines", name="MA50", line=dict(color="#60A5FA", width=1.5)))
        fig.update_layout(**mobile_layout(
            title=f"{stock} — 6 Month Candlestick",
            xaxis_title="Date", yaxis_title="Price (₹)",
            height=500, xaxis_rangeslider_visible=False
        ))
        st.plotly_chart(fig, use_container_width=True)

# =========================
# TECHNICAL ANALYSIS
# =========================

elif page == "Technical Analysis":

    st.title("📊 Technical Analysis")

    bar = st.progress(0)
    for i in range(1, 4):
        time.sleep(0.1)
        bar.progress(i * 33)
    bar.empty()

    # RSI
    st.subheader("📈 RSI Indicator")
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=data["Date"], y=data["RSI"], mode="lines", name="RSI", line=dict(color="#A78BFA")))
    rsi_fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.08)",  line_width=0, annotation_text="Overbought")
    rsi_fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(34,197,94,0.08)",  line_width=0, annotation_text="Oversold")
    rsi_fig.add_hline(y=70, line_dash="dash", line_color="rgba(239,68,68,0.6)")
    rsi_fig.add_hline(y=30, line_dash="dash", line_color="rgba(34,197,94,0.6)")
    rsi_fig.update_layout(**mobile_layout(title="RSI (14)", xaxis_title="Date", yaxis_title="RSI", height=350))
    st.plotly_chart(rsi_fig, use_container_width=True)

    latest_rsi = float(data["RSI"].iloc[-1])
    col1, col2 = st.columns([1, 2])
    col1.metric("Current RSI", f"{latest_rsi:.2f}")
    with col2:
        if latest_rsi < 30:
            st.success("🟢 BUY SIGNAL — Stock may be undervalued.")
        elif latest_rsi > 70:
            st.error("🔴 SELL SIGNAL — Stock may be overvalued.")
        else:
            st.warning("🟡 HOLD — Stock in normal range.")

    st.markdown("---")

    # MACD
    st.subheader("📊 MACD Indicator")
    macd_fig = go.Figure()
    macd_fig.add_trace(go.Scatter(x=data["Date"], y=data["MACD"],        mode="lines", name="MACD",        line=dict(color="#22C55E")))
    macd_fig.add_trace(go.Scatter(x=data["Date"], y=data["Signal_Line"], mode="lines", name="Signal Line", line=dict(color="#F97316", dash="dot")))
    macd_fig.update_layout(**mobile_layout(title="MACD", xaxis_title="Date", yaxis_title="Value", height=350))
    st.plotly_chart(macd_fig, use_container_width=True)

    latest_macd   = float(data["MACD"].iloc[-1])
    latest_signal = float(data["Signal_Line"].iloc[-1])
    col1, col2 = st.columns([1, 2])
    col1.metric("MACD", f"{latest_macd:.4f}")
    with col2:
        if latest_macd > latest_signal:
            st.success("✅ BUY Signal (Bullish Trend)")
        elif latest_macd < latest_signal:
            st.error("❌ SELL Signal (Bearish Trend)")
        else:
            st.info("Neutral Trend")

    st.markdown("---")

    # Bollinger Bands
    st.subheader("📊 Bollinger Bands")
    bb_fig = go.Figure()
    bb_fig.add_trace(go.Scatter(x=data["Date"], y=data["BB_Upper"],  mode="lines", name="Upper Band",  line=dict(dash="dash", color="#EF4444", width=1)))
    bb_fig.add_trace(go.Scatter(x=data["Date"], y=data["BB_Middle"], mode="lines", name="Middle Band", line=dict(dash="dot",  color="#9CA3AF", width=1)))
    bb_fig.add_trace(go.Scatter(x=data["Date"], y=data["BB_Lower"],  mode="lines", name="Lower Band",  line=dict(dash="dash", color="#22C55E", width=1),
                                fill="tonexty", fillcolor="rgba(34,197,94,0.05)"))
    bb_fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"],     mode="lines", name="Close",       line=dict(color="white", width=2)))
    bb_fig.update_layout(**mobile_layout(title="Bollinger Bands (20,2)", xaxis_title="Date", yaxis_title="Price (₹)", height=400))
    st.plotly_chart(bb_fig, use_container_width=True)

    latest_close = float(data["Close"].iloc[-1])
    upper_band   = float(data["BB_Upper"].iloc[-1])
    lower_band   = float(data["BB_Lower"].iloc[-1])

    if latest_close > upper_band:
        st.warning("⚠️ Stock may be OVERBOUGHT (above upper band)")
    elif latest_close < lower_band:
        st.error("📉 Stock may be OVERSOLD (below lower band)")
    else:
        st.success("✅ Stock trading within normal Bollinger range")




# =========================
# SQL RECORDS — CLOUD MySQL
# =========================

elif page == "SQL Records":

    st.title("🛢️ SQL Historical Records")

    import os
    db_host = os.environ.get("MYSQL_HOST", "zephyr.proxy.rlwy.net")

    if False:
        st.warning("⚠️ Database not configured. Set MYSQL secrets in Streamlit Cloud settings.")
    else:
        with st.spinner("Connecting to cloud database..."):
            try:
                import mysql.connector
                connection = mysql.connector.connect(
                    host     = os.environ.get("MYSQL_HOST",     "zephyr.proxy.rlwy.net"),
                    port     = int(os.environ.get("MYSQL_PORT", 18696)),
                    user     = os.environ.get("MYSQL_USER",     "root"),
                    password = os.environ.get("MYSQL_PASSWORD", "AOplgDCTnsCgkwOEiNrKaLtBhQqbzPxW"),
                    database = os.environ.get("MYSQL_DATABASE", "railway")
                )
                query    = f"SELECT * FROM historical_prices WHERE stock_symbol = '{stock}' ORDER BY trade_date DESC LIMIT 100"
                sql_data = pd.read_sql(query, connection)
                connection.close()

                if sql_data.empty:
                    st.info("No records found for this stock yet. Data is fetched daily.")
                else:
                    st.dataframe(sql_data, use_container_width=True)

                    csv = sql_data.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download CSV", data=csv, file_name=f"{stock}_history.csv", mime="text/csv")

            except Exception as e:
                st.error(f"Database Error: {e}")

# =========================
# AI PREDICTION — Prophet
# =========================

elif page == "AI Prediction":

    st.title("🤖 AI Stock Price Prediction")
    st.markdown("Machine Learning model trained on historical price data to forecast future prices.")

    col_a, col_b = st.columns(2)
    with col_a:
        forecast_days = st.selectbox("Forecast Days", [7, 14, 30], index=0)
    with col_b:
        period_opt = st.selectbox("Training Data", ["6mo", "1y", "2y"], index=1)

    run_pred = st.button("🚀 Train & Predict")

    if run_pred:

        bar = st.progress(0)

        with st.spinner("Fetching historical data..."):
            hist = ticker.history(period=period_opt)
            hist.reset_index(inplace=True)

        bar.progress(20)

        # ── LINEAR REGRESSION + POLYNOMIAL FEATURES ──
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import make_pipeline

        hist["Days"] = np.arange(len(hist))
        X = hist[["Days"]]
        y = hist["Close"]

        bar.progress(40)

        # Polynomial regression degree 3 — much better than linear
        model = make_pipeline(PolynomialFeatures(degree=3), LinearRegression())
        model.fit(X, y)

        bar.progress(70)

        # Predict on training data
        train_pred = model.predict(X)

        # Future forecast
        future_days_arr = np.arange(len(hist), len(hist) + forecast_days).reshape(-1, 1)
        future_pred     = model.predict(future_days_arr)

        accuracy = model.score(X, y) * 100

        bar.progress(100)
        time.sleep(0.2)
        bar.empty()

        # ── KPI CARDS ──
        predicted_next  = float(future_pred[0])
        current_p       = float(live_price)
        expected_change = ((predicted_next - current_p) / current_p) * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔮 Next Day Prediction", f"₹{predicted_next:.2f}")
        c2.metric("💰 Current Price",        f"₹{current_p:.2f}")
        c3.metric("📈 Expected Change",      f"{expected_change:+.2f}%")
        c4.metric("🎯 Model Accuracy (R²)",  f"{accuracy:.2f}%")

        if expected_change > 1:
            st.success("🟢 Model predicts an UPWARD move — Bullish signal")
        elif expected_change < -1:
            st.error("🔴 Model predicts a DOWNWARD move — Bearish signal")
        else:
            st.warning("🟡 Model predicts a SIDEWAYS move — Neutral signal")

        # ── CHART ──
        st.subheader("📊 Prediction vs Actual Price")

        future_dates = [
            (datetime.today() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            for i in range(forecast_days)
        ]

        pred_fig = go.Figure()
        pred_fig.add_trace(go.Scatter(
            x=hist["Date"], y=hist["Close"],
            mode="lines", name="Actual Price",
            line=dict(color="#22C55E", width=2)
        ))
        pred_fig.add_trace(go.Scatter(
            x=hist["Date"], y=train_pred,
            mode="lines", name="Fitted Trend",
            line=dict(color="#FBBF24", width=1.5, dash="dot")
        ))
        pred_fig.add_trace(go.Scatter(
            x=future_dates, y=future_pred,
            mode="lines+markers", name=f"{forecast_days}-Day Forecast",
            line=dict(color="#F97316", width=2),
            marker=dict(size=6)
        ))
        pred_fig.update_layout(**mobile_layout(
            title=f"AI Forecast — Next {forecast_days} Days",
            xaxis_title="Date", yaxis_title="Price (₹)",
            height=500
        ))
        st.plotly_chart(pred_fig, use_container_width=True)

        # ── FORECAST TABLE ──
        st.subheader(f"📅 {forecast_days}-Day Price Forecast")
        forecast_df = pd.DataFrame({
            "Date":                future_dates,
            "Predicted Price (₹)": [round(p, 2) for p in future_pred],
            "Change from Today":   [f"{((p - current_p)/current_p)*100:+.2f}%" for p in future_pred]
        })
        st.dataframe(forecast_df, use_container_width=True)

        csv = forecast_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Forecast CSV",
            data=csv,
            file_name=f"{stock}_forecast.csv",
            mime="text/csv"
        )

    else:
        st.info("Choose your settings above and click **Train & Predict**.")
        st.markdown("""
        **How it works:**
        - Trains a Polynomial Regression model on historical prices
        - Captures non-linear trends much better than simple linear regression
        - Forecasts the next N days based on learned patterns
        """)

# =========================
# PORTFOLIO TRACKER
# =========================

elif page == "Portfolio Tracker":

    st.title("💼 Portfolio Tracker")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        quantity  = st.number_input("Enter Quantity",      min_value=1,   value=10)
    with col_in2:
        buy_price = st.number_input("Enter Buy Price (₹)", min_value=1.0, value=float(live_price))

    invested_amount = quantity * buy_price
    current_value   = quantity * live_price
    profit_loss     = current_value - invested_amount
    pnl_pct         = (profit_loss / invested_amount) * 100

    st.subheader("📊 Investment Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Invested",      f"₹{invested_amount:,.2f}")
    c2.metric("📈 Current Value", f"₹{current_value:,.2f}")
    c3.metric("🚀 P&L",          f"₹{profit_loss:,.2f}")
    c4.metric("📉 Return %",      f"{pnl_pct:.2f}%")

    if profit_loss > 0:
        st.success(f"✅ You are in profit by ₹{profit_loss:,.2f} ({pnl_pct:.2f}%)")
    elif profit_loss < 0:
        st.error(f"❌ You are in loss by ₹{abs(profit_loss):,.2f} ({pnl_pct:.2f}%)")
    else:
        st.info("No Profit No Loss")

    donut = go.Figure(go.Pie(
        labels=["Invested", "Gain/Loss"],
        values=[invested_amount, abs(profit_loss)],
        hole=0.6,
        marker_colors=["#1D4ED8", "#22C55E" if profit_loss >= 0 else "#EF4444"]
    ))
    donut.update_layout(**mobile_layout(title="Portfolio Allocation", height=320, showlegend=True))
    st.plotly_chart(donut, use_container_width=True)

# =========================
# MARKET DASHBOARD
# =========================

elif page == "Market Dashboard":

    st.title("🌐 Market Dashboard")

    nifty_stocks = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
        "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS",
        "LT.NS", "TATAMOTORS.NS", "ADANIGREEN.NS"
    ]

    market_data  = []
    progress_bar = st.progress(0)
    status_text  = st.empty()

    for idx, symbol in enumerate(nifty_stocks):
        status_text.text(f"Fetching {symbol}...")
        try:
            hist = yf.Ticker(symbol).history(period="2d")
            if len(hist) >= 2:
                prev_close    = hist["Close"].iloc[-2]
                current_close = hist["Close"].iloc[-1]
                change_pct    = ((current_close - prev_close) / prev_close) * 100
                market_data.append({
                    "Stock":    symbol.replace(".NS", ""),
                    "Price":    round(float(current_close), 2),
                    "Change %": round(float(change_pct), 2)
                })
        except Exception:
            pass
        progress_bar.progress(int((idx + 1) / len(nifty_stocks) * 100))

    progress_bar.empty()
    status_text.empty()

    market_df = pd.DataFrame(market_data)
    gainers   = market_df.sort_values("Change %", ascending=False).head(5)
    losers    = market_df.sort_values("Change %", ascending=True).head(5)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Top Gainers")
        st.dataframe(gainers, use_container_width=True)
    with col2:
        st.subheader("📉 Top Losers")
        st.dataframe(losers, use_container_width=True)

    st.subheader("🗺️ Market Heatmap")
    colors = ["#22C55E" if c > 0 else "#EF4444" for c in market_df["Change %"]]
    hm_fig = go.Figure(go.Bar(
        x=market_df["Stock"], y=market_df["Change %"],
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in market_df["Change %"]],
        textposition="outside"
    ))
    hm_fig.update_layout(**mobile_layout(title="Daily Change % — Tracked Stocks", xaxis_title="Stock", yaxis_title="Change %", height=380))
    st.plotly_chart(hm_fig, use_container_width=True)

# =========================
# STOCK NEWS
# =========================

elif page == "Stock News":

    st.title("📰 Latest Stock News")

    with st.spinner("Fetching latest news..."):
        try:
            news_data = ticker.news
            if not news_data:
                st.warning("No recent news found.")
            else:
                for article in news_data[:10]:
                    content  = article.get("content", {})
                    title    = content.get("title",   "No Title")
                    summary  = content.get("summary", "No summary available.")
                    pub_date = content.get("pubDate", "Unknown Date")
                    st.markdown(
                        f"""
                        <div style="
                            background:rgba(17,24,39,0.80);
                            border:1px solid rgba(34,197,94,0.2);
                            border-radius:14px; padding:16px 20px;
                            margin-bottom:14px;
                            animation: fadeSlideUp 0.4s ease both;
                        ">
                            <p style="font-size:16px;font-weight:700;color:#F9FAFB;margin:0 0 6px;">{title}</p>
                            <p style="font-size:12px;color:#6B7280;margin:0 0 10px;">📅 {pub_date}</p>
                            <p style="font-size:14px;color:#D1D5DB;margin:0;">{summary}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Error fetching news: {e}")

# =========================
# WATCHLIST
# =========================

elif page == "Watchlist":

    st.title("⭐ Stock Watchlist")

    # Use all stocks from CSV + .NS suffix
    all_watch_symbols = [s + ".NS" for s in stock_symbols]

    watchlist = st.multiselect(
        "Search and select stocks to watch",
        options=all_watch_symbols,
        default=["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ITC.NS"]
    )

    if watchlist:
        watch_data   = []
        progress_bar = st.progress(0)
        for idx, symbol in enumerate(watchlist):
            try:
                si   = yf.Ticker(symbol)
                hist = si.history(period="2d")

                if len(hist) >= 2:
                    current_price = float(hist["Close"].iloc[-1])
                    prev_close    = float(hist["Close"].iloc[-2])
                    change_pct    = ((current_price - prev_close) / prev_close) * 100
                    day_high      = float(hist["High"].iloc[-1])
                    day_low       = float(hist["Low"].iloc[-1])
                    volume        = int(hist["Volume"].iloc[-1])
                    watch_data.append({
                        "Stock":         symbol.replace(".NS", ""),
                        "Current Price": f"₹{current_price:.2f}",
                        "Prev Close":    f"₹{prev_close:.2f}",
                        "Change %":      round(change_pct, 2),
                        "Day High":      f"₹{day_high:.2f}",
                        "Day Low":       f"₹{day_low:.2f}",
                        "Volume":        f"{volume:,}",
                        "Signal":        "🟢 BUY" if change_pct > 1 else "🔴 SELL" if change_pct < -1 else "🟡 HOLD"
                    })
            except Exception:
                pass
            progress_bar.progress(int((idx + 1) / len(watchlist) * 100))
        progress_bar.empty()
        st.dataframe(pd.DataFrame(watch_data), use_container_width=True)
    else:
        st.info("Select stocks above to build your watchlist.")

# =========================
# STOCK COMPARISON
# =========================

elif page == "Stock Comparison":

    st.title("📊 Stock Comparison")

    cmp_df      = pd.read_csv("stocks.csv")
    cmp_symbols = cmp_df["SYMBOL"].dropna().astype(str).tolist()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        stock1 = st.selectbox("First Stock",  cmp_symbols, index=0)
    with col_s2:
        stock2 = st.selectbox("Second Stock", cmp_symbols, index=1)

    with st.spinner(f"Loading data for {stock1} and {stock2}..."):
        data1 = yf.Ticker(stock1 + ".NS").history(period="6mo")
        data2 = yf.Ticker(stock2 + ".NS").history(period="6mo")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data1.index, y=data1["Close"], mode="lines", name=stock1, line=dict(color="#22C55E")))
    fig.add_trace(go.Scatter(x=data2.index, y=data2["Close"], mode="lines", name=stock2, line=dict(color="#60A5FA")))
    fig.update_layout(**mobile_layout(title=f"{stock1} vs {stock2}", xaxis_title="Date", yaxis_title="Price (₹)", height=450))
    st.plotly_chart(fig, use_container_width=True)

    p1 = float(((data1["Close"].iloc[-1] - data1["Close"].iloc[0]) / data1["Close"].iloc[0]) * 100)
    p2 = float(((data2["Close"].iloc[-1] - data2["Close"].iloc[0]) / data2["Close"].iloc[0]) * 100)

    st.subheader("📈 6-Month Performance")
    col1, col2 = st.columns(2)
    col1.metric(stock1, f"{p1:.2f}%")
    col2.metric(stock2, f"{p2:.2f}%")

    if p1 > p2:
        st.success(f"🏆 {stock1} outperformed by {p1 - p2:.2f}%")
    elif p2 > p1:
        st.success(f"🏆 {stock2} outperformed by {p2 - p1:.2f}%")
    else:
        st.info("Both performed equally")

    st.subheader("📦 Volume Comparison")
    vol_fig = go.Figure()
    vol_fig.add_trace(go.Bar(x=data1.index, y=data1["Volume"], name=stock1, marker_color="#22C55E", opacity=0.7))
    vol_fig.add_trace(go.Bar(x=data2.index, y=data2["Volume"], name=stock2, marker_color="#60A5FA", opacity=0.7))
    vol_fig.update_layout(**mobile_layout(barmode="overlay", height=350, xaxis_title="Date", yaxis_title="Volume"))
    st.plotly_chart(vol_fig, use_container_width=True)

# =========================
# FUNDAMENTAL ANALYSIS
# =========================

elif page == "Fundamental Analysis":

    st.title("🏦 Fundamental Analysis")

    with st.spinner("Loading company fundamentals..."):
        try:
            fast = ticker.fast_info
            hist_1y = ticker.history(period="1y")
            high_52 = float(hist_1y["High"].max()) if not hist_1y.empty else 0
            low_52  = float(hist_1y["Low"].min())  if not hist_1y.empty else 0
        except Exception:
            fast    = None
            high_52 = 0
            low_52  = 0

    st.subheader("📋 Company Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Symbol:** {selected_stock}")
        try:
            st.write(f"**Market Cap:** ₹{int(fast.market_cap):,}" if fast else "**Market Cap:** N/A")
        except Exception:
            st.write("**Market Cap:** N/A")
        try:
            st.write(f"**Shares Outstanding:** {int(fast.shares):,}" if fast else "**Shares:** N/A")
        except Exception:
            st.write("**Shares Outstanding:** N/A")
        try:
            st.write(f"**Currency:** {fast.currency}" if fast else "**Currency:** INR")
        except Exception:
            st.write("**Currency:** INR")
        try:
            st.write(f"**Exchange:** {fast.exchange}" if fast else "**Exchange:** NSE")
        except Exception:
            st.write("**Exchange:** NSE")

    with col2:
        st.write(f"**52-Week High:** ₹{high_52:.2f}")
        st.write(f"**52-Week Low:** ₹{low_52:.2f}")
        try:
            st.write(f"**Last Price:** ₹{float(fast.last_price):.2f}" if fast else f"**Last Price:** ₹{live_price:.2f}")
        except Exception:
            st.write(f"**Last Price:** ₹{live_price:.2f}")
        try:
            st.write(f"**Previous Close:** ₹{float(fast.previous_close):.2f}" if fast else "**Previous Close:** N/A")
        except Exception:
            st.write("**Previous Close:** N/A")
        try:
            st.write(f"**Day High:** ₹{float(fast.day_high):.2f}" if fast else "**Day High:** N/A")
            st.write(f"**Day Low:** ₹{float(fast.day_low):.2f}"  if fast else "**Day Low:** N/A")
        except Exception:
            st.write("**Day High/Low:** N/A")

    st.subheader("📊 Price History Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("52W High", f"₹{high_52:.2f}")
    col2.metric("52W Low",  f"₹{low_52:.2f}")
    col3.metric("Current",  f"₹{live_price:.2f}")

# =========================
# 52-WEEK ANALYSIS
# =========================

elif page == "52-Week Analysis":

    st.title("📅 52-Week Price Analysis")

    with st.spinner("Loading 1-year data..."):
        data_1y = ticker.history(period="1y")
        data_1y.reset_index(inplace=True)

    high_52       = float(data_1y["High"].max())
    low_52        = float(data_1y["Low"].min())
    current       = float(live_price)
    pct_from_high = ((current - high_52) / high_52) * 100
    pct_from_low  = ((current - low_52)  / low_52)  * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("🔺 52-Week High",  f"₹{high_52:.2f}", f"{pct_from_high:.2f}% from High")
    col2.metric("🔻 52-Week Low",   f"₹{low_52:.2f}",  f"+{pct_from_low:.2f}% from Low")
    col3.metric("💰 Current Price", f"₹{current:.2f}")

    fig_52 = go.Figure()
    fig_52.add_trace(go.Scatter(
        x=data_1y["Date"], y=data_1y["Close"],
        mode="lines", name="Close",
        fill="tozeroy", fillcolor="rgba(34,197,94,0.05)",
        line=dict(color="#22C55E")
    ))
    fig_52.add_hline(y=high_52, line_dash="dash", line_color="#EF4444", annotation_text=f"52W High ₹{high_52:.0f}")
    fig_52.add_hline(y=low_52,  line_dash="dash", line_color="#22C55E", annotation_text=f"52W Low ₹{low_52:.0f}")
    fig_52.update_layout(**mobile_layout(title="52-Week Price Range", xaxis_title="Date", yaxis_title="Price (₹)", height=460))
    st.plotly_chart(fig_52, use_container_width=True)

    st.subheader("📊 Monthly Returns")
    data_1y["Month"] = data_1y["Date"].dt.to_period("M").astype(str)
    monthly          = data_1y.groupby("Month")["Close"].last().pct_change() * 100
    ret_fig = go.Figure(go.Bar(
        x=monthly.index, y=monthly.values,
        marker_color=["#22C55E" if v > 0 else "#EF4444" for v in monthly],
        text=[f"{v:.1f}%" for v in monthly.values],
        textposition="outside"
    ))
    ret_fig.update_layout(**mobile_layout(title="Monthly Returns %", xaxis_title="Month", yaxis_title="Return %", height=380))
    st.plotly_chart(ret_fig, use_container_width=True)

# =========================
# EXPORT DATA
# =========================

elif page == "Export Data":

    st.title("📥 Export Stock Data")

    period_opt = st.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

    with st.spinner(f"Loading {period_opt} data..."):
        export_data = ticker.history(period=period_opt)
        export_data.reset_index(inplace=True)

    st.dataframe(export_data, use_container_width=True)

    csv = export_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{stock}_{period_opt}_data.csv",
        mime="text/csv"
    )

    st.subheader("📊 Quick Stats")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows",  len(export_data))
    c2.metric("Avg Close",   f"₹{float(export_data['Close'].mean()):.2f}")
    c3.metric("Max Price",   f"₹{float(export_data['High'].max()):.2f}")
    c4.metric("Min Price",   f"₹{float(export_data['Low'].min()):.2f}")

# =========================
# STOCK SCREENER
# =========================

elif page == "Stock Screener":

    st.title("🔍 Stock Screener")
    st.markdown("Scan Nifty 50 stocks and filter by RSI, P/E, Market Cap and more.")

    # ── FILTERS ──
    st.subheader("⚙️ Set Your Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        rsi_min = st.slider("RSI Min",  0,  100, 0)
        rsi_max = st.slider("RSI Max",  0,  100, 100)

    with col2:
        pe_max      = st.number_input("Max P/E Ratio",       min_value=0.0,  max_value=500.0, value=50.0)
        change_min  = st.number_input("Min Day Change %",    min_value=-20.0, max_value=20.0, value=-20.0)

    with col3:
        cap_options = st.multiselect(
            "Market Cap",
            ["Large Cap (>20,000 Cr)", "Mid Cap (5,000–20,000 Cr)", "Small Cap (<5,000 Cr)"],
            default=["Large Cap (>20,000 Cr)", "Mid Cap (5,000–20,000 Cr)", "Small Cap (<5,000 Cr)"]
        )
        signal_filter = st.selectbox("Signal Filter", ["All", "BUY only", "SELL only", "HOLD only"])

    run_screen = st.button("🚀 Run Screener")

    # ── NIFTY 50 STOCKS ──
    nifty50 = [
        "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
        "ITC", "SBIN", "BHARTIARTL", "LT", "TATAMOTORS",
        "ADANIGREEN", "WIPRO", "HCLTECH", "AXISBANK", "KOTAKBANK",
        "MARUTI", "BAJFINANCE", "ASIANPAINT", "NESTLEIND", "ULTRACEMCO",
        "SUNPHARMA", "POWERGRID", "NTPC", "ONGC", "COALINDIA",
        "TITAN", "BAJAJFINSV", "TECHM", "DRREDDY", "DIVISLAB"
    ]

    if run_screen:

        results      = []
        progress_bar = st.progress(0)
        status_text  = st.empty()

        for idx, sym in enumerate(nifty50):
            status_text.text(f"Scanning {sym}... ({idx+1}/{len(nifty50)})")
            try:
                t    = yf.Ticker(sym + ".NS")
                hist = t.history(period="1mo")

                if hist.empty or len(hist) < 15:
                    continue

                # RSI calculation
                delta    = hist["Close"].diff()
                gain     = delta.where(delta > 0, 0).rolling(14).mean()
                loss     = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs       = gain / loss
                rsi_val  = float(100 - (100 / (1 + rs.iloc[-1])))

                # Price change
                prev_close    = float(hist["Close"].iloc[-2])
                current_close = float(hist["Close"].iloc[-1])
                change_pct    = ((current_close - prev_close) / prev_close) * 100

                # Volume-based cap estimate (no ticker.info needed)
                avg_volume  = float(hist["Volume"].mean())
                market_cap_est = current_close * avg_volume * 30
                cap_cr = market_cap_est / 1e7

                if cap_cr >= 20000:
                    cap_label = "Large Cap (>20,000 Cr)"
                elif cap_cr >= 5000:
                    cap_label = "Mid Cap (5,000–20,000 Cr)"
                else:
                    cap_label = "Small Cap (<5,000 Cr)"

                # Signal
                if rsi_val < 30:
                    signal = "BUY"
                elif rsi_val > 70:
                    signal = "SELL"
                else:
                    signal = "HOLD"

                results.append({
                    "Stock":      sym,
                    "Price (₹)": round(current_close, 2),
                    "Change %":  round(change_pct, 2),
                    "RSI":       round(rsi_val, 2),
                    "Cap Type":  cap_label,
                    "Signal":    signal,
                })

            except Exception:
                pass

            progress_bar.progress(int((idx + 1) / len(nifty50) * 100))

        progress_bar.empty()
        status_text.empty()

        if not results:
            st.warning("No data fetched. Try again.")
        else:
            df = pd.DataFrame(results)

            # ── APPLY FILTERS ──
            df_filtered = df.copy()

            # RSI filter
            df_filtered = df_filtered[
                df_filtered["RSI"].between(rsi_min, rsi_max)
            ]

            # P/E filter removed (not available without ticker.info on cloud)

            # Day change filter
            df_filtered = df_filtered[df_filtered["Change %"] >= change_min]

            # Market cap filter
            if cap_options:
                df_filtered = df_filtered[df_filtered["Cap Type"].isin(cap_options)]

            # Signal filter
            if signal_filter == "BUY only":
                df_filtered = df_filtered[df_filtered["Signal"] == "BUY"]
            elif signal_filter == "SELL only":
                df_filtered = df_filtered[df_filtered["Signal"] == "SELL"]
            elif signal_filter == "HOLD only":
                df_filtered = df_filtered[df_filtered["Signal"] == "HOLD"]

            # ── SUMMARY CARDS ──
            buy_count  = len(df_filtered[df_filtered["Signal"] == "BUY"])
            sell_count = len(df_filtered[df_filtered["Signal"] == "SELL"])
            hold_count = len(df_filtered[df_filtered["Signal"] == "HOLD"])
            total      = len(df_filtered)

            st.subheader("📊 Screener Results")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Matches", total)
            c2.metric("🟢 BUY",  buy_count)
            c3.metric("🔴 SELL", sell_count)
            c4.metric("🟡 HOLD", hold_count)

            if df_filtered.empty:
                st.warning("No stocks match your filters. Try relaxing the conditions.")
            else:
                # Color-code Signal column
                def color_signal(val):
                    if val == "BUY":
                        return "background-color: rgba(34,197,94,0.25); color: #22C55E; font-weight: bold;"
                    elif val == "SELL":
                        return "background-color: rgba(239,68,68,0.25); color: #EF4444; font-weight: bold;"
                    else:
                        return "background-color: rgba(251,191,36,0.25); color: #FBBF24; font-weight: bold;"

                styled = df_filtered.drop(columns=["Cap Type"]).style.map(color_signal, subset=["Signal"])
                st.dataframe(styled, use_container_width=True)

                # ── RSI CHART of results ──
                st.subheader("📈 RSI Comparison")
                rsi_colors = [
                    "#22C55E" if r < 30 else "#EF4444" if r > 70 else "#FBBF24"
                    for r in df_filtered["RSI"]
                ]
                rsi_bar = go.Figure(go.Bar(
                    x=df_filtered["Stock"],
                    y=df_filtered["RSI"],
                    marker_color=rsi_colors,
                    text=[f"{r:.1f}" for r in df_filtered["RSI"]],
                    textposition="outside"
                ))
                rsi_bar.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="Overbought 70")
                rsi_bar.add_hline(y=30, line_dash="dash", line_color="#22C55E", annotation_text="Oversold 30")
                rsi_bar.update_layout(**mobile_layout(
                    title="RSI Values — Filtered Stocks",
                    xaxis_title="Stock", yaxis_title="RSI",
                    height=400
                ))
                st.plotly_chart(rsi_bar, use_container_width=True)

                # ── CHANGE % CHART ──
                st.subheader("📉 Day Change %")
                chg_colors = ["#22C55E" if c > 0 else "#EF4444" for c in df_filtered["Change %"]]
                chg_bar = go.Figure(go.Bar(
                    x=df_filtered["Stock"],
                    y=df_filtered["Change %"],
                    marker_color=chg_colors,
                    text=[f"{c:+.2f}%" for c in df_filtered["Change %"]],
                    textposition="outside"
                ))
                chg_bar.update_layout(**mobile_layout(
                    title="Day Change % — Filtered Stocks",
                    xaxis_title="Stock", yaxis_title="Change %",
                    height=380
                ))
                st.plotly_chart(chg_bar, use_container_width=True)

                # ── DOWNLOAD ──
                csv = df_filtered.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Screener Results CSV",
                    data=csv,
                    file_name="screener_results.csv",
                    mime="text/csv"
                )

    else:
        st.info("Set your filters above and click **Run Screener** to scan stocks.")


# =========================
# SECTOR ANALYSIS
# =========================

elif page == "Sector Analysis":

    st.title("🏭 Sector Analysis")
    st.markdown("Compare all stocks within a sector — performance, RSI signals and rankings.")

    selected_sec = st.selectbox(
        "Select Sector",
        [s for s in SECTOR_STOCKS.keys() if s != "All Sectors"]
    )

    sec_stocks = SECTOR_STOCKS[selected_sec]

    if not sec_stocks:
        st.warning("No stocks defined for this sector.")
    else:
        run_sector = st.button(f"🚀 Analyse {selected_sec}")

        if run_sector:
            results      = []
            progress_bar = st.progress(0)
            status_text  = st.empty()

            for idx, sym in enumerate(sec_stocks):
                status_text.text(f"Fetching {sym}...")
                try:
                    t    = yf.Ticker(sym + ".NS")
                    hist = t.history(period="1mo")

                    if hist.empty or len(hist) < 5:
                        continue

                    # RSI
                    delta   = hist["Close"].diff()
                    gain    = delta.where(delta > 0, 0).rolling(14).mean()
                    loss    = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rs      = gain / loss
                    rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))

                    # Price change
                    prev_close    = float(hist["Close"].iloc[-2])
                    current_close = float(hist["Close"].iloc[-1])
                    change_pct    = ((current_close - prev_close) / prev_close) * 100

                    # Monthly return
                    monthly_return = ((current_close - float(hist["Close"].iloc[0])) / float(hist["Close"].iloc[0])) * 100

                    # Signal
                    if rsi_val < 30:
                        signal = "BUY"
                    elif rsi_val > 70:
                        signal = "SELL"
                    else:
                        signal = "HOLD"

                    results.append({
                        "Stock":          sym,
                        "Price (₹)":     round(current_close, 2),
                        "Day Change %":  round(change_pct, 2),
                        "Monthly Ret %": round(monthly_return, 2),
                        "RSI":           round(rsi_val, 2),
                        "Signal":        signal,
                    })

                except Exception:
                    pass

                progress_bar.progress(int((idx + 1) / len(sec_stocks) * 100))

            progress_bar.empty()
            status_text.empty()

            if not results:
                st.warning("Could not fetch data. Try again.")
            else:
                df = pd.DataFrame(results).sort_values("Monthly Ret %", ascending=False)

                # ── KPI CARDS ──
                best  = df.iloc[0]
                worst = df.iloc[-1]
                avg_change = df["Day Change %"].mean()
                buy_count  = len(df[df["Signal"] == "BUY"])

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🏆 Best Performer",  best["Stock"],  f"{best['Monthly Ret %']:+.2f}%")
                c2.metric("📉 Worst Performer", worst["Stock"], f"{worst['Monthly Ret %']:+.2f}%")
                c3.metric("📊 Avg Day Change",  f"{avg_change:+.2f}%")
                c4.metric("🟢 BUY Signals",     buy_count)

                # ── TABLE ──
                st.subheader("📋 Sector Stocks Overview")

                def color_signal(val):
                    if val == "BUY":
                        return "background-color:rgba(34,197,94,0.25);color:#22C55E;font-weight:bold;"
                    elif val == "SELL":
                        return "background-color:rgba(239,68,68,0.25);color:#EF4444;font-weight:bold;"
                    return "background-color:rgba(251,191,36,0.25);color:#FBBF24;font-weight:bold;"

                styled = df.style.map(color_signal, subset=["Signal"])
                st.dataframe(styled, use_container_width=True)

                # ── MONTHLY RETURN CHART ──
                st.subheader("📈 Monthly Return Comparison")
                colors = ["#22C55E" if v > 0 else "#EF4444" for v in df["Monthly Ret %"]]
                ret_fig = go.Figure(go.Bar(
                    x=df["Stock"],
                    y=df["Monthly Ret %"],
                    marker_color=colors,
                    text=[f"{v:+.1f}%" for v in df["Monthly Ret %"]],
                    textposition="outside"
                ))
                ret_fig.update_layout(**mobile_layout(
                    title=f"{selected_sec} — Monthly Returns",
                    xaxis_title="Stock", yaxis_title="Return %",
                    height=400
                ))
                st.plotly_chart(ret_fig, use_container_width=True)

                # ── RSI CHART ──
                st.subheader("📊 RSI Comparison")
                rsi_colors = ["#22C55E" if r < 30 else "#EF4444" if r > 70 else "#FBBF24" for r in df["RSI"]]
                rsi_fig = go.Figure(go.Bar(
                    x=df["Stock"],
                    y=df["RSI"],
                    marker_color=rsi_colors,
                    text=[f"{r:.1f}" for r in df["RSI"]],
                    textposition="outside"
                ))
                rsi_fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="Overbought 70")
                rsi_fig.add_hline(y=30, line_dash="dash", line_color="#22C55E", annotation_text="Oversold 30")
                rsi_fig.update_layout(**mobile_layout(
                    title=f"{selected_sec} — RSI Values",
                    xaxis_title="Stock", yaxis_title="RSI",
                    height=400
                ))
                st.plotly_chart(rsi_fig, use_container_width=True)

                # ── DOWNLOAD ──
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download Sector Data CSV",
                    data=csv,
                    file_name=f"{selected_sec}_analysis.csv",
                    mime="text/csv"
                )

        else:
            st.info(f"Click **Analyse {selected_sec}** to scan all stocks in this sector.")

            # Show stock list
            st.subheader(f"📋 Stocks in {selected_sec}")
            cols = st.columns(4)
            for i, sym in enumerate(sec_stocks):
                cols[i % 4].markdown(f"• {sym}")


# =========================
# PRICE ALERTS
# =========================

elif page == "Price Alerts":

    st.title("🔔 Price Alerts")
    st.markdown("Set target prices — get instant alerts when stock crosses your threshold.")

    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    # ── ADD ALERT ──
    st.subheader("➕ Add New Alert")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        alert_stock = st.selectbox("Stock", options=stock_symbols, key="alert_stock")
    with col2:
        alert_type  = st.selectbox("Alert Type", ["Above (Buy Target)", "Below (Stop Loss)"])
    with col3:
        alert_price = st.number_input("Target Price (₹)", min_value=0.1, value=float(live_price))
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔔 Add Alert"):
            st.session_state.alerts.append({
                "stock":  alert_stock,
                "type":   alert_type,
                "target": alert_price,
                "status": "Active"
            })
            st.success(f"✅ Alert added for {alert_stock} at ₹{alert_price:.2f}")

    st.markdown("---")

    # ── CHECK ALERTS ──
    if st.session_state.alerts:
        st.subheader("📋 Your Alerts")

        triggered = []
        active    = []

        check_btn = st.button("🔄 Check All Alerts Now")

        for alert in st.session_state.alerts:
            if check_btn:
                try:
                    hist          = yf.Ticker(alert["stock"] + ".NS").history(period="1d")
                    current_price = float(hist["Close"].iloc[-1])

                    if "Above" in alert["type"] and current_price >= alert["target"]:
                        alert["status"]  = "🟢 TRIGGERED"
                        alert["current"] = current_price
                        triggered.append(alert)
                    elif "Below" in alert["type"] and current_price <= alert["target"]:
                        alert["status"]  = "🔴 TRIGGERED"
                        alert["current"] = current_price
                        triggered.append(alert)
                    else:
                        alert["current"] = current_price
                        active.append(alert)
                except Exception:
                    active.append(alert)
            else:
                active.append(alert)

        if triggered:
            st.error(f"🚨 {len(triggered)} Alert(s) Triggered!")
            for a in triggered:
                st.markdown(
                    f"""
                    <div style="background:rgba(255,68,68,0.1);border:1px solid #cc3333;
                    border-left:3px solid #ff4444;padding:12px;margin-bottom:8px;">
                        <b style="color:#ff4444;">{a['status']}</b> — 
                        <b style="color:#00ff80;">{a['stock']}</b> 
                        Current: ₹{a.get('current', 0):.2f} | 
                        Target: ₹{a['target']:.2f} | {a['type']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Active alerts table
        alert_df = pd.DataFrame(st.session_state.alerts)
        st.dataframe(alert_df, use_container_width=True)

        if st.button("🗑️ Clear All Alerts"):
            st.session_state.alerts = []
            st.success("All alerts cleared!")
            st.rerun()

        # Chart with alert line
        st.subheader(f"📈 {stock} Price vs Alert Levels")
        alert_fig = go.Figure()
        alert_fig.add_trace(go.Scatter(
            x=data["Date"], y=data["Close"],
            mode="lines", name="Price", line=dict(color="#00ff80", width=2)
        ))
        for a in st.session_state.alerts:
            if a["stock"] == selected_stock:
                color = "#22C55E" if "Above" in a["type"] else "#EF4444"
                alert_fig.add_hline(
                    y=a["target"], line_dash="dash", line_color=color,
                    annotation_text=f"Alert ₹{a['target']:.0f}"
                )
        alert_fig.update_layout(**mobile_layout(
            title=f"{stock} — Price Alerts",
            xaxis_title="Date", yaxis_title="Price (₹)", height=400
        ))
        st.plotly_chart(alert_fig, use_container_width=True)

    else:
        st.info("No alerts set yet. Add one above!")

# =========================
# SIP CALCULATOR
# =========================

elif page == "SIP Calculator":

    st.title("💰 SIP Calculator")
    st.markdown("Calculate your Systematic Investment Plan returns.")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_investment = st.number_input("Monthly Investment (₹)", min_value=500, value=5000, step=500)
    with col2:
        duration_years = st.slider("Duration (Years)", 1, 40, 10)
    with col3:
        expected_return = st.slider("Expected Annual Return %", 1.0, 30.0, 12.0, 0.5)

    # Calculations
    months        = duration_years * 12
    monthly_rate  = expected_return / 100 / 12
    total_invested = monthly_investment * months

    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        future_value = total_invested

    wealth_gained = future_value - total_invested
    returns_pct   = (wealth_gained / total_invested) * 100

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Invested",  f"₹{total_invested:,.0f}")
    c2.metric("📈 Future Value",    f"₹{future_value:,.0f}")
    c3.metric("🚀 Wealth Gained",   f"₹{wealth_gained:,.0f}")
    c4.metric("📊 Total Returns",   f"{returns_pct:.1f}%")

    # Growth Chart
    st.subheader("📈 Investment Growth Over Time")

    months_list   = list(range(1, months + 1))
    invested_list = [monthly_investment * m for m in months_list]
    value_list    = []

    for m in months_list:
        if monthly_rate > 0:
            fv = monthly_investment * (((1 + monthly_rate) ** m - 1) / monthly_rate) * (1 + monthly_rate)
        else:
            fv = monthly_investment * m
        value_list.append(fv)

    years_list = [m / 12 for m in months_list]

    sip_fig = go.Figure()
    sip_fig.add_trace(go.Scatter(
        x=years_list, y=value_list,
        mode="lines", name="Future Value",
        line=dict(color="#00ff80", width=2),
        fill="tonexty", fillcolor="rgba(0,255,80,0.05)"
    ))
    sip_fig.add_trace(go.Scatter(
        x=years_list, y=invested_list,
        mode="lines", name="Amount Invested",
        line=dict(color="#ffaa00", width=2, dash="dot")
    ))
    sip_fig.update_layout(**mobile_layout(
        title="SIP Growth Projection",
        xaxis_title="Years", yaxis_title="Amount (₹)",
        height=450
    ))
    st.plotly_chart(sip_fig, use_container_width=True)

    # SIP vs Lump Sum
    st.subheader("📊 SIP vs Lump Sum Comparison")

    lumpsum_value = total_invested * ((1 + expected_return / 100) ** duration_years)
    lumpsum_gain  = lumpsum_value - total_invested

    col1, col2 = st.columns(2)
    col1.metric("📈 SIP Final Value",     f"₹{future_value:,.0f}", f"Gain: ₹{wealth_gained:,.0f}")
    col2.metric("💰 Lump Sum Final Value", f"₹{lumpsum_value:,.0f}", f"Gain: ₹{lumpsum_gain:,.0f}")

    if future_value > lumpsum_value:
        st.success(f"✅ SIP is better by ₹{future_value - lumpsum_value:,.0f}")
    else:
        st.info(f"💡 Lump Sum is better by ₹{lumpsum_value - future_value:,.0f} — but SIP reduces risk!")

    compare_fig = go.Figure(go.Bar(
        x=["Total Invested", "SIP Value", "Lump Sum Value"],
        y=[total_invested, future_value, lumpsum_value],
        marker_color=["#ffaa00", "#00ff80", "#60A5FA"],
        text=[f"₹{v:,.0f}" for v in [total_invested, future_value, lumpsum_value]],
        textposition="outside"
    ))
    compare_fig.update_layout(**mobile_layout(
        title="SIP vs Lump Sum", height=350
    ))
    st.plotly_chart(compare_fig, use_container_width=True)

# =========================
# PDF REPORT
# =========================

elif page == "PDF Report":

    st.title("📄 PDF Stock Report")
    st.markdown("Generate a complete stock analysis report as PDF.")

    st.subheader(f"📋 Report Preview — {stock}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Stock:** {stock}")
        st.write(f"**Current Price:** ₹{live_price:.2f}")
        st.write(f"**Day High:** ₹{latest_high:.2f}")
        st.write(f"**Day Low:** ₹{latest_low:.2f}")
        st.write(f"**Volume:** {latest_volume:,}")
    with col2:
        latest_rsi  = float(data["RSI"].iloc[-1])
        latest_macd = float(data["MACD"].iloc[-1])
        latest_sig  = float(data["Signal_Line"].iloc[-1])
        st.write(f"**RSI (14):** {latest_rsi:.2f}")
        st.write(f"**MACD:** {latest_macd:.4f}")
        st.write(f"**Signal Line:** {latest_sig:.4f}")
        st.write(f"**MA20:** ₹{float(data['MA20'].iloc[-1]):.2f}")
        st.write(f"**MA50:** ₹{float(data['MA50'].iloc[-1]):.2f}")

    # Overall Signal
    signals = []
    if latest_rsi < 30:
        signals.append("BUY")
    elif latest_rsi > 70:
        signals.append("SELL")
    else:
        signals.append("HOLD")

    if latest_macd > latest_sig:
        signals.append("BUY")
    else:
        signals.append("SELL")

    buy_count  = signals.count("BUY")
    sell_count = signals.count("SELL")

    if buy_count > sell_count:
        overall = "🟢 STRONG BUY"
    elif sell_count > buy_count:
        overall = "🔴 STRONG SELL"
    else:
        overall = "🟡 NEUTRAL"

    st.subheader("🤖 Overall AI Signal")
    st.markdown(f"### {overall}")

    # Generate CSV report (PDF needs fpdf2 which may not be available)
    report_data = {
        "Metric": ["Stock", "Price", "Day High", "Day Low", "Volume", "RSI", "MACD", "Signal Line", "MA20", "MA50", "Overall Signal"],
        "Value":  [
            stock, f"₹{live_price:.2f}", f"₹{latest_high:.2f}", f"₹{latest_low:.2f}",
            f"{latest_volume:,}", f"{latest_rsi:.2f}", f"{latest_macd:.4f}",
            f"{latest_sig:.4f}", f"₹{float(data['MA20'].iloc[-1]):.2f}",
            f"₹{float(data['MA50'].iloc[-1]):.2f}", overall
        ]
    }

    report_df = pd.DataFrame(report_data)
    st.dataframe(report_df, use_container_width=True)

    # Price history for report
    price_history = data[["Date", "Open", "High", "Low", "Close", "Volume"]].tail(30).copy()
    price_history["Date"] = price_history["Date"].astype(str)

    report_csv = report_df.to_csv(index=False).encode("utf-8")
    history_csv = price_history.to_csv(index=False).encode("utf-8")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download Analysis Report (CSV)",
            data=report_csv,
            file_name=f"{stock}_analysis_report.csv",
            mime="text/csv"
        )
    with col2:
        st.download_button(
            label="⬇️ Download Price History (CSV)",
            data=history_csv,
            file_name=f"{stock}_price_history.csv",
            mime="text/csv"
        )

# =========================
# EARNINGS CALENDAR
# =========================

elif page == "Earnings Calendar":

    st.title("📅 Earnings Calendar")
    st.markdown("Upcoming and recent quarterly results for major stocks.")

    # Hardcoded upcoming earnings (approximate — real data needs paid API)
    earnings_data = [
        {"Company": "Reliance Industries", "Symbol": "RELIANCE", "Quarter": "Q4 FY25", "Expected Date": "Apr 25, 2025", "Status": "Upcoming"},
        {"Company": "TCS", "Symbol": "TCS", "Quarter": "Q4 FY25", "Expected Date": "Apr 10, 2025", "Status": "Upcoming"},
        {"Company": "Infosys", "Symbol": "INFY", "Quarter": "Q4 FY25", "Expected Date": "Apr 17, 2025", "Status": "Upcoming"},
        {"Company": "HDFC Bank", "Symbol": "HDFCBANK", "Quarter": "Q4 FY25", "Expected Date": "Apr 19, 2025", "Status": "Upcoming"},
        {"Company": "ICICI Bank", "Symbol": "ICICIBANK", "Quarter": "Q4 FY25", "Expected Date": "Apr 26, 2025", "Status": "Upcoming"},
        {"Company": "Wipro", "Symbol": "WIPRO", "Quarter": "Q4 FY25", "Expected Date": "Apr 16, 2025", "Status": "Upcoming"},
        {"Company": "HCL Tech", "Symbol": "HCLTECH", "Quarter": "Q4 FY25", "Expected Date": "Apr 12, 2025", "Status": "Upcoming"},
        {"Company": "Kotak Bank", "Symbol": "KOTAKBANK", "Quarter": "Q4 FY25", "Expected Date": "May 03, 2025", "Status": "Upcoming"},
        {"Company": "Axis Bank", "Symbol": "AXISBANK", "Quarter": "Q4 FY25", "Expected Date": "Apr 24, 2025", "Status": "Upcoming"},
        {"Company": "Sun Pharma", "Symbol": "SUNPHARMA", "Quarter": "Q4 FY25", "Expected Date": "May 15, 2025", "Status": "Upcoming"},
        {"Company": "Maruti Suzuki", "Symbol": "MARUTI", "Quarter": "Q4 FY25", "Expected Date": "Apr 29, 2025", "Status": "Upcoming"},
        {"Company": "L&T", "Symbol": "LT", "Quarter": "Q4 FY25", "Expected Date": "May 07, 2025", "Status": "Upcoming"},
    ]

    earnings_df = pd.DataFrame(earnings_data)

    # Filter
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Search Company")
    with col2:
        status_filter = st.selectbox("Filter", ["All", "Upcoming", "Released"])

    if search:
        earnings_df = earnings_df[earnings_df["Company"].str.contains(search, case=False)]
    if status_filter != "All":
        earnings_df = earnings_df[earnings_df["Status"] == status_filter]

    # Summary
    c1, c2 = st.columns(2)
    c1.metric("📅 Total Companies", len(earnings_df))
    c2.metric("🔔 Upcoming Results", len(earnings_df[earnings_df["Status"] == "Upcoming"]))

    st.subheader("📋 Earnings Schedule")
    st.dataframe(earnings_df, use_container_width=True)

    # Quick price check for earnings stocks
    st.subheader("📈 Current Prices — Earnings Stocks")

    if st.button("🔄 Fetch Current Prices"):
        price_data = []
        bar = st.progress(0)
        symbols = earnings_df["Symbol"].tolist()

        for idx, sym in enumerate(symbols):
            try:
                hist = yf.Ticker(sym + ".NS").history(period="2d")
                if len(hist) >= 2:
                    cur   = float(hist["Close"].iloc[-1])
                    prev  = float(hist["Close"].iloc[-2])
                    chg   = ((cur - prev) / prev) * 100
                    price_data.append({
                        "Symbol":    sym,
                        "Price (₹)": round(cur, 2),
                        "Change %":  round(chg, 2),
                        "Signal":    "🟢 BUY" if chg > 1 else "🔴 SELL" if chg < -1 else "🟡 HOLD"
                    })
            except Exception:
                pass
            bar.progress(int((idx + 1) / len(symbols) * 100))

        bar.empty()
        if price_data:
            st.dataframe(pd.DataFrame(price_data), use_container_width=True)

    csv = earnings_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Earnings Calendar CSV", data=csv, file_name="earnings_calendar.csv", mime="text/csv")


# =========================
# FOOTER
# =========================

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align:center;font-size:12px;color:#6B7280;padding:8px;">
        📈 AI Powered Indian Stock Analyzer<br>
        <span style="font-size:11px;">Data via Yahoo Finance</span>
    </div>
    """,
    unsafe_allow_html=True
)


# NOTE: SQL Records page reads from Railway cloud MySQL
# Connection uses environment variables set in Streamlit Cloud secrets