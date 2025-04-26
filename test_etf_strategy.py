import pandas as pd
from market_data.etf_strategy import get_monthly_price_summary, generate_prompt
from config_assets import ASSETS_TO_WATCH
from app.claude_client import ask_claude

# ✅ Načteš všechny ETF a akcie z configu
tickers = ASSETS_TO_WATCH["etf"] + ASSETS_TO_WATCH["stocks"]

for t in tickers:
    print(f"\n===== {t} =====")
    summary = get_monthly_price_summary(t)

    if isinstance(summary, pd.DataFrame) and not summary.empty:
        prompt = generate_prompt(t, summary)
        print(prompt)

        print("\n📨 Odesílám do Claude...")
        response = ask_claude(prompt)
        print(f"\n🤖 Claude doporučuje:\n{response}")
    else:
        print("Data nelze načíst.")
