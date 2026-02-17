import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- FUNGSI CORE ---
def calculate_swings_with_points(prices, threshold=0.02):
    total_up = 0
    total_down = 0
    last_pivot = prices[0]
    direction = 0 
    
    pivot_points = [] # Untuk keperluan visualisasi
    
    for i, p in enumerate(prices):
        diff = (p - last_pivot) / last_pivot
        
        if direction <= 0 and diff >= threshold:
            total_up += diff
            last_pivot = p
            direction = 1
            pivot_points.append((i, p, 'up'))
            
        elif direction >= 0 and diff <= -threshold:
            total_down += diff
            last_pivot = p
            direction = -1
            pivot_points.append((i, p, 'down'))
            
        elif (direction <= 0 and p < last_pivot) or (direction >= 0 and p > last_pivot):
            last_pivot = p
            
    return total_up, total_down, pivot_points

# --- UI DASHBOARD ---
st.set_page_config(page_title="Price Swing Tracker", layout="wide")
st.title("📈 Swing Points & Volatility Dashboard")

# Sidebar untuk Input
st.sidebar.header("Konfigurasi")
threshold = st.sidebar.slider("Threshold Swing (%)", 0.5, 10.0, 2.0) / 100
data_points = st.sidebar.number_input("Jumlah Data Dummy", 50, 1000, 200)

# Generate Dummy Data (Simulasi Harga Saham/Kripto)
np.random.seed(42)
returns = np.random.normal(0, 0.01, data_points)
prices = 100 * (1 + returns).cumprod()

# Hitung Swing
up, down, pivots = calculate_swings_with_points(prices, threshold)

# --- VISUALISASI ---
col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()
    # Plot Harga Asli
    fig.add_trace(go.Scatter(y=prices, mode='lines', name='Price', line=dict(color='gray', width=1)))
    
    # Plot Titik Pivot
    if pivots:
        idx, vals, types = zip(*pivots)
        colors = ['green' if t == 'up' else 'red' for t in types]
        fig.add_trace(go.Scatter(x=idx, y=vals, mode='markers+lines', 
                                 marker=dict(color=colors, size=8),
                                 line=dict(dash='dash', color='rgba(0,0,0,0.3)'),
                                 name='Swing Points'))

    fig.update_layout(title="Deteksi Swing Harga", template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Total Cumulative Up", f"{up:.2%}")
    st.metric("Total Cumulative Down", f"{abs(down):.2%}")
    st.metric("Net Momentum", f"{(up + down):.2%}")
    
    st.write("---")
    st.write("**Ringkasan Logika:**")
    st.caption(f"Mendeteksi perubahan harga minimal **{threshold*100}%** dari titik pivot terakhir.")

# Tabel Data
if st.checkbox("Lihat Data Mentah"):
    df_pivots = pd.DataFrame(pivots, columns=['Index', 'Price', 'Type'])
    st.dataframe(df_pivots, use_container_width=True)

