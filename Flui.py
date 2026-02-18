import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock Focus Dashboard")

# --- FUNGSI AMBIL DATA ---
def get_stock_data(ticker):
    try:
        # Ambil data 1 menit
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        # Jika market tutup/libur, ambil data hari terakhir tersedia
        if df.empty:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if not df.empty:
                last_date = df.index[-1].date()
                df = df[df.index.date == last_date]
        
        # Penting: Ratakan kolom jika Multi-Index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df.dropna(subset=['Close'])
    except:
        return None

# --- UI ---
st.title("📈 Anti-Flat Stock Dashboard")
search_input = st.text_input("Ketik Kode Saham (Pisahkan Spasi):", "BBCA.JK BBRI.JK BMRI.JK")
tickers = [t.strip().upper() for t in search_input.split() if t.strip()]

if tickers:
    for i in range(0, len(tickers), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(tickers):
                ticker = tickers[idx]
                with cols[j]:
                    df = get_stock_data(ticker)
                    
                    if df is not None and not df.empty:
                        prices = df['Close']
                        last_price = float(prices.iloc[-1])
                        open_price = float(prices.iloc[0])
                        change = last_price - open_price
                        pct_change = (change / open_price) * 100
                        
                        # Tentukan warna
                        color = "#00FF41" if change >= 0 else "#FF4B4B"

                        # Menghitung Range Y agar tidak flat (Margin 0.5% atas bawah)
                        y_min = prices.min() * 0.998
                        y_max = prices.max() * 1.002

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df.index, 
                            y=prices,
                            mode='lines',
                            line=dict(color=color, width=2.5),
                            # Jangan gunakan fill='tozeroy' karena ini yang bikin flat!
                            # Gunakan fill='tonexty' atau tanpa fill untuk tampilan lebih bersih
                            name=ticker
                        ))

                        fig.update_layout(
                            title=f"<b>{ticker}</b>: {last_price:,.0f} ({pct_change:+.2f}%)",
                            template="plotly_dark",
                            height=350,
                            margin=dict(l=10, r=10, t=50, b=10),
                            xaxis=dict(showgrid=False),
                            yaxis=dict(
                                showgrid=True, 
                                gridcolor="#333", 
                                side="right",
                                # KUNCI UTAMA: Membatasi range hanya di sekitar harga
                                range=[y_min, y_max], 
                                autorange=False, # Matikan otomatis agar tidak narik ke 0
                                tickformat=",.0f"
                            ),
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Data {ticker} Kosong")
