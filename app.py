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

    .stApp {
        background:
        radial-gradient(circle at top right, rgba(0,255,100,0.10), transparent 30%),
        radial-gradient(circle at bottom left, rgba(0,150,255,0.08), transparent 30%),
        linear-gradient(135deg, #050B18 0%, #081223 50%, #0F172A 100%);
        color: white;
    }

    .block-container {
        background: rgba(10,15,30,0.65);
        border-radius: 20px;
        padding: clamp(1rem, 3vw, 2rem);
        backdrop-filter: blur(10px);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1220, #111827);
        border-right: 1px solid #1F2937;
    }

    [data-testid="metric-container"] {
        background: rgba(17,24,39,0.95);
        border: 1px solid rgba(34,197,94,0.25);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0,255,100,0.10);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeSlideUp 0.5s ease both;
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 0 28px rgba(0,255,100,0.22);
    }

    h1, h2, h3 {
        color: #F9FAFB;
        font-weight: 700;
        animation: fadeSlideUp 0.4s ease both;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(90deg, #16A34A, #22C55E);
        color: white;
        border: none;
        font-weight: bold;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(34,197,94,0.35);
    }

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        animation: fadeSlideUp 0.5s ease both;
    }

    .js-plotly-plot { animation: fadeIn 0.6s ease both; }

    @keyframes tickerScroll {
        0%   { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    .ticker-track {
        display: flex;
        gap: 40px;
        animation: tickerScroll 30s linear infinite;
        white-space: nowrap;
    }

    .ticker-wrap {
        overflow: hidden;
        background: linear-gradient(90deg, #0B1220, #111827);
        padding: 14px 0;
        border-radius: 18px;
        margin-bottom: 25px;
        border: 1px solid rgba(34,197,94,0.2);
        font-size: 16px;
        font-weight: bold;
        color: white;
    }

    @keyframes skeletonPulse {
        0%   { opacity: 0.4; }
        50%  { opacity: 0.8; }
        100% { opacity: 0.4; }
    }

    .skeleton {
        background: rgba(34,197,94,0.12);
        border-radius: 10px;
        height: 80px;
        animation: skeletonPulse 1.4s ease-in-out infinite;
        margin-bottom: 12px;
    }

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }

    .stSpinner > div { border-top-color: #22C55E !important; }

    .stProgress > div > div {
        background: linear-gradient(90deg, #16A34A, #22C55E) !important;
        border-radius: 99px;
    }

    @media (max-width: 768px) {
        [data-testid="column"] { min-width: 100% !important; flex: 1 1 100% !important; }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1rem !important; }
        [data-testid="metric-container"] { padding: 12px !important; border-radius: 12px !important; }
        .ticker-wrap { font-size: 13px !important; }
        .block-container { padding: 0.75rem !important; border-radius: 12px !important; }
        .js-plotly-plot .plotly { height: 300px !important; }
        .stDownloadButton > button { width: 100% !important; }
    }

    @media (max-width: 480px) {
        h1 { font-size: 1.2rem !important; }
        [data-testid="metric-container"] { padding: 10px !important; }
        .block-container { padding: 0.5rem !important; }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown(
    """
    <div style="
        text-align:center; padding:18px; border-radius:18px;
        background:rgba(17,24,39,0.90); border:1px solid rgba(34,197,94,0.25);
        margin-bottom:20px; box-shadow:0 0 20px rgba(0,255,100,0.08);
    ">
    <h2 style="margin:0;color:white;">📈 Indian Stock Analyzer</h2>
    <p style="color:#9CA3AF;margin-top:8px;font-size:14px;">AI Powered Market Intelligence</p>
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
    ]
)

# =========================
# STOCK SEARCH FROM CSV
# =========================

stock_df      = pd.read_csv("stocks.csv")
stock_symbols = stock_df["SYMBOL"].dropna().astype(str).tolist()

selected_stock = st.sidebar.selectbox("🔍 Search Stock", options=stock_symbols)
stock          = selected_stock + ".NS"

# =========================
# LIVE MARKET TICKER
# =========================

try:
    with st.spinner("Loading live market data..."):
        nifty    = yf.download("^NSEI",       period="2d", progress=False)
        sensex   = yf.download("^BSESN",      period="2d", progress=False)
        reliance = yf.download("RELIANCE.NS", period="2d", progress=False)
        tcs      = yf.download("TCS.NS",      period="2d", progress=False)
        wipro    = yf.download("WIPRO.NS",    period="2d", progress=False)

    def get_change(df):
        latest   = float(df["Close"].iloc[-1])
        previous = float(df["Close"].iloc[-2])
        return ((latest - previous) / previous) * 100

    def ticker_item(label, change):
        color = "#22C55E" if change >= 0 else "#EF4444"
        arrow = "▲" if change >= 0 else "▼"
        return f'<span style="color:{color};">{arrow} {label} {change:+.2f}%</span>'

    items = "  &nbsp;|&nbsp;  ".join([
        ticker_item("NIFTY",    get_change(nifty)),
        ticker_item("SENSEX",   get_change(sensex)),
        ticker_item("RELIANCE", get_change(reliance)),
        ticker_item("TCS",      get_change(tcs)),
        ticker_item("WIPRO",    get_change(wipro)),
    ])

    st.markdown(
        f"""
        <div class="ticker-wrap">
            <div class="ticker-track">{items} &nbsp;&nbsp;&nbsp; {items}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

except Exception:
    st.warning("⚠️ Live Market Ticker unavailable")

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
        plot_bgcolor="rgba(15,23,42,0.6)",
        font=dict(color="#E5E7EB"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=10, r=10, t=50, b=10),
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

    watchlist = st.multiselect(
        "Select stocks to watch",
        ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
         "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS",
         "LT.NS", "TATAMOTORS.NS", "ADANIGREEN.NS"]
    )

    if watchlist:
        watch_data   = []
        progress_bar = st.progress(0)
        for idx, symbol in enumerate(watchlist):
            try:
                si            = yf.Ticker(symbol)
                try:
                    si_info = si.info
                except Exception:
                    si_info = {}
                current_price = si_info.get("currentPrice", 0)
                prev_close    = si_info.get("previousClose", current_price)
                change_pct    = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0
                watch_data.append({
                    "Stock":         symbol,
                    "Current Price": f"₹{current_price:.2f}",
                    "Prev Close":    f"₹{prev_close:.2f}",
                    "Change %":      round(change_pct, 2)
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
            info = ticker.info
        except Exception:
            info = {}
            st.warning("⚠️ Could not load fundamentals — Yahoo Finance rate limit. Try again in a moment.")

    st.subheader("📋 Company Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Company:** {info.get('longName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Market Cap:** ₹{info.get('marketCap', 0):,}")
        st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
        st.write(f"**EPS (TTM):** {info.get('trailingEps', 'N/A')}")

    with col2:
        div_yield = info.get("dividendYield", 0) or 0
        st.write(f"**Dividend Yield:** {div_yield * 100:.2f}%")
        st.write(f"**52-Week High:** ₹{info.get('fiftyTwoWeekHigh', 'N/A')}")
        st.write(f"**52-Week Low:** ₹{info.get('fiftyTwoWeekLow', 'N/A')}")
        st.write(f"**Beta:** {info.get('beta', 'N/A')}")
        st.write(f"**Book Value:** {info.get('bookValue', 'N/A')}")
        st.write(f"**Price to Book:** {info.get('priceToBook', 'N/A')}")

    st.subheader("📝 Business Summary")
    with st.expander("Read full summary"):
        st.write(info.get("longBusinessSummary", "No summary available."))

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
                info = t.info
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

                # Fundamentals
                pe         = info.get("trailingPE",  None)
                market_cap = info.get("marketCap",   0) or 0
                cap_cr     = market_cap / 1e7   # convert to crores

                # Market cap category
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
                    "Stock":       sym,
                    "Price (₹)":  round(current_close, 2),
                    "Change %":   round(change_pct, 2),
                    "RSI":        round(rsi_val, 2),
                    "P/E":        round(pe, 2) if pe else "N/A",
                    "Market Cap": f"₹{cap_cr:,.0f} Cr",
                    "Cap Type":   cap_label,
                    "Signal":     signal,
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

            # P/E filter (skip N/A rows)
            df_filtered = df_filtered[
                df_filtered["P/E"].apply(lambda x: float(x) <= pe_max if x != "N/A" else True)
            ]

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

                styled = df_filtered.drop(columns=["Cap Type"]).style.applymap(
                    color_signal, subset=["Signal"]
                )
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