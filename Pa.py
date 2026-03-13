import yfinance as yf
import pandas as pd

tickers = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

data = []

for t in tickers:
    stock = yf.Ticker(t)
    
    # income statement
    income = stock.financials.T
    
    net_income = income["Net Income"].head(3)
    
    # price history
    price = stock.history(period="3y")
    
    data.append({
        "ticker": t,
        "net_income": net_income
    })

print(data)
