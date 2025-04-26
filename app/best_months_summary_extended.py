import os
import pandas as pd
from app.config_assets import ASSETS_TO_WATCH

# Spojíme všechny tickery z různých kategorií do jednoho seznamu
TICKERS = [ticker for sublist in ASSETS_TO_WATCH.values() for ticker in sublist]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICES_FOLDER = os.path.join(BASE_DIR, "data", "prices")
EXTENDED_SUMMARY_FOLDER = os.path.join(BASE_DIR, "data", "best_buy_months_extended_summary")

os.makedirs(EXTENDED_SUMMARY_FOLDER, exist_ok=True)

def summarize_extended_months(ticker, years_back=1):
    file_path = os.path.join(PRICES_FOLDER, f"{ticker}.csv")
    if not os.path.exists(file_path):
        print(f"❌ Data pro {ticker} nenalezena.")
        return

    df = pd.read_csv(file_path, parse_dates=["Date"])
    if df.empty:
        print(f"⚠️ Žádná data pro {ticker}.")
        return

    # Převod sloupce Close na čísla
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df = df.dropna(subset=['Close'])

    if df.empty:
        print(f"⚠️ Všechna data 'Close' jsou neplatná pro {ticker}.")
        return

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    try:
        # Měsíční statistiky (průměr, min, max)
        monthly_stats = df.groupby(["Year", "Month"]).agg(
            Avg_Close=("Close", "mean"),
            Min_Close=("Close", "min"),
            Max_Close=("Close", "max")
        ).reset_index()

        monthly_stats["Month_Name"] = monthly_stats["Month"].apply(lambda x: pd.Timestamp(month=int(x), day=1, year=2000).strftime('%B'))
        monthly_stats = monthly_stats[["Year", "Month_Name", "Avg_Close", "Min_Close", "Max_Close"]]

        output_path = os.path.join(EXTENDED_SUMMARY_FOLDER, f"{ticker}_extended_month_summary.csv")
        monthly_stats.to_csv(output_path, index=False)
        print(f"✅ Rozšířený měsíční souhrn pro {ticker} uložen do {output_path}")

        # --- Nejnižší dny za poslední X let ---
        max_year = df['Year'].max()
        min_year = max_year - years_back + 1
        df_recent_years = df[df['Year'] >= min_year]

        lowest_days = []

        for year in range(min_year, max_year + 1):
            for month in range(1, 13):
                monthly_data = df_recent_years[(df_recent_years['Year'] == year) & (df_recent_years['Month'] == month)]
                if not monthly_data.empty:
                    lowest_row = monthly_data.loc[monthly_data['Close'].idxmin()]
                    lowest_days.append({
                        "Year": year,
                        "Month": pd.Timestamp(year=2000, month=month, day=1).strftime('%B'),
                        "Date": lowest_row['Date'].strftime('%Y-%m-%d'),
                        "Lowest_Close": lowest_row['Close']
                    })

        if lowest_days:
            lowest_days_df = pd.DataFrame(lowest_days)
            output_lowest_path = os.path.join(EXTENDED_SUMMARY_FOLDER, f"{ticker}_lowest_days_last_{years_back}_years.csv")
            lowest_days_df.to_csv(output_lowest_path, index=False)
            print(f"✅ Nejnižší dny pro {ticker} za posledních {years_back} let uloženy do {output_lowest_path}")
        else:
            print(f"⚠️ Žádná data pro nejnižší dny za posledních {years_back} let pro {ticker}.")

    except Exception as e:
        print(f"❌ Chyba při zpracování {ticker}: {e}")

def main(tickers, years_back=1):
    print(f"\n📊 Generuji rozšířené měsíční statistiky za posledních {years_back} let...")
    for ticker in tickers:
        print(f"\n📊 Zpracovávám {ticker}...")
        summarize_extended_months(ticker, years_back)

if __name__ == "__main__":
    # Defaultně 1 rok, můžeš změnit na libovolný počet let
    main(TICKERS, years_back=2)
