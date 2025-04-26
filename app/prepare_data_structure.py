import os
import pandas as pd
from config_assets import ASSETS_TO_WATCH

DATA_FOLDER = "../data/prices"

def create_empty_csv(ticker):
    file_path = os.path.join(DATA_FOLDER, f"{ticker}.csv")
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
        df.to_csv(file_path, index=False)
        print(f"✅ Vytvořen soubor: {file_path}")
    else:
        print(f"ℹ️ Soubor už existuje: {file_path}")

def main():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"📁 Vytvořena složka: {DATA_FOLDER}")

    tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]
    for ticker in tickers:
        create_empty_csv(ticker)

if __name__ == "__main__":
    main()
