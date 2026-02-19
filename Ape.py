import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide", page_title="Stock Monitor")

# List saham untuk Tab 2
DAFTAR_SAHAM = ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", "GOTO.JK"]

def ambil_data(kode_raw):
    """Fungsi download data yang paling stabil"""
    nama = kode_raw.strip().upper()
    if len(nama) == 4 and "." not in nama:
        ticker = f"{nama}.JK"
    else:
        ticker = nama
        
    df = yf.download(ticker, period="1d", interval="1m", progress=False)
    
    # Jika market tutup, ambil data backup
    if df is None or df.empty:
        df = yf.download(ticker, period="5d", interval="1m", progress=False)
        
    if df is not None and not df.empty:
        # Ratakan kolom (Fix Multi-index)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df['Close'].astype(float).dropna(), ticker
        
    return None, ticker

st.title("📊 Real-Time Stock Pulse")

t1, t2 = st.tabs(["🔍 Search", "⚡ Pergerakan 5 Menit"])

with t1:
    input_user = st.text_input("Masukkan kode saham:", "BBCA BBRI")
    list_input = input_user.split()
    if list_input:
        for i in range(0, len(list_input), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(list_input):
                    with cols[j]:
                        data_close, nama_fix = ambil_data(list_input[idx])
                        if data_close is not None and len(data_close) >= 2:
                            sekarang = float(data_close.iloc[-1])
                            # Ambil harga 5 menit lalu
                            posisi_lama = -6 if len(data_close) >= 6 else 0
                            harga_lama = float(data_close.iloc[posisi_lama])
                            
                            # Hitung persentase
                            skor = ((sekarang - harga_lama) / harga_lama) * 100
                            
                            fig = go.Figure(go.Scatter(
                                x=data_close.index, y=data_close.values,
                                mode='lines', line=dict(color="#00FF41" if skor >= 0 else "#FF4B4B", width=2)
                            ))
                            fig.update_layout(
                                title=f"<b>{nama_fix}</b>: {sekarang:,.0f} ({skor:+.2f}%)",
                                template="plotly_dark", height=250, margin=dict(l=5,r=5,t=40,b=5),
                                yaxis=dict(autorange=True, side="right")
                            )
                            st.plotly_chart(fig, use_container_width=True)

with t2:
    if st.button("Update Data"):
        st.rerun()
    
    hasil_analisa = []
    for s in DAFTAR_SAHAM:
        p, n = ambil_data(s)
        
        # Validasi data
        if p is not None and len(p) >= 2:
            current_val = float(p.iloc[-1])
            past_val = float(p.iloc[-6]) if len(p) >= 6 else float(p.iloc[0])
            
            # Ganti rumus & nama variabel (Tanpa diff_pct)
            persen_baru = ((current_val - past_val) / past_val) * 100
            
            # Simpan ke list
            baris = {"Ticker": n, "Harga": current_val, "Update_5m": persen_baru}
            hasil_analisa.append(baris)
            
    if len(hasil_analisa) > 0:
        df_final = pd.DataFrame(hasil_analisa)
        df_urut = df_final.sort_values("Update_5m", ascending=False)
        
        c1, c2 = st.columns(2)
        with c1:
            st.success("🚀 TOP GAINERS")
            st.table(df_urut.head(5))
        with c2:
            st.error("📉 TOP LOSERS")
            st.table(df_urut.tail(5))
