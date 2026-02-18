import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Smart Stock Dashboard")

# --- FUNGSI AMBIL DATA (DENGAN AUTO .JK) ---
def get_stock_data(ticker_input):
    # Logika Auto-Suffix: Jika 4 huruf dan tidak ada titik, tambahkan .JK
    if len(ticker_input) == 4 and "." not in ticker_input:
        ticker = f"{ticker_input}.JK"
    else:
        ticker = ticker_input
        
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if df.empty:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df.dropna(subset=['Close']), ticker
    except:
        return None, ticker_input

# --- UI ---
st.title("📈 Smart Intraday Dashboard")
st.markdown("Ketik `bbca bbri tlkm` (tanpa .JK sudah otomatis)")

search_input = st.text_input("Search:", "BBCA BBRI BMRI")
tickers_raw = [t.strip().upper() for t in search_input.split() if t.strip()]

if tickers_raw:
    for i in range(0, len(tickers_raw), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(tickers_raw):
                with cols[j]:
                    df, full_ticker = get_stock_data(tickers_raw[idx])
                    
                    if df is not None and not df.empty:
                        prices = df['Close']
                        
                        # FITUR SMOOTHING: Menambahkan Moving Average 5 menit
                        # Agar grafik tidak terlalu "berduri" (seperti per)
                        df['Smooth'] = prices.rolling(window=5, min_periods=1).mean()
                        
                        last_price = float(prices.iloc[-1])
                        open_price = float(prices.iloc[0])
                        change = last_price - open_price
                        pct_change = (change / open_price) * 100
                        color = "#00FF41" if change >= 0 else "#FF4B4B"

                        # Set Range Y agar pas (tidak flat)
                        y_min, y_max = prices.min() * 0.999, prices.max() * 1.001

                        fig = go.Figure()
                        
                        # Garis Asli (Tipis/Transparan)
                        fig.add_trace(go.Scatter(
                            x=df.index, y=prices,
                            mode='lines', line=dict(color=color, width=1, shape='spline'),
                            opacity=0.3, name="Asli"
                        ))
                        
                        # Garis Smooth (Tebal)
                        fig.add_trace(go.Scatter(
                            x=df.index, y=df['Smooth'],
                            mode='lines', line=dict(color=color, width=3, shape='spline'),
                            name="Smooth"
                        ))

                        fig.update_layout(
                            title=f"<b>{full_ticker}</b>: {last_price:,.0f} ({pct_change:+.2f}%)",
                            template="plotly_dark",
                            height=350,
                            margin=dict(l=10, r=10, t=50, b=10),
                            showlegend=False,
                            yaxis=dict(range=[y_min, y_max], autorange=False, side="right"),
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Ticker {tickers_raw[idx]} Error")
