import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICES_FOLDER = os.path.join(BASE_DIR, "data", "prices")
MONTH_SUMMARY_FOLDER = os.path.join(BASE_DIR, "data", "best_buy_months_summary")
os.makedirs(MONTH_SUMMARY_FOLDER, exist_ok=True)

def summarize_best_months(ticker):
    file_path = os.path.join(PRICES_FOLDER, f"{ticker}.csv")
    if not os.path.exists(file_path):
        print(f"❌ Data pro {ticker} nenalezena.")
        return

    df = pd.read_csv(file_path, parse_dates=["Date"])
    if df.empty:
        print(f"⚠️ Žádná data pro {ticker}.")
        return

    # Převod sloupce Close na číslo a odstranění chybných hodnot
    df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
    df = df.dropna(subset=["Close"])

    if df.empty:
        print(f"⚠️ Po očištění žádná validní data pro {ticker}.")
        return

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # Najít nejnižší cenu v každém roce (a odpovídající měsíc)
    best_months = df.loc[df.groupby("Year")["Close"].idxmin()]

    # Spočítat četnost jednotlivých měsíců
    month_counts = best_months["Month"].value_counts().sort_values(ascending=False)
    summary_df = month_counts.reset_index()
    summary_df.columns = ['Month', 'Count']

    # Převod čísel na názvy měsíců
    summary_df["Month"] = summary_df["Month"].apply(lambda x: pd.Timestamp(month=int(x), day=1, year=2000).strftime('%B'))

    output_path = os.path.join(MONTH_SUMMARY_FOLDER, f"{ticker}_month_summary.csv")
    summary_df.to_csv(output_path, index=False)
    print(f"✅ Měsíční souhrn pro {ticker} uložen do {output_path}")

def main(tickers):
    for ticker in tickers:
        print(f"\n📅 Zpracovávám {ticker}...")
        summarize_best_months(ticker)

if __name__ == "__main__":
    print("⚠️ Tento skript očekává seznam tickerů jako argument.")
