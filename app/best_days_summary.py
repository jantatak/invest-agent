import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEST_DAYS_FOLDER = os.path.join(BASE_DIR, "data", "best_buy_days")
SUMMARY_FOLDER = os.path.join(BASE_DIR, "data", "best_buy_days_summary")
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

def summarize_best_days(ticker):
    file_path = os.path.join(BEST_DAYS_FOLDER, f"{ticker}_best_days.csv")
    if not os.path.exists(file_path):
        print(f"❌ Data pro {ticker} nenalezena.")
        return

    df = pd.read_csv(file_path, parse_dates=["Date"])
    if df.empty:
        print(f"⚠️ Žádná data pro {ticker}.")
        return

    df['Day'] = df['Date'].dt.day
    day_counts = df['Day'].value_counts().sort_values(ascending=False)
    summary_df = day_counts.reset_index()
    summary_df.columns = ['Day_of_Month', 'Count']

    output_path = os.path.join(SUMMARY_FOLDER, f"{ticker}_day_summary.csv")
    summary_df.to_csv(output_path, index=False)
    print(f"✅ Souhrn pro {ticker} uložen do {output_path}")

def main(tickers):
    for ticker in tickers:
        print(f"\n📊 Zpracovávám {ticker}...")
        summarize_best_days(ticker)

if __name__ == "__main__":
    print("⚠️ Tento skript očekává seznam tickerů jako argument.")
