import pandas as pd
from config_assets import ASSETS_TO_WATCH
from claude_client import ask_claude

def get_full_history_summary(ticker):
    file_path = f"../data/prices/{ticker}.csv"
    try:
        df = pd.read_csv(file_path, skiprows=[1], parse_dates=['Date'])
    except FileNotFoundError:
        print(f"❌ Soubor pro {ticker} nenalezen.")
        return None

    if df.empty:
        print(f"⚠️ Data pro {ticker} jsou prázdná.")
        return None

    average_close = df['Close'].mean()
    min_close = df['Close'].min()
    max_close = df['Close'].max()
    latest_close = df['Close'].iloc[-1]

    return {
        "latest_close": float(latest_close),
        "average_close": float(average_close),
        "min_close": float(min_close),
        "max_close": float(max_close)
    }

def generate_prompt(ticker, summary):
    prompt = (
        f"Analyzuj historická denní data pro {ticker} a doporuč obchodní strategii.\n"
        f"- Aktuální cena: {summary['latest_close']:.2f} USD\n"
        f"- Průměrná cena: {summary['average_close']:.2f} USD\n"
        f"- Minimum: {summary['min_close']:.2f} USD\n"
        f"- Maximum: {summary['max_close']:.2f} USD\n"
        "Zohledni vývoj ceny za celé období a navrhni, zda BUY / SELL / HOLD pro krátkodobé obchodování."
    )
    return prompt

def main():
    tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]

    for t in tickers:
        print(f"\n===== {t} =====")
        summary = get_full_history_summary(t)
        if summary:
            prompt = generate_prompt(t, summary)
            print(prompt)

            print("\n📨 Odesílám do Claude...")
            response = ask_claude(prompt)
            print(f"\n🤖 Claude doporučuje:\n{response}")
        else:
            print("❌ Data nelze načíst nebo soubor chybí.")

if __name__ == "__main__":
    main()
