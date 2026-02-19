import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Professional Stock Dashboard", layout="wide")

# ==============================
# SMART TICKER FORMATTER
# ==============================
def format_ticker(ticker):
    ticker = ticker.strip().upper()
    if "." not in ticker and len(ticker) == 4:
        return ticker + ".JK"
    return ticker

# ==============================
# FETCH DATA WITH AUTO FALLBACK
# ==============================
def fetch_data(ticker):
    try:
        df = yf.download(
            ticker,
            period="1d",
            interval="1m",
            progress=False
        )

        # Fix Multi-Index Columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # If empty (market closed), fetch last available day
        if df.empty:
            df = yf.download(
                ticker,
                period="5d",
                interval="1m",
                progress=False
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

        return df

    except Exception:
        return pd.DataFrame()

# ==============================
# CALCULATE 5-MIN CHANGE
# ==============================
def calculate_change(df):
    try:
        if len(df) < 6:
            return None, None

        latest_price = df["Close"].iloc[-1]
        price_5m_ago = df["Close"].iloc[-6]

        pct_change = ((latest_price - price_5m_ago) / price_5m_ago) * 100

        return latest_price, pct_change

    except Exception:
        return None, None

# ==============================
# PLOT SMOOTH CHART
# ==============================
def plot_chart(df, ticker):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            line_shape="spline",
            name=ticker
        )
    )

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="Time",
        yaxis_title="Price",
        yaxis=dict(autorange=True),
        template="plotly_white"
    )

    return fig

# ==============================
# UI HEADER
# ==============================
st.title("📈 Professional Real-Time Stock Dashboard")

search_input = st.text_input(
    "Enter ticker(s) separated by space (example: bbca bbri aapl)",
    value="bbca bbri"
)

tickers = [format_ticker(t) for t in search_input.split() if t.strip() != ""]

# ==============================
# TABS
# ==============================
tab1, tab2 = st.tabs(["Monitor", "Movers"])

# =====================================================
# TAB 1 - MONITOR
# =====================================================
with tab1:

    cols = st.columns(3)

    for i, ticker in enumerate(tickers[:3]):
        with cols[i]:
            try:
                df = fetch_data(ticker)

                if df.empty:
                    st.warning(f"No data for {ticker}")
                    continue

                latest_price, pct_change = calculate_change(df)

                if latest_price is None:
                    st.warning(f"Not enough data for {ticker}")
                    continue

                st.subheader(ticker)
                st.metric(
                    label="Current Price",
                    value=f"{latest_price:.2f}",
                    delta=f"{pct_change:.2f}% (5m)"
                )

                fig = plot_chart(df, ticker)
                st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.error(f"Error loading {ticker}")

# =====================================================
# TAB 2 - MOVERS
# =====================================================
with tab2:

    st.subheader("Market Movers (5-Min Change)")

    # Predefined Watchlist
    watchlist = [
        "BBCA.JK", "BBRI.JK", "TLKM.JK",
        "BMRI.JK", "ASII.JK", "ADRO.JK",
        "GOTO.JK", "ICBP.JK", "INDF.JK",
        "UNTR.JK"
    ]

    movers = []

    for ticker in watchlist:
        try:
            df = fetch_data(ticker)

            if df.empty or len(df) < 6:
                continue

            latest_price = df["Close"].iloc[-1]
            price_5m_ago = df["Close"].iloc[-6]
            pct_change = ((latest_price - price_5m_ago) / price_5m_ago) * 100

            movers.append({
                "Ticker": ticker,
                "Price": round(latest_price, 2),
                "Change (%)": round(pct_change, 2)
            })

        except Exception:
            continue

    try:
        movers_df = pd.DataFrame(movers)

        if not movers_df.empty:
            top_gainers = movers_df.sort_values(
                by="Change (%)",
                ascending=False
            ).head(5)

            top_losers = movers_df.sort_values(
                by="Change (%)",
                ascending=True
            ).head(5)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔥 Top 5 Gainers")
                st.dataframe(top_gainers, use_container_width=True)

            with col2:
                st.subheader("🔻 Top 5 Losers")
                st.dataframe(top_losers, use_container_width=True)

        else:
            st.warning("No movers data available.")

    except Exception:
        st.error("Error processing movers data.")
