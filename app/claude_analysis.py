import os
import feedparser
from app.claude_client import ask_claude
import pandas as pd
from datetime import datetime, timedelta

DAYS_BACK = 365  # Prodlouženo na celý rok

def get_market_news(max_items=5):
    print("🔎 Načítám aktuální zprávy z trhů...")
    try:
        rss_feeds = [
            "https://finance.yahoo.com/rss/topstories",
            "https://www.marketwatch.com/rss/topstories",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://www.investing.com/rss/news_25.rss"
        ]

        news_items = []
        for feed_url in rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_items]:
                news_items.append(f"- {entry.title}")

        unique_news = list(dict.fromkeys(news_items))
        print(f"✅ Načteno {len(unique_news[:10])} novinek.")
        return "\n".join(unique_news[:10])
    except Exception as e:
        print(f"❌ Chyba při načítání zpráv: {e}")
        return "Nepodařilo se načíst aktuální zprávy."

def load_recent_data(folder_path):
    months = DAYS_BACK // 30
    print(f"📂 Načítám data z CSV za posledních {months} měsíců...")
    summaries = []
    today = datetime.today()
    date_limit = today - timedelta(days=DAYS_BACK)

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)
                df = pd.read_csv(file_path, parse_dates=["Date"])

                recent_data = df[df["Date"] >= date_limit]

                if not recent_data.empty:
                    summaries.append(f"📄 {filename}:\n{recent_data[['Date', 'Close']].to_string(index=False)}\n")
                else:
                    summaries.append(f"📄 {filename}:\nŽádná data za posledních {months} měsíců.\n")
        print("✅ Data úspěšně načtena.")
        return "\n".join(summaries)
    except Exception as e:
        print(f"❌ Chyba při načítání CSV: {e}")
        return "Nepodařilo se načíst data z CSV."

def load_months_summary(folder_path):
    print("📥 Načítám souhrny nejlevnějších měsíců...")
    summaries = []
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith("_month_summary.csv"):
                ticker = filename.replace("_month_summary.csv", "")
                df = pd.read_csv(os.path.join(folder_path, filename))
                top_months = df.head(3)
                summaries.append(f"{ticker}: Nejčastěji nejlevnější měsíce (poslední roky):\n{top_months.to_string(index=False)}\n")
        return "\n".join(summaries)
    except Exception as e:
        print(f"❌ Chyba při načítání měsíčních souhrnů: {e}")
        return "Nepodařilo se načíst měsíční souhrny."

def load_months_frequency_summary(folder_path):
    print("📊 Vytvářím souhrny četnosti nejlevnějších měsíců...")
    summaries = []
    output_folder = folder_path.replace("best_buy_months_extended_summary", "best_buy_months_frequency_summary")
    os.makedirs(output_folder, exist_ok=True)

    try:
        for filename in os.listdir(folder_path):
            if filename.endswith("_extended_month_summary.csv"):
                ticker = filename.replace("_extended_month_summary.csv", "")
                df = pd.read_csv(os.path.join(folder_path, filename))

                min_months = df.loc[df.groupby('Year')['Avg_Close'].idxmin()]
                month_counts = min_months['Month_Name'].value_counts().reset_index()
                month_counts.columns = ['Month_Name', 'Count']
                month_counts = month_counts.sort_values(by='Count', ascending=False)

                output_file = os.path.join(output_folder, f"{ticker}_month_frequency_summary.csv")
                month_counts.to_csv(output_file, index=False)

                top_months = month_counts.head(3)
                summaries.append(f"{ticker}: Historicky nejčastější levné měsíce:\n{top_months.to_string(index=False)}\n")
        print("✅ Souhrny četnosti vytvořeny.")
        return "\n".join(summaries)
    except Exception as e:
        print(f"❌ Chyba při vytváření souhrnů četnosti: {e}")
        return "Nepodařilo se vytvořit souhrny četnosti."

def run_claude_analysis(extra_summary=""):
    print("🚀 Spouštím analýzu Claude...")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prices_folder = os.path.join(BASE_DIR, "data", "prices")
    months_summary_folder = os.path.join(BASE_DIR, "data", "best_buy_months_summary")
    months_extended_summary_folder = os.path.join(BASE_DIR, "data", "best_buy_months_extended_summary")
    logs_folder = os.path.join(BASE_DIR, "logs")

    os.makedirs(logs_folder, exist_ok=True)

    csv_summary = load_recent_data(prices_folder)
    market_news = get_market_news()
    months_summary = load_months_summary(months_summary_folder)
    months_frequency_summary = load_months_frequency_summary(months_extended_summary_folder)

    today_str = datetime.today().strftime("%Y-%m-%d")
    months = DAYS_BACK // 30

    prompt = f"""
Dnes je {today_str}.

Jsi považován za nejúspěšnějšího investora a analytika všech dob. Máš více než 25 let zkušeností na finančních trzích, spravoval jsi miliardová portfolia a dokázal jsi konzistentně porážet trh díky svým znalostem, intuici a strategii.

Tvá specializace zahrnuje:
- Pokročilou technickou a fundamentální analýzu.
- Využívání sezónnosti, historických dat a tržních cyklů.
- Precizní řízení rizik a identifikaci příležitostí.
- Orientaci na dlouhodobý růst s důrazem na dividendové akcie a ETF.

Nyní ti předkládám aktuální data pro analýzu:

1. **Denní ceny akcií a ETF za posledních {months} měsíců:**
{csv_summary}

2. **Dnešní tržní zprávy:**
{market_news}

3. **Historické nejlevnější měsíce:**
{months_summary}

4. **Dlouhodobá četnost levných měsíců:**
{months_frequency_summary}

🎯 **Tvůj úkol:**
- Pro každý ticker navrhni: `TICKER: XX% BUY, XX% HOLD, XX% SELL` (včetně poznámky, pokud jde o "📢 Okamžitou příležitost k nákupu").
- Vysvětli klíčové důvody doporučení (stručně, ale odborně).
- Upozorni na blížící se levná sezónní období.
- Přidej strategii pro příští týden.
- Pokud odpověď zkrátíš kvůli limitu, uveď to na konci.
"""

    if extra_summary:
        prompt += f"\nNavíc souhrn nejčastějších dnů pro nákup:\n{extra_summary}\n"

    print("📨 Odesílám data do Claude...")

    try:
        response = ask_claude(prompt, model="claude-3-haiku-20240307", max_tokens=5000)
    except Exception as e:
        print(f"❌ Chyba při komunikaci s Claude API: {e}")
        response = "Nepodařilo se získat odpověď od Claude."

    log_file = os.path.join(logs_folder, f"claude_report_{today_str}.txt")

    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(response)
        print(f"✅ Výstup uložen do {log_file}")
    except Exception as e:
        print(f"❌ Chyba při ukládání logu: {e}")

    return response

if __name__ == "__main__":
    run_claude_analysis()
