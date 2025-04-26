import os
import pandas as pd
from config_assets import ASSETS_TO_WATCH
from claude_client import ask_claude

BEST_DAYS_FOLDER = "../data/best_buy_days"

def prepare_prompt(ticker, best_days_df):
    # Připravíme textový seznam pro Claude
    day_counts = best_days_df['Date'].dt.day.value_counts().sort_index()

    summary_lines = [f"Den {day}: {count}x byl nejlevnější den v měsíci" for day, count in day_counts.items()]
    summary_text = "\n".join(summary_lines)

    prompt = (
        f"Analyzuj historická data nejlevnějších dnů v měsíci pro {ticker}.\n"
        f"Zde je počet výskytů, kdy byl konkrétní den v měsíci nejlevnější za celé období:\n\n"
        f"{summary_text}\n\n"
        "➤ Na základě této statistiky vytvoř investiční kalendář:\n"
        "- Urči ideální den v měsíci pro pravidelnou investici (např. 1x měsíčně fixní den).\n"
        "- Označ měsíce, kdy bývají ceny výrazně nižší a doporučil bys nárazovou větší investici.\n"
        "- Zohledni volatilitu a sezónní trendy.\n"
        "- Navrhni strategii pro dlouhodobého investora.\n"
    )
    return prompt

def main():
    tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]

    for ticker in tickers:
        print(f"\n===== {ticker} =====")
        file_path = os.path.join(BEST_DAYS_FOLDER, f"{ticker}_best_days.csv")
        if not os.path.exists(file_path):
            print(f"❌ Chybí data pro {ticker}")
            continue

        best_days_df = pd.read_csv(file_path, parse_dates=["Date"])

        if best_days_df.empty:
            print(f"⚠️ Žádná data pro {ticker}")
            continue

        prompt = prepare_prompt(ticker, best_days_df)
        print("📨 Odesílám prompt do Claude...")

        response = ask_claude(prompt)
        print(f"\n🤖 Claude doporučuje pro {ticker}:\n{response}")

if __name__ == "__main__":
    main()
