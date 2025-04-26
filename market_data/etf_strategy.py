
import yfinance as yf
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_monthly_price_summary(ticker, years=3):
    end = datetime.today()
    start = end - relativedelta(years=years)
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)

    # 🔹 Převod MultiIndex columns na jednoduché názvy
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    print(f"📊 Sloupce pro {ticker}: {df.columns.tolist()}")

    if df.empty:
        print(f"⚠️ Data pro {ticker} nejsou dostupná.")
        return {}

    # Výběr správného cenového sloupce
    price_col = None
    if 'Close' in df.columns:
        price_col = 'Close'
    elif 'Adj Close' in df.columns:
        price_col = 'Adj Close'
    else:
        print(f"⚠️ Ticker {ticker} neobsahuje sloupec 'Close' ani 'Adj Close'.")
        return {}

    summary = df.groupby(pd.Grouper(freq='M')).agg({price_col: ['mean', 'min', 'max']}).reset_index()
    summary.columns = ['Month', 'mean', 'min', 'max']
    return summary.tail(36)  # poslední 3 roky jako ukázka

def generate_prompt(ticker, summary):
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            f"{row['Month'].strftime('%Y-%m')}: avg={row['mean']:.2f}, min={row['min']:.2f}, max={row['max']:.2f}"
        )
    prompt = (
        f"Zde jsou měsíční ceny za poslední 3 roky pro {ticker}. "
        f"Analyzuj data a doporuč nejlepší den v měsíci pro pravidelný nákup, "
        f"zohledni i ex-dividend data, pokud existují:\n" + "\n".join(rows)
    )
    return prompt
