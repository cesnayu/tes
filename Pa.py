import streamlit as st
import yfinance as yf

st.title("Stock Dashboard")

ticker = st.text_input("Ticker", "BBCA.JK")

stock = yf.Ticker(ticker)

data = stock.history(period="3y")

st.subheader("Price Data")
st.dataframe(data)

st.line_chart(data["Close"])
