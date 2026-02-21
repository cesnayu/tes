import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. DAFTAR SAHAM ANDA (Edit di sini) ---
LIST_SAHAM = ["BBCA.JK", "BBRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK", "ADRO.JK"]

# Konfigurasi Halaman
st.set_page_config(layout="wide", page_title="Stock Grid Dashboard")
st.title("📈 Performance Dashboard (%)")

# 2. Fungsi Ambil Data dengan Cache (Mencegah Limit)
@st.cache_data(ttl=3600) # Data disimpan 1 jam, tidak akan download ulang
def get_bulk_data(tickers, start, end):
    try:
        # Menarik semua data sekaligus (Bulk)
        data = yf.download(tickers, start=start, end=end, group_by='ticker', progress=False)
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data: {e}")
        return None

# Sidebar untuk filter waktu
rentang = st.sidebar.selectbox("Pilih Rentang Waktu", ["1 bln", "6 bln", "1 thn"])
days_map = {"1 bln": 30, "6 bln": 180, "1 thn": 365}

end_date = datetime.now()
start_date = end_date - timedelta(days=days_map[rentang])

# 3. Proses Pengambilan Data
data_raw = get_bulk_data(LIST_SAHAM, start_date, end_date)

if data_raw is not None:
    # Membuat Layout Kotak-kotak (3 kolom)
    cols = st.columns(3)
    
    for i, ticker in enumerate(LIST_SAHAM):
        with cols[i % 3]:
            try:
                # Mengambil kolom Close untuk saham tertentu
                if len(LIST_SAHAM) > 1:
                    df_ticker = data_raw[ticker]['Close'].dropna()
                else:
                    df_ticker = data_raw['Close'].dropna()

                if not df_ticker.empty:
                    # Normalisasi: Harga awal jadi 0%
                    harga_awal = df_ticker.iloc[0]
                    pct_change = ((df_ticker / harga_awal) - 1) * 100
                    
                    # Hitung Statistik
                    min_p = pct_change.min()
                    max_p = pct_change.max()
                    jarak_persen = max_p - min_p
                    harga_terakhir = df_ticker.iloc[-1]

                    # Buat Grafik Line Standard
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=pct_change.index, 
                        y=pct_change, 
                        mode='lines',
                        line=dict(width=2, color='#1f77b4')
                    ))

                    fig.update_layout(
                        title=f"<b>{ticker}</b>",
                        height=280,
                        margin=dict(l=10, r=10, t=40, b=10),
                        template="plotly_dark",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(ticksuffix="%"),
                        # Garis horizontal di 0%
                        shapes=[dict(type='line', y0=0, y1=0, x0=pct_change.index[0], x1=pct_change.index[-1], 
                                     line=dict(color='gray', width=1, dash='dot'))]
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Menampilkan info di bawah grafik
                    st.markdown(f"""
                    <div style='background-color: #262730; padding: 10px; border-radius: 5px;'>
                    Harga: <b>Rp {harga_terakhir:,.0f}</b> | Range: <b>{jarak_persen:.2f}%</b>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("") # Spacer
            except:
                st.warning(f"Data {ticker} tidak tersedia.")
