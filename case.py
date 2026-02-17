# --- Update pada bagian Tab List ---
for i, t in enumerate(current_batch):
    with cols[i % 3]:
        df = st.session_state.stock_data[t]['Close'].dropna().tail(30) # Ambil 30 hari terakhir
        if not df.empty:
            first_p = df.iloc[0] # Harga awal sebagai basis 0%
            last_p = df.iloc[-1]
            change_pct = ((last_p - first_p) / first_p) * 100
            daily_change = ((last_p - df.iloc[-2]) / df.iloc[-2]) * 100
            
            # Buat figure dengan secondary y-axis
            from plotly.subplots import make_subplots
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # Trace 1: Harga (Sumbu Kiri)
            fig.add_trace(
                go.Scatter(x=df.index, y=df, name="Harga", line_color='blue', fill='tozeroy'),
                secondary_y=False,
            )

            # Trace 2: Persentase (Sumbu Kanan)
            # Kita buat dummy trace agar sumbu kanan sinkron dengan sumbu kiri
            fig.add_trace(
                go.Scatter(x=df.index, y=((df / first_p) - 1) * 100, name="Perubahan %", opacity=0),
                secondary_y=True,
            )

            fig.update_layout(
                title=f"<b>{t}</b> <br>Hari ini: {daily_change:+.2f}% | Total: {change_pct:+.2f}%",
                title_font_size=14,
                height=300,
                margin=dict(l=0, r=0, t=50, b=0),
                showlegend=False,
                xaxis_visible=False
            )

            # Label Sumbu
            fig.update_yaxes(title_text="Harga (IDR)", secondary_y=False, tickfont_size=10)
            fig.update_yaxes(title_text="Return %", secondary_y=True, tickfont_size=10, side="right")

            st.plotly_chart(fig, use_container_width=True)
