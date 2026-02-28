import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Saham", layout="wide")

# --- 1. FITUR CACHING UNTUK MENCEGAH RATE LIMIT ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(page, time_range):
    days = 7 if time_range == '1w' else 30 if time_range == '1m' else 90
    stocks = []
    
    start_idx = (page - 1) * 20 + 1
    end_idx = start_idx + 20
    
    dates = [datetime.today() - timedelta(days=x) for x in range(days)]
    dates.reverse() 
    
    for i in range(start_idx, end_idx):
        start_price = np.random.randint(1000, 5000)
        price_changes = np.random.normal(loc=0.5, scale=20, size=days)
        prices = start_price + np.cumsum(price_changes)
        
        df = pd.DataFrame({'Tanggal': dates, 'Harga': prices})
        
        stocks.append({
            'name': f'SAHAM KODE {i}',
            'data': df,
            'min': df['Harga'].min(),
            'max': df['Harga'].max()
        })
        
    return stocks

# --- 2. KOMPONEN GRAFIK KOLOM (BAR CHART) ---
def draw_chart(stock):
    df = stock['data'].copy()
    
    # Menghitung Return (Persentase perubahan harga dari hari sebelumnya)
    df['Return_%'] = df['Harga'].pct_change() * 100
    df['Return_%'] = df['Return_%'].fillna(0) # Hari pertama di-set 0
    
    # Menentukan Warna Kolom: 1 Hari = 1 Kolom
    # Hijau jika Return >= 0, Merah jika Return < 0
    colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['Return_%']]
    
    fig = go.Figure()
    
    # Membuat Grafik Kolom
    fig.add_trace(go.Bar(
        x=df['Tanggal'], 
        y=df['Return_%'], # Sumbu Y adalah Return
        marker_color=colors,
        name='Return Harian',
        # Saat mouse di-hover, tampilkan Tanggal, Return (%), dan Harga Asli (Rp)
        hovertemplate='Tanggal: %{x}<br>Return: %{y:.2f}%<br>Harga: Rp %{customdata:,.0f}<extra></extra>',
        customdata=df['Harga'] 
    ))
    
    # Mengatur layout agar minimalis dan menampilkan Min/Max Harga
    fig.update_layout(
        title={
            'text': f"<b>{stock['name']}</b><br><span style='font-size: 12px; color: #ef4444;'>Min Harga: Rp {stock['min']:.0f}</span> | <span style='font-size: 12px; color: #10b981;'>Max Harga: Rp {stock['max']:.0f}</span>",
            'y':0.9, 'x':0.05, 'xanchor': 'left', 'yanchor': 'top'
        },
        margin=dict(l=20, r=20, t=60, b=20),
        height=250,
        xaxis_title="",
        yaxis_title="Return (%)",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    
    # Menambahkan grid yang tipis
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    # Garis nol (0%) dibuat lebih tebal agar jelas batas positif/negatifnya
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', zeroline=True, zerolinewidth=2, zerolinecolor='black')
    
    return fig

# --- 3. UI DASHBOARD ---
st.title("📊 Dashboard Return Saham (Harian)")

# Manajemen State untuk Halaman 
if 'page' not in st.session_state:
    st.session_state.page = 1

# Kontrol Filter & Paginasi
col_filter, col_spacer, col_prev, col_page, col_next = st.columns([3, 4, 1, 1, 1])

with col_filter:
    time_range = st.radio(
        "Pilih Rentang Waktu:",
        ['1w', '1m', '3m'],
        format_func=lambda x: '1 Minggu' if x == '1w' else '1 Bulan' if x == '1m' else '3 Bulan',
        horizontal=True
    )

with col_prev:
    if st.button("⬅️ Prev", use_container_width=True, disabled=(st.session_state.page == 1)):
        st.session_state.page -= 1
        st.rerun()

with col_page:
    st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold;'>Hal {st.session_state.page}</div>", unsafe_allow_html=True)

with col_next:
    if st.button("Next ➡️", use_container_width=True):
        st.session_state.page += 1
        st.rerun()

st.divider()

# Load data dengan fungsi Caching yang sudah kita buat
with st.spinner('Memuat 20 data saham...'):
    stocks_data = fetch_stock_data(st.session_state.page, time_range)

# Menampilkan 20 Grafik dalam format 2 Kolom
for i in range(0, len(stocks_data), 2):
    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(draw_chart(stocks_data[i]), use_container_width=True)
    with cols[1]:
        if i + 1 < len(stocks_data):
            st.plotly_chart(draw_chart(stocks_data[i+1]), use_container_width=True)
