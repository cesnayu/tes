import yfinance as yf

bbca = yf.Ticker("BBCA.JK")
print(bbca.fast_info)
print(bbca.get_income_stmt())
