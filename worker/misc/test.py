import yfinance as yf

# https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=nvidia&apikey=0PYQLP64BOPZPR80

tick = yf.Ticker("AAPL")
print(tick.info)