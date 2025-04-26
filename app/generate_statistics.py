import yfinance as yf
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config_assets import ASSETS_TO_WATCH
from claude_client import ask_claude


# Funkce pro získání měsíčního souhrnu cen
def get_monthly_price_summary(ticker, years=3):
    end = datetime.today()
    start = end - relativedelta(years=years)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)

    # Převod MultiIndex columns na jednoduché názvy
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    print(f"📊 Sloupce pro {ticker}: {df.columns.tolist()}")

    if df.empty:
        print(f"⚠️ Data pro {ticker} nejsou dostupná.")
        return None

    # Výběr správného cenového sloupce
    price_col = None
    if 'Close' in df.columns:
        price_col = 'Close'
    elif 'Adj Close' in df.columns:
        price_col = 'Adj Close'
    else:
        print(f"⚠️ Ticker {ticker} neobsahuje sloupec 'Close' ani 'Adj Close'.")
        return None

    # Použití 'ME' místo 'M' kvůli FutureWarning
    summary = df.groupby(pd.Grouper(freq='ME')).agg({price_col: ['mean', 'min', 'max']}).reset_index()
    summary.columns = ['Month', 'mean', 'min', 'max']
    return summary.tail(36)  # poslední 3 roky

# Funkce pro generování promptu pro Claude
def generate_prompt(ticker, summary):
    rows = []
    for idx, row in summary.iterrows():
        date_str = row['Month'].strftime('%Y-%m')
        rows.append(f"{date_str}: avg={row['mean']:.2f}, min={row['min']:.2f}, max={row['max']:.2f}")
    
    prompt = f"Zde jsou měsíční ceny za poslední 3 roky pro {ticker}. Analyzuj data a doporuč nejlepší den v měsíci pro pravidelný nákup, zohledni i ex-dividend data, pokud existují:\n" + "\n".join(rows)
    return prompt

# Hlavní funkce
def main():
    tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]

    for t in tickers:
        print(f"\n===== {t} =====")
        summary = get_monthly_price_summary(t)
        if summary is not None and not summary.empty:
            prompt = generate_prompt(t, summary)
            print(prompt)

            print("\n📨 Odesílám do Claude...")
            response = ask_claude(prompt)
            print(f"\n🤖 Claude doporučuje:\n{response}")
        else:
            print("⚠️ Data nelze načíst.")

if __name__ == "__main__":
    main()
