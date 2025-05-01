import yfinance as yf
df = yf.download("JEPQ", start="2025-04-23", end="2025-05-02")
print(df)
