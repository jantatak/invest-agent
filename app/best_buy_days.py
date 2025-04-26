import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "prices")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data", "best_buy_days")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def find_best_buy_days(ticker):
    file_path = os.path.join(INPUT_FOLDER, f"{ticker}.csv")
    if not os.path.exists(file_path):
        print(f"❌ Data pro {ticker} nenalezena.")
        return

    df = pd.read_csv(file_path, parse_dates=["Date"])

    if df.empty:
        print(f"⚠️ Žádná data pro {ticker}.")
        return

    # Převod sloupce Close na číslo + odstranění neplatných hodnot
    df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
    df = df.dropna(subset=["Close"])

    if df.empty:
        print(f"⚠️ Po vyčištění žádná platná data pro {ticker}.")
        return

    df["YearMonth"] = df["Date"].dt.to_period("M")
    best_days = df.loc[df.groupby("YearMonth")["Close"].idxmin()]
    best_days = best_days[["Date", "Close"]].sort_values("Date")

    output_path = os.path.join(OUTPUT_FOLDER, f"{ticker}_best_days.csv")
    best_days.to_csv(output_path, index=False)
    print(f"✅ Nejlepší dny pro {ticker} uloženy do {output_path}")

def main(tickers):
    report = []
    for ticker in tickers:
        find_best_buy_days(ticker)
        file_path = os.path.join(OUTPUT_FOLDER, f"{ticker}_best_days.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, parse_dates=["Date"])
            if not df.empty:
                # Zajištění, že Close je číslo
                df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
                df = df.dropna(subset=["Close"])
                if not df.empty:
                    last_day = df.iloc[-1]
                    report.append(f"{ticker}: {last_day['Date'].date()} za {last_day['Close']:.2f} USD")
                else:
                    report.append(f"{ticker}: ⚠️ Žádná platná data po vyčištění.")
            else:
                report.append(f"{ticker}: ⚠️ Soubor je prázdný.")
        else:
            report.append(f"{ticker}: ⚠️ Výstupní soubor nenalezen.")
    return "\n".join(report)

if __name__ == "__main__":
    print("⚠️ Tento skript očekává seznam tickerů jako argument.")
